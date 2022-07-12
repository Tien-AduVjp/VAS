from odoo.tests import tagged, Form

from odoo.addons.viin_hr.tests.common import HrTestEmployeeCommon


@tagged('post_install', '-at_install')
class HrTestEmployeeCommon(HrTestEmployeeCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # =======Applicant========
        cls.applicant_a = cls.env['hr.applicant'].create({
            'name': 'Applicant Man',
            'partner_name': 'Applicant Man'
            })

        # Odoo user form to create employee
        applicant_dict = cls.applicant_a.create_employee_from_applicant()
        employee_form = Form(cls.env['hr.employee'].with_context(applicant_dict['context']))
        employee_form.save()

        # =======Employee=========
        cls.employee_a = cls.applicant_a.emp_id
