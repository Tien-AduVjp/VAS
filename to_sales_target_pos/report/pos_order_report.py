from odoo import api, fields, models, tools


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    crm_team_id = fields.Many2one('crm.team', string='Team/Channel', index=True)

    def _select(self):
        select_str = super(PosOrderReport, self)._select()
        select_str += """,
        s.crm_team_id AS crm_team_id
        """
        return select_str

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ", s.crm_team_id"
