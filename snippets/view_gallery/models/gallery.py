from odoo import api, fields, models


class GalleryStage(models.Model):
    _name = "gallery.stage"
    _description = "Gallery Stage"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()


class GalleryTag(models.Model):
    _name = "gallery.tag"
    _description = "Gallery Tag"

    name = fields.Char(required=True)
    color = fields.Integer()


class GalleryItem(models.Model):
    _name = "gallery.item"
    _description = "Gallery Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, id desc"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner")
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    stage_id = fields.Many2one(
        "gallery.stage", group_expand="_read_group_stage_ids",
        default=lambda self: self.env["gallery.stage"].search([], limit=1),
    )
    tag_ids = fields.Many2many("gallery.tag")
    date_start = fields.Datetime(default=fields.Datetime.now)
    date_end = fields.Datetime()
    priority = fields.Selection([("0", "Normal"), ("1", "Low"), ("2", "High"), ("3", "Urgent")], default="0")
    amount = fields.Float()
    color = fields.Integer()
    active = fields.Boolean(default=True)
    state = fields.Selection([("new", "New"), ("done", "Done")], default="new")
    line_ids = fields.One2many("gallery.item.line", "item_id")
    line_total = fields.Float(compute="_compute_line_total", store=True)

    @api.depends("line_ids.subtotal")
    def _compute_line_total(self):
        for rec in self:
            rec.line_total = sum(rec.line_ids.mapped("subtotal"))

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """Show ALL stages as kanban columns, even empty ones."""
        return stages.search([], order=stages._order)

    def action_done(self):
        self.write({"state": "done"})


class GalleryItemLine(models.Model):
    _name = "gallery.item.line"
    _description = "Gallery Item Line"

    item_id = fields.Many2one("gallery.item", required=True, ondelete="cascade")
    name = fields.Char()
    qty = fields.Float(default=1)
    price = fields.Float()
    subtotal = fields.Float(compute="_compute_subtotal", store=True)

    @api.depends("qty", "price")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.price


class ResPartner(models.Model):
    _inherit = "res.partner"   # extending a core model

    gallery_note = fields.Char(string="Gallery Note")
    gallery_count = fields.Integer(compute="_compute_gallery_count")

    def _compute_gallery_count(self):
        data = self.env["gallery.item"]._read_group([("partner_id", "in", self.ids)], ["partner_id"], ["__count"])
        counts = {partner.id: count for partner, count in data}
        for rec in self:
            rec.gallery_count = counts.get(rec.id, 0)

    def action_view_gallery(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", "name": "Gallery Items", "res_model": "gallery.item",
            "view_mode": "list,form", "domain": [("partner_id", "=", self.id)],
            "context": {"default_partner_id": self.id},
        }
