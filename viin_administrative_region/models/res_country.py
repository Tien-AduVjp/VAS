from odoo import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    administrative_region_ids = fields.One2many('administrative.region', 'country_id', string='Administrative Regions')

    def action_view_administrative_regions(self):
        administrative_regions = self.administrative_region_ids
        action = self.env['ir.actions.act_window']._for_xml_id('viin_administrative_region.administrative_region_action')
        action['context'] = {'default_country_id': self[:1].id}
        if len(administrative_regions) != 1:
            action['domain'] = "[('id', 'in', %s)]" % str(administrative_regions.ids)
        elif len(administrative_regions) == 1:
            res = self.env.ref('viin_administrative_region.administrative_region_view_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = administrative_regions.id
        return action
