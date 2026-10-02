# Functional Flow Cheat Sheet (developer view)

For each flow: steps → model → state → method that moves it → accounting/stock effect.
✔ = model names, states and method names checked against the **Odoo 18 source** in this workspace. States/labels differ slightly in older versions (e.g. payment states) — look at the version on the test machine (`grep -n "state = fields.Selection" -A8 addons/<module>/models/<file>.py`).

---

## 0. Big picture
```
Customer side (Order-to-Cash)                  Vendor side (Procure-to-Pay)
Quotation → Sales Order → Delivery → Invoice → Payment      RFQ → Purchase Order → Receipt → Vendor Bill → Payment
 sale.order   sale.order   stock.picking  account.move  account.payment   purchase.order  purchase.order  stock.picking  account.move  account.payment
```
Everything that touches money ends as an `account.move` (journal entry) with `account.move.line` rows. Everything that touches stock ends as `stock.move` → `stock.move.line` (+ `stock.quant` = on-hand quantity per product/location/lot).

---

## 1. Order-to-Cash

| # | Step | Model / state | Method (UI button) | Effect |
|---|---|---|---|---|
| 1 | Create quotation | `sale.order` `draft` ("Quotation") | — | no stock/accounting effect |
| 2 | Send by email | `sent` ("Quotation Sent") | `action_quotation_send` | chatter message + template |
| 3 | **Confirm** | `sale` ("Sales Order") | `action_confirm` → `_action_confirm` | creates delivery (`stock.picking`) via procurement rules/routes; locks if setting enabled (`locked` field) |
| 4 | Delivery | `stock.picking` `draft → confirmed/waiting → assigned (Ready) → done` | `action_confirm`, `action_assign` (reserve), **`button_validate`** → `_action_done` | `stock.move.line` done, `stock.quant` decreases; backorder wizard if partial |
| 5 | Invoice | `account.move` `move_type='out_invoice'`, `draft` | SO button "Create Invoice" → wizard → `_create_invoices` (uses `_prepare_invoice`) | invoice lines copy SO lines; SO line `qty_invoiced` updates |
| 6 | **Post** invoice | `posted` | `action_post` (`_post`) | gets number; journal entry becomes final |
| 7 | Payment | `account.payment` `draft → in_process → paid` (v18) | "Pay" / register payment wizard → `action_post` | payment entry; **reconciled** with invoice receivable line; invoice `payment_state` → `in_payment`/`paid`/`partial` |

Key fields
- `sale.order.invoice_status`: `no` (nothing to invoice) · `to invoice` · `invoiced` · `upselling` ✔
- `product.template.invoice_policy`: `order` (invoice ordered qty) vs `delivery` (invoice delivered qty) ✔ — decides whether step 5 is possible before step 4.
- `account.move.payment_state`: `not_paid, in_payment, paid, partial, reversed, blocked` ✔ (`invoicing_legacy` too)
- `account.move.state`: `draft, posted, cancel` (`button_draft` resets, `button_cancel` cancels).
- Invoice status vs picking: you can invoice before delivery with policy `order`.

Accounting entries
```
Customer invoice (posted):      Dr Accounts Receivable      total
                                    Cr Income (product/category account)   untaxed amount
                                    Cr Tax payable (tax account)           tax amount
Customer payment (bank journal): Dr Bank (or Outstanding Receipts)  amount
                                    Cr Accounts Receivable          amount        ← reconciled with invoice line
Credit note (reverse):          Dr Income / Tax,  Cr Receivable (move_type='out_refund')
```
With **automated (real-time) inventory valuation** (product category property) add at delivery:
`Dr Cost of Goods Sold / Cr Stock Valuation (Inventory)` — created by `stock_account` (`_account_entry_move`, svl = stock valuation layer) at `button_validate`.

Reports to know: Sales Analysis, Invoices Analysis, Aged Receivable, Customer statement.

---

## 2. Procure-to-Pay

