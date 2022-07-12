import base64

from io import BytesIO
from configparser import ConfigParser

from odoo import models, fields, api


class OdooVersionConfig(models.Model):
    _name = 'odoo.version.config'
    _inherit = 'abstract.config.directive'
    _description = 'Odoo Version Config. Directive'

    odoo_version_id = fields.Many2one('odoo.version', string='Odoo Version', required=True, ondelete='restrict', tracking=True)

    _sql_constraints = [
        ('name_odoo_version_id_unique',
         'UNIQUE(name,odoo_version_id)',
         "The Key must be unique per Odoo version"),
    ]

    def to_text(self):
        f = BytesIO()
        config = ConfigParser()
        section_ids = self.mapped('section_id')
        for section_id in section_ids:
            config_ids = section_id.odoo_version_config_ids.filtered(lambda c: c.section_id == section_id)
            directives_dict = dict([(directive.name, directive.value) for directive in config_ids])
            config[section_id.name] = directives_dict

        with open(f, 'w') as configfile:
            config.write(configfile)

        # Change the stream position to the start of the stream
        # see https://docs.python.org/3/library/io.html#io.IOBase.seek
        f.seek(0)
        # read bytes to the EOF
        f_read = f.read()
        # encode bytes for output to return
        out = base64.encodebytes(f_read)
        return out
