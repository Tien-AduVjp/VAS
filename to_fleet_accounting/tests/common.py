from odoo.tests import SavepointCase


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.service_1 = cls.env.ref('fleet.type_service_service_1')
        cls.service_2 = cls.env.ref('fleet.type_service_service_2')

        cls.vendor_1 = cls.env.ref('base.res_partner_3')
        cls.vendor_2 = cls.env.ref('base.res_partner_4')

        cls.vehicle_1 = cls.env.ref('fleet.vehicle_1')
        cls.vehicle_2 = cls.env.ref('fleet.vehicle_2')

    @classmethod
    def create_invoice_from_services(self, services):
        self.env['fleet.vehicle.log.services.invoicing.wizard'].with_context(active_ids=services.ids).create_invoices()
        services.invalidate_cache()
        return services.invoice_id

    @classmethod
    def generate_service_vehicle(self, vehicle, service_type, vendor, contract=False, amount=999, user_created=False):
        return self.env['fleet.vehicle.log.services'].with_user(user_created or self.env.user).create({
                    'vehicle_id': vehicle.id,
                    'service_type_id': service_type.id,
                    'vendor_id': vendor and vendor.id or False,
                    'amount': amount,
                })
