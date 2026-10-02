{
    "name": "Library Demo",
    "summary": "Generic skeleton: models, views, security, wizard, cron, mail, report, API, tests",
    "version": "18.0.1.0.0",
    "category": "Services",
    "license": "LGPL-3",
    "author": "Your Name",
    "depends": ["base", "mail", "contacts"],
    # ORDER MATTERS: security first, then data, then views/wizards, menus last.
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "data/mail_template.xml",
        "data/cron_data.xml",
        "views/library_book_views.xml",
        # Actions/reports must load BEFORE views whose buttons reference them
        # (%(module.action_id)d is resolved at load time).
        "wizard/loan_extend_wizard_views.xml",
        "report/library_loan_report.xml",
        "views/library_loan_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "installable": True,
}
