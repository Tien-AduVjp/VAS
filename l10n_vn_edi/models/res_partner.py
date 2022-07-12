from odoo import models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _einvoice_display_address(self):
        """
        :return return address string for displaying on E-Invoice
        :rtype: str
        """

        def deduplicate(seq):
            """
            Deduplicate item in list while preserving its order

            :param seq: list of items for deduplication
            :return: deduplicated list. For example, ['20 De La Thanh', 'Dong Da', 'Ha Noi', 'Ha Noi', 'Vietnam']
                will become ['20 De La Thanh', 'Dong Da', 'Ha Noi', 'Vietnam']
            :rtype: list
            """
            seen = set()
            seen_add = seen.add

            result = []
            for x in seq:
                if not (x in seen or seen_add(x)):
                    result.append(x)
            return result

        address = []
        commercial_partner = self.commercial_partner_id if self.type != 'invoice' else self
        for field in self._formatting_address_fields():
            if field == 'zip':
                continue
            val = getattr(commercial_partner, field)
            if val:
                if isinstance(val, models.Model):
                    if not hasattr(val, 'name'):
                        raise ValidationError(_("The model %s has no field name for displaying address on E-Invoice") % val._name)
                    val = val.name
                address.append(val)
        address = deduplicate(address)
        return ', '.join(address)
