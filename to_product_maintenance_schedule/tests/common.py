from odoo.tests.common import SavepointCase


class MaintenanceScheduleCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(MaintenanceScheduleCommon, cls).setUpClass()
        group_user = cls.env.ref('base.group_user')
        cls.group_maintenance_user = cls.env.ref('to_product_maintenance_schedule.group_maintenance_user')
        cls.group_equipment_manager = cls.env.ref('maintenance.group_equipment_manager')
        res_users = cls.env['res.users']
        cls.main_company = cls.env.ref('base.main_company')
        cls.team = cls.env['maintenance.team'].create({
            'name': 'Metrology',
            'company_id': cls.main_company.id,
        })
        cls.user_1 = res_users.create({
            'name': 'user_1',
            'login': 'user_1',
            'email': 'user_1.u0@example.viindoo.com',
            'company_id': cls.main_company.id,
            'groups_id': [(6, 0, [group_user.id,
                                  cls.group_equipment_manager.id])]
        })
        cls.user_2 = res_users.create({
            'name': 'user_2',
            'login': 'user_2',
            'email': 'user_2.u0@example.viindoo.com',
            'company_id': cls.main_company.id,
            'groups_id': [(6, 0, [group_user.id])]
        })

        cls.equipment_1 = cls.env['maintenance.equipment']\
            .with_user(cls.user_1).create(cls.equipment_vals(cls.user_1))
        cls.equipment_2 = cls.env['maintenance.equipment']\
            .with_user(cls.user_1).create(cls.equipment_vals(cls.user_2))
        cls.maintenance_state_new = cls.env['maintenance.stage'].create({
            'name': 'new',
            'sequence': 1,
        })
        cls.maintenance_state_done = cls.env['maintenance.stage'].create({
            'name': 'done',
            'sequence': 2,
        })

        cls.product = cls.env['product.product'].create({
            'name': 'Product',
            'type': 'service',
        })
        cls.action = cls.env['maintenance.action'].create({
            'name': 'test_action',
            'service_id': cls.product.id,
            'part_replacement': False
        })
        uom_unit = cls.env.ref('uom.product_uom_unit')
        uom_dunit = cls.env['uom.uom'].create({
            'name': 'DeciUnit',
            'category_id': uom_unit.category_id.id,
            'factor_inv': 0.1,
            'factor': 10.0,
            'uom_type': 'smaller',
            'rounding': 0.001})
        cls.milestone = cls.env['product.milestone'].create({
            'name': 'milestone',
            'amount': 10000000,
            'uom_id': uom_dunit.id
        })
        cls.schedule = cls.env['maintenance.schedule'].create({
            'part': 'test_part',
            'product_milestone_id': cls.milestone.id,
            'maintenance_action_id': cls.action.id,
        })

    @classmethod
    def equipment_vals(cls, user):
        return {
            'name': 'equipment_1',
            'owner_user_id': user.id,
            'company_id': cls.main_company.id,
            'active': True,
        }

    @classmethod
    def maintenance_vals(cls, user, equipment):
        return {
            'name': 'Some keys are not working',
            'company_id': cls.main_company.id,
            'user_id': user.id,
            'maintenance_team_id': cls.team.id,
            'equipment_id': equipment.id,
            'stage_id': cls.maintenance_state_new.id,
        }
