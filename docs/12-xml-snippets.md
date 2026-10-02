# XML snippets (copy-paste). Working, installed-and-validated versions in `snippets/view_gallery/` (Odoo 18).

Open `snippets/view_gallery/views/gallery_views.xml` — it contains: editable list, form (statusbar, notebook, inline one2many), kanban (grouped, quick create, priority, activity, avatar), calendar, pivot, graph, activity, search (filter_domain, date filters, group by), action with all view modes, server action, menus.
`partner_inherit_views.xml` shows inheriting a core view (smart button, field after, change attributes, new page).
Validated by installing on a fresh Odoo 18 DB (Odoo validates view XML on load). Kanban/calendar *rendering* in the browser was not clicked through.

## Version translation cheat (apply when their Odoo ≠ 18)
| Odoo 18 (gallery) | v17 | v16/v15 |
|---|---|---|
| `<list>` / `view_mode list,form` | `<tree>` / `tree,form` | `<tree>` / `tree,form` |
| `<t t-name="card">` in kanban | `<t t-name="kanban-box">` with full `<div class="oe_kanban_card oe_kanban_global_click">` | same as v17 |
| `invisible="state != 'x'"` | same | `attrs="{'invisible': [('state','!=','x')]}"` |
| `<chatter/>` | `<div class="oe_chatter">…` | same |
| `column_invisible="True"` | same | `invisible="1"` on list field |
| `readonly="expr"`, `required="expr"` | same | `attrs="{'readonly': [...], 'required': [...]}"` |
| `<field widget="priority">`, `many2many_tags`, `badge` | same | `badge` v15+ ; `many2one_avatar_user` v15+ |

### Kanban in v17/v16 (full example — written from core patterns, not installed in my test run)
```xml
<kanban default_group_by="stage_id" class="o_kanban_small_column">
    <field name="name"/><field name="color"/>
    <templates>
        <t t-name="kanban-box">
            <div t-attf-class="oe_kanban_color_#{kanban_getcolor(record.color.raw_value)} oe_kanban_card oe_kanban_global_click">
                <div class="oe_kanban_content">
                    <strong><field name="name"/></strong>
                    <div><field name="partner_id"/></div>
                    <field name="tag_ids" widget="many2many_tags"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

## Quick patterns
```xml
<!-- Button types -->
<button name="action_x" type="object" string="X" class="btn-primary" invisible="state != 'draft'" confirm="Are you sure?"/>
<button name="%(module.action_xmlid)d" type="action" string="Open wizard"/>      <!-- action must be loaded BEFORE this view -->

<!-- Smart button -->
<div class="oe_button_box" name="button_box">
  <button name="action_view_x" type="object" class="oe_stat_button" icon="fa-list">
    <field name="x_count" widget="statinfo" string="Items"/></button></div>

<!-- Conditional / dynamic domain / context on a field -->
<field name="partner_id" domain="[('is_company', '=', True)]" context="{'default_is_company': True}" options="{'no_create': True, 'no_open': True}"/>
<field name="type" required="state == 'x'" readonly="state != 'draft'"/>
<field name="note" invisible="not note and state == 'done'" groups="base.group_system"/>

<!-- Group / separators / labels -->
<group string="Title"><group><field name="a"/></group><group><field name="b"/></group></group>
<label for="x"/><div class="o_row"><field name="x"/><span>units</span></div>

<!-- Statusbar clickable -->
<field name="state" widget="statusbar" statusbar_visible="draft,done" options="{'clickable': '1'}"/>

<!-- Ribbon, alert -->
<widget name="web_ribbon" title="Archived" bg_color="text-bg-danger" invisible="active"/>
<div class="alert alert-warning" role="alert" invisible="not warning_text"><field name="warning_text"/></div>

<!-- One2many with inline create/edit and custom list -->
<field name="line_ids"><list editable="bottom"><field name="name"/><field name="qty"/></list></field>

<!-- Many2many checkboxes / tags / binary / image / html -->
<field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
<field name="image" widget="image" class="oe_avatar" options="{'preview_image': 'image_128'}"/>
<field name="doc" widget="binary" filename="doc_name"/>
<field name="body" widget="html"/>

<!-- Search view -->
<field name="name" filter_domain="['|', ('name', 'ilike', self), ('ref', 'ilike', self)]"/>
<filter name="mine" string="Mine" domain="[('user_id', '=', uid)]"/>
<filter name="g_state" string="Status" context="{'group_by': 'state'}"/>

<!-- Action with domain/context/limit -->
<record id="action_x" model="ir.actions.act_window">
  <field name="name">X</field><field name="res_model">x.model</field>
  <field name="view_mode">list,form</field><field name="domain">[('state', '!=', 'cancel')]</field>
  <field name="context">{'default_state': 'draft', 'search_default_mine': 1}</field><field name="limit">80</field></record>

<!-- Bind a specific view to an action (instead of default) -->
<record id="action_x_list" model="ir.actions.act_window.view">
  <field name="sequence" eval="1"/><field name="view_mode">list</field>
  <field name="view_id" ref="view_x_list"/><field name="act_window_id" ref="action_x"/></record>

<!-- Menu with groups -->
<menuitem id="menu_x" name="X" parent="menu_root" action="action_x" sequence="10" groups="module.group_manager"/>

<!-- Inherit: after/before/inside/replace/attributes -->
<xpath expr="//field[@name='phone']" position="after"><field name="my"/></xpath>
<xpath expr="//page[@name='sales_purchases']" position="inside"><group><field name="my2"/></group></xpath>
<field name="email" position="attributes"><attribute name="invisible">1</attribute></field>
<xpath expr="//button[@name='action_old']" position="replace"/>            <!-- removes it -->

<!-- Data record with relations -->
<record id="demo_1" model="x.model">
  <field name="name">Demo</field><field name="partner_id" ref="base.res_partner_1"/>
  <field name="tag_ids" eval="[(6, 0, [ref('tag_a'), ref('tag_b')])]"/>
  <field name="date" eval="(DateTime.today() + relativedelta(days=3)).strftime('%Y-%m-%d')"/></record>

<!-- Server action (python) + automated action idea -->
<record id="sa_x" model="ir.actions.server"><field name="name">Do X</field><field name="model_id" ref="model_x_model"/>
  <field name="binding_model_id" ref="model_x_model"/><field name="state">code</field><field name="code">records.action_x()</field></record>

<!-- Security group + ACL + rule: see snippets/library_demo/security -->
```
