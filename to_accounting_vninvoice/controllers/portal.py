import base64

from odoo import _
from odoo.http import request, content_disposition
from odoo.addons.account.controllers import portal
from odoo.exceptions import MissingError


class PortalAccount(portal.PortalAccount):

    def _show_report(self, model, report_type, report_ref, download=False):
        """
        Override to add support for downloading VN-Invoice in zipped XML
        """
        if model._name == 'account.move' and model.einvoice_state != 'not_issued' and report_type == 'xml' and model.vninvoice_transactionid:
            if not model.check_vninvoice_approved_and_signed:
                return _("E-invoice is not signed, so you cannot download the XML file")
            try:
                model._ensure_vninvoice_representation_files(retries=3)
            except MissingError as e:
                return str(e)

            filecontent = base64.b64decode(model.vninvoice_representation_xml)
            reporthttpheaders = [
                ('Content-Type', 'application/json'),
            ]
            if download:
                reporthttpheaders.append(('Content-Disposition', content_disposition(model.vninvoice_representation_filename_xml)))
            return request.make_response(filecontent, headers=reporthttpheaders)
        else:
            return super(PortalAccount, self)._show_report(model, report_type, report_ref, download)

