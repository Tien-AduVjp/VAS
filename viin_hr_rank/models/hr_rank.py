from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrRank(models.Model):
    _name = 'hr.rank'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'role_id, grade_sequence, id'
    _description = "HR Rank"

    name = fields.Char(string='Name', compute='_compute_name', translate=True, compute_sudo=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    department_id = fields.Many2one('hr.department', string='Department',
                                    compute='_compute_department_id', store=True, readonly=False,
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                    help="Once specified, the rank is ONLY available for the selected department. In most cases,"
                                    " this field is preferred to be left blank.")
    role_id = fields.Many2one('hr.role', string='Role', required=True,
                              domain="['&','|',('department_id', '=', False),('department_id', '=', department_id),'|',('company_id', '=', False),('company_id', '=', company_id)]")
    grade_id = fields.Many2one('hr.employee.grade', string='Level', required=True,
                               domain="['&','|',('department_id', '=', False),('department_id', '=', department_id),'|',('company_id', '=', False),('company_id', '=', company_id)]")
    grade_sequence = fields.Integer(related='grade_id.sequence', store=True, index=True)
    parent_id = fields.Many2one('hr.rank', string='Higher Rank', compute='_compute_parent_id', store=True)
    child_ids = fields.One2many('hr.rank', 'parent_id', string='Lower Rank', readonly=True)
    recursive_child_ids = fields.Many2many('hr.rank', 'hr_rank_hr_rank_child_rel', 'parent_id', 'child_id', compute='_compute_recursive_child_ids', store=True,
                                           string='Recursive Children',
                                           help="Direct and indirect lower ranks")
    job_line_ids = fields.One2many('hr.job.rank.line', 'rank_id', string='Job Positions Applied')
    matched_job_ids = fields.Many2many('hr.job', 'hr_job_hr_rank_rel', 'rank_id', 'job_id', string='Jobs that match this rank')
    matched_jobs_count = fields.Integer(string='Related Job Positions', compute='_compute_matched_jobs_count')
    employee_ids = fields.One2many('hr.employee', 'rank_id', string='Employees', help="All the employees that are currently set at this rank.")
    employees_count = fields.Integer(string='Employees Count', compute='_compute_employees_count', compute_sudo=True)
    active = fields.Boolean(compute='_compute_active', store=True, string='Active')
    
    _sql_constraints = [
        (
            'name_uniq',
            'unique(role_id, grade_id, company_id, active)',
            "The combination of Role and Grade must be unique per company!"
            ),
    ]

    @api.depends('role_id.active','grade_id.active')
    def _compute_active(self):
        for r in self:
            if r.role_id and r.grade_id:
                r.active = r.role_id.active and r.grade_id.active
            else:
                r.active = True #When create rank on form
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        ranks = super(HrRank, self).create(vals_list)
        # recompute other ranks in the parent-child chain
        to_recompute = (ranks.role_id.rank_ids | ranks.grade_id.rank_ids) | ranks
        to_recompute._compute_parent_id()
        return ranks

    def write(self, vals):
        """
        Override to recompute ranks in the parent-child chain
        """
        org_ranks = self
        if 'role_id' in vals or 'grade_id' in vals:
            org_ranks |= self.role_id.rank_ids | self.grade_id.rank_ids
        res = super(HrRank, self).write(vals)
        if not self._context.get('donot_recompute_rank_parent_id', False):
            org_ranks.with_context(donot_recompute_rank_parent_id=True)._compute_parent_id()
        return res

    def unlink(self):
        """
        Override to recompute ranks in the parent-child chain
        """
        to_recompute = self.child_ids | self.parent_id
        res = super(HrRank, self).unlink()
        to_recompute._compute_parent_id()
        return res

    @api.depends('role_id.name', 'grade_id.name')
    def _compute_name(self):
        for r in self:
            if r.role_id and r.grade_id:
                r.name = _("{role} | {grade}").format(role=r.role_id.name, grade=r.grade_id.name)
            else:
                r.name = False

    @api.depends('role_id', 'grade_id.recursive_parent_ids')
    def _compute_parent_id(self):
        self.flush()
        candidates = self.env['hr.rank'].search([
            ('role_id', 'in', self.role_id.ids),
            ('grade_id', 'in', self.grade_id.recursive_parent_ids.ids)
            ])
        for r in self:
            r.parent_id = candidates.filtered(lambda c: c.role_id.id == r.role_id.id and c.grade_id.id in r.grade_id.recursive_parent_ids.ids)[:1]

    @api.depends('role_id', 'grade_id')
    def _compute_department_id(self):
        for r in self:
            department = r.department_id
            r.department_id = r.role_id.department_id or r.grade_id.department_id or department

    @api.depends('child_ids')
    def _compute_recursive_child_ids(self):
        for r in self:
            r.recursive_child_ids = r._get_recursive_children()

    def _compute_matched_jobs_count(self):
        for r in self:
            r.matched_jobs_count = len(r.matched_job_ids)

    def _compute_employees_count(self):
        employees_data = self.env['hr.employee'].read_group([('rank_id', 'in', self.ids)], ['rank_id'], ['rank_id'])
        mapped_data = dict([(dict_data['rank_id'][0], dict_data['rank_id_count']) for dict_data in employees_data])
        for r in self:
            r.employees_count = mapped_data.get(r.id, 0)

    @api.constrains('department_id', 'role_id', 'grade_id', 'company_id')
    def _chech_department(self):
        for r in self:
            if r.department_id:
                if r.role_id.department_id and r.role_id.department_id != r.department_id:
                    raise UserError(_("The role %s cannot be applied for the department %s"
                                      " while it is dedicated for the department %s only.")
                                      % (r.role_id.name, r.department_id.name, r.role_id.department_id.name))
                if r.grade_id.department_id and r.grade_id.department_id != r.department_id:
                    raise UserError(_("The grade %s cannot be applied for the department %s"
                                      " while it is dedicated for the department %s only.")
                                      % (r.grade_id.name, r.department_id.name, r.grade_id.department_id.name))
                if r.department_id.company_id != r.company_id:
                    raise UserError(_("The department %s is invalid for the company %s"
                                      " while it is dedicated for the company %s only.")
                                      % (r.department_id.name, r.company_id.name, r.department_id.company_id.name))

    def _get_recursive_children(self):
        children = self.child_ids
        for child in self.child_ids:
            children |= child._get_recursive_children()
        return children

    @api.model
    def _find(self, roles, grades, logic='&'):
        return self.env['hr.rank'].search([logic, ('role_id', 'in', roles.ids), ('grade_id', 'in', grades.ids)])

    @api.model
    def _get_ranks_without_department(self):
        return self.env['hr.rank'].search([('department_id', '=', False)])

    def action_view_hr_jobs(self):
        action = self.env['ir.actions.act_window']._for_xml_id('hr.action_hr_job')
        action['context'] = {}
        action['domain'] = "[('rank_ids','in',%s)]" % self.ids
        return action

    def action_view_employees(self):
        if self.env.user.has_group('hr.group_hr_user'):
            action_xmlid = 'hr.open_view_employee_list_my'
        else:
            action_xmlid = 'hr.hr_employee_public_action'
        action = self.env['ir.actions.act_window']._for_xml_id(action_xmlid)
        # override to get rid off the default context
        ctx = dict(self._context or {})
        ctx.update({
            'default_grade_id': self.grade_id[:1].id,
            'default_role_id': self.role_id[:1].id,
            'default_department_id': self.department_id[:1].id,
            'default_company_id': self.company_id[:1].id,
            })
        action['context'] = ctx
        action['domain'] = [('rank_id', 'in', self.ids)]
        return action
