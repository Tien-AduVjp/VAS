from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit='res.partner'

    ownership_type_id = fields.Many2one('res.partner.ownership.type',
                                        string="Ownership Type", tracking=True,
                                        ondelete='restrict', compute="_compute_ownership_type_id",
                                        readonly=False, store=True)

    @api.depends('is_company')
    def _compute_ownership_type_id(self):
        for r in self:
            r.ownership_type_id = False if not r.is_company else r.ownership_type_id
