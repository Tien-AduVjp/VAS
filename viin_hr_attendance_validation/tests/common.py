from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        # timezone: ''

        cls.employee_1 = cls.env['hr.employee'].create({
            'name': 'employee 1'
        })

    def create_attendance(self, employee_id, check_in, check_out=False):
        return self.env['hr.attendance'].with_context(tracking_disable=True).create({
            'employee_id': employee_id,
            'check_in': check_in,
            'check_out': check_out
        })
