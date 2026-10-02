# Odoo Cheat Sheet (written for v18; version differences in 03-version-differences.md)

## 1. Module layout
```
my_module/
  __init__.py            # from . import models, controllers, wizard
  __manifest__.py
  models/ views/ security/ data/ wizard/ report/ controllers/ static/ tests/ i18n/
```
Manifest keys: `name, version, depends, data, demo, assets, application, installable, license`.
`data` ORDER: security → data/sequences → views that define actions → views using those actions → menus.
(`%(module.action_xmlid)d` in a button is resolved at load time -> the action file must load first.)

## 2. Model & fields
```python
class Thing(models.Model):
    _name = "x.thing"                 # new model (table x_thing)
    _description = "Thing"            # REQUIRED (warning otherwise)
    _inherit = ["mail.thread", "mail.activity.mixin"]   # chatter
    _order = "name"; _rec_name = "name"; _check_company_auto = True
```
| Field | Notes |
|---|---|
| `Char/Text/Html/Integer/Float/Boolean/Date/Datetime/Binary/Selection/Json` | `Float(digits=(16,2))` |
| `Monetary(currency_field=)` | needs a currency Many2one |
| `Many2one(comodel, ondelete="restrict"/"cascade"/"set null", domain=, check_company=True)` | |
| `One2many(comodel, inverse_name)` / `Many2many(comodel)` | write commands below |
| common kwargs | `required, readonly, index, copy, default, tracking, string, help, groups, company_dependent, store, compute, inverse, search, related` |
Computed: `compute="_compute_x"`, `store=True` to persist/search/group; non-stored needs `search=` to be searchable.
Related: `partner_name = fields.Char(related="partner_id.name", store=True)`.
Default: `default=lambda self: self.env.user.id`; `fields.Date.context_today`; `fields.Datetime.now`.
Selection add: `selection_add=[("x", "X")], ondelete={"x": "set default"}`.

## 3. Decorators
```python
@api.depends("line_ids.price", "qty")      # compute; list EVERY field used (dotted for related)
@api.depends_context("company")            # compute depends on context
@api.constrains("date_from", "date_to")    # python validation, raise ValidationError
@api.onchange("partner_id")                # UI only, not persisted until save
@api.model                                 # no recordset (self is empty), e.g. cron, defaults
@api.model_create_multi                    # create(self, vals_list)
@api.ondelete(at_uninstall=False)          # block unlink: raise UserError
```
Compute pattern (ALWAYS loop `for rec in self`, ALWAYS assign every record):
```python
@api.depends("line_ids.subtotal")
def _compute_total(self):
    for rec in self:
        rec.total = sum(rec.line_ids.mapped("subtotal"))
```
Inverse (make a computed field editable): `inverse="_inverse_x"`.
Prefer compute over onchange when the value is derivable. `@api.onchange` can return `{"warning": {"title": "", "message": ""}}`.

## 4. ORM operations
```python
Model = self.env["x.thing"]
Model.create({...}) / Model.create([{...}, {...}])
rec.write({...});  rec.unlink();  rec.copy({"name": "x"})
Model.browse(ids);  rec.exists()   # filter deleted
Model.search(domain, limit=, offset=, order="name desc")
Model.search_count(domain);  Model.search_read(domain, ["name"], limit=5)
Model.read_group / _read_group   # aggregation, avoids python loops
rec.mapped("line_ids.price");  recs.filtered(lambda r: r.state == "x");  recs.sorted("name")
recs.ids; recs.with_context(k=v); recs.with_company(c); recs.with_user(u); recs.sudo()
rec.ensure_one();  rec.id; len(recs); recs[0]; recs | other; recs & other; recs - other
rec.display_name; rec.env.user; rec.env.company; rec.env.context.get("active_ids")
self.env.ref("module.xmlid")      # raise_if_not_found=False
fields.Date.today(); fields.Datetime.now(); fields.Date.context_today(self)
```
Domain: `[("a", "=", 1), "|", ("b", "ilike", "x"), ("c", "in", [1, 2]), "!", ("d", "=", False)]`
Operators: `= != > < >= <= like ilike =like =ilike in not in child_of parent_of any not any`
(`('line_ids', 'any', [('qty', '>', 5)])` — sub-domain on x2many.)