| # | Step | Model / state | Method | Effect |
|---|---|---|---|---|
| 1 | RFQ | `purchase.order` `draft` ("RFQ") | — | none |
| 2 | Send RFQ | `sent` | `action_rfq_send` | email |
| 3 | **Confirm order** | `purchase` ("Purchase Order") | `button_confirm` → may go to `to approve` first if double validation (`company.po_double_validation`, amount ≥ `po_double_validation_amount`) | creates receipt (`stock.picking` incoming) |
| 3b | Approve | `to approve → purchase` | `button_approve` | manager approval step |
| 4 | Receipt | `stock.picking` incoming | `button_validate` | `stock.quant` increases; valuation layer created |
| 5 | Vendor bill | `account.move` `move_type='in_invoice'`, `draft` | PO button "Create Bill" → `action_create_invoice` | bill lines from PO lines |
| 6 | Post bill | `posted` | `action_post` | entry final |
| 7 | Pay | `account.payment` (outbound) | register payment | reconciles payable |
- States ✔: `draft, sent, to approve, purchase, done (Locked), cancel`.
- `product.purchase_method` ✔: `purchase` (control bills on ordered qty) vs `receive` (on received qty) — decides if you can bill before receiving.
- 3-way match = PO ↔ receipt ↔ bill quantities/prices.

Accounting
```
Vendor bill (posted):  Dr Expense / Stock Input (product account)  untaxed
                       Dr Tax receivable (input tax)               tax
                           Cr Accounts Payable                     total
Vendor payment:        Dr Accounts Payable   Cr Bank/Outstanding Payments
Receipt with real-time valuation: Dr Stock Valuation  Cr Stock Interim (Received)   (cleared when bill is posted)
```

---

## 3. Inventory basics

- **Locations** (`stock.location`): `usage` = internal / customer / supplier / inventory (adjustments) / production / transit / view. A warehouse = tree of locations (Stock, Input, Output…).
- **Operation types** (`stock.picking.type`): Receipts, Delivery Orders, Internal Transfers, Manufacturing… (each with sequence, default locations, "allow new products"…).
- **Moves**: `stock.move` (demand: product + qty + from/to) → `stock.move.line` (reserved/done: specific lot, location, qty). `stock.picking` groups moves.
- **Quants**: `stock.quant` = physical stock per product/location/lot/package. Inventory adjustment = writes `inventory_quantity` then `action_apply_inventory`.
- **Tracking**: product `tracking` = `none` / `lot` (many units per lot) / `serial` (1 per serial). Lots = `stock.lot`.
- **Routes / rules** (`stock.route`, `stock.rule`): Buy, Manufacture, Make-to-order (MTO), Dropship; "Replenishment" via reordering rules (`stock.warehouse.orderpoint`: min/max).
- **Reservation**: `action_assign` reserves available quants → picking `assigned` (Ready) when fully reserved; `confirmed` (Waiting) when not.
- **Backorder**: validating partial quantities offers backorder (new picking for remainder).
- **Valuation** (product category): costing method (Standard / FIFO / AVCO) × valuation (Manual / Automated). Valuation layers `stock.valuation.layer` hold qty & value per move.
- **Scrap**, **returns** (reverse transfer wizard), **units of measure** (`uom.uom`, conversion factors – common bug source).
- Stock states ✔: `draft, waiting (Waiting Another Operation), confirmed (Waiting), assigned (Ready), done, cancel`.
- Your experience: barcode/QR lot scan → create/assign `stock.lot` + set done qty on `stock.move.line`.

---

## 4. Accounting basics

- **Chart of accounts** (`account.account`): types asset/liability/equity/income/expense (receivable, payable, bank, cash…).
- **Journals** (`account.journal`): Sales, Purchase, Bank, Cash, Miscellaneous; each has a sequence and default accounts.
- **Journal entry** = `account.move` (`move_type='entry'`) with balanced lines (Σ debit = Σ credit). Invoices/bills/payments are specialised moves: `out_invoice, out_refund, in_invoice, in_refund, entry`.
- **Taxes** (`account.tax`): percent/fixed, price included or excluded, tax repartition → accounts, tax groups. Fiscal positions map taxes/accounts per partner.
- **Payment terms** (`account.payment.term`): due date lines (e.g. 30 days, 50% now).
- **Reconciliation**: matching debit & credit lines on a reconcilable account (receivable/payable) → `account.partial.reconcile` / `account.full.reconcile`; bank reconciliation matches statement lines with entries.
- **Lock dates** (fiscal lock / tax lock): block posting into closed periods.
- **Multi-currency**: `currency_id` on moves/lines + exchange rate difference entries.
- **Analytic accounting** (`account.analytic.account`, plans in v17+): tag lines for cost/profit centres; budgets (enterprise or OCA/om_account_budget).
- **Reports**: Trial Balance, General Ledger, Partner Ledger, Aged Receivable/Payable, Profit & Loss, Balance Sheet, Tax report.
- Dev tips: never write into `account.move.line` directly for posted moves; use `button_draft` → edit → `action_post`, or reversal (`_reverse_moves`). Amounts computed in `_compute_amount`; payment state in `_compute_payment_state`.

