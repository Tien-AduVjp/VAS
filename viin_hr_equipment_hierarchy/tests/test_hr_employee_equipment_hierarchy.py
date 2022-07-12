from odoo.tests.common import tagged
from odoo.addons.to_equipment_hierarchy.tests.common import Common


@tagged('-at_install', 'post_install')
class TestHrEmployeeEquipmentHierarchy(Common):

    @classmethod
    def setUpClass(cls):
        super(TestHrEmployeeEquipmentHierarchy, cls).setUpClass()
        #Nhân viên
        cls.employee_1 = cls.env.ref('hr.employee_admin')
        cls.employee_2 = cls.env.ref('hr.employee_qdp')

        # Thiết bị
        cls.parent_equipment_1.write({'equipment_assign_to': 'employee', 'employee_id': cls.employee_1.id})
        cls.equipment_test = cls.env['maintenance.equipment'].create({
            'name':'Equipment Test',
        })

    def test_01_employee_equipment_hierarchy(self):
        """
        Case 1: Tạo thiết bị có thiết bị cha
        Input:
            - Thiết bị cha có kiểu phân công là Nhân viên
            - Chọn hoặc tạo thiết bị là con của thiết bị cha
        Output: Ngày phân công, kiểu phân công, nhân viên của thiết bị con được tính toán giống với thiếu bị cha
        """
        self.equipment_test.write({'parent_id': self.parent_equipment_1.id})
        self.assertRecordValues(
            self.equipment_test,
            [{
                'employee_id': self.parent_equipment_1.employee_id.id,
                'equipment_assign_to': 'employee',
                'assign_date': self.parent_equipment_1.assign_date
            }]
        )

    def test_02_employee_equipment_hierarchy(self):
        """
        Case 2: Thay đổi ngày phân công, kiểu phân công, hoặc nhân viên phân công của thiết bị cha
        Input:
            - Thay đổi ngày phân công, kiểu phân công, hoặc nhân viên phân công của thiết bị cha
        Output: Các thiết bị con trực tiếp và gián tiếp thay đổi tương ứng với thiết bị cha
        """
        self.parent_equipment_1.write({
            'employee_id': self.employee_2.id,
            'assign_date': '2021-11-03',
            'equipment_assign_to': 'other'
        })
        self.assertRecordValues(
            self.child_equipment_1 | self.child_equipment_2 | self.child_equipment_1_1,
            [
                {
                    'employee_id': self.parent_equipment_1.employee_id.id,
                    'equipment_assign_to': self.parent_equipment_1.equipment_assign_to,
                    'assign_date': self.parent_equipment_1.assign_date,
                    'department_id': self.parent_equipment_1.department_id
                },
                {
                    'employee_id': self.parent_equipment_1.employee_id.id,
                    'equipment_assign_to': self.parent_equipment_1.equipment_assign_to,
                    'assign_date': self.parent_equipment_1.assign_date,
                    'department_id': self.parent_equipment_1.department_id
                },
                {
                    'employee_id': self.parent_equipment_1.employee_id.id,
                    'equipment_assign_to': self.parent_equipment_1.equipment_assign_to,
                    'assign_date': self.parent_equipment_1.assign_date,
                    'department_id': self.parent_equipment_1.department_id
                }
            ]
        )
