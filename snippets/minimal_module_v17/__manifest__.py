{
    "name": "Task Demo (minimal, Odoo 17)",
    "version": "17.0.1.0.0",
    "summary": "Smallest useful module: model + views + ACL + menu + state buttons",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/task_item_views.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
