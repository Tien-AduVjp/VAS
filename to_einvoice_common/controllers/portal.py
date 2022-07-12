from odoo import http
from odoo.http import request
from odoo.addons.account.controllers import portal
from odoo.exceptions import AccessError, MissingError


class PortalAccount(portal.PortalAccount):

    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        """
        Override to add support for downloading E-Invoice in zipped XML
        """
        try:
            invoice_sudo = self._document_check_access('account.move', invoice_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if report_type == 'xml':
            return self._show_report(model=invoice_sudo, report_type=report_type, report_ref='account.account_invoices', download=download)
        else:
            return super(PortalAccount, self).portal_my_invoice_detail(invoice_id, access_token, report_type, download, **kw)