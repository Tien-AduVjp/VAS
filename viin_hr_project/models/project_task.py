from odoo import models, fields, api, _
from lxml import etree
 
 
class ProjectTask(models.Model):
    _inherit = 'project.task'

    department_id = fields.Many2one(related='project_id.department_id', string='Department', store=True)
    assign_employee_id = fields.Many2one('hr.employee', string='Assigned Employee', compute='_compute_assign_employee',
                                         store=True)
    employee_ids = fields.Many2many('hr.employee', string='Associated Employees', compute='_compute_employee_ids',
                                    compute_sudo=True, search='_search_employee_ids',
                                    help="Employees involving the task by logging timesheet.")
    associated_department_ids = fields.Many2many('hr.department', string='Associated Departments',
                                                 compute='_compute_involving_department', search='_search_department_ids',
                                                 compute_sudo=True)
  
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Adding filter by user department and subordinate
        """

        res = super(ProjectTask, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        name_field = doc.xpath("//separator[@name='department_subordinate_separator']")        
        
        if view_id == self.env.ref('project.view_task_search_form').id and name_field:
            current_user = self.env.user
            management_departments = self.env['hr.department'].search([('manager_id', '=', current_user.employee_id.id)])
            current_user_departments = (current_user.employee_id.department_id | management_departments)
            name_field[0].addnext(etree.Element('filter', {
                'string':_('My Subordinate Tasks'),
                'name':'subordinate_tasks',
                'domain':"[('assign_employee_id','in',%s)]" % current_user.employee_id.subordinate_ids.ids
            }))              
            name_field[0].addnext(etree.Element('filter', {
                'string':_('My Department Tasks'),
                'name':'department_task' ,
                'domain':"[('department_id','in',%s)]" % current_user_departments.ids
            }))  
            name_field[0].addnext(etree.Element("filter", {
                'string':_('My Department Involve Tasks'),
                'name':'associated_with_my_department',
                'domain':"[('associated_department_ids','in',%s)]" % current_user_departments.ids
            }))          
            name_field[0].addnext(etree.Element('filter', {
                'string':_('My Subordinates Involve Tasks'),
                'name':'associated_with_my_subordinate',
                'domain':"[('employee_ids','in',%s)]" % current_user.employee_id.subordinate_ids.ids
            }))
            res['arch'] = etree.tostring(doc, encoding='unicode')           
        return res

    @api.depends('user_id.employee_ids', 'company_id')
    def _compute_assign_employee(self):
        employees = self.env['hr.employee'].search([
            ('user_id', 'in', self.user_id.ids),
            '|', ('company_id', 'in', self.company_id.ids), ('company_id', '=', False)
            ])
        for r in self:
            r.assign_employee_id = employees.filtered_domain(
                [('user_id', '=', r.user_id.id),
                 '|', ('company_id', '=', r.company_id.id), ('company_id', '=', False)]
                )[:1]

    @api.depends('timesheet_ids')
    def _compute_employee_ids(self): 
        for r in self:
            r.employee_ids = r.timesheet_ids.employee_id.ids

    @api.depends('employee_ids')
    def _compute_involving_department(self):
        for r in self:
            r.associated_department_ids = r.employee_ids.department_id

    def _search_employee_ids(self, operator, operand):
        """Search tasks by associated employee"""

        if operator == 'in':
            domain = [('id', operator, operand)]
        else:
            domain = [('name', operator, operand)]  
        employees = self.env['hr.employee'].search(domain)
        tasks = self.env['account.analytic.line'].search([('employee_id', 'in', employees.ids)]).task_id
        return[('id', 'in', tasks.ids)]

    def _search_department_ids(self, operator, operand):
        """Search tasks by associated deparment"""

        if operator == 'in':
            domain = [('id', operator, operand)]
        else:
            domain = [('name', operator, operand)]        
        deparments = self.env['hr.department'].search(domain)
        tasks = self.env['account.analytic.line'].search([('department_id', 'in', deparments.ids)]).task_id 
        return[('id', 'in', tasks.ids)]
 
