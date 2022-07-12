from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import MaintenanceScheduleCommon


@tagged('access_rights')
class TestMaintenanceSecurity(MaintenanceScheduleCommon):

    def test_00_no_group(self):
        """ test case 1
            user_2 has no group of maintenance
            user_2 can only read change stage own equipment
            user_2 can't create equipment
            user_2 can only read action, schedule"""

        self.equipment_2.with_user(self.user_2).read(['id'])

        self.assertRaises(AccessError, self.equipment_2.with_user(self.user_2).write, {'name': 'error'})

        equipment = self.env['maintenance.equipment']\
            .with_user(self.user_1).create(self.equipment_vals(self.user_2))
        self.assertRaises(AccessError, equipment.with_user(self.user_2).unlink)

        self.assertRaises(AccessError, self.equipment_1.with_user(self.user_2).read, ['id'])
        self.assertRaises(AccessError, self.equipment_1.with_user(self.user_2).write, {'name': 'error'})

        self.assertRaises(AccessError, self.env['maintenance.equipment']
                          .with_user(self.user_2).create, self.equipment_vals(self.user_2))

        self.action.with_user(self.user_2).read(['id'])
        self.assertRaises(AccessError, self.action.with_user(self.user_2).write, {'name': 'error'})
        self.assertRaises(AccessError, self.action.with_user(self.user_2).unlink)

    def test_01_no_group_set_technician(self):
        """ test case 1
            user_2 has no group of maintenance
            set user_2 is Technician of equipment_1
            Not change permission"""
        self.equipment_1.write({'technician_user_id': self.user_2.id})
        self.test_00_no_group()

    def test_02_group_equipment_manager(self):
        """  test case 2
            user_2 has group group_equipment_manager,
            user_2 can read, create, write, unlink all document
            user_2 can setting
            user_2 can only read action, schedule"""
        self.user_2.write({'groups_id': [(6, 0, [self.group_equipment_manager.id])]})
        self._check_full_permission()

    def test_03_group_maintenance_user(self):
        """ test case 3
            user_2 has group group_maintenance_user,
            user_2 can read, create, write all equipment, can't unlink
            user_2 can't setting
            user_2 can read, create, write, unlink action, schedule"""
        self.user_2.write({'groups_id': [(6, 0, [self.group_maintenance_user.id])]})

        self.equipment_2.with_user(self.user_2).read(['id'])
        self.equipment_2.with_user(self.user_2).write({'name': 'error'})
        self.assertRaises(AccessError, self.equipment_2.with_user(self.user_2).unlink)

        self.equipment_1.with_user(self.user_2).read(['id'])
        self.equipment_1.with_user(self.user_2).write({'name': 'error'})
        equipment = self.env['maintenance.equipment']\
            .with_user(self.user_2).create(self.equipment_vals(self.user_1))
        self.assertRaises(AccessError, equipment.with_user(self.user_2).unlink)

        self._check_full_permission_action_schedule()

    def test_04_group_maintenance_user_group_equipment_manager(self):
        """ test case 3
            user_2 has group group_equipment_manager, group_maintenance_user
            user_2 can read, create, write, unlink all document
            user_2 can setting
            user_2 can read, create, write, unlink action, schedule"""
        self.user_2.write({'groups_id': [(6, 0, [self.group_maintenance_user.id, self.group_equipment_manager.id])]})
        self._check_full_permission()
        self._check_full_permission_action_schedule()

    def test_05_group_maintenance_manager(self):
        """ test case 4
            user_2 has group group_maintenance_manager,
            user_2 can read, create, write, unlink all equipment
            user_2 can't read, write, unlink another document
            user_2 can't setting
            user_2 can read, create, write, unlink action, schedule"""
        self.user_2.write({'groups_id': [(6, 0, [self.group_equipment_manager.id])]})
        self.equipment_2.with_user(self.user_2).read(['id'])
        self.equipment_2.with_user(self.user_2).write({'name': 'error'})

        self.equipment_1.with_user(self.user_2).read(['id'])
        self.equipment_1.with_user(self.user_2).write({'name': 'error'})
        equipment = self.env['maintenance.equipment']\
            .with_user(self.user_2).create(self.equipment_vals(self.user_1))
        equipment.with_user(self.user_2).unlink()

        self._check_full_permission_action_schedule()

    def test_06_group_equipment_manager(self):
        """ test case 4
            user_2 has group group_equipment_manager
            user_2 can read, create, write, unlink all document
            user_2 can setting
            user_2 can read, create, write, unlink action, schedule"""
        self.user_2.write({'groups_id': [(6, 0, [self.group_equipment_manager.id])]})
        self._check_full_permission()
        self._check_full_permission_action_schedule()

    def _check_full_permission(self):

        self.equipment_2.with_user(self.user_2).read(['id'])
        self.equipment_2.with_user(self.user_2).write({'name': 'error'})

        self.equipment_1.with_user(self.user_2).read(['id'])
        self.equipment_1.with_user(self.user_2).write({'name': 'error'})
        self.equipment_1.with_user(self.user_2).unlink()
        self.equipment_2.with_user(self.user_2).unlink()

    def _check_only_read_action_schedule(self):
        self.action.with_user(self.user_2).read(['id'])
        self.assertRaises(AccessError, self.action.with_user(self.user_2).write, {'name': 'error'})
        self.assertRaises(AccessError, self.action.with_user(self.user_2).unlink)
        self.assertRaises(AccessError, self.env['maintenance.action'].with_user(self.user_2).create, {
            'name': 'test_action_2',
            'service_id': self.product.id,
            'part_replacement': False
        })

        self.schedule.with_user(self.user_2).read(['id'])
        self.assertRaises(AccessError, self.schedule.with_user(self.user_2).write, {'name': 'error'})
        self.assertRaises(AccessError, self.schedule.with_user(self.user_2).unlink)
        self.assertRaises(AccessError, self.env['maintenance.schedule'].with_user(self.user_2).create, {
            'part': 'test_part_2',
            'product_milestone_id': self.milestone.id,
            'maintenance_action_id': self.action.id,
        })

    def _check_full_permission_action_schedule(self):
        self.user_2.write({'groups_id': [(6, 0, [self.group_maintenance_user.id])]})
        self.action.with_user(self.user_2).read(['id'])
        self.action.with_user(self.user_2).write({'name': 'error'})
        action_1 = self.env['maintenance.action'].with_user(self.user_2).create({
            'name': 'test_action_2',
            'service_id': self.product.id,
            'part_replacement': False
        })

        self.schedule.with_user(self.user_2).read(['id'])
        self.schedule.with_user(self.user_2).write({'part': 'error'})
        self.schedule.with_user(self.user_2).unlink()
        self.action.with_user(self.user_2).unlink()
        self.env['maintenance.schedule'].with_user(self.user_2).create({
            'part': 'test_part_2',
            'product_milestone_id': self.milestone.id,
            'maintenance_action_id': action_1.id,
        })
