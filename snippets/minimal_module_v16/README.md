# minimal_module_v16 (Odoo 16)
Differences vs the Odoo 18 version (`../minimal_module`):
- `<list>` -> `<tree>`; `view_mode` `tree,form`
- `invisible="state != 'draft'"` -> `attrs="{'invisible': [('state', '!=', 'draft')]}"` (attrs exist until v16)
- list column hidden with `invisible="1"` (not `column_invisible`)
- `<chatter/>` -> `<div class="oe_chatter">...</div>`
Also valid for Odoo 15 in most cases (Python 3.8-compatible code).
