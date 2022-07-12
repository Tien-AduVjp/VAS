from psycopg2 import sql

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone_no_format = fields.Char(string='Phone No Format', compute='_compute_phone_mobile_no_format', search='_search_phone_no_format',
                                  help="Technical field to support searching by phone criteria without being affected by phone format.")
    mobile_no_format = fields.Char(string='Mobile No Format', compute='_compute_phone_mobile_no_format', search='_search_mobile_no_format',
                                  help="Technical field to support searching by mobile phone criteria without being affected by mobile phone format.")

    def _compute_phone_mobile_no_format(self):
        if not self.ids:
            return
        self.env.cr.execute("""
        SELECT id,
            regexp_replace(coalesce(phone, ''), '[^0-9]+','','g') AS phone_no_format,
            regexp_replace(coalesce(mobile, ''), '[^0-9]+','','g') AS mobile_no_format
        FROM res_partner
        WHERE id in %s
        """, (tuple(self.ids),)
        )
        partner_data = self.env.cr.dictfetchall()
        mapped_data = dict([
            (
                row['id'],
                {
                    'phone_no_format': row['phone_no_format'],
                    'mobile_no_format': row['mobile_no_format']
                    }
                ) for row in partner_data])
        for r in self:
            r.phone_no_format = mapped_data.get(r.id, {}).get('phone_no_format', False)
            r.mobile_no_format = mapped_data.get(r.id, {}).get('mobile_no_format', False)

    def _search_phone_no_format(self, operator, operand):
        return [('id', 'in', self._query_res_partner_by_phone_mobile_no_format(self._process_phone_mobile_number_search(operand), 'phone'))]

    def _search_mobile_no_format(self, operator, operand):
        return [('id', 'in', self._query_res_partner_by_phone_mobile_no_format(self._process_phone_mobile_number_search(operand), 'mobile'))]

    def _remove_characters_in_phone_number(self, phone_number):
        phone_number = phone_number.replace(' ', '')
        phone_number = phone_number.replace('-', '')
        phone_number = phone_number.replace('(', '')
        phone_number = phone_number.replace(')', '')
        phone_number = phone_number.replace('+', '')
        phone_number = phone_number.replace('.', '')
        return phone_number

    def _process_phone_mobile_number_search(self, condition_value):
        if condition_value[:1] == '0':
            condition_value = condition_value[1:]
        return self._remove_characters_in_phone_number(condition_value)

    @api.model
    def _query_res_partner_by_phone_mobile_no_format(self, operand, phone_field):
        query = sql.SQL("""
            SELECT id
            FROM res_partner
            WHERE regexp_replace(coalesce({field},''),'[^0-9]+','','g') like %s
            """).format(
                field=sql.Identifier(phone_field),
                )
        self.env.cr.execute(query, ('%' + operand + '%',))
        return [x[0] for x in set(self.env.cr.fetchall())]
