import logging
import time

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mapping_address = fields.Char(string='Mapping Address', compute='_compute_mapping_address', store=True,
                                   help="The complete address of the partner which will be used for map view")
    partner_latitude = fields.Float(compute='_compute_coordinates', store=True, readonly=False)
    partner_longitude = fields.Float(compute='_compute_coordinates', store=True, readonly=False)

    def _update_latitude_longitude(self, partner_latitude, partner_longitude):
        self.write({
            'partner_latitude': partner_latitude,
            'partner_longitude': partner_longitude,
            'date_localization': fields.Date.context_today(self)
            })

    def _get_geocoder_context(self):
        self.ensure_one()
        ctx = dict(self._context)
        if self.is_company:
            ctx.update(force_partner_company_name=self.name)
        elif self.parent_id and self.parent_id.is_company:
            ctx.update(force_partner_company_name=self.parent_id.name)
        return ctx

    def geo_find(self):
        res = []
        for r in self:
            geocoder_sudo = r.env['base.geocoder'].sudo().with_context(r._get_geocoder_context())
            addr = geocoder_sudo.geo_query_address(
                r.street or None,
                r.zip or None,
                r.city or None,
                r.state_id.name or None,
                r.country_id.name or None
                )
            if r.country_id:
                coord = geocoder_sudo.geo_find(addr)
            else:
                coord = geocoder_sudo.geo_find(addr, force_country=self.env.company.country_id.name)
            if coord:
                res.append({
                    'lat': coord[0],
                    'lon': coord[1]
                    })
        return res

    @api.depends('street', 'zip', 'city', 'state_id', 'country_id')
    def _compute_coordinates(self):
        for r in self:
            r.partner_latitude = False
            r.partner_longitude = False

    @api.depends('street', 'street2', 'zip', 'city', 'country_id')
    def _compute_mapping_address(self):
        for record in self:
            record.mapping_address = ''
            if record.street:
                record.mapping_address += record.street + ','
            if record.street2:
                record.mapping_address += record.street2 + ','
            if record.zip:
                record.mapping_address += record.zip + ' '
            if record.city:
                record.mapping_address += record.city + ','
            if record.country_id:
                record.mapping_address += record.country_id.name

    @api.model
    def _fill_coordinates(self):
        partners = self.env['res.partner'].search([
            ('mapping_address', '!=', False),
            ('mapping_address', '!=', ''),
            '|', ('partner_latitude', '=', 0), ('partner_longitude', '=', 0)
            ])
        geo_obj = self.env['base.geocoder']
        provider = geo_obj._get_provider().tech_name
        delay_time = 1.5
        if provider in ['google', 'mapbox']:
            delay_time = 0.1
        try:
            for partner in partners:
                partner.geo_localize()
                time.sleep(delay_time)
        except Exception as e:
            _logger.error(e)

    @api.model
    def _geo_localize(self, street='', zip='', city='', state='', country=''):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_obj.geo_find(search, force_country=country)
        time.sleep(5)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result
