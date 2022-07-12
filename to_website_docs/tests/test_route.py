from odoo.tests import HttpSavepointCase, tagged
from odoo.tools import mute_logger

from odoo.addons.website.tools import MockRequest

from .common import TestDocsCommon


@tagged('post_install', '-at_install', 'external')
class TestDocsRoute(HttpSavepointCase, TestDocsCommon):

    def prepare_json_create_doc(self):
        return {
            'params': {
                'category_id': self.category_general_2.id,
                'name': 'Test Document API',
            }
        }

    def prepare_json_update_doc(self, record_id):
        return {
            'params': {
                'document_id': record_id,
                'name': 'Test Document API 2',
            }
        }

    def prepare_json_delete(self, res_id, res_model):
        return {
            'params': {
                'res_id': res_id,
                'res_model': res_model,
            }
        }

    def prepare_json_create_category(self, parent_id=False):
        return {
            'params': {
                'name': 'Category Test',
                'parent_id': parent_id
            }
        }

    def prepare_json_update_category(self, category_id):
        return {
            'params': {
                'category_id': category_id,
                'name': 'Category Test 2'
            }
        }

    def prepare_request_actions(self, action, obj_name, record_id, cat_parent_id):
        if action == 'create':
            if obj_name == 'website.document':
                return self.prepare_json_create_doc(), '/docs/create'
            else:
                return self.prepare_json_create_category(cat_parent_id), '/docs/create_category'
        if action == 'update':
            if obj_name == 'website.document':
                return self.prepare_json_update_doc(record_id), '/docs/update_document'
            else:
                return self.prepare_json_update_category(record_id), '/docs/update_category'
        if action == 'delete':
            return self.prepare_json_delete(record_id, obj_name), '/docs/delete'

    @mute_logger('odoo.http')
    def do_request(self, action, obj_name, record_id=False, error=False, **kwargs):
        obj = self.env[obj_name]
        json, route = self.prepare_request_actions(action, obj_name, record_id, kwargs.get('parent_id'))
        with MockRequest(self.env, website=self.website, context={'lang': 'en_US'}):
            resp = self.opener.post(self.base_url + route, json=json)
        if error:
            self.assertTrue(resp.json().get('error'), 'Response should be returned as error')
        else:
            if action != 'delete':
                obj = obj.browse(resp.json().get('result', {}).get('id')).exists()
                self.assertTrue(obj, '%s should be %sd' % (obj._description, action))
            self.assertTrue(resp.json().get('result'), 'Response should be returned as result')
        return obj

    def test_route_document__user_public(self):
        # Auth: public
        # Action: post request (create, update, delete document)
        # Result: get error
        obj_name = 'website.document'
        self.do_request('create', obj_name, error=True)
        self.do_request('update', obj_name, record_id=self.doc.id, error=True)
        self.do_request('delete', obj_name, record_id=self.doc.id, error=True)

    def test_route_document__user_portal(self):
        # Auth: portal
        # Action: post request (create, update, delete document)
        # Result: get error
        obj_name = 'website.document'
        self.authenticate('portal_doc', 'portal_doc')
        self.do_request('create', obj_name, error=True)
        self.do_request('update', obj_name, record_id=self.doc.id, error=True)
        self.do_request('delete', obj_name, record_id=self.doc.id, error=True)

    def test_route_document__user_editor(self):
        # Auth: editor
        # Action: post request (create, update, delete document)
        # Result: success
        obj_name = 'website.document'
        self.authenticate('editor_doc', 'editor_doc')
        # with own document
        own_doc = self.do_request('create', obj_name)
        self.do_request('update', obj_name, record_id=own_doc.id)
        self.do_request('delete', obj_name, record_id=own_doc.id)
        # with another document
        self.do_request('update', obj_name, record_id=self.doc.id, error=True)
        self.do_request('delete', obj_name, record_id=self.doc.id, error=True)

    def test_route_document__user_reviewer(self):
        # Auth: reviewer
        # Action: post request (create, update, delete document)
        # Result: success
        obj_name = 'website.document'
        self.authenticate('reviewer_doc', 'reviewer_doc')
        own_doc = self.do_request('create', obj_name)
        self.do_request('update', obj_name, record_id=own_doc.id)
        self.do_request('delete', obj_name, record_id=own_doc.id)
        # with another document
        self.do_request('update', obj_name, record_id=self.doc.id, error=True)
        self.do_request('delete', obj_name, record_id=self.doc.id, error=True)

    def test_route_document__user_designer(self):
        # Auth: Designer
        # Action: post request (create, update, delete document)
        # Result: success
        obj_name = 'website.document'
        self.authenticate('designer_doc', 'designer_doc')
        own_doc = self.do_request('create', obj_name)
        self.do_request('update', obj_name, record_id=own_doc.id)
        self.do_request('delete', obj_name, record_id=own_doc.id)
        # with another document
        self.do_request('update', obj_name, record_id=self.doc.id, error=True)
        self.do_request('delete', obj_name, record_id=self.doc.id, error=True)

    def test_route_document__user_manager(self):
        # Auth: Manager
        # Action: post request (create, update, delete document)
        # Result: success
        obj_name = 'website.document'
        self.authenticate('manager_doc', 'manager_doc')
        own_doc = self.do_request('create', obj_name)
        self.do_request('update', obj_name, record_id=own_doc.id)
        self.do_request('delete', obj_name, record_id=own_doc.id)
        # with another document
        self.do_request('update', obj_name, record_id=self.doc.id)
        self.do_request('delete', obj_name, record_id=self.doc.id)

    def test_route_category__user_public(self):
        # Auth: public
        # Action: post request (create, update, delete category)
        # Result: get error
        obj_name = 'website.doc.category'
        self.do_request('create', obj_name, error=True)
        self.do_request('update', obj_name, record_id=self.category_general.id, error=True)
        self.do_request('delete', obj_name, record_id=self.category_general.id, error=True)

    def test_route_category__user_portal(self):
        # Auth: portal
        # Action: post request (create, update, delete category)
        # Result: get error
        obj_name = 'website.doc.category'
        self.authenticate('portal_doc', 'portal_doc')
        self.do_request('create', obj_name, error=True)
        self.do_request('update', obj_name, record_id=self.category_general.id, error=True)
        self.do_request('delete', obj_name, record_id=self.category_general.id, error=True)

    def test_route_category__user_reviewer(self):
        # Auth: reviewer
        # Action: post request (create, update, delete category)
        # Result: success
        obj_name = 'website.doc.category'
        self.authenticate('reviewer_doc', 'reviewer_doc')

        # create subject
        self.do_request('create', obj_name, error=True)

        own_category = self.do_request('create', obj_name, parent_id=self.section_applications.id)
        self.do_request('update', obj_name, record_id=own_category.id)
        self.do_request('delete', obj_name, record_id=own_category.id, error=True)
        # with another category
        self.do_request('update', obj_name, record_id=self.category_general.id)
        self.do_request('delete', obj_name, record_id=self.category_general.id, error=True)

    def test_route_category__user_designer(self):
        # Auth: designer
        # Action: post request (create, update, delete category)
        # Result: success
        obj_name = 'website.doc.category'
        self.authenticate('designer_doc', 'designer_doc')

        # create subject
        self.do_request('create', obj_name, error=True)

        own_category = self.do_request('create', obj_name, parent_id=self.section_applications.id)
        self.do_request('update', obj_name, record_id=own_category.id)
        self.do_request('delete', obj_name, record_id=own_category.id, error=True)
        # with another category
        self.do_request('update', obj_name, record_id=self.category_general.id)
        self.do_request('delete', obj_name, record_id=self.category_general.id, error=True)

    def test_route_category__user_manager(self):
        # Auth: manager
        # Action: post request (create, update, delete category)
        # Result: success
        obj_name = 'website.doc.category'
        self.authenticate('manager_doc', 'manager_doc')
        own_category = self.do_request('create', obj_name)
        self.do_request('update', obj_name, record_id=own_category.id)
        self.do_request('delete', obj_name, record_id=own_category.id)
        # with another category
        self.do_request('update', obj_name, record_id=self.category_general.id)
        self.do_request('delete', obj_name, record_id=self.category_general.id)
