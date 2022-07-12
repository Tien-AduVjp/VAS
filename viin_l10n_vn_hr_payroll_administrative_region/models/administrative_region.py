from odoo import models


class AdministrativeRegion(models.Model):
    _inherit = 'administrative.region'
    
    def _l10n_vn_set_minimum_wage(self):
        """
        Reference link: https://ebh.vn/tin-tuc/muc-luong-toi-thieu-vung-nam-2021
        """
        ADMIN_REGION_VALS = {
            'viin_administrative_region.administrative_region_1': {'minimum_wage': 4420000},
            'viin_administrative_region.administrative_region_2': {'minimum_wage': 3920000},
            'viin_administrative_region.administrative_region_3': {'minimum_wage': 3430000},
            'viin_administrative_region.administrative_region_4': {'minimum_wage': 3070000},
        }
        for xml_region, vals in ADMIN_REGION_VALS.items():
            self.env.ref(xml_region).write(vals)
