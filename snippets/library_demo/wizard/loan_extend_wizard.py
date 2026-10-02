from odoo import _, fields, models
from odoo.exceptions import UserError


class LoanExtendWizard(models.TransientModel):
    _name = "library.loan.extend.wizard"
    _description = "Extend Loan Wizard"

    loan_ids = fields.Many2many("library.loan", string="Loans")
    days = fields.Integer(default=7, required=True)

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # active_ids comes from the context when launched from a list/form
        if "loan_ids" in fields_list and self.env.context.get("active_model") == "library.loan":
            res["loan_ids"] = [(6, 0, self.env.context.get("active_ids", []))]
        return res

    def action_extend(self):
        self.ensure_one()
        if self.days <= 0:
            raise UserError(_("Days must be positive."))
        self.loan_ids.extend_due_date(self.days)
        return {"type": "ir.actions.act_window_close"}
