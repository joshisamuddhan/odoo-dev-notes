from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class LibraryLoan(models.Model):
    _name = "library.loan"
    _description = "Library Loan"
    _inherit = ["mail.thread"]
    _order = "date_out desc, id desc"

    name = fields.Char(default=lambda self: _("New"), copy=False, readonly=True)
    book_id = fields.Many2one(
        "library.book", required=True, ondelete="restrict", tracking=True,
        domain="[('state', '=', 'available')]",
    )
    partner_id = fields.Many2one("res.partner", string="Borrower", required=True, tracking=True)
    date_out = fields.Date(default=fields.Date.context_today, required=True)
    date_due = fields.Date(required=True, tracking=True)
    date_return = fields.Date(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("open", "On Loan"), ("returned", "Returned"), ("overdue", "Overdue")],
        default="draft", tracking=True,
    )
    days_overdue = fields.Integer(compute="_compute_overdue", store=True)
    fine = fields.Float(compute="_compute_overdue", store=True)
    company_id = fields.Many2one(related="book_id.company_id", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("library.loan") or _("New")
        return super().create(vals_list)

    @api.constrains("date_out", "date_due")
    def _check_dates(self):
        for rec in self:
            if rec.date_due and rec.date_out and rec.date_due < rec.date_out:
                raise ValidationError(_("Due date cannot be before the loan date."))

    @api.depends("date_due", "date_return", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            end = rec.date_return or today
            if rec.date_due and rec.state in ("open", "overdue", "returned") and end > rec.date_due:
                rec.days_overdue = (end - rec.date_due).days
            else:
                rec.days_overdue = 0
            rec.fine = rec.days_overdue * 5.0  # 5 per day: put in a config param in real life

    # ---- workflow buttons -------------------------------------------------
    def action_confirm(self):
        for rec in self:
            if rec.book_id.state != "available":
                raise UserError(_("Book '%s' is not available.", rec.book_id.name))
            rec.book_id.state = "borrowed"
            rec.state = "open"
        self._send_confirmation_mail()

    def action_return(self):
        for rec in self.filtered(lambda r: r.state in ("open", "overdue")):
            rec.write({"state": "returned", "date_return": fields.Date.context_today(rec)})
            rec.book_id.state = "available"

    def _send_confirmation_mail(self):
        template = self.env.ref("library_demo.mail_template_loan_confirm", raise_if_not_found=False)
        for rec in self.filtered(lambda r: r.partner_id.email):
            if template:
                template.send_mail(rec.id, force_send=False)

    # ---- cron -------------------------------------------------------------
    @api.model
    def _cron_mark_overdue(self):
        today = fields.Date.context_today(self)
        loans = self.search([("state", "=", "open"), ("date_due", "<", today)])
        loans.write({"state": "overdue"})
        # large volumes: process in batches and commit:
        #   for batch in split_every(500, ids): ...; self.env.cr.commit()
        return True

    def extend_due_date(self, days):
        for rec in self:
            rec.date_due = rec.date_due + timedelta(days=days)
            if rec.state == "overdue" and rec.date_due >= fields.Date.context_today(rec):
                rec.state = "open"
