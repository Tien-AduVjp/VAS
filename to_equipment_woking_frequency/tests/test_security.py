from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSecurity(TransactionCase):

    def setUp(self):
        super().setUp()
        self.working_frequency_template_obj = self.env['working.frequency.template']
        self.equipment_working_frequency_obj = self.env['equipment.working.frequency']
        self.product_uom_unit_id = self.ref('uom.product_uom_unit')
        self.product_uom_kgm_id = self.ref('uom.product_uom_kgm')
        self.day_uom_id = self.ref('uom.product_uom_day')
        self.res_users = self.env['res.users']
        self.group_base_user = self.env.ref('base.group_user')
        self.group_maintenance_user = self.env.ref('to_product_maintenance_schedule.group_maintenance_user')
        self.group_equipment_manager = self.env.ref('maintenance.group_equipment_manager')
        self.maintenance_manager = self.res_users.create({
            'name':'Manager Working Frequency Template',
            'login':'manager_wft',
            'email':'manager.working_frequency@example.viindoo.com',
            'groups_id':[(6, 0, [self.group_equipment_manager.id])]
        })
        self.maintenance_user = self.res_users.create({
            'name':'User Working Frequency Template',
            'login':'user_wft',
            'email':'user.working_frequency@example.viindoo.com',
            'groups_id':[(6, 0, [self.group_maintenance_user.id])]
        })
        self.base_user = self.res_users.create({
            'name':'Base User',
            'login':'base_user',
            'email':'base_user.working_frequency@example.viindoo.com',
            'groups_id':[(6, 0, [self.group_base_user.id])]
        })
        self.working_frequency_template_data = {
            'working_amount':140.0,
            'working_uom_id':self.product_uom_unit_id,
            'period_time':7.0,
        }

    def test_manager_access_right(self):
        """
            User in group manager working frequency template have access right: read/create/edit/unlink
        """
         # Check accessright maintenance manager with model working.frequency.template
        working_frequency_template = self.working_frequency_template_obj\
                                    .with_user(self.maintenance_manager)\
                                    .create(self.working_frequency_template_data)
        self.assertTrue(working_frequency_template and True , "Manager can create product working frequency.")
        is_write_working_frequency = working_frequency_template.with_user(self.maintenance_manager).write({
            'working_amount':280.0
        })
        self.assertTrue(is_write_working_frequency, "Maintenance Manager can edit product working frequency.")
        is_unlink_working_frequency = working_frequency_template.with_user(self.maintenance_manager).unlink()
        self.assertTrue(is_unlink_working_frequency, "Maintenance Manager can unlink product working frequency.")
        # Check accessright maintenance manager with model equipment.working.frequency
        equipment_working_frequency = self.equipment_working_frequency_obj\
                                    .with_user(self.maintenance_manager)\
                                    .create(self.working_frequency_template_data)
        self.assertTrue(equipment_working_frequency and True , "Maintenance Manager can create equipment working frequency.")
        is_write_equipment_working_frequency = equipment_working_frequency\
                                                .with_user(self.maintenance_manager)\
                                                .write({
                                                    'working_amount':280.0
                                                })
        self.assertTrue(is_write_equipment_working_frequency, "Maintenance Manager can edit equipment working frequency")
        is_unlink_equipment_working_frequency = equipment_working_frequency.with_user(self.maintenance_manager).unlink()
        self.assertTrue(is_unlink_equipment_working_frequency, "Maintenance Manager can unlink equipment working frequency.")

    def test_user_working_frequence_access_right(self):
        """
            User in group working frequency template have access right: read/create/edit/unlink
        """
        # Check accessright maintenance user with model working.frequency.template.
        working_frequency_template = self.working_frequency_template_obj\
                                    .with_user(self.maintenance_user)\
                                    .create(self.working_frequency_template_data)
        self.assertTrue(working_frequency_template and True , "Maintenance User can create product working frequency")
        is_update_working_frequency = working_frequency_template.with_user(self.maintenance_user).write({
            'working_amount':280.0
        })
        self.assertTrue(is_update_working_frequency, "Maintenance User can edit product working frequency")
        is_unlink_working_frequency = working_frequency_template.with_user(self.maintenance_user).unlink()
        self.assertTrue(is_unlink_working_frequency, "Maintenance User can unlink product working frequency")
        # Check accessright maintenance user with model equipment.working.frequency.
        equipment_working_frequency = self.equipment_working_frequency_obj\
                                    .with_user(self.maintenance_user)\
                                    .create(self.working_frequency_template_data)
        self.assertTrue(equipment_working_frequency and True , "Maintenance Manager can create equipment working frequency.")
        is_write_equipment_working_frequency = equipment_working_frequency\
                                                .with_user(self.maintenance_user)\
                                                .write({
                                                    'working_amount':280.0
                                                })
        self.assertTrue(is_write_equipment_working_frequency, "Maintenance Manager can edit equipment working frequency")
        is_unlink_equipment_working_frequency = equipment_working_frequency.with_user(self.maintenance_user).unlink()
        self.assertTrue(is_unlink_equipment_working_frequency, "Maintenance Manager can unlink equipment working frequency.")

    def test_base_user_access_right(self):
        """
            User in group base user can have read only access right.
        """
        # Check accessright base user with model working.frequency.template.
        with self.assertRaises(AccessError):
            self.working_frequency_template_obj.with_user(self.base_user).create(self.working_frequency_template_data)
        self.working_frequency = self.working_frequency_template_obj.create(self.working_frequency_template_data)
        with self.assertRaises(AccessError):
            self.working_frequency.with_user(self.base_user).write({
                'working_amount':280.0
            })
        with self.assertRaises(AccessError):
            self.working_frequency.with_user(self.base_user).unlink()
        self.assertTrue(self.working_frequency.with_user(self.base_user).read(['id']) and True, "Base User can read product working frequency")
        # Check accessright base user with model equipment.working.frequency
        with self.assertRaises(AccessError):
            self.equipment_working_frequency_obj.with_user(self.base_user).create(self.working_frequency_template_data)
        self.equipment_working_frequency = self.equipment_working_frequency_obj.create(self.working_frequency_template_data)
        with self.assertRaises(AccessError):
            self.equipment_working_frequency.with_user(self.base_user).write({
                'working_amount':280.0
            })
        with self.assertRaises(AccessError):
            self.equipment_working_frequency.with_user(self.base_user).unlink()
        self.assertTrue(self.equipment_working_frequency.with_user(self.base_user).read(['id']) and True, "Base User can read equipment working frequency")
