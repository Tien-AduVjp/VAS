from odoo.tests.common import TransactionCase

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()

        #Create product voucher
        self.product_voucher = self.env.ref('point_of_sale.desk_organizer')
        self.product_voucher.write({
            'tracking':'serial',
            'is_promotion_voucher': True,
            'voucher_type_id': self.env.ref('to_promotion_voucher.voucher_type_generic').id,
        })

        #Create picking type
        self.picking_type = self.env['stock.picking.type'].search([('code', '=', 'voucher_issue_order'), ('company_id', '=', self.env.company.id)], limit=1)
        self.picking_type.write({
            'default_location_dest_id': self.env.ref('stock.stock_location_stock').id
        })

        #Issue voucher
        self.voucher = self.env['voucher.issue.order'].create({
            'product_id': self.product_voucher.id,
            'voucher_qty': 10,
            'product_uom_id': self.product_voucher.uom_id.id,
            'picking_type_id': self.picking_type.id,
            'valid_duration': 30,
            'company_id': self.env.company.id
        })
        self.voucher.action_confirm()
        self.voucher.action_issue()

        #Create user
        self.group_pos_user = self.env.ref('base.user_admin')
        self.group_pos_user.write({
            'groups_id': [(6, 0, [self.env.ref('point_of_sale.group_pos_user').id, self.env.ref('stock.group_stock_user').id])]
        })
