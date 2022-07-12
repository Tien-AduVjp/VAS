from odoo import fields, models

class product_template(models.Model):
    _inherit = 'product.template'
          
    export_tax_ids = fields.Many2many('account.tax', 'product_export_taxes_rel', 'prod_id', 'tax_id',
                                      string="Exporting Taxes",
                                      domain=[('type_tax_use','in',['sale', 'none'])]
                                      )
    
    import_tax_ids = fields.Many2many('account.tax', 'product_import_taxes_rel', 'prod_id', 'tax_id',
                                      string="Importing Taxes",
                                      domain=[('type_tax_use','in',['purchase', 'none'])]
                                      )

    