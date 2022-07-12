from odoo import fields

from odoo.addons.to_approvals.tests.common import Common


class CommonMaintenanceApproval(Common):

    @classmethod
    def setUpClass(cls):
        super(CommonMaintenanceApproval, cls).setUpClass()
        cls.equipment_1 = cls.env['maintenance.equipment'].create({
            'name': 'Equiment 1',
            'employee_id': cls.employee1.id
        })
        cls.maintenance_request_type = cls.env['approval.request.type'].search([('type', '=', 'maintenance_type')], limit=1)
        cls.maintenance_approval = cls.env['approval.request'].create({
            'title':'Maintenance Approval Request',
            'approval_type_id': cls.maintenance_request_type.id,
            'currency_id': cls.env.company.currency_id.id,
            'employee_id': cls.employee1.id,
            'deadline': fields.Date.today()
        })
