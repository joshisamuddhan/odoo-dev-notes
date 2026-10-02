from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Library Book"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # chatter
    _order = "name"
    _rec_name = "name"

    name = fields.Char(required=True, tracking=True)
    isbn = fields.Char(string="ISBN", copy=False, index=True)
    author = fields.Char()
    price = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )
    active = fields.Boolean(default=True)  # enables archive
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    state = fields.Selection(
        [("available", "Available"), ("borrowed", "Borrowed"), ("lost", "Lost")],
        default="available",
        required=True,
        tracking=True,
    )
    loan_ids = fields.One2many("library.loan", "book_id", string="Loans")
    loan_count = fields.Integer(compute="_compute_loan_count", store=True)

    # SQL constraint (v17/18 style). In v19 use models.Constraint instead.
    _sql_constraints = [
        ("isbn_uniq", "unique(isbn, company_id)", "ISBN must be unique per company."),
        ("price_positive", "CHECK(price >= 0)", "Price cannot be negative."),
    ]

    @api.depends("loan_ids")
    def _compute_loan_count(self):
        # read_group avoids N+1 queries. (v18: _read_group returns tuples)
        data = self.env["library.loan"]._read_group(
            [("book_id", "in", self.ids)], ["book_id"], ["__count"]
        )
        counts = {book.id: count for book, count in data}
        for rec in self:
            rec.loan_count = counts.get(rec.id, 0)

    @api.constrains("isbn")
    def _check_isbn(self):
        for rec in self:
            if rec.isbn and not rec.isbn.replace("-", "").isalnum():
                raise ValidationError(_("ISBN may only contain letters, digits and dashes."))

    def action_mark_lost(self):
        self.write({"state": "lost"})

    def action_view_loans(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Loans"),
            "res_model": "library.loan",
            "view_mode": "list,form",
            "domain": [("book_id", "=", self.id)],
            "context": {"default_book_id": self.id},
        }
