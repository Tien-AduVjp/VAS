from odoo import fields

from odoo.addons.to_approvals.tests.common import Common

class Common(Common):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        cls.department = cls.env.ref('hr.dep_ps')

        User = cls.env['res.users'].with_context(no_reset_password=True, tracking_disable=True)

        cls.base_user = cls.env.ref('base.user_demo')
        cls.base_user.groups_id = [(6, 0, [cls.env.ref('base.group_user').id])]

        cls.user_officer = User.create({
            'name': 'User Officer',
            'login': 'user officer',
            'email': 'officer.user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('hr_recruitment.group_hr_recruitment_user').id])]
        })
        cls.user_officer.action_create_employee()
        cls.user_officer.department_id = cls.department

        cls.user_manager = User.create({
            'name': 'User Manager',
            'login': 'user manager',
            'email': 'manager.user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('hr_recruitment.group_hr_recruitment_manager').id])]
        })
        cls.user_manager.action_create_employee()
        cls.user_manager.department_id = cls.department

        cls.hr_job = cls.env.ref('hr.job_developer')
        cls.hr_job.description = 'hr_job description'
        cls.hr_job.requirements = 'hr_job requirement'

        cls.approval_recruitment_type = cls.env['approval.request.type'].search([('type', '=', 'recruitment')], limit=1)

    @classmethod
    def create_recruitment_request(cls, job, exp_count=1, user_create=False):
        request = cls.env['approval.request'].with_user(user_create or cls.env.user).with_context(tracking_disable=True).create({
            'title': 'request',
            'approval_type_id': cls.approval_recruitment_type.id,
            'job_tmp': 'job',
            'job_id': job.id if job else False,
            'description': 'desc',
            'description_job': 'desc job',
            'currency_id':cls.env.company.currency_id.id,
            'requirements': 'req',
            'expected_employees': exp_count,
            'deadline': fields.Date.today()
            })

        request = request.with_user(cls.env.user)
        return request

    @classmethod
    def create_validated_recruitment_request(cls, job=False, exp_count=1, user_create=False):
        request = cls.create_recruitment_request(job, exp_count, user_create)
        request.action_confirm()
        request.with_context(force_approval=True).action_validate()
        return request

    @classmethod
    def create_applicant_apply_job(cls, job):
        return cls.env['hr.applicant'].with_context(tracking_disable=True).create({
            'name': 'H',
            'job_id': job.id
            })

    @classmethod
    def action_recruit_applicant(cls, applicant):
        applicant.partner_name = applicant.name
        res = applicant.create_employee_from_applicant()
        cls.env['hr.employee'].with_context(res['context'], tracking_disable=True).create({'name': 'H'})
        return applicant
