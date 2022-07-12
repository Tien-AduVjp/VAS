from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"
    
    use_intermediary_account = fields.Boolean(string='Use Intermediary Account', default=True, help="Define whether the user uses an intermediary account or not when making an Internal Transfer")

    def write(self, values):
        chart_template_id = values.get('chart_template_id', False)
        if chart_template_id:
            vn_chart_of_account_c133 = self.env.ref('l10n_vn_c133.vn_template_c133')
            vn_chart_of_account_c200 = self.env.ref('l10n_vn.vn_template')
            if chart_template_id == vn_chart_of_account_c133.id:
                values.update({'use_intermediary_account': False})
            elif chart_template_id == vn_chart_of_account_c200.id:
                values.update({'use_intermediary_account': True})
        return super(ResCompany, self).write(values)
