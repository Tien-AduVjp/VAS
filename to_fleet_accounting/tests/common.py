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
    def create_invoice_from_costs(self, costs):
        self.env['fleet.vehicle.cost.invoicing.wizard'].with_context(active_ids=costs.ids).create_invoices()
        return costs.invoice_id

    @classmethod
    def generate_cost_vehicle(self, vehicle, service, vendor, contract=False, amount=999, user_created=False):
        return self.env['fleet.vehicle.cost'].with_user(user_created or self.env.user).create({
                    'vehicle_id': vehicle.id,
                    'cost_subtype_id': service.id,
                    'vendor_id': vendor and vendor.id or False,
                    'amount': amount,
                    'contract_id': contract and contract.id or False
                })
