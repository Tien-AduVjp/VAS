from odoo import fields, models, tools


class ReportHelpdeskTicket(models.Model):
    _name = 'report.helpdesk.sla'
    _description = 'SLA Report'
    _auto = False

    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', readonly=True, help="The Team which direct handling this ticket")
    ticket_id = fields.Many2one('helpdesk.ticket', readonly=True)
    sla_id = fields.Many2one('helpdesk.sla', string='SLA Policies', readonly=True)
    sla_reached = fields.Integer(string='SLA Reached', readonly=True)
    sla_ongoing = fields.Integer(string='SLA Ongoing', readonly=True)
    sla_failed = fields.Integer(string='SLA Failed', readonly=True)
    create_date = fields.Date(string='Create Date', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def _select(self):
        return """
         SELECT
            COUNT(CASE WHEN sla_line.status = 'reached' THEN True END) as sla_reached,
            COUNT(CASE WHEN sla_line.status = 'ongoing'THEN True END) as sla_ongoing,
            COUNT(CASE WHEN sla_line.status = 'failed' THEN True END) as sla_failed,
            sla_line.sla_id as sla_id,
            sla_line.id as id,
            sla_line.ticket_id as ticket_id,
            t.team_id as team_id,
            t.company_id as company_id,
            t.create_date as create_date
        """

    def _from(self):
        return """
        FROM helpdesk_sla_line AS sla_line
        LEFT JOIN helpdesk_ticket as t ON sla_line.ticket_id = t.id
        """

    def _group_by(self):
        return """
        GROUP BY
            sla_line.id,
            sla_line.ticket_id,
            t.team_id,
            t.create_date,
            t.company_id
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS
            %s
            %s
            %s
        """ % (
            self._table,
            self._select(),
            self._from(),
            self._group_by()
            )
        )
