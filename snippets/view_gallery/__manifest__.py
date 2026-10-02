{
    "name": "View Gallery (Odoo 18)",
    "version": "18.0.1.0.0",
    "summary": "Copy-paste examples of every common view type + view inheritance + server action",
    "depends": ["base", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "data/gallery_data.xml",
        "views/gallery_views.xml",
        "views/partner_inherit_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
