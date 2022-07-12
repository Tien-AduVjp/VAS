from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    project_id = fields.Many2one('project.project', string='Project', tracking=True, compute='_compute_project_id', store=True, readonly=False,
                                 inverse='_inverse_project_id',
                                 help="Project which the helpdesk tickets and timesheets will be used.")
    task_id = fields.Many2one('project.task', string='Task', domain="[('project_id', '=', project_id)]", tracking=True,
                                 help="Task which the helpdesk tickets and timesheets will be used.")
    use_helpdesk_timesheet = fields.Boolean(string='Timesheet on Tickets', related='project_id.allow_timesheets', store=True)
    timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id', string='Timesheets', groups='hr_timesheet.group_hr_timesheet_user')

    def write(self, vals):
        if not self.env.user.has_group('viin_helpdesk.group_helpdesk_manager') and len(vals) == 1 and 'timesheet_ids' in vals:
            return super(HelpdeskTicket, self.sudo()).write(vals)
        return super(HelpdeskTicket, self).write(vals)

    @api.depends('team_id', 'task_id.project_id')
    def _compute_project_id(self):
        for r in self:
            if r.task_id.project_id:
                r.project_id = r.task_id.project_id
            else:
                r.project_id = r.team_id.project_id

    def action_tasks_view(self):
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_name': self[:1].name,
            'default_description': self[:1].description,
            'default_ticket_id': self[:1].id,
            'default_company_id': self[:1].company_id.id,
            'default_project_id': self[:1].project_id.id
            })

        view_mode = 'kanban,tree,form,pivot,calendar,graph'
        action = {
            'name': _('Tasks'),
            'view_mode': view_mode,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('id', 'in', ctx.get('create_task', []))],
        }
        if not self[:1].project_id.id and ctx.get('create_new_task', False):
            action.update({
                'view_mode': 'form'
                })
        elif len(ctx.get('create_task', [])) == 1 and not ctx.get('create_new_task', False):
            action.update({
                'view_mode': 'form',
                'res_id': ctx['create_task'][0]
            })
        return action

    def _prepare_task_vals(self, wizard):
        self.ensure_one()
        vals = {
            'name': self.name,
            'tag_ids': wizard.tag_ids.ids,
            'user_id': wizard.assign_to_me and self.env.user.id,
            'partner_id': wizard.partner_id.id,
            'project_id': wizard.project_id.id,
            'date_deadline': wizard.date_deadline,
            'ticket_ids': self.ids
            }
        if self.description:
            vals['description'] = self.description
        return vals

    def _prepare_task_vals_list(self, wizard):
        vals_list = []
        for r in self:
            vals_list.append(r._prepare_task_vals(wizard))
        return vals_list

    def _convert_tasks(self, wizard):
        vals_list = self._prepare_task_vals_list(wizard)
        tasks = self.env['project.task'].create(vals_list)
        # move attachments and messages to tasks
        for task in tasks:
            all_attachments = self.env['ir.attachment'].search([('res_model', '=', 'helpdesk.ticket'), ('res_id', 'in', self.ids)])
            attachments = all_attachments.filtered(lambda att: att.res_id == self.id)
            if attachments:
                attachments.write({'res_model': 'project.task', 'res_id': task.id})
            messages = task.message_ids
            if messages:
                messages.write({'model': 'project.task', 'res_id': task.id})
        return tasks

    def _inverse_project_id(self):
        for r in self:
            if not r.project_id:
                r.task_id = False
