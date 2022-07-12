import json

from odoo import http
from odoo.http import content_disposition, request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape


class StockAgeReportController(http.Controller):

    def _get_headers_by_output_format(self, output_format, report_obj, report_name, options):
        data = None
        headers = []
        
        if output_format == 'xlsx':
            headers = [
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition(report_name + '.xlsx'))
            ]
        elif output_format == 'pdf':
            data = report_obj.get_pdf(options)
            headers = [
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', content_disposition(report_name + '.pdf'))
            ]
        elif output_format == 'xml':
            data = report_obj.get_xml(options)
            headers = [
                ('Content-Type', 'application/vnd.sun.xml.writer'),
                ('Content-Disposition', content_disposition(report_name + '.xml')),
                ('Content-Length', len(data))
            ]
        elif output_format == 'xaf':
            data = report_obj.get_xaf(options)
            headers = [
                ('Content-Type', 'application/vnd.sun.xml.writer'),
                ('Content-Disposition', 'attachment; filename=' + content_disposition(report_name + '.xaf;')),
                ('Content-Length', len(data))
            ]
        elif output_format == 'txt':
            data = report_obj.get_txt(options)
            headers = [
                ('Content-Type', 'text/plain'),
                ('Content-Disposition', content_disposition(report_name + '.txt')),
                ('Content-Length', len(data))
            ]
        elif output_format == 'csv':
            data = report_obj.get_csv(options)
            headers = [
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', 'attachment; filename=' + content_disposition(report_name + '.csv;')),
                ('Content-Length', len(data))
            ]
        elif output_format == 'zip':
            data = report_obj._get_zip(options)
            headers = [
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', 'attachment; filename=' + content_disposition(report_name + '.zip')),
            ]
        return data, headers

    @http.route('/to_stock_report', type='http', auth='user', methods=['POST'], csrf=False)
    def get_report(self, model, options, output_format, token, financial_id=None, **kw):
        report_obj = request.env[model]
        options = json.loads(options)
        try:
            if financial_id and financial_id != 'null':
                report_obj = report_obj.browse(int(financial_id))
            
            report_name = report_obj.get_report_filename(options)
            
            data, headers = self._get_headers_by_output_format(output_format, report_obj, report_name, options)
            response = request.make_response(data, headers)
            
            if output_format == 'xlsx':
                report_obj.get_xlsx(options, response)
            elif output_format == 'zip':
                # Adding direct_passthrough to the response and giving it a file
                # as content means that we will stream the content of the file to the user
                # Which will prevent having the whole file in memory
                response.direct_passthrough = True
            
            response.set_cookie('fileToken', token)
            return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
