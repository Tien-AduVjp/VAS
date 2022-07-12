from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    inter_comp_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
                                              help="Default value to set on Purchase(Sales) Orders that will be created based on"
                                              " Sale(Purchase) Orders made to this company")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResCompany, self).create(vals_list)
        res_to_set = res.filtered(lambda r: not r.inter_comp_warehouse_id)
        warehouses = self.env['stock.warehouse'].search([('company_id','in', res_to_set.ids)])
        for r in res_to_set:
            warehouse = warehouses.filtered(lambda w: w.company_id == r)
            if warehouse:
                r.inter_comp_warehouse_id = warehouse[0]
        return res