x2many write commands: `Command.create(vals)`, `.update(id, vals)`, `.delete(id)`, `.unlink(id)`, `.link(id)`, `.clear()`, `.set(ids)`
(`from odoo import Command`; old tuples `(0,0,v) (1,id,v) (2,id) (3,id) (4,id) (5,) (6,0,ids)`).

Override pattern:
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list: ...
    return super().create(vals_list)
def write(self, vals):
    res = super().write(vals); return res
```
Performance: no `search()` inside loops (batch with `in`), use `mapped`, `read_group`, `search_fetch`, prefetch works on recordsets, avoid `self.env.cr.commit()` in request code.

Errors: `from odoo.exceptions import UserError, ValidationError, AccessError, MissingError, RedirectWarning`.
Translatable strings: `_("Text %s", value)` (v17+ lazy) ; v14-16 `_("Text %s") % value`.

## 5. Inheritance
| Need | Code |
|---|---|
| Extend model (same table) | `_inherit = "res.partner"` + new fields/methods |
| New model copying another | `_name = "new"; _inherit = "old"` |
| Delegation (join table) | `_inherits = {"res.partner": "partner_id"}` |
| Mixin/abstract | `models.AbstractModel` |
| Extend view | `<record><field name="inherit_id" ref="base.view_partner_form"/>` + xpath |
```xml
<record id="view_partner_form_inherit" model="ir.ui.view">
  <field name="name">res.partner.form.inherit.x</field>
  <field name="model">res.partner</field>
  <field name="inherit_id" ref="base.view_partner_form"/>
  <field name="arch" type="xml">
    <xpath expr="//field[@name='phone']" position="after"><field name="my_field"/></xpath>
    <field name="email" position="attributes"><attribute name="required">1</attribute></field>
    <xpath expr="//notebook" position="inside"><page string="X"><field name="x_ids"/></page></xpath>
  </field>
