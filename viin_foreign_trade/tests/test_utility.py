from odoo.tests import Form, tagged

from .common import TestCommon
from odoo.exceptions import UserError

@tagged('post_install', '-at_install')
class TestPartner(TestCommon):

    def test_update_picking_type_01(self):
        """
        [Form Test] - TC07

        - Case: Update type of operation of picking type to internal transfer while it is set as foreign trade
        - Expected Result:
            + picking type will not be set foreign trade
        """
        # Create test picking type
        test_picking_type = self.env['stock.picking.type'].create({
            'name': 'Test Import - Custom Zone',
            'warehouse_id': self.checked_warehouse.id,
            'code': 'incoming',
            'sequence_code': 'IN',
            'is_foreign_trade': True,
            'use_create_lots': True,
            'use_existing_lots': False,
            'custom_clearance_type': 'import',
            'active': True,
            'company_id': self.checked_warehouse.company_id.id,
        })

        with Form(test_picking_type) as f:
            f.code = 'internal'
            f.default_location_src_id = self.env.ref('stock.stock_location_suppliers')
            f.default_location_dest_id = self.env.ref('stock.stock_location_stock')
            self.assertTrue(not f.is_foreign_trade)

    def test_after_install_module_01(self):
        """
        [Functional Test] - TC01

        - Case: After install module, check created data
        - Expected Result:
            + There is a new journal, which created for custom clearance.
                And each company, which has chart of account setting up, will have default journal for custom clearance
            + There are sequences, which created for import/export custom declaration, and they are setup for companies
            + There are locations, which created for import/export custom zone
            + There are sequences, which created for import/export operation, and they are setup for warehouses
            + There are picking types, which created for import/export operation for warehouses
            + 1st warehouse is enabled for foreign trade import/export, and rules,
                routes related to import/export are created for this warehouse
            + partner of each company will be updated (is foreign trade or not)
            + PO which has partner is marked as foreign trade partner will be marked as foreign trade
            + SO which has partner is marked as foreign trade partner will be marked as foreign trade
            + PO which is marked as foreign trade, and state is not in [purchase,done] will be updated
                to use picking type related to import operation
            + There is a new journal, which created for landed cost .
                And each company, which has chart of account setting up, will have default journal for landed cost.
        """
        # check created journal
        for company in self.env['res.company'].search([('chart_template_id', '!=', False)]):
            journal_id = self.env['account.journal'].search([('code', '=', 'CDJ'), ('company_id', '=', company.id)])
            self.assertTrue(len(journal_id) == 1)

        # check created stock location, picking type and their sequences used for import/export custom zone
        for warehouse in self.env['stock.warehouse'].search([]):
            import_custom_zone_loc = warehouse.imp_custom_zone_loc_id
            export_custom_zone_loc = warehouse.exp_custom_zone_loc_id
            exp_custom_zone_type = warehouse.exp_custom_zone_type_id
            imp_custom_zone_type = warehouse.imp_custom_zone_type_id
            exp_type = warehouse.exp_type_id
            imp_type = warehouse.imp_type_id
            self.assertTrue(all([import_custom_zone_loc, export_custom_zone_loc, exp_custom_zone_type, imp_custom_zone_type,
                                 exp_type, imp_type]))
            self.assertTrue(all([exp_custom_zone_type.sequence_id, imp_custom_zone_type.sequence_id,
                                 exp_type.sequence_id, imp_type.sequence_id]))

        # check rules and routes created for 1st warehouse
        self.assertTrue(self.checked_warehouse.import_to_resupply)
        self.assertTrue(all([self.checked_warehouse.buy_import_pull_id,
                             self.checked_warehouse.foreign_mto_pull_id,
                             self.checked_warehouse.import_route_id,
                             self.checked_warehouse.export_route_id]))

        # check PO
        purchase_orders = self.env['purchase.order'].search([('partner_id.property_foreign_trade_partner', '=', True)])
        purchase_orders_foreign_trade = purchase_orders.filtered(lambda po: po.foreign_trade)
        unconfirmed_orders = purchase_orders.filtered(lambda po: po.state not in ['purchase', 'done'])
        unconfirmed_orders_picking_type = unconfirmed_orders.picking_type_id
        unconfirmed_orders_picking_type_foreign_trade = unconfirmed_orders_picking_type.filtered(lambda pk: pk.is_custom_clearance
                                                                                                 and pk.custom_clearance_type == 'import')
        self.assertEqual(purchase_orders_foreign_trade, purchase_orders)
        self.assertEqual(unconfirmed_orders_picking_type, unconfirmed_orders_picking_type_foreign_trade)

        # check SO
        sale_orders = self.env['sale.order'].search([('partner_id.property_foreign_trade_partner', '=', True)])
        sale_orders_foreign_trade = sale_orders.filtered(lambda so: so.foreign_trade)
        self.assertEqual(sale_orders_foreign_trade, sale_orders)


        # check created sequences for import/export custom declaration, partner on each company
        Parner = self.env['res.partner']
        export_customer_loc_id = self.env.ref('viin_foreign_trade.to_stock_location_customers_export')
        for company in self.env['res.company'].search([]):
            import_dec_seq = company.imp_custom_dec_sequence_id
            export_dec_seq = company.exp_custom_dec_sequence_id
            self.assertTrue(import_dec_seq and export_dec_seq)

            company_partners = Parner.search([('company_id', '=', company.id)])
            for partner in company_partners:
                if partner.country_id.id != company.country_id.id:
                    self.assertTrue(partner.property_foreign_trade_partner)
                    self.assertEqual(partner.property_stock_customer, export_customer_loc_id)

        for company in self.env['res.company'].search([('chart_template_id', '!=', False)]):
            journal_id = self.env['account.journal'].search([('code', '=', 'ITLC'), ('company_id', '=', company.id)])
            self.assertTrue(len(journal_id) == 1)

    def test_create_company_01(self):
        """
        [Functional Test] - TC02

        - Case: Create new company
        - Expected Result:
            + created company has sequence for import/export custom declaration
            + created company has default journal for landed cost
            + created company has default journal for custom declaration
        """
        new_company = self.env['res.company'].create({
            'name': 'Test New Company'
        })
        self.assertTrue(all([new_company.imp_custom_dec_sequence_id, new_company.exp_custom_dec_sequence_id]))

        self.env.company.chart_template_id._load(15.0, 15.0, new_company)
        self.assertTrue(new_company.landed_cost_journal_id.code == 'ITLC')
        self.assertTrue(new_company.account_journal_custom_clearance.code == 'CDJ')

    def test_update_warehouse_01(self):
        """
        [Functional Test] - TC03

        - Case: Update incoming shipment warehouse of warehouse to 2/3 steps
        - Expected Result:
            + rule and routes related to incoming shipment of warehouse will be updated
        """
        self.checked_warehouse.write({
            'reception_steps': 'two_steps'
        })
        self.assertEqual(self.checked_warehouse.imp_custom_zone_type_id.default_location_dest_id,
                         self.checked_warehouse.wh_input_stock_loc_id)

        self.checked_warehouse.write({
            'reception_steps': 'one_step'
        })
        self.assertEqual(self.checked_warehouse.imp_custom_zone_type_id.default_location_dest_id,
                         self.checked_warehouse.lot_stock_id)

        self.checked_warehouse.write({
            'reception_steps': 'three_steps'
        })
        self.assertEqual(self.checked_warehouse.imp_custom_zone_type_id.default_location_dest_id,
                         self.checked_warehouse.wh_input_stock_loc_id)

    def test_update_warehouse_02(self):
        """
        [Functional Test] - TC04

        - Case: Update outgoing shipment warehouse of warehouse to 2/3 steps
        - Expected Result:
            + rule and routes related to outgoing shipment of warehouse will be updated
        """
        self.checked_warehouse.write({
            'delivery_steps': 'pick_ship'
        })
        self.assertEqual(self.checked_warehouse.exp_custom_zone_type_id.default_location_src_id,
                         self.checked_warehouse.wh_output_stock_loc_id)
        self.assertTrue(not self.checked_warehouse.foreign_mto_pull_id.active)

        self.checked_warehouse.write({
            'delivery_steps': 'ship_only'
        })
        self.assertEqual(self.checked_warehouse.exp_custom_zone_type_id.default_location_src_id,
                         self.checked_warehouse.lot_stock_id)
        self.assertTrue(self.checked_warehouse.foreign_mto_pull_id.active)

        self.checked_warehouse.write({
            'delivery_steps': 'pick_pack_ship'
        })
        self.assertEqual(self.checked_warehouse.exp_custom_zone_type_id.default_location_src_id,
                         self.checked_warehouse.wh_output_stock_loc_id)
        self.assertTrue(not self.checked_warehouse.foreign_mto_pull_id.active)

    def test_update_warehouse_03(self):
        """
        [Functional Test] - TC05

        - Case: Disable foreign import/export for warehouse
        - Expected Result:
            + related location, picking type, rule, route of warehouse will not be activated
        """
        new_warehouse = self.env['stock.warehouse'].create({
            'name': 'Test New Warehouse',
            'reception_steps': 'one_step',
            'delivery_steps': 'ship_only',
            'import_to_resupply': True,
            'code': 'NTWH'})

        new_warehouse.write({
            'import_to_resupply': False
        })
        self.assertTrue(not new_warehouse.imp_custom_zone_loc_id.active)
        self.assertTrue(not new_warehouse.exp_custom_zone_loc_id.active)
        self.assertTrue(not new_warehouse.imp_type_id.active)
        self.assertTrue(not new_warehouse.exp_type_id.active)
        self.assertTrue(not new_warehouse.imp_custom_zone_type_id.active)
        self.assertTrue(not new_warehouse.exp_custom_zone_type_id.active)
        self.assertTrue(not new_warehouse.import_route_id.active)
        self.assertTrue(not new_warehouse.export_route_id.active)
        self.assertTrue(not new_warehouse.buy_import_pull_id.active)
        self.assertTrue(not new_warehouse.foreign_mto_pull_id.active)

    def test_update_warehouse_04(self):
        """
        [Functional Test] - TC06

        - Case: Enable foreign import/export for warehouse
        - Expected Result:
            + related location, picking type, rule, route of warehouse will be activated
        """
        new_warehouse = self.env['stock.warehouse'].create({
            'name': 'Test New Warehouse',
            'reception_steps': 'one_step',
            'delivery_steps': 'ship_only',
            'code': 'NTWH'})

        new_warehouse.write({
            'import_to_resupply': True
        })
        self.assertTrue(new_warehouse.imp_custom_zone_loc_id.active)
        self.assertTrue(new_warehouse.exp_custom_zone_loc_id.active)
        self.assertTrue(new_warehouse.imp_type_id.active)
        self.assertTrue(new_warehouse.exp_type_id.active)
        self.assertTrue(new_warehouse.imp_custom_zone_type_id.active)
        self.assertTrue(new_warehouse.exp_custom_zone_type_id.active)
        self.assertTrue(new_warehouse.import_route_id.active)
        self.assertTrue(new_warehouse.export_route_id.active)
        self.assertTrue(new_warehouse.buy_import_pull_id.active)
        self.assertTrue(new_warehouse.foreign_mto_pull_id.active)

    def test_update_warehouse_05(self):
        """
        [Functional Test] - TC07

        - Case: Update name/code of warehouse
        - Expected Result:
            + name of foreign import rule will be updated
        * Note: In odoo 14, _update_name_and_code() is called after name of warehouse is updated,
        so there is no change for foreign import rule. We are waiting for Odoo fixing
        """
        # old_rule_name = self.checked_warehouse.buy_import_pull_id.name
        # new_name = 'WH1'
        # self.checked_warehouse.name = new_name
        # # self.checked_warehouse.write({'name': new_name})
        # new_rule_name = self.checked_warehouse.buy_import_pull_id.name
        # self.assertTrue(old_rule_name != new_rule_name)
        # self.assertTrue(new_name in new_rule_name)
        pass

    def test_custom_authority_of_picking_type_01(self):
        """
        [Functional Test] - TC10

        - Case: Update default destination of picking type, which marked as foreign trade
        - Expected Result:
            + custom authority of picking type will be updated based on custom authority of new default destination
        """
        test_picking_type = self.env['stock.picking.type'].create({
            'name': 'Test Import - Custom Zone',
            'warehouse_id': self.checked_warehouse.id,
            'code': 'incoming',
            'sequence_code': 'IN',
            'is_foreign_trade': True,
            'use_create_lots': True,
            'use_existing_lots': False,
            'custom_clearance_type': 'import',
            'active': True,
            'company_id': self.checked_warehouse.company_id.id,
        })

        new_location = self.env['stock.location'].create({
            'name': 'Test Import - Custom Zone',
            'active': True,
            'is_custom_clearance': True,
            'usage': 'internal',
            'location_id': self.checked_warehouse.view_location_id.id,
            'company_id': self.checked_warehouse.company_id.id,
            'custom_authority_id': self.partner_custom_authority.id
        })
        test_picking_type.write({
            'default_location_dest_id': new_location.id
        })
        self.assertEqual(test_picking_type.custom_authority_id, self.partner_custom_authority)

    def test_custom_authority_of_picking_type_02(self):
        """
        [Functional Test] - TC11

        - Case: Change custom authority of default destination of picking type, which marked as foreign trade
        - Expected Result:
            + custom authority of picking type will be updated based on custom authority of default destination
        """
        test_picking_type = self.env['stock.picking.type'].create({
            'name': 'Test Import - Custom Zone',
            'warehouse_id': self.checked_warehouse.id,
            'code': 'incoming',
            'sequence_code': 'IN',
            'is_foreign_trade': True,
            'use_create_lots': True,
            'use_existing_lots': False,
            'custom_clearance_type': 'import',
            'active': True,
            'company_id': self.checked_warehouse.company_id.id,
        })

        new_location = self.env['stock.location'].create({
            'name': 'Test Import - Custom Zone',
            'active': True,
            'is_custom_clearance': True,
            'usage': 'internal',
            'location_id': self.checked_warehouse.view_location_id.id,
            'company_id': self.checked_warehouse.company_id.id,
            'custom_authority_id': self.partner_custom_authority.id
        })
        test_picking_type.write({
            'default_location_dest_id': new_location.id
        })

        self.assertEqual(test_picking_type.custom_authority_id, self.partner_custom_authority)

        new_location.write({
            'custom_authority_id': self.partner_custom_authority_2.id
        })
        self.assertEqual(test_picking_type.custom_authority_id, self.partner_custom_authority_2)

    def test_custom_authority_of_picking_type_03(self):
        """
        [Functional Test] - TC12

        - Case: Remove custom authority of default destination of picking type, which marked as foreign trade
        - Expected Result:
            + custom authority of picking type will be removed
        """
        test_picking_type = self.env['stock.picking.type'].create({
            'name': 'Test Import - Custom Zone',
            'warehouse_id': self.checked_warehouse.id,
            'code': 'incoming',
            'sequence_code': 'IN',
            'is_foreign_trade': True,
            'use_create_lots': True,
            'use_existing_lots': False,
            'custom_clearance_type': 'import',
            'active': True,
            'company_id': self.checked_warehouse.company_id.id,
        })

        new_location = self.env['stock.location'].create({
            'name': 'Test Import - Custom Zone',
            'active': True,
            'is_custom_clearance': True,
            'usage': 'internal',
            'location_id': self.checked_warehouse.view_location_id.id,
            'company_id': self.checked_warehouse.company_id.id,
            'custom_authority_id': self.partner_custom_authority.id
        })
        test_picking_type.write({
            'default_location_dest_id': new_location.id
        })

        self.assertEqual(test_picking_type.custom_authority_id, self.partner_custom_authority)

        new_location.write({
            'custom_authority_id': False
        })
        self.assertTrue(not test_picking_type.custom_authority_id)

    def test_available_import_tax_cost_product_on_tax_form_01(self):
        """
         [Form Test] - TC27

        - Case: Check available import tax cost product for tax, which has tax type is purchase or none
        - Expected Result:
            + available import tax cost product is import tax cost product, which we created when installing module
        """
        import_tax_cost_product = self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost')
        with Form(self.env['account.tax']) as f:
            f.name = 'Test Tax Import 1'
            f.amount_type = 'percent'
            f.type_tax_use = 'purchase'
            f.amount = 10.0
            self.assertEqual(f.import_tax_cost_product_id, import_tax_cost_product)

        with Form(self.env['account.tax']) as f:
            f.name = 'Test Tax Import 2'
            f.amount_type = 'percent'
            f.type_tax_use = 'none'
            f.amount = 20.0
            self.assertEqual(f.import_tax_cost_product_id, import_tax_cost_product)

    def test_available_import_tax_cost_product_on_tax_form_02(self):
        """
         [Form Test] - TC28

        - Case: Check available import tax cost product for tax, which has tax type is sale
        - Expected Result:
            + There is not available import tax cost product
        """
        with Form(self.env['account.tax']) as f:
            f.name = 'Test Tax Import'
            f.amount_type = 'percent'
            f.type_tax_use = 'sale'
            f.amount = 10.0
            self.assertEqual(f.import_tax_cost_product_id, self.env['product.product'])

    def test_delete_import_tax_cost_product_01(self):
        """
        [Functional Test] - TC69

        - Case: Delete import tax cost product by open form of product.product
        - Expected Result:
            + Can't delete
        """
        import_tax_cost_product = self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost')
        with self.assertRaises(UserError):
            import_tax_cost_product.unlink()

    def test_delete_import_tax_cost_product_02(self):
        """
        [Functional Test] - TC70

        - Case: Delete import tax cost product by open form of product.template
        - Expected Result:
            + Can't delete
        """
        import_tax_cost_product = self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost')
        with self.assertRaises(UserError):
            import_tax_cost_product.product_tmpl_id.unlink()
