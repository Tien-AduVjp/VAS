from odoo.tests.common import tagged, Form

from .common import Common


@tagged('-at_install', 'post_install')
class TestOnchangeAssignDate(Common):
    
    def test_onchange_assign_date(self):
        """
        Input: Thay đổi parent trên thiết bị
        Output: Ngày phân công trên thiết bị thay đổi theo ngày phân công của thiết bị cha
        """
        equipment_form = Form(self.env['maintenance.equipment'])
        equipment_form.name = 'Equipment Test'
        equipment_form.parent_id = self.parent_equipment_1
        self.assertEqual(equipment_form.assign_date, self.parent_equipment_1.assign_date)
