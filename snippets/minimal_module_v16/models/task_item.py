from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class TaskItem(models.Model):
    _name = "task.item"
    _description = "Task Item"
    _inherit = ["mail.thread"]
    _order = "deadline, id"

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Customer")
    deadline = fields.Date()
    description = fields.Text()
    amount = fields.Float()
    state = fields.Selection(
        [("draft", "Draft"), ("progress", "In Progress"), ("done", "Done"), ("cancel", "Cancelled")],
        default="draft", tracking=True,
    )
    # Non-stored compute used in a filter/domain MUST have a search method (or store=True).
    is_late = fields.Boolean(compute="_compute_is_late", search="_search_is_late")
    active = fields.Boolean(default=True)

    @api.depends("deadline", "state")
    def _compute_is_late(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_late = bool(rec.deadline and rec.deadline < today and rec.state not in ("done", "cancel"))

    def _search_is_late(self, operator, value):
        if operator not in ("=", "!=") or not isinstance(value, bool):
            raise UserError(_("Unsupported search on 'is_late'."))
        today = fields.Date.context_today(self)
        late = ["&", ("deadline", "<", today), ("state", "not in", ("done", "cancel"))]
        wants_late = (operator == "=") == value
        return late if wants_late else ["!"] + late  # prefix notation: NOT (A AND B)

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError(_("Amount cannot be negative."))

    def action_start(self):
        self.write({"state": "progress"})

    def action_done(self):
        if any(rec.state != "progress" for rec in self):
            raise UserError(_("Only tasks in progress can be completed."))
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset(self):
        self.write({"state": "draft"})
