from odoo import http, _
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError


class GeneralLedgerController(http.Controller):
    
    def _download_excel(self, file_data, file_name):
        """Method use download Excel
        :return: file excel"""
        content_length = len(file_data.getvalue())
        http_headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),  # xlsx mimetype
            ('Content-Length', content_length),
            ('Content-Disposition', content_disposition(file_name))
             ]
        return request.make_response(file_data, headers=http_headers)
        
    @http.route('/invoice-declaration-sales/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def c119_01gtgt_export_xlsx(self, wizard_id, **kwargs):
        wizard_c119_01gtgt = request.env['wizard.l10n_vn_c119.01gtgt'].browse(wizard_id)
        if not wizard_c119_01gtgt.exists():
            raise AccessError(_('Record not found: id: %s, uid: %s') % (wizard_id, request.env.user.id))
        file_data = wizard_c119_01gtgt.export_excel_sale()
        file_name = _('Invoice Declaration Sales.xlsx')
        return self._download_excel(file_data, file_name)

    @http.route('/invoice-declaration-purchase/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def c119_02gtgt_export_xlsx(self, wizard_id, **kwargs):
        wizard_c119_02gtgt = request.env['wizard.l10n_vn_c119.02gtgt'].browse(wizard_id)
        if not wizard_c119_02gtgt.exists():
            raise AccessError(_('Record not found: id: %s, uid: %s') % (wizard_id, request.env.user.id))
        file_data = wizard_c119_02gtgt.export_excel_purchase()
        file_name = _('Invoice Declaration Puchases.xlsx')
        return self._download_excel(file_data, file_name)
