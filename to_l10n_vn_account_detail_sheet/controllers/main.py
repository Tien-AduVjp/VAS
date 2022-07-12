from odoo import http, _
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError

class GeneralLedgerController(http.Controller):

    @http.route('/account-detail-sheet/download/xlsx/<int:wizard_id>', type='http', auth='user')
    def c200_s03adn_export_xlsx(self, wizard_id, **kwargs):
        wizard_c200_s38dn = request.env['wizard.l10n_vn.c200_s38dn'].search([('id', '=', wizard_id)])
        if not wizard_c200_s38dn:
            raise AccessError(_('Record not found: id: %s, uid: %s') % (wizard_id, request.env.user.id))
        file_data = wizard_c200_s38dn.report_excel()
        file_name = _('Account Detail Sheet.xlsx')
        content_length = len(file_data.getvalue())
        http_headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),  # xlsx mimetype
            ('Content-Length', content_length),
            ('Content-Disposition', content_disposition(file_name))
             ]
        return request.make_response(file_data, headers=http_headers) 