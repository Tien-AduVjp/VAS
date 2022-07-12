from odoo import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'
    
    administrative_region_ids = fields.One2many('administrative.region', 'country_id', string='Administrative Regions')
    
    def action_view_administrative_regions(self):
        administrative_regions = self.administrative_region_ids

        action = self.env.ref('viin_administrative_region.administrative_region_action')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        result['context'] = {'default_country_id': self[:1].id}

        # choose the view_mode accordingly
        if len(administrative_regions) != 1:
            result['domain'] = "[('id', 'in', %s)]" % str(administrative_regions.ids)
        elif len(administrative_regions) == 1:
            res = self.env.ref('viin_administrative_region.administrative_region_view_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = administrative_regions.id
        return result
