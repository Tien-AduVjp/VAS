from odoo import fields, models, api


class Partner(models.Model):
    _inherit='res.partner'

    business_type_id = fields.Many2one('res.partner.business.type', string='Business Type', tracking=True, ondelete='restrict')

    @api.onchange('company_type')
    def onchange_company_type(self):
        super(Partner, self).onchange_company_type()
        if self.company_type == 'person':
            self.business_type_id = False
        elif self.company_type == 'company' and self._origin:
            self.business_type_id = self._origin.business_type_id
