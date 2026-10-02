# minimal_module_v17 (Odoo 17)
Differences vs the Odoo 18 version (`../minimal_module`):
- `<list>` -> `<tree>` and `view_mode` `list,form` -> `tree,form`
- `<chatter/>` -> `<div class="oe_chatter">...</div>` inside `<form>` (after `</sheet>`)
Everything else (invisible="expr", column_invisible) is already v17 syntax.
