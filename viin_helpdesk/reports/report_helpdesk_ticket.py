from odoo import fields, models, tools


class ReportHelpdeskTicket(models.Model):
    _name = 'report.helpdesk.ticket'
    _description = 'Ticket Report'
    _order = 'name desc'
    _auto = False

    name = fields.Char(string='Title', readonly=True)
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', readonly=True, help="The Team which direct handling this ticket")
    user_id = fields.Many2one('res.users', string='Owner', readonly=True, help="The employee which direct handling this ticket")
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string='Ticket Type', readonly=True, help="Used to classify question type for customer")
    stage_id = fields.Many2one('helpdesk.stage', string='Stage', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    priority_level = fields.Selection([('0', 'All'),
                                 ('1', 'Low Priority'),
                                 ('2', 'High Priority'),
                                 ('3', 'Urgent')], string='Priority', readonly=True)
    create_date = fields.Datetime(string='Create Date', readonly=True)
    assign_date = fields.Datetime(string='Assign Date', readonly=True)
    end_date = fields.Datetime(string='End Date', readonly=True)
    assign_duration = fields.Float(string='Assigning Duration (hours)', readonly=True, group_operator='avg')
    resolved_duration = fields.Float(string='Resolving Duration (hours)', readonly=True, group_operator='avg')
    ticket_life = fields.Float(string='Ticket Life (hours)', readonly=True, group_operator='avg')
    state = fields.Selection([
            ('normal', 'In Progress'),
            ('blocked', 'Blocked'),
            ('done', 'Ready for next stage')
        ], string='Kanban State', readonly=True)
    done = fields.Integer(string='Done', readonly=True)
    not_done = fields.Integer(string='Not Done', readonly=True)
    not_assign = fields.Integer(string='Not Assign', readonly=True)
    def _select(self):
        return """
         SELECT
            COUNT(CASE WHEN (stage.is_final_stage OR stage.fold) THEN TRUE END) as done,
            COUNT(CASE WHEN (stage.is_final_stage AND stage.fold) IS NULL THEN True END ) as not_done,
            COUNT(CASE WHEN t.user_id IS NULL THEN True END) as not_assign,
            t.id as id,
            t.user_id as user_id,
            t.team_id as team_id,
            t.ticket_type_id as ticket_type_id,
            t.priority_level as priority_level,
            t.name as name,
            t.partner_id as partner_id,
            t.stage_id as stage_id,
            t.create_date as create_date,
            t.assign_date as assign_date,
            t.end_date as end_date,
            t.company_id as company_id,
            t.kanban_state as state,
            t.assign_duration,
            t.resolved_duration,
            t.ticket_life
        """

    def _from(self):
        return """
        FROM helpdesk_ticket AS t
        LEFT JOIN helpdesk_ticket_type AS type ON type.id = t.ticket_type_id
        LEFT JOIN helpdesk_team AS team ON team.id = t.team_id
        LEFT JOIN res_users AS u ON u.id = t.user_id
        LEFT JOIN helpdesk_stage AS stage ON stage.id = t.stage_id
        """

    def _group_by(self):
        return """
        GROUP BY
            t.id,
            t.user_id,
            t.team_id,
            t.ticket_type_id,
            t.priority_level,
            t.name,
            t.partner_id,
            t.stage_id,
            t.create_date,
            t.assign_date,
            t.end_date,
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
