from odoo.tests.common import TransactionCase


class TestDocsCommon2(TransactionCase):

    def setUp(self):
        super(TestDocsCommon2, self).setUp()

        self.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        self.env = self.env(context=dict(self.no_mailthread_features_ctx, **self.env.context))

        self.group_public = self.env.ref('base.group_public')
        self.group_portal = self.env.ref('base.group_portal')
        self.group_internal = self.env.ref('base.group_user')
        self.group_editor_user = self.env.ref('to_website_docs.group_website_doc_editor')
        self.group_reviewer_user = self.env.ref('to_website_docs.group_website_doc_reviewer')
        self.group_designer_user = self.env.ref('to_website_docs.group_website_doc_designer')
        self.group_manager_user = self.env.ref('to_website_docs.group_website_doc_manager')

        self.lang_en = self.env.ref('base.lang_en').sudo()
        self.lang_vi = self.env.ref('base.lang_vi_VN').sudo()
        self.lang_vi.active = True

        # Test users to use through the various tests
        self.admin = self.env.ref('base.user_admin')

        self.base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        self.website = self.env['website'].browse(1)

        # objects
        Document = self.env['website.document']
        Category = self.env['website.doc.category']
        Content = self.env['website.document.content']
        Users = self.env['res.users'].with_context({'no_reset_password': True, 'tracking_disable': True})

        self.user_portal = Users.create({
            'name': 'User Portal',
            'login': 'portal_doc',
            'password': 'portal_doc',
            'email': 'portal_doc@@example.viindoo.com',
            'signature': 'SignChell',
            'notification_type': 'email',
            'groups_id': [(6, 0, [self.group_portal.id])]
            })

        self.editor_user = Users.create({
            'name': 'Editor User',
            'login': 'editor_doc',
            'password': 'editor_doc',
            'email': 'editor_doc@example.viindoo.com',
            'groups_id': [(6, 0, [self.group_internal.id, self.group_editor_user.id])]
            })

        self.reviewer_user = Users.create({
            'name': 'Reviewer User',
            'login': 'reviewer_doc',
            'password': 'reviewer_doc',
            'email': 'reviewer_doc@example.viindoo.com',
            'groups_id': [(6, 0, [self.group_internal.id, self.group_reviewer_user.id])]
            })

        self.designer_user = Users.create({
            'name': 'Designer User',
            'login': 'designer_doc',
            'password': 'designer_doc',
            'email': 'designer_doc@example.viindoo.com',
            'groups_id': [(6, 0, [self.group_internal.id, self.group_designer_user.id])]
            })

        self.manager_user = Users.create({
            'name': 'Manager User',
            'login': 'manager_doc',
            'password': 'manager_doc',
            'email': 'manager_doc@example.viindoo.com',
            'groups_id': [(6, 0, [self.group_internal.id, self.group_manager_user.id])]
            })

        # Subjects data
        self.subject_user = Category.create({
            'name': 'Odoo User Documentation', 
            'sequence': 5,
            'description': 'An introduction guides for Odoo end-user. Easily locate functional tutorials, helpful tips, and reference information for a wide array of apps and processes.',
            'type': 'subject',
            'document_type': 'link',
            })

        self.subject_user_2 = Category.create({
            'name': 'Odoo User Documentation 2',
            'sequence': 5,
            'description': 'An introduction guides for Odoo end-user 2',
            'type': 'subject',
            'document_type': 'link',
            })

        # Sections data
        self.section_applications = Category.create({
            'name': 'Applications',
            'parent_id': self.subject_user.id,
            'sequence': 10,
            'type': 'section',
            'document_type': 'link',
            'css_section_item': 'col-md-3',
            })

        # Categories data : No documentation
        self.category_general = Category.create({
            'name': 'General',
            'parent_id': self
            .section_applications.id,
            'sequence': 10,
            'type': 'category',
            'document_type': 'link',
            })

        self.category_general_2 = Category.create({
            'name': 'General',
            'parent_id': self.section_applications.id,
            'sequence': 10,
            'type': 'category',
            'document_type': 'link',
            })

        self.category_general_3 = Category.create({
            'name': 'General',
            'parent_id': self.subject_user_2.id,
            'sequence': 20,
            'type': 'category',
            'document_type': 'link',
        })

        # Docs data
        self.doc = Document.create({
            'name': 'Activate the Developer (Debug) Mode',
            'category_id': self.category_general.id,
            })
        self.doc_2 = Document.create({
            'name': "Welcome To Summoner's Rift",
            'category_id': self.category_general_3.id,
            })
        # Docs content data
        self.doc_content_2 = Content.create({
            'document_id': self.doc_2.id,
            'fulltext': 'Introduction to the Angular Docs v20',
        })
