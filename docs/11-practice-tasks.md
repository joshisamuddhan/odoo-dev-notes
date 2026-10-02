# Practice tasks (timed). Use no AI; docs/search allowed. Work in a fresh folder, DB `practice_N`.

Rubric for each: installs on a fresh DB (/10) · works end-to-end (/20) · security & validation (/15) · code quality (/15) · README/demo (/10) · edge cases (/10) · API/report/etc. as asked (/20).

## Task A — Room Booking (3h)
Models: `booking.room` (name, capacity, active), `booking.reservation` (room, partner, start, end, state draft/confirmed/cancelled, seq name).
Rules: no overlapping confirmed reservations for same room (constraint); end > start; capacity vs `attendees`.
UI: statusbar buttons Confirm/Cancel, list with decoration, calendar view (bonus), search filters by room/date.
Security: Booking User (own reservations only) / Booking Manager (all).
Extras: PDF confirmation slip, cron cancelling unconfirmed drafts older than 2 days, mail on confirm.
API: `GET /api/bookings?room_id=&date_from=` (pagination), `POST /api/bookings` (validation + 409 on overlap).

## Task B — Expense Approval (3h)
Expense request with lines, total computed, 2-tier approval (manager if > 1000, director if > 10000), reject with reason (wizard), chatter tracking, approval history tab, dashboard pivot by state.
Security: employee sees own; approver sees assigned; record rules.

## Task C — Integration Sync (2.5h)
Pull products from a public mock API (e.g. `https://fakestoreapi.com/products` or `https://dummyjson.com/products` — pagination), upsert into `product.template` using an `external_id`, per-record error handling, "Sync now" button, last-sync timestamp, cron every hour, log model with success/fail counts. Handle timeouts/retries.

## Task D — Debug & Fix (1.5h)
Take `library_demo`, introduce 5 bugs (missing ACL for wizard, wrong `@api.depends`, attrs syntax for wrong version, action defined after the view in manifest, SQL injection in a controller) → have a friend/AI-free self-check list find them. Practise reading tracebacks.

## Task E — Report & Wizard (2h)
Sales summary wizard: date range + partner → PDF (QWeb) and XLSX (xlsxwriter) with totals per product; `read_group`/SQL aggregation, not Python loops.

## After every task
1. Fresh DB install test · 2. `09-security-performance-checklist.md` · 3. List what ate time · 4. Add the lesson to `08-troubleshooting.md`.
