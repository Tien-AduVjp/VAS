from datetime import date

from odoo.tests.common import SavepointCase


class Common(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        
        #Người dùng
        cls.owner_user_1 = cls.env.ref('base.user_admin')
        cls.owner_user_2 = cls.env.ref('base.user_demo')
        # Thiết bị
        # Thiết bị cha
        cls.parent_equipment_1 = cls.env['maintenance.equipment'].with_context(tracking_disable=True).create({
            'name':'Parent Equipment 1',
            'assign_date': date(2021, 10, 1),
            'location':'Location of Parent Equipment 1',
            'employee_id': cls.owner_user_1.employee_id.id
        })
        cls.parent_equipment_2 = cls.env['maintenance.equipment'].with_context(tracking_disable=True).create({
            'name':'Parent Equipment 2',
            'assign_date': date(2021,10,1),
            'location':'Location of Parent Equipment 2',
            'employee_id': cls.owner_user_2.employee_id.id
        })
        # Thiết bị con
        cls.child_equipment_1 = cls.env['maintenance.equipment'].with_context(tracking_disable=True).create({
            'name':'Child Equipment 1',
            'parent_id': cls.parent_equipment_1.id
        })
        cls.child_equipment_2 = cls.env['maintenance.equipment'].with_context(tracking_disable=True).create({
            'name':'Child Equipment 2',
            'parent_id': cls.parent_equipment_1.id
        })
        # Thiết bị đệ quy
        cls.child_equipment_1_1 = cls.env['maintenance.equipment'].with_context(tracking_disable=True).create({
            'name':'Child Equipment 01_01',
            'parent_id': cls.child_equipment_1.id
        })
        
        # Yêu cầu bảo trì thiết bị
        cls.maintenence_request_1 = cls.env['maintenance.request'].with_context(tracking_disable=True).create({
            'name':'Maintenence Request Parent Equipment 1',
            'equipment_id': cls.parent_equipment_1.id
        })
        cls.maintenence_request_2 = cls.env['maintenance.request'].with_context(tracking_disable=True).create({
            'name':'Maintenence Request Parent Equipment 2',
            'equipment_id': cls.parent_equipment_2.id
        })
        cls.maintenence_request_3 = cls.env['maintenance.request'].with_context(tracking_disable=True).create({
            'name':'Maintenence Request Child Equipment 1',
            'equipment_id': cls.child_equipment_1.id
        })
