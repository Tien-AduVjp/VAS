from odoo import models
from odoo.exceptions import AccessError


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def binary_content(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='name', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None):
        """
            Override to avoid access `zipped_source_code` directly via `web/content/<string:model>/<int:id>/<string:field>`.
        """
        if model == 'odoo.module.version' and field == 'zipped_source_code' and not self.env.user.has_group('to_odoo_module.odoo_module_user'):
            raise AccessError

        return super(Http, self).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            default_mimetype=default_mimetype, access_token=access_token)
