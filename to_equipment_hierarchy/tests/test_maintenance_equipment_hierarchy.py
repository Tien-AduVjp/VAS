from datetime import date

from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestMaintenanceEquipmentHierarchy(Common):
    
    def test_01_maintenance_equipment_hierarchy(self):
        """
        Các thiết bị được thêm vào mục "Bộ phận trực tiếp" sẽ tự động xuất hiện ở mục "Tất cả Bộ phận (đệ quy)"
        - Input: Thêm một dòng thiết bị ở mục Bộ phận trực tiếp trên thiết bị
        - Output: Dòng thiết bị vừa thêm ở "Bộ phận trực tiếp" sẽ tự động xuất hiện ở mục "Tất cả Bộ phận (đệ quy)
        """
        self.parent_equipment_2.write({'child_ids': [(0, 0, {'name' : 'Direct Parts Test'})]})
        self.assertEqual(self.parent_equipment_2.child_ids, self.parent_equipment_2.recursive_child_ids)
    
    def test_02_maintenance_equipment_hierarchy(self):
        """
        Các thiết bị được xoá ở mục "Bộ phận trực tiếp" sẽ tự động xoá ở mục "Tất cả Bộ phận (đệ quy)"
        - Input: Xoá dòng thiết bị ở mục Bộ phận trực tiếp
        - Output: Dòng thiết bị vừa xoá ở "Bộ phận trực tiếp" sẽ tự động xoá ở mục "Tất cả Bộ phận (đệ quy)"
        """
        self.parent_equipment_2.write({'child_ids': [(0, 0, {'name' : 'Direct Parts Test'})]})
        self.assertEqual(self.parent_equipment_2.child_ids, self.parent_equipment_2.recursive_child_ids)
        self.parent_equipment_2.child_ids.unlink()
        self.assertFalse(self.parent_equipment_2.recursive_child_ids)
    
    def test_03_maintenance_equipment_hierarchy(self):
        """
        Kiểm tra thiết bị con và đệ quy của thiết bị ( phân cấp thiết bị)
        - Input: 
            + Thiết bị parent_equipment_1
            + Thiết bị  child_equipment_1, child_equipment_2 là thiết bị con của parent_equipment_1
            + Thiết bị child_equipment_1_1  là con của child_equipment_1
        - Output:
            + Mục Bộ phận trực tiếp của thiết bị parent_equipment_1 sẽ gồm child_equipment_1, child_equipment_2
            + Mục Tất cả Bộ phận( đệ quy) của thiết bị parent_equipment_1 sẽ gồm child_equipment_1, 
              child_equipment_2, child_equipment_1_1
            + Thông tin người sở hữu, vị trí, của thiết bị con và đệ quy cập nhật theo thiết bị cha
        """
        self.assertIn(self.child_equipment_1, self.parent_equipment_1.child_ids)
        self.assertIn(self.child_equipment_2, self.parent_equipment_1.child_ids)
        
        self.assertIn(self.child_equipment_1, self.parent_equipment_1.recursive_child_ids)
        self.assertIn(self.child_equipment_2, self.parent_equipment_1.recursive_child_ids)
        self.assertIn(self.child_equipment_1_1, self.parent_equipment_1.recursive_child_ids)
        
        all_parts = self.child_equipment_1 | self.child_equipment_2 | self.child_equipment_1_1
        self.assertEqual(self.parent_equipment_1.owner_user_id, all_parts.owner_user_id)
        self.assertEqual(set([self.parent_equipment_1.location]), set(all_parts.mapped('location')))
    
    def test_04_maintenance_equipment_hierarchy(self):
        """
        Kiểm tra thay đổi thiết bị cha của thiết bị
        - Input: Thay đổi thiết bị cha của child_equipment_1 từ parent_equipment_1 sang parent_equipment_2 
        - Output:
            + Mục Bộ phận trực tiếp của thiết bị parent_equipment_2 sẽ gồm child_equipment_1
            + Mục Tất cả Bộ phận( đệ quy) của thiết bị parent_equipment_2 sẽ gồm child_equipment_1, child_equipment_1_1
            + Thông tin người sở hữu, vị trí, của child_equipment_1 và con cháu của nó sẽ cập nhật theo parent_equipment_2
        """
        self.child_equipment_1.write({'parent_id': self.parent_equipment_2.id})
        self.assertIn(self.child_equipment_1, self.parent_equipment_2.child_ids)
        
        self.assertIn(self.child_equipment_1, self.parent_equipment_2.recursive_child_ids)
        self.assertIn(self.child_equipment_1_1, self.parent_equipment_2.recursive_child_ids)
        
        all_parts = self.child_equipment_1 | self.child_equipment_1_1
        self.assertEqual(self.parent_equipment_2.owner_user_id, all_parts.owner_user_id)
        self.assertEqual(set([self.parent_equipment_2.location]), set(all_parts.mapped('location')))
    
    def test_05_maintenance_equipment_hierarchy(self):
        """
        Kiểm tra thay đổi thông tin người sở hữu, ngày phân công, vị trí trên thiết bị cha parent_equipment_1
        - Input: Thay đổi thông tin người sở hữu, ngày phân công, vị trí trên thiết bị cha
        - Output: Các thiết bị con trực tiếp và đệ quy sẽ cập nhật theo thiết bị cha
        """
        # Change Owner
        self.assertEqual(self.parent_equipment_1.owner_user_id, self.owner_user_1)
        self.parent_equipment_1.write({'owner_user_id': self.owner_user_2.id})
        self.assertEqual(self.parent_equipment_1.recursive_child_ids.owner_user_id, self.owner_user_2)
        
        #Change Assign Date              
        self.assertEqual(self.parent_equipment_1.assign_date, date(2021,10,1))
        self.parent_equipment_1.write({'assign_date': date.today()})
        self.assertEqual(set(self.parent_equipment_1.recursive_child_ids.mapped('assign_date')), set([date.today()]))
        
        #Change Location              
        self.parent_equipment_1.write({'location': 'Location Test'})
        self.assertEqual(set(self.parent_equipment_1.recursive_child_ids.mapped('location')), set(['Location Test']))
        
    def test_06_maintenance_equipment_hierarchy(self):
        """
        Kiểm tra yêu cầu Bảo trì của một thiết bị sẽ bao gồm tất cả các yêu cầu bảo trì của thiết bị con và đệ
        - Input: 
            + Tạo một bảo trì cho thiết bị cha
            + Tạo bảo trì cho thiết bị con
        - Output: Mục tất cả bảo trì của thiết bị cha sẽ bao gồm bảo trì của chính nó và các thiết bị con trực tiếp và đệ quy
        """
        self.assertIn(self.maintenence_request_1, self.parent_equipment_1.recursive_maintenance_ids)
        self.assertIn(self.maintenence_request_3, self.parent_equipment_1.recursive_maintenance_ids)
    
    def test_07_maintenance_equipment_hierarchy(self):
        """
        Thay đổi thiết bị cha của thiết bị child_equipment_1 từ parent_equipment_1 sang parent_equipment_2
        - Input: child_equipment_1 có yêu cầu bảo trì liên kết tới
        - Output: Mục tất cả bảo trì của thiết bị parent_equipment_2 sẽ bao gồm bảo trì của chính nó 
                  và các thiết bị con trực tiếp và đệ quy
        """
        self.child_equipment_1.write({'parent_id': self.parent_equipment_2.id})
        self.assertIn(self.maintenence_request_2, self.parent_equipment_2.recursive_maintenance_ids)
        self.assertIn(self.maintenence_request_3, self.parent_equipment_2.recursive_maintenance_ids)
    
    def test_08_maintenance_equipment_hierarchy(self):
        """
        Thay đổi ngày phân công trên thiết bị, cập nhật lại ngày phân công trên tất cả thiết bị con của nó
        - Input: Thay đổi ngày phân công của thiết bị parent_equipment_1
        - Output: Thiết bị con của nó là child_equipment_1, child_equipment_1_1 được thay đổi theo
        """
        self.parent_equipment_1.write({'assign_date': '2021-10-10'})
        self.assertEqual(self.child_equipment_1.assign_date, date(2021, 10, 10))
        self.assertEqual(self.child_equipment_1_1.assign_date, date(2021, 10, 10))
