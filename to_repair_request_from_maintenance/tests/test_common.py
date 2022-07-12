from odoo.tests import SavepointCase

class TestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.partner_a = cls.env.ref('base.res_partner_1')
        cls.partner_b = cls.env.ref('base.res_partner_2')
        cls.partner_c = cls.env.ref('base.res_partner_3')
        
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        
        # Create products to repair
        cls.product_to_repair1,\
        cls.product_to_repair2,\
        cls.product_to_repair3 = cls.env['product.product'].create([
            {
                'name': 'Product To Repair 1',
                'type': 'product',
                'tracking': 'lot',
                },
            {
                'name': 'Product To Repair 2',
                'type': 'product',
                'tracking': 'lot',
                },
            {
                'name': 'Product To Repair 3',
                'type': 'product',
                'tracking': 'lot',
                }])

        cls.lot1, cls.lot2, cls.lot3 = cls.env['stock.production.lot'].create([
            {
                'name': 'lot1',
                'product_id': cls.product_to_repair1.id,
                'company_id': cls.env.company.id,
                'customer_id': cls.partner_a.id,
                },
            {
                'name': 'lot2',
                'product_id': cls.product_to_repair2.id,
                'company_id': cls.env.company.id,
                'customer_id': cls.partner_b.id,
                },
            {
                'name': 'lot3',
                'product_id': cls.product_to_repair3.id,
                'company_id': cls.env.company.id,
                'customer_id': cls.partner_c.id,
                }])

        cls.equipment1,\
        cls.equipment2,\
        cls.equipment3 = cls.env['maintenance.equipment'].create([
            {
                'name': 'Test Equipment 1',
                'lot_id': cls.lot1.id,
                'product_id': cls.product_to_repair1.id
                },
            {
                'name': 'Test Equipment 2',
                'lot_id': cls.lot2.id,
                'product_id': cls.product_to_repair2.id
                },
            {
                'name': 'Test Equipment 3',
                }])

        cls.equipment3.write({'product_id': cls.product_to_repair3.id})

        cls.maintenance_request1,\
        cls.maintenance_request2,\
        cls.maintenance_request3,\
        cls.maintenance_request4 = cls.env['maintenance.request'].create([
            {
                'name': 'Maintenance Request 1',
                'equipment_id': cls.equipment1.id,
                'maintenance_type': 'corrective',
                'duration': 24,
                'company_id': cls.env.company.id,
                },
            {
                'name': 'Maintenance Request 2',
                'equipment_id': cls.equipment2.id,
                'maintenance_type': 'corrective',
                'duration': 48,
                'company_id': cls.env.company.id,
                },
            {
                'name': 'Maintenance Request 3',
                'equipment_id': cls.equipment3.id,
                'maintenance_type': 'corrective',
                'duration': 32,
                'company_id': cls.env.company.id,
                },
            {
                'name': 'Maintenance Request 4',
                'maintenance_type': 'corrective',
                'duration': 24,
                'company_id': cls.env.company.id,
                }])
