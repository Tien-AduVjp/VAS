from odoo import fields, models


class ActivityReport(models.Model):
    _inherit = 'crm.activity.report'

    team_leader_id = fields.Many2one('res.users', string='Team Leader', readonly=True)
    regional_manager_id = fields.Many2one('res.users', string='Regional Manager', readonly=True)
    crm_team_region_id = fields.Many2one('crm.team.region', string='Sales Region', readonly=True)

    def _select(self):
        sql = super(ActivityReport, self)._select()
        sql += """,
            t.user_id AS team_leader_id,
            rmg.id AS regional_manager_id,
            tr.id AS crm_team_region_id
        """
        return sql

    def _join(self):
        sql = super(ActivityReport, self)._join()
        sql += """
            LEFT JOIN crm_team AS t ON t.id = l.team_id
            LEFT JOIN crm_team_region AS tr ON tr.id = l.crm_team_region_id
            LEFT JOIN res_users AS rmg ON rmg.id = l.regional_manager_id
        """
        return sql