</record>
```
positions: `before after inside replace attributes`. Find xmlids: Settings → Technical → Views, or grep `odoo/addons/*/views`.
MRO: Python multiple inheritance — later module overrides earlier; always call `super()`.

## 6. Views (v18 syntax)
- `<list>` (v16/17: `<tree>`), `<form>`, `<search>`, `<kanban>`, `<graph>`, `<pivot>`, `<calendar>`, `<gantt>(ent)`, `<activity>`.
- Conditions are Python expressions: `invisible="state != 'draft'"`, `readonly="state != 'draft'"`, `required="type == 'x'"`,
  list column: `column_invisible="True"`. (v16 and below: `attrs="{'invisible': [('state','!=','draft')]}"`.)
- Buttons: `<button name="action_x" type="object" string="X" class="btn-primary" invisible="..." confirm="Sure?"/>`; `type="action"` calls an action xmlid.
- Widgets: `statusbar badge many2many_tags many2one_avatar_user handle monetary percentage progressbar priority boolean_toggle image binary html phone email url radio selection_badge`.
- Decorations in lists: `decoration-danger/success/warning/info/muted/bf/it="expr"`.
- Smart button: `<div class="oe_button_box" name="button_box"><button type="object" name="action_view_x" class="oe_stat_button" icon="fa-list"><field name="x_count" widget="statinfo" string="X"/></button></div>`.
- Statusbar: `<field name="state" widget="statusbar" statusbar_visible="draft,done"/>`.
- Chatter: v18 `<chatter/>`; before: `<div class="oe_chatter"><field name="message_follower_ids"/><field name="activity_ids"/><field name="message_ids"/></div>`.
- Context/default: `context="{'default_partner_id': partner_id}"`, domain on field: `domain="[('state','=','available')]"`, dynamic domain on field in model: `domain="[('id', 'in', allowed_ids)]"`.
- Search view: `filter_domain`, `<filter domain=...>`, group by: `context="{'group_by': 'state'}"`, default filter in action context `{'search_default_myfilter': 1}`.

## 7. Actions, menus
```xml
<record id="action_x" model="ir.actions.act_window">
  <field name="name">X</field><field name="res_model">x.thing</field>
  <field name="view_mode">list,form</field>
  <field name="domain">[]</field><field name="context">{}</field>
</record>
<menuitem id="menu_root" name="App" sequence="10"/>
<menuitem id="menu_x" parent="menu_root" action="action_x" groups="module.group_user"/>
```
Server action (code): `<field name="state">code</field><field name="code">records.action_x()</field>` + `binding_model_id` to show in Action menu.
Python action: `return {"type": "ir.actions.act_window", "res_model": "...", "res_id": id, "view_mode": "form", "target": "current|new"}`.
Notification: `{"type": "ir.actions.client", "tag": "display_notification", "params": {"title": "", "message": "", "type": "success", "sticky": False}}`.
Reload: `{"type": "ir.actions.client", "tag": "reload"}`. Close wizard: `{"type": "ir.actions.act_window_close"}`.
URL: `{"type": "ir.actions.act_url", "url": "...", "target": "new"}`.

## 8. Security
- `security/ir.model.access.csv`: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`
  model xmlid = `model_` + model name with dots→underscores. **Missing ACL = "You are not allowed to access" error.** Leave `group_id:id` empty = all users.
- Groups: `res.groups` with `implied_ids`; category = `ir.module.category`.
- Record rules: `ir.rule` with `domain_force` (`user`, `company_ids`, `company_id` available); `groups` empty = global rule (AND-ed), with groups = OR-ed within groups.
- Field groups: `groups="base.group_system"` on field or view element.
- `sudo()` bypasses ACL & rules -> use narrowly; prefer `with_user`, or check access explicitly `rec.check_access("read")` (v18) / `check_access_rights` (≤17).
- Multi-company: `company_id` field + rule `[('company_id','in',company_ids)]`.

## 9. Data files
```xml
<odoo><data noupdate="1">      <!-- noupdate: not overwritten on -u -->
  <record id="x1" model="x.thing"><field name="name">A</field>
     <field name="partner_id" ref="base.res_partner_1"/>
     <field name="line_ids" eval="[Command.create({'qty': 1})]"/>
     <field name="date" eval="(DateTime.today() + relativedelta(days=5)).strftime('%Y-%m-%d')"/></record>
</data></odoo>
```
Sequence: `ir.sequence` (`code`, `prefix`, `padding`) → `self.env["ir.sequence"].next_by_code("code")`.
Cron (v18): `ir.cron` with `model_id, state=code, code=model._method(), interval_number, interval_type, active` (v≤16 also `numbercall`, `doall`).
Mail template: `mail.template` fields `subject, email_to, body_html` with `{{ object.x }}` inline & `<t t-out="object.x"/>`; send: `template.send_mail(rec.id, force_send=False)`; post to chatter: `rec.message_post(body="", subtype_xmlid="mail.mt_note")`; activity: `rec.activity_schedule("mail.mail_activity_data_todo", user_id=..., summary="")`.
Config param: `self.env["ir.config_parameter"].sudo().get_param("key", default)`.
Settings: model `_inherit = "res.config.settings"` + `fields.Char(config_parameter="my.key")`.

## 10. Wizard (TransientModel)
Model `models.TransientModel` → ACL needed → form with `<footer>` buttons → action with `target="new"` → read context `self.env.context.get("active_ids")` / `active_model` → `default_get` to prefill → return `{"type": "ir.actions.act_window_close"}`.
See `snippets/library_demo/wizard`.

## 11. QWeb / reports
```xml
<record id="action_report_x" model="ir.actions.report">
  <field name="name">X</field><field name="model">x.thing</field>
  <field name="report_type">qweb-pdf</field>
  <field name="report_name">module.report_x_doc</field><field name="report_file">module.report_x_doc</field>
  <field name="binding_model_id" ref="model_x_thing"/><field name="binding_type">report</field>
</record>
<template id="report_x_doc"><t t-call="web.html_container"><t t-foreach="docs" t-as="o">
  <t t-call="web.external_layout"><div class="page">
    <h2 t-field="o.name"/>
    <t t-foreach="o.line_ids" t-as="l"><div t-if="l.qty > 1"><span t-out="l.qty"/></div></t>
  </div></t></t></t></template>
```
QWeb directives: `t-if t-elif t-else t-foreach t-as t-set t-value t-esc(old)/t-out t-field t-options t-att-* t-attf-* t-call t-raw(avoid)`.
Loop vars: `l_index l_first l_last l_size l_even l_odd`.
Inherit report: `<template id="x" inherit_id="account.report_invoice_document"><xpath .../></template>`.
Excel: `xlsxwriter` in a controller returning `request.make_response(data, headers=[("Content-Type","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), ("Content-Disposition", "attachment; filename=x.xlsx")])`.
Debug: `?debug=assets`; view report HTML: `/report/html/module.report_name/<id>`.

## 12. Controllers
```python
class X(http.Controller):
    @http.route("/x/page", type="http", auth="public", website=True)   # HTML page
    @http.route("/api/x", type="json", auth="user", methods=["POST"])  # JSON-RPC envelope (v19: type="jsonrpc")
    @http.route("/api/x", type="http", auth="none", methods=["GET"], csrf=False)  # plain REST
```
`auth`: `user` (login), `public` (anonymous OK; env user = public), `none` (no DB env until you set one). `csrf=False` for token APIs only.
**For type="http" JSON body: client MUST send `Content-Type: application/json`, then read `request.httprequest.get_data()`** (with form content-type Odoo consumes the body and it's empty — tested).
Return: `request.make_response(json.dumps(x), headers=[("Content-Type","application/json")], status=200)`; `request.render("module.template", values)`; `request.redirect("/path")`; `request.not_found()`.
Params: `request.params`, `request.httprequest.headers`, `request.env`, `request.session`.
Full REST example: `snippets/library_demo/controllers/main.py`.

## 13. JS/OWL (only if asked)
Registry patterns: `registry.category("actions").add("tag", Component)`, `patch(Component.prototype, {...})`, assets in manifest `"assets": {"web.assets_backend": ["module/static/src/**/*"]}`. Tour/test via `?debug=1`. Keep any UI task minimal.

## 14. Misc
- Debug mode: `?debug=1`; Developer tools: view fields, edit view, metadata (shows xmlid), Technical menu.
- `_logger = logging.getLogger(__name__)`; `_logger.info("x %s", var)`.
- Raw SQL (read-only, parameterised): `self.env.cr.execute("SELECT id FROM t WHERE x = %s", (val,)); rows = self.env.cr.fetchall()`; after raw writes call `self.env.invalidate_all()`. **Never** f-string user input.
- Attachments: `self.env["ir.attachment"].create({"name": n, "datas": base64.b64encode(b), "res_model": m, "res_id": i})`.
- Send mail ad hoc: `self.env["mail.mail"].create({"subject": "", "body_html": "", "email_to": ""}).send()`.
- Dates: `from dateutil.relativedelta import relativedelta`; `fields.Date.to_date(str)`; `fields.Datetime.to_string`.
- Currency: `currency.round(x)`, `float_compare/float_is_zero` from `odoo.tools`.
- Archive: `active` field; `rec.action_archive()`.
- Menu icons / `web_icon` optional.
