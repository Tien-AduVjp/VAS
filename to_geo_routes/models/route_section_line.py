from odoo import fields, models, api


class RouteSectionLine(models.Model):
    _name = 'route.section.line'
    _description = 'Route Section Line'
    _order = 'route_id, sequence, id'
    _rec_name = 'section_id'

    route_id = fields.Many2one('route.route', string='Route', required=True, ondelete='cascade', index=True, copy=False, readonly=True)
    sequence = fields.Integer(string="Sequence", help="Gives the sequence order when displaying a list of section.", default=10)
    section_id = fields.Many2one('route.section', string='Section', readonly=True, ondelete='restrict')
    address_from_id = fields.Many2one('res.partner', string="From", required=True, readonly=True, index=True)
    address_to_id = fields.Many2one('res.partner', string="To", required=True, readonly=True, index=True)
    distance = fields.Float(string='Distance (km)', help='The distance in kilometers between the From and To',
                            compute='_compute_distance_ave_speed', inverse='_set_distance_ave_speed', store=True)
    distance_in_miles = fields.Float(string='Distance (mi.)', help='The distance in miles between the From and To', related='section_id.distance_in_miles', store=True)
    ave_speed = fields.Float(string='Ave. Speed', help='The average speed in kilometer/hour that you can reach on this section', default=0.0,
                             compute='_compute_distance_ave_speed', inverse='_set_distance_ave_speed', store=True)
    est_trip_time = fields.Float(string='Est. Time',
                                 related='section_id.est_trip_time', store=True,
                                 help='The estimated time in hours spent to go through the section')

    @api.depends('section_id', 'section_id.distance', 'section_id.ave_speed')
    def _compute_distance_ave_speed(self):
        for r in self:
            if r.section_id:
                r.distance = r.section_id.distance
                r.ave_speed = r.section_id.ave_speed
            else:
                r.distance = 0.0
                r.ave_speed = 0.0

    def _set_distance_ave_speed(self):
        # keep distance and ave_speed in synch with the section's ones
        for r in self:
            if r.section_id:
                r.section_id.write({
                    'distance': r.distance,
                    'ave_speed': r.ave_speed,
                    })

    def _attach_section(self):
        """
        This method will look for a route.section record that matches address_from_id and address_to_id with the route.section.line record.
        If one found, it will attach the route.section record to the line. Otherwise, new route.section record will be created to attach.
        """
        Section = self.env['route.section']
        for r in self:
            section_id = Section.search([('address_from_id', '=', r.address_from_id.id), ('address_to_id', '=', r.address_to_id.id)], limit=1)
            # create new section if not found
            if not section_id:
                section_id = Section.create({
                    'address_from_id': r.address_from_id.id,
                    'address_to_id': r.address_to_id.id,
                    'distance': r.distance,
                    'ave_speed': r.ave_speed,
                })
            r.write({
                'section_id': section_id.id,
                })

    @api.model_create_multi
    def create(self, vals_list):
        records = super(RouteSectionLine, self).create(vals_list)
        records.filtered(lambda r: not r.section_id)._attach_section()
        return records
