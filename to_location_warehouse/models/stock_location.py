from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    warehouse_ids = fields.One2many('stock.warehouse', 'view_location_id', string='Warehouses', readonly=True)

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', compute='_compute_warehouse', store=True,
                                   help="The warehouse to which this location belongs")

    @api.constrains('warehouse_ids')
    def _check_number_of_wh(self):
        for r in self:
            if len(r.warehouse_ids) > 1:
                raise ValidationError(_("You cannot point a location to more than one warehouse."
                                        " In other words, Multiple warehouses cannot use the same location."))

    @api.depends('location_id', 'location_id.warehouse_ids', 'warehouse_ids', 'warehouse_ids.view_location_id')
    def _compute_warehouse(self):
        for r in self:
            r.warehouse_id = r.location_id.get_warehouse()
            
    @api.model
    def get_sublocations(self):
        """ return all sub-locations of the given stock location (included) """
        return self.search([('id', 'child_of', self.id)])
    
    def _get_recursive_children(self):
        """
        Method to find all recursive child locations of self
        then return them all (include self) in a stock.location record set

        @return: recordset of the locations in self and their recursive children
        """
        children = self.child_ids
        if children.child_ids:
            children |= children._get_recursive_children()
        return self | children