---

## 5. Manufacturing (if asked)  — states `to_close` and method `button_mark_done` ✔; the rest from experience ◇

`BoM` (`mrp.bom`, lines = components, operations) → `Manufacturing Order` (`mrp.production`): `draft → confirmed → progress → to_close → done` · Work orders (`mrp.workorder`) per operation · consumes components (stock moves raw), produces finished good · cost = components + work centre cost. Multi-level BoM: finished good (FG) built from semi-finished (SFG). Methods: `action_confirm`, `button_mark_done`. Valuation: Dr Stock FG / Cr Stock components (+ work centre expense).

---

## 6. HR / Payroll / Approvals (your strong area) — leave states ✔; expense/payroll flow ◇

- **Employee** (`hr.employee`), contract (`hr.contract` in ≤17), departments, job positions, leaves (`hr.leave` ✔ v18: `confirm` To Approve → `validate1` Second Approval → `validate` Approved; or `refuse` / `cancel`), attendances, expenses (`hr.expense` → `hr.expense.sheet`: submit → approve → post → pay).
- ◇ (not in the community source here; from experience) **Payroll** (Enterprise, or OCA/community `payroll`): salary structure → rules (python/amount) → `hr.payslip` (`draft → verify → done → cancel`) → payslip run (batch) → accounting entry (Dr salary expense, Cr payable/bank).
- **Approvals**: tier validation (OCA `base_tier_validation`): tier definitions by model + domain + reviewer → reviews `waiting/pending/approved/rejected` → record locked until validated.

---

## 7. Other common apps in 30 seconds
- **CRM**: lead → opportunity (`crm.lead`) → stages → won/lost → quotation. 
- **Project / Timesheet**: `project.project` → `project.task` (stages) → `account.analytic.line` timesheets → billable via SO (service products: "timesheets on tasks").
- **Helpdesk** (Enterprise / OCA `helpdesk_mgmt`): ticket → stage → SLA → close.
- **Subscriptions / recurring**: recurring plans create invoices on schedule (cron).
- **Website/eCommerce**: product → cart → checkout → SO → payment transaction (`payment.transaction`) → invoice.
- **POS**: session → orders (`pos.order`) → payments → closing entry.
- **Multi-company**: `company_id` on records, intercompany rules, per-company chart of accounts.

---

## 8. Mapping flows to developer tasks (what a test task might ask)
| Likely requirement | Where to hook |
|---|---|
| "When SO is confirmed, do X" | override `sale.order.action_confirm` (call `super()` first) |
| "Add field to invoice / print on report" | `_inherit = "account.move"` + inherit view/report template |
| "Validate delivery only if…" | override `stock.picking.button_validate` (check conditions, `raise UserError`) |
| "Create invoice automatically" | `order._create_invoices()` then `invoice.action_post()` |
| "Approval before confirming PO/payment" | tier validation, or state `to approve` + group-guarded button |
| "Custom report / Excel" | QWeb report or xlsxwriter controller + `read_group`/SQL |
| "Sync with external system" | cron + `external_id` + REST client (see `05-api-and-integrations.md`) |
| "Restrict by company/department" | record rule on the model (see cheat sheet §8) |
| "Auto-number" | `ir.sequence` + `create` override |
| "Notify on state change" | `message_post` / mail template / activity |

## 9. How to practise the flow in 15 minutes (local Odoo 18)
1. Install Sales, Inventory, Purchase, Accounting (`-i sale_management,stock,purchase,account`) with demo data.
2. Create a storable product; create a PO for 10 units → confirm → receive → bill → pay.
3. Create an SO for 4 units → confirm → validate delivery → invoice → post → register payment.
4. Open **Accounting → Journal Entries** and read each entry's debit/credit lines; open **Inventory → Reporting → Stock** to see moves/quants.
5. Open the Odoo shell and look at the records:
```python
so = env['sale.order'].search([], limit=1)
so.state, so.invoice_status, so.picking_ids.mapped('state'), so.invoice_ids.mapped('payment_state')
so.invoice_ids.line_ids.mapped(lambda l: (l.account_id.code, l.debit, l.credit))
```
