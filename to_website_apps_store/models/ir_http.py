from odoo import models
from odoo.exceptions import AccessError


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def binary_content(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='name', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None):
        """
            Override to allow access image and icon of unpublished odoo.module.version records
        """
        if id and model == 'odoo.module.version' and model in self.env and field in ['icon', 'image_1920']:
            obj = self.env[model].browse(int(id)).sudo()
            if not obj.is_published:
                self = self.sudo()

        return super(Http, self).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            default_mimetype=default_mimetype, access_token=access_token)
