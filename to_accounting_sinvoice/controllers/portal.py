import base64
from odoo.http import request, content_disposition
from odoo.addons.account.controllers import portal
from odoo.exceptions import MissingError


class PortalAccount(portal.PortalAccount):

    def _show_report(self, model, report_type, report_ref, download=False):
        """
        Override to add support for downloading S-Invoice in zipped XML
        """
        if model._name == 'account.move' and model.einvoice_state != 'not_issued' and report_type == 'xml' and model.sinvoice_transactionid:
            try:
                model._ensure_sinvoice_representation_files(retries=3)
            except MissingError as e:
                return str(e)

            filecontent = base64.b64decode(model.sinvoice_representation_zip)
            reporthttpheaders = [
                ('Content-Type', 'application/zip'),
                ('Content-Length', len(filecontent)),
            ]
            if download:
                reporthttpheaders.append(('Content-Disposition', content_disposition(model.sinvoice_representation_filename_zip)))
            return request.make_response(filecontent, headers=reporthttpheaders)
        else:
            return super(PortalAccount, self)._show_report(model, report_type, report_ref, download)

