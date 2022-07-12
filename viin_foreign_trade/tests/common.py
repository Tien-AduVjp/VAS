from odoo import fields
from odoo.tests import SavepointCase

class TestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        # ============================================ Set up environment ============================================
        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.env.user.lang = 'en_US'

        Users = cls.env['res.users']

        cls.checked_warehouse = cls.env.ref('stock.warehouse0')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')

        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.uom_dozen = cls.env.ref('uom.product_uom_dozen')

        cls.tax_paid_account = cls.env.ref('l10n_generic_coa.1_tax_paid')
        cls.tax_paid_account.reconcile = True

        # ============================================ Active currency ================================================
        # Active currency
        cls.currency_eur = cls.env.ref('base.EUR')
        cls.currency_usd = cls.env.ref('base.USD')
        cls.currency_eur.active = True
        cls.currency_usd.active = True

        cls.env['res.currency.rate'].create({
            'name': '2021-01-01',
            'rate': 1.000000,
            'currency_id': cls.currency_eur.id,
            'company_id': cls.env.company.id,
        })
        cls.env['res.currency.rate'].create({
            'name': '2021-01-01',
            'rate': 1.52000,
            'currency_id': cls.currency_usd.id,
            'company_id': cls.env.company.id,
        })
        cls.env['res.currency.rate'].create({
            'name': '2021-10-20',
            'rate': 1.54000,
            'currency_id': cls.currency_usd.id,
            'company_id': cls.env.company.id,
        })
        cls.env['res.currency.rate'].create({
            'name': '2021-10-22',
            'rate': 1.50000,
            'currency_id': cls.currency_usd.id,
            'company_id': cls.env.company.id,
        })

        cls.pricelist_eur = cls.env['product.pricelist'].create({
            'name': 'EUR pricelist',
            'active': True,
            'currency_id': cls.currency_eur.id,
            'company_id': cls.env.company.id,
        })

        # ============================================ Create user ===================================================
        # Create a users
        cls.normal_user = Users.create({
            'name': 'Normal User',
            'login': 'normal_user',
            'email': 'normal_user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
            'company_ids': [(6, 0, [cls.env.ref('base.main_company').id])],
            'company_id': cls.env.ref('base.main_company').id
        })
        cls.foreign_trade_user = Users.create({
            'name': 'Test Foreign Trade User',
            'login': 'user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('viin_foreign_trade.group_foreign_trade_user').id])],
            'company_ids': [(6, 0, [cls.env.ref('base.main_company').id])],
            'company_id': cls.env.ref('base.main_company').id
        })
        cls.foreign_trade_manager = Users.create({
            'name': 'Test Foreign Trade Manager',
            'login': 'manager',
            'email': 'manager@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('viin_foreign_trade.group_foreign_trade_manager').id])],
            'company_ids': [(6, 0, [cls.env.ref('base.main_company').id])],
            'company_id': cls.env.ref('base.main_company').id
        })
        cls.stock_user = Users.create({
            'name': 'Test Stock User',
            'login': 'stock_user',
            'email': 'stock_user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('stock.group_stock_user').id])],
            'company_ids': [(6, 0, [cls.env.ref('base.main_company').id])],
            'company_id': cls.env.ref('base.main_company').id
        })
        cls.foreign_trade_user_2 = Users.create({
            'name': 'Test Foreign Trade User 2',
            'login': 'user2',
            'email': 'user2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('viin_foreign_trade.group_foreign_trade_user').id])],
            'company_ids': [(6, 0, [cls.env.ref('stock.res_company_1').id])],
            'company_id': cls.env.ref('stock.res_company_1').id
        })

        # ============================================ Create partner ================================================
        # Create foreign trade partner
        cls.foreign_trade_partner = cls.env['res.partner'].create({
            'name': 'Test Foreign Partner 1',
            'email': 'vn1.partner@example.viindoo.com',
            'country_id': cls.env.ref('base.vn').id,
            'property_foreign_trade_partner': True,
            'property_stock_customer': cls.env.ref('viin_foreign_trade.to_stock_location_customers_export')
        })

        # Same country but still set property_foreign_trade_partner
        cls.foreign_trade_partner_same_country = cls.env['res.partner'].create({
            'name': 'Test Foreign Partner 2',
            'email': 'us1.partner@example.viindoo.com',
            'country_id': cls.env.ref('base.us').id,
            'property_foreign_trade_partner': True,
            'property_stock_customer': cls.env.ref('viin_foreign_trade.to_stock_location_customers_export')
        })

        # Don't set property_foreign_trade_partner but has country differ from system company
        cls.foreign_trade_partner_abnormal = cls.env['res.partner'].create({
            'name': 'Test Foreign Partner 3',
            'email': 'us2.partner@example.viindoo.com',
            'country_id': cls.env.ref('base.vn').id,
        })

        # Same country partner
        cls.partner_same_country = cls.env['res.partner'].create({
            'name': 'Test Same Country Partner 1',
            'email': 'us3.partner@example.viindoo.com',
            'country_id': cls.env.ref('base.us').id
        })

        # Custom authority partner
        cls.partner_custom_authority = cls.env['res.partner'].create({
            'name': 'Test Custom Authority Partner 1',
            'email': 'us4.partner@example.viindoo.com',
            'country_id': cls.env.ref('base.us').id
        })
        cls.partner_custom_authority_2 = cls.env['res.partner'].create({
            'name': 'Test Custom Authority Partner 2',
            'email': 'us5.partner@example.viindoo.com',
            'country_id': cls.env.ref('base.us').id
        })

        cls.checked_warehouse.imp_custom_zone_loc_id.custom_authority_id = cls.partner_custom_authority
        cls.checked_warehouse.exp_custom_zone_loc_id.custom_authority_id = cls.partner_custom_authority

        # ============================================ Create taxes ==================================================
        cls.sale_tax = cls.env.ref('l10n_generic_coa.1_sale_tax_template')
        cls.purchase_tax = cls.env.ref('l10n_generic_coa.1_purchase_tax_template')

        cls.tax_group_import_1 = cls.env['account.tax.group'].create({
            'name': 'Test Tax Group Import 1',
            'is_vat': True
        })

        cls.tax_group_import_2 = cls.env['account.tax.group'].create({
            'name': 'Test Tax Group Import 2',
            'is_vat': True
        })
        cls.tax_group_export_1 = cls.env['account.tax.group'].create({
            'name': 'Test Tax Group Export 1',
            'is_vat': True
        })

        cls.tax_group_export_2 = cls.env['account.tax.group'].create({
            'name': 'Test Tax Group Export 2',
            'is_vat': True
        })

        cls.tax_group3 = cls.env['account.tax.group'].create({
            'name': 'Test Tax Group 3',
            'is_vat': False
        })

        cls.tax_import_1 = cls.env['account.tax'].create({
            'name': 'Test Tax Import 1',
            'amount_type': 'percent',
            'amount': 10.0,
            'type_tax_use': 'purchase',
            'import_tax_cost_product_id': cls.env.ref('viin_foreign_trade.to_product_product_import_tax_cost').id,
            'price_include': False,
            'include_base_amount': True,
            'tax_group_id': cls.tax_group_import_1.id,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                    'vat_ctp_account_id': cls.tax_paid_account.id
                })
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                    'vat_ctp_account_id': cls.tax_paid_account.id
                })
            ],
        })
        cls.tax_import_2 = cls.env['account.tax'].create({
            'name': 'Test Tax Import 2',
            'amount_type': 'percent',
            'amount': 5.0,
            'type_tax_use': 'purchase',
            'import_tax_cost_product_id': cls.env.ref('viin_foreign_trade.to_product_product_import_tax_cost').id,
            'price_include': False,
            'include_base_amount': True,
            'tax_group_id': cls.tax_group_import_2.id,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                    'vat_ctp_account_id': cls.tax_paid_account.id
                })
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                    'vat_ctp_account_id': cls.tax_paid_account.id
                })
            ],
        })
        cls.tax_export_1 = cls.env['account.tax'].create({
            'name': 'Test Tax Export 1',
            'amount_type': 'percent',
            'amount': 10.0,
            'type_tax_use': 'sale',
            'price_include': False,
            'include_base_amount': True,
            'tax_group_id': cls.tax_group_export_1.id,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                    'vat_ctp_account_id': cls.tax_paid_account.id
                })
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                    'vat_ctp_account_id': cls.tax_paid_account.id
                })
            ],
        })
        cls.tax_export_2 = cls.env['account.tax'].create({
            'name': 'Test Tax Export 2',
            'amount_type': 'percent',
            'amount': 5.0,
            'type_tax_use': 'sale',
            'price_include': False,
            'include_base_amount': True,
            'tax_group_id': cls.tax_group_export_2.id,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                    'vat_ctp_account_id': cls.tax_paid_account.id
                })
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base',
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                    'vat_ctp_account_id': cls.tax_paid_account.id
                })
            ],
        })

        # tax without account and VAT account
        cls.tax_import_3 = cls.env['account.tax'].create({
            'name': 'Test Tax Import 3',
            'amount_type': 'percent',
            'amount': 10.0,
            'type_tax_use': 'purchase',
            'import_tax_cost_product_id': cls.env.ref('viin_foreign_trade.to_product_product_import_tax_cost').id,
            'price_include': False,
            'include_base_amount': True,
            'tax_group_id': cls.tax_group_import_1.id,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base'
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax'
                })
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base'
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax'
                })
            ],
        })

        # tax without VAT account
        cls.tax_import_4 = cls.env['account.tax'].create({
            'name': 'Test Tax Import 4',
            'amount_type': 'percent',
            'amount': 10.0,
            'type_tax_use': 'purchase',
            'import_tax_cost_product_id': cls.env.ref('viin_foreign_trade.to_product_product_import_tax_cost').id,
            'price_include': False,
            'include_base_amount': True,
            'tax_group_id': cls.tax_group_import_1.id,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base'
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                })
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'base'
                }),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': cls.tax_paid_account.id,
                })
            ],
        })

        # ============================================ Setup product category=========================================
        cls.product_category_saleable = cls.env.ref('product.product_category_1')
        cls.product_category_saleable.property_cost_method = 'fifo'
        cls.product_category_saleable.property_valuation = 'real_time'

        cls.product_category_internal = cls.env.ref('product.product_category_2')
        cls.product_category_internal.property_cost_method = 'fifo'

        cls.product_category_expense = cls.env.ref('product.cat_expense')
        cls.product_category_expense.property_valuation = 'real_time'

        # ============================================ Create products ===============================================
        cls.import_product_1 = cls.env['product.product'].create({
            'name': 'Import Product 1',
            'type': 'product',
            'categ_id': cls.product_category_saleable.id,
            'import_tax_ids': [(6, 0, [cls.tax_import_1.id, cls.tax_import_2.id])]
        })
        cls.import_product_2 = cls.env['product.product'].create({
            'name': 'Import Product 2',
            'type': 'product',
            'categ_id': cls.product_category_saleable.id,
            'import_tax_ids': [(6, 0, [cls.tax_import_1.id, cls.tax_import_2.id])]
        })
        cls.export_product_1 = cls.env['product.product'].create({
            'name': 'Export Product 1',
            'type': 'product',
            'categ_id': cls.product_category_saleable.id,
            'export_tax_ids': [(6, 0, [cls.tax_export_1.id, cls.tax_export_2.id])]
        })
        cls.export_product_2 = cls.env['product.product'].create({
            'name': 'Export Product 2',
            'type': 'product',
            'categ_id': cls.product_category_saleable.id,
            'export_tax_ids': [(6, 0, [cls.tax_export_1.id, cls.tax_export_2.id])]
        })
        cls.import_product_not_real_time = cls.env['product.product'].create({
            'name': 'Import Product Not Real Time',
            'type': 'product',
            'categ_id': cls.product_category_internal.id,
            'import_tax_ids': [(6, 0, [cls.tax_import_1.id, cls.tax_import_2.id])]
        })
        cls.import_product_not_fifo = cls.env['product.product'].create({
            'name': 'Import Product Not FIFO',
            'type': 'product',
            'categ_id': cls.product_category_expense.id,
            'import_tax_ids': [(6, 0, [cls.tax_import_1.id, cls.tax_import_2.id])]
        })
        cls.import_product_abnormal_1 = cls.env['product.product'].create({
            'name': 'Import Product Abnormal 1',
            'type': 'product',
            'categ_id': cls.product_category_saleable.id,
            'import_tax_ids': [(6, 0, [cls.tax_import_3.id])]
        })
        cls.import_product_abnormal_2 = cls.env['product.product'].create({
            'name': 'Import Product Abnormal 2',
            'type': 'product',
            'categ_id': cls.product_category_saleable.id,
            'import_tax_ids': [(6, 0, [cls.tax_import_4.id])]
        })
        cls.expense_product_1 = cls.env['product.product'].create({
            'name': 'Expense Product 1',
            'type': 'service',
            'categ_id': cls.product_category_expense.id,
        })
        cls.expense_product_2 = cls.env['product.product'].create({
            'name': 'Expense Product 2',
            'type': 'service',
            'categ_id': cls.product_category_expense.id,
        })
        cls.expense_product_3 = cls.env['product.product'].create({
            'name': 'Expense Product 3',
            'type': 'service',
            'categ_id': cls.product_category_expense.id,
        })

        # ============================================ Create PO =====================================================
        cls.po1 = cls.env['purchase.order'].create({
            'partner_id': cls.foreign_trade_partner.id,
            'currency_id': cls.currency_eur.id,
            'picking_type_id': cls.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': cls.import_product_1.name,
                    'product_id': cls.import_product_1.id,
                    'product_uom': cls.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [cls.purchase_tax.id])]
                }),
                (0, 0, {
                    'name': cls.import_product_2.name,
                    'product_id': cls.import_product_2.id,
                    'product_uom': cls.uom_dozen.id,
                    'product_qty': 3.0,
                    'price_unit': 3600.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [cls.purchase_tax.id])]
                })
            ],
        })
        cls.po1.button_confirm()
        cls.po1_picking1 = cls.po1.picking_ids[0]
        cls.po1_stock_move1 = cls.po1_picking1.move_lines.filtered(lambda ml: ml.product_id == cls.import_product_1)[0]
        cls.po1_stock_move2 = cls.po1_picking1.move_lines.filtered(lambda ml: ml.product_id == cls.import_product_2)[0]

        cls.po1_picking1.button_validate()
        cls.po1_picking1.action_confirm()
        cls.po1_picking1.action_assign()

        cls.po1_stock_move1.move_line_ids.write({'qty_done': 2.0})
        # set qty_done is less than expected to create backorders
        cls.po1_stock_move2.move_line_ids.write({'qty_done': 12.0})

        # if there is no context cancel_backorder, backorder will be created automatically
        cls.po1_picking1._action_done()

        # process backorder
        backorders = cls.env['stock.picking'].search([('backorder_id', '=', cls.po1_picking1.id)])
        cls.po1_picking2 = backorders[0]
        cls.po1_stock_move3 = cls.po1_picking2.move_lines.filtered(lambda ml: ml.product_id == cls.import_product_2)[0]
        cls.po1_picking2.button_validate()
        cls.po1_picking2.action_confirm()
        cls.po1_picking2.action_assign()
        cls.po1_stock_move3.move_line_ids.write({'qty_done': 24.0})
        cls.po1_picking2._action_done()

        # ============================================ Create SO =====================================================
        cls.env['stock.quant']._update_available_quantity(cls.export_product_1, cls.stock_location, 2)
        cls.env['stock.quant']._update_available_quantity(cls.export_product_2, cls.stock_location, 24)

        # create SO1
        cls.so1 = cls.env['sale.order'].create({
            'partner_id': cls.foreign_trade_partner.id,
            'partner_invoice_id': cls.foreign_trade_partner.id,
            'partner_shipping_id': cls.foreign_trade_partner.id,
            'pricelist_id': cls.pricelist_eur.id,
            'order_line': [
                (0, 0, {
                    'name': cls.export_product_1.name,
                    'product_id': cls.export_product_1.id,
                    'product_uom': cls.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                    'tax_id': [(6, 0, [cls.sale_tax.id])]
                }),
                (0, 0, {
                    'name': cls.export_product_2.name,
                    'product_id': cls.export_product_2.id,
                    'product_uom': cls.uom_dozen.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 2400.0,
                    'tax_id': [(6, 0, [cls.sale_tax.id])]
                })
            ],
        })
        cls.so1.action_confirm()
        cls.so1_picking1 = cls.so1.picking_ids.filtered(lambda pk: pk.location_dest_id == cls.checked_warehouse.exp_custom_zone_loc_id)
        cls.so1_stock_move1 = cls.so1_picking1.move_lines.filtered(lambda ml: ml.product_id == cls.export_product_1)[0]
        cls.so1_stock_move2 = cls.so1_picking1.move_lines.filtered(lambda ml: ml.product_id == cls.export_product_2)[0]

        cls.so1_picking1.button_validate()
        cls.so1_picking1.action_confirm()
        cls.so1_picking1.action_assign()

        cls.so1_stock_move1.move_line_ids.write({'qty_done': 2.0})
        # set qty_done is less than expected to create backorders
        cls.so1_stock_move2.move_line_ids.write({'qty_done': 12.0})

        # if there is no context cancel_backorder, backorder will be created automatically
        cls.so1_picking1._action_done()

        # process backorder
        backorders = cls.env['stock.picking'].search([('backorder_id', '=', cls.so1_picking1.id)])
        cls.so1_picking2 = backorders[0]
        cls.so1_stock_move3 = cls.so1_picking2.move_lines.filtered(lambda ml: ml.product_id == cls.export_product_2)[0]

        cls.so1_picking2.action_confirm()
        cls.so1_picking2.action_assign()
        cls.so1_picking2.button_validate()
        cls.so1_stock_move3.move_line_ids.write({'qty_done': 12.0})
        cls.so1_picking2._action_done()
