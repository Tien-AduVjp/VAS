from odoo.tests.common import SavepointCase, Form


class Common(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))
        
        cls.vehicle1 = cls.env.ref('fleet.vehicle_1')
        cls.vehicle2 = cls.env.ref('fleet.vehicle_2')
        
        cls.haiphong = cls.env['res.partner'].create({'name': 'Haiphong'})
        cls.hanoi = cls.env['res.partner'].create({'name': 'Hanoi'})
        
        cls.route_section1 = cls.env['route.section'].create({
            'address_from_id': cls.haiphong.id,
            'address_to_id': cls.hanoi.id,
            'distance': 100,
            'ave_speed': 70
        })
        with Form(cls.env['route.route']) as route_form:
            route_form.name = 'Haiphong - Hainoi'
            with route_form.waypoint_ids.new() as point:
                point.address_id = cls.haiphong
            with route_form.waypoint_ids.new() as point:
                point.address_id = cls.hanoi
        cls.route1 = route_form.save()
       
        with Form(cls.env['fleet.vehicle.trip']) as trip_form:
            trip_form.route_id = cls.route1
            trip_form.vehicle_id = cls.vehicle1
            trip_form.driver_id = cls.env.ref('base.partner_demo')
            trip_form.expected_start_date = '2021-10-18 08:00:00'
        cls.vehicle_trip1 = trip_form.save()
        
        cls.service_type1 = cls.env['fleet.service.type'].create({
            'name': 'Car wash',
            'product_id': cls.env.ref('product.product_order_01').id,
            'category': 'service'
        })
        cls.partner1 = cls.env.ref('base.res_partner_1')
        cls.partner2 = cls.env.ref('base.res_partner_2')
        
        cls.company1, cls.company2 = cls.env['res.company'].create([
            {'name': 'Company A'},
            {'name': 'Company B'}
        ])
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_admin = cls.env.ref('base.user_admin')
 
    @classmethod
    def record_revenue_from_trip(cls, fleet_vehicle_trip_id, amount, user=None, **kwargs):
        Wizard = cls.env['vehicle.trip.register.revenue.wizard']
        if user:
            Wizard = Wizard.with_user(user)
            
        wizard = Wizard.with_context(active_id=fleet_vehicle_trip_id.id).create({
            'customer_id': cls.partner1.id,
            'trip_waypoint_id': cls.vehicle_trip1.trip_waypoint_ids[0].id,
            'amount': amount
        }) 
        wizard.write(kwargs)
        wizard.action_register_revenue()
    
    @classmethod
    def create_customer_invoice_from_trip(cls, fleet_vehicle_trip_ids, user=None, **kwargs):
        Wizard = cls.env['trip.invoicing.revenue.wizard'].with_context(active_ids=fleet_vehicle_trip_ids.ids)
        if user:
            Wizard = Wizard.with_user(user)
        
        wizard_form = Form(Wizard)
        wizard = wizard_form.save()
        wizard.write(kwargs)
        wizard.create_invoices()
