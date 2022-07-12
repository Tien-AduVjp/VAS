# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductMilestone(models.Model):
    _name = 'product.milestone'
    _description = 'Product Milestone'

    name = fields.Char('Name', required=True)
    amount = fields.Integer('Milestone', required=True)
    uom_id = fields.Many2one('uom.uom', string='Milestone UoM', required=True, help="The unit of measure in which the Milestone is")
    operation_time = fields.Boolean('Working Hour Milestone', default=False,
                                    help="The milestone by working hours of the product (1000 hours, 2000 hours) that will help Odoo"
                                    " to define the milestones of the product by its working hours. That will be useful for other"
                                    " calculation that will be based on the working hours milestones. For example, clean after 2000"
                                    " hours, replace after 100,000 hours, etc.")
    
    _sql_constraints = [
        ('product_milestone_unique',
         'unique(amount, uom_id)',
         _("Product Milestone must be unique!")),
    ]

    def name_get(self):
        return [(p.id, "%s [%s %s]" % (p.name, p.amount, p.uom_id.name)) for p in self]
    
