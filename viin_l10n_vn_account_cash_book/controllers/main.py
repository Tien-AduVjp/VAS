from odoo import http, _
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError


class GeneralLedgerController(http.Controller):

    def download_excel (self, wizard_id, res_model, file_name):
        """Method use download excel
        :return: file excel"""
        res_wizard = request.env[res_model].browse(wizard_id)
        if not res_wizard.exists():
            raise AccessError(_('Record not found: id: %s, uid: %s') % (wizard_id, request.env.user.id))
        file_data = res_wizard.report_excel()
        content_length = len(file_data.getvalue())
        http_headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),  # xlsx mimetype
            ('Content-Length', content_length),
            ('Content-Disposition', content_disposition(file_name))
             ]
        return request.make_response(file_data, headers=http_headers) 

    @http.route('/account-cash-book/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def c200_s07dn_export_xlsx(self, wizard_id, **kwargs): 
        file_name = _('Account Cash Book.xlsx')
        res_model = 'wizard.l10n_vn.c200.s07dn'
        return self.download_excel (wizard_id, res_model, file_name)
    
    @http.route('/account-bank-book/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def c200_s08dn_export_xlsx(self, wizard_id, **kwargs):
        file_name = _('Account Bank Book.xlsx')
        res_model = 'wizard.l10n_vn.c200.s08dn'
        return self.download_excel (wizard_id, res_model, file_name)
    

        
