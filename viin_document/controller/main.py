import base64
import json
import logging
import zipfile
from datetime import date
from io import BytesIO

from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import (html_escape, human_size)

logger = logging.getLogger(__name__)

class DocumentController(http.Controller):

    @http.route('/document/upload_document', type='http', methods=['POST'], auth="user")
    def upload_document(self, ufile, workspace_id):
        # Refer to Odoo CE (mrp)
        # https://github.com/odoo/odoo/blob/14.0/addons/mrp/controller/main.py#L18
        files = request.httprequest.files.getlist('ufile')
        result = {'success': _("All files uploaded")}
        vals_list = []
        for ufile in files:
            try:
                name = ufile.filename
                mimetype = ufile.content_type
                datas = base64.encodebytes(ufile.read())
                workspace_id = int(workspace_id)
                vals_list.append(request.env['document.document']._prepare_upload_document_value(
                    name,
                    mimetype,
                    datas,
                    workspace_id
                ))
            except Exception as e:
                logger.exception("Fail to upload document %s" % ufile.filename)
                result = {'error': str(e)}
        try:
            with request.env.cr.savepoint():
                documents = request.env['document.document'].create(vals_list)
                result['document_ids'] = documents.ids
        except Exception as e:
            result = {'error': str(e)}

        return json.dumps(result)

    @http.route('/document/record', type='json', auth='user')
    def read_record(self, document_id=None):
        return request.env['document.document'].search([('id', '=', document_id)]).read()

    @http.route('/document/read', type='json', auth='user')
    def infos(self, document_ids = None, fields = None):
        documents = request.env['document.document'].search([('id', 'in', document_ids)])
        result = documents.mapped(
            lambda d : {
                    "doc_id": d.id,
                    "mimetype": d.mimetype,
                    "display_name": d.name,
                    "attachment_id": {
                        "id": d.attachment_id.id,
                        "display_name": d.name
                    },
                    "workspace_id": {
                        "id": d.workspace_id.id,
                        "display_name": d.workspace_id.name
                    },
                    "tag_ids": d.tag_ids.mapped(lambda t : {"id": t.id, "display_name": t.name}),
                    "action_ids": d.action_ids.mapped(lambda a : {"id": a.id, "display_name": a.name}),
                    "owner_id": {
                        "id": d.owner_id.id,
                        "display_name": d.owner_id.name
                    },
                    "url": d.url,
                    "ytb_video_id": d.ytb_video_id
                })
        return result

    @http.route('/document/update', type='json', auth='user')
    def update_document(self, **kwargs):
        documents = request.env['document.document'].search([('id', 'in', kwargs['data']['document_ids'])])
        update_fiels = {}
        fields_value = kwargs['data']['value']

        if 'tag_ids' in fields_value and fields_value['tag_ids'].get('id', False):
            if fields_value['tag_ids']['action'] == 'ADD_NEW':
                update_fiels['tag_ids'] = [(4, fields_value['tag_ids']['id'], 0)]
            if fields_value['tag_ids']['action'] == 'REMOVE':
                update_fiels['tag_ids'] = [(3, fields_value['tag_ids']['id'], 0)]
        if 'owner_id' in fields_value and fields_value['owner_id'].get('id', False):
            if fields_value['owner_id']['action'] == 'CHANGE':
                update_fiels['owner_id'] = fields_value['owner_id']['id']
        if 'workspace_id' in fields_value and fields_value['workspace_id'].get('id', False):
            if fields_value['workspace_id']['action'] == 'CHANGE':
                update_fiels['workspace_id'] = fields_value['workspace_id']['id']
        if 'name' in fields_value and fields_value['name'].get('data', False):
            if fields_value['name']['action'] == 'CHANGE':
                update_fiels['name'] = fields_value['name']['data']

        result = documents.write(update_fiels)

        if result:
            result = documents.mapped(
            lambda d : {
                    "doc_id": d.id,
                    "mimetype": d.mimetype,
                    "display_name": d.name,
                    "attachment_id": {
                        "id": d.attachment_id.id,
                        "display_name": d.name
                    },
                    "workspace_id": {
                        "id": d.workspace_id.id,
                        "display_name": d.workspace_id.name
                    },
                    "tag_ids": d.tag_ids.mapped(lambda t : {"id": t.id, "display_name": t.name}),
                    "action_ids": d.action_ids.mapped(lambda a : {"id": a.id, "display_name": a.name}),
                    "owner_id": {
                        "id": d.owner_id.id,
                        "display_name": d.owner_id.name
                    },
                    "url": d.url,
                    "ytb_video_id": d.ytb_video_id
                })
        return result

    @http.route('/document/download', type='http', auth='user')
    def download_document(self, ids):
        list_ids = list(ids.split(","))
        list_ids = [int(i) for i in list_ids]
        documents = request.env['document.document'].search([('id', 'in', list_ids),('url','=', False)])
        return self._download_multiple_document(documents)

    @http.route('/document/share/<string:token>', type='http', auth='public', website=True)
    def share_document(self, token):
        import re
        document_share = request.env['document.share'].sudo().search([('access_token', '=', token)])
        if len(document_share) == 0:
            return request.render("viin_document.document_share_invalid_token")
        if document_share.rotating_token_id.is_expired():
            return request.render("viin_document.document_share_expired_layout",{
                'owner': document_share.create_uid.name,
                'expired_date': "%s %s, %s" % (document_share.expire_date.strftime('%b'), document_share.expire_date.strftime('%d'), document_share.expire_date.strftime('%Y'))})
        documents = document_share.document_ids.read()
        for doc  in documents:
            if doc['mimetype']:
                doc['binary_previewable'] = re.match("(image|video|application/pdf|text)", doc['mimetype']) and doc['type'] == 'binary'
                doc['webimage'] = re.match('image.*(gif|jpeg|jpg|png)', doc['mimetype'])
            else:
                doc['binary_previewable'] = False
                doc['webimage'] = False
            doc['create_date'] = "%s %s, %s" % (doc['create_date'].strftime('%b'), doc['create_date'].strftime('%d'), doc['create_date'].strftime('%Y'))
            if doc['attachment_id']:
                doc['file_size'] = human_size(request.env['ir.attachment'].browse(doc['attachment_id'][0]).file_size)
            else:
                doc['file_size'] = 'OB'

        return request.render("viin_document.document_share_layout",{
            'documents': documents,
            'owner': document_share.create_uid.name,
            'owner_id': document_share.create_uid.id,
            'res_model': 'document.document',
            'share_token': token
        })

    @http.route('/document/share/content/<int:doc_id>/<string:share_token>', type='http', auth='public', website=True)
    def download_share_document(self, doc_id, share_token, download=None):
        document_share = request.env['document.share'].sudo().search([('access_token','=', share_token)])
        if len(document_share) == 0:
            return request.render("viin_document.document_share_invalid_token")
        if document_share.rotating_token_id.is_expired():
            return request.render("viin_document.document_share_expired_layout",{
                'owner': document_share.create_uid.name,
                'expired_date': "%s %s, %s" % (document_share.expire_date.strftime('%b'), document_share.expire_date.strftime('%d'), document_share.expire_date.strftime('%Y'))})
        document = document_share.document_ids.filtered(lambda d: d.id == doc_id)
        status, headers, content = request.env['ir.http'].sudo().binary_content(
            xmlid=None, model='document.document', id=document.id, field='datas', unique=None, filename=None,
            filename_field='name', download=download, mimetype=None, access_token=None)
        if status != 200:
            return request.env['ir.http']._response_by_status(status, headers, content)
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        return response

    @http.route('/document/avatar/<int:user_id>/<string:share_token>', type='http', auth='public', website=True)
    def get_user_avatar(self, user_id, share_token):
        document_share = request.env['document.share'].sudo().search([('access_token','=', share_token)])
        if not document_share:
            return False
        user = request.env['res.users'].sudo().search([('id','=',user_id)])
        content_base64 = base64.b64decode(user.image_1920)
        headers = [
            ('Content-Type', ' text/plain; charset="utf-8"'),
            ('Content-Length', len(content_base64)),
            ('Content-Transfer-Encoding', 'base64')
        ]
        return request.make_response(content_base64, headers)

    @http.route('/document/share/download_all/<string:token>', type='http', auth='public', website=True)
    def download_all_share_document(self, token):
        document_share = request.env['document.share'].sudo().search([('access_token','=', token)])
        if len(document_share) == 0:
            return request.render("viin_document.document_share_invalid_token")
        if document_share.rotating_token_id.is_expired():
            return request.render("viin_document.document_share_expired_layout",{
                'owner': document_share.create_uid.name,
                'expired_date': "%s %s, %s" % (document_share.expire_date.strftime('%b'), document_share.expire_date.strftime('%d'), document_share.expire_date.strftime('%Y'))})
        documents = document_share.document_ids.filtered(lambda d: d.url == False)
        return self._download_multiple_document(documents)

    @http.route('/document/handle_action', type='json', auth='user')
    def handle_document_action(self, document_ids, action_id):
        result = {}
        action = request.env['document.action'].search([('id', '=', action_id)])
        documents = request.env['document.document'].search([('id','in',document_ids)])
        tags = documents.tag_ids
        update_fiels = {'tag_ids': []}
        if action.set_owner_id:
            update_fiels['owner_id'] = action.set_owner_id.id
        if action.move_to_workspace_id:
            update_fiels['workspace_id'] = action.move_to_workspace_id.id
        if action.set_tag_ids:
            for action_set_tag in action.set_tag_ids:
                if action_set_tag.action_type == 'add':
                    update_fiels['tag_ids'] += [(4, tag_id, 0) for tag_id in action_set_tag.tag_ids.ids]
                if action_set_tag.action_type == 'remove':
                    update_fiels['tag_ids'] += [(3, tag_id, 0) for tag_id in action_set_tag.tag_ids.ids]
                if action_set_tag.action_type == 'replace':
                    tags_to_add = action_set_tag.tag_ids
                    if action_set_tag.category_id:
                        tags_to_remove = tags.filtered(lambda t: action_set_tag.category_id.id in t.category_ids.ids)
                        tag_ids =  [(3, tag_id, 0) for tag_id in tags_to_remove.ids]
                        tag_ids += [(4, tag_id, 0) for tag_id in tags_to_add.ids]
                        update_fiels['tag_ids'] += tag_ids
                    else:
                        update_fiels['tag_ids'] += [(6, 0, tags_to_add.ids)]

        if action.create_document_activity:
            documents.update_schedule_activity(action)

        documents_updated = documents.write(update_fiels)
        if documents_updated:
            documents_updated = documents.mapped(
            lambda d : {
                    "doc_id": d.id,
                    "mimetype": d.mimetype,
                    "display_name": d.name,
                    "attachment_id": {
                        "id": d.attachment_id.id,
                        "display_name": d.name
                    },
                    "workspace_id": {
                        "id": d.workspace_id.id,
                        "display_name": d.workspace_id.name
                    },
                    "tag_ids": d.tag_ids.mapped(lambda t : {"id": t.id, "display_name": t.name}),
                    "action_ids": d.action_ids.mapped(lambda a : {"id": a.id, "display_name": a.name}),
                    "owner_id": {
                        "id": d.owner_id.id,
                        "display_name": d.owner_id.name
                    },
                    "url": d.url
                })
            result['documents'] = documents_updated
        return result

    def _download_multiple_document(self, documents):
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
                for d in documents:
                    status, content, filename, mimetype, filehash = request.env['ir.http']._binary_record_content(
                        d, field='datas', filename=d.name, filename_field='name',
                        default_mimetype='application/octet-stream')
                    if status == 200:
                        zip_file.writestr(filename, base64.b64decode(content))
            content_base64 = zip_buffer.getvalue()
            headers = [
                ('Content-Type', 'application/zip'),
                ('X-Content-Type-Options', 'nosniff'),
                ('Cache-Control', 'max-age=0'),
                ('Content-Length', len(content_base64)),
                ("Content-Disposition", "attachment; filename*=UTF-8''download-documents-%s.zip" % date.today().strftime("%d-%m-%Y"))
            ]
            response = request.make_response(content_base64, headers)
            return response
        except MemoryError as e:
            error = {
                'code': 500,
                'message': 'Memory Limit Exceeded Error!',
            }
            logger.exception("Fail to download document %s" % _serialize_exception(e))
            return request.make_response(html_escape(json.dumps(error)))
        except Exception as e:
            error = {
                'code': 500,
                'message': 'Unknow error!',
            }
            logger.exception("Fail to download document %s" % _serialize_exception(e))
            return request.make_response(html_escape(json.dumps(error)))
