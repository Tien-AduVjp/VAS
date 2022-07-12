from odoo import models, api


class AbstractFleetVehicleLog(models.AbstractModel):
    _name = 'abstract.fleet.vehicle.log'
    _description = 'Fleet Vehicle Log Abstract'

    """
    models that inherit this abstract model must inherit fleet.vehicle.cost in the form of delegation inheritance (using inherits)
    """

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AbstractFleetVehicleLog, self).create(vals_list)
        for record in records:
            record.cost_id.write({
                'vendor_id': record.vendor_id.id,
                })
        return records

    def write(self, vals):
        if 'vendor_id' in vals.keys():
            self.mapped('cost_id').write({
                'vendor_id': vals['vendor_id'],
                })
        return super(AbstractFleetVehicleLog, self).write(vals)

    # TODO: remove me in master/14+
    #---------------------------------------#
    def action_confirm(self):
        self.mapped('cost_id').action_confirm()

    def action_cancel(self):
        self.mapped('cost_id').action_cancel()

    def action_draft(self):
        self.mapped('cost_id').action_draft()
    #---------------------------------------#

