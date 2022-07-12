from odoo.tests.common import SavepointCase


class TestDocsCommon1(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestDocsCommon1, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.group_public = cls.env.ref('base.group_public')
        cls.group_portal = cls.env.ref('base.group_portal')
        cls.group_internal = cls.env.ref('base.group_user')
        cls.group_editor_user = cls.env.ref('to_website_docs.group_website_doc_editor')
        cls.group_reviewer_user = cls.env.ref('to_website_docs.group_website_doc_reviewer')
        cls.group_designer_user = cls.env.ref('to_website_docs.group_website_doc_designer')
        cls.group_manager_user = cls.env.ref('to_website_docs.group_website_doc_manager')

        cls.lang_en = cls.env.ref('base.lang_en').sudo()
        cls.lang_vi = cls.env.ref('base.lang_vi_VN').sudo()
        cls.lang_vi.active = True

        # Test users to use through the various tests
        cls.admin = cls.env.ref('base.user_admin')

        cls.base_url = cls.env['ir.config_parameter'].get_param('web.base.url')
        cls.website = cls.env['website'].browse(1)

        # objects
        Document = cls.env['website.document']
        Category = cls.env['website.doc.category']
        Content = cls.env['website.document.content']
        DocTag = cls.env['website.doc.tag']
        Users = cls.env['res.users'].with_context({'no_reset_password': True, 'tracking_disable': True})

        cls.user_public = Users.create({
            'name': 'User Public',
            'login': 'public_doc',
            'email': 'public_doc@example.viindoo.com',
            'signature': 'SignBert',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.group_public.id])]
            })
        
        cls.user_portal = Users.create({
            'name': 'User Portal',
            'login': 'portal_doc',
            'password': 'portal_doc',
            'email': 'portal_doc@@example.viindoo.com',
            'signature': 'SignChell',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.group_portal.id])]
            })
        
        cls.user_internal = Users.create({
            'name': 'User Internal',
            'login': 'internal_doc',
            'password': 'internal_doc',
            'email': 'internal_doc@example.viindoo.com',
            'groups_id': [(6, 0, [cls.group_internal.id])]
            })
        
        cls.editor_user = Users.create({
            'name': 'Editor User',
            'login': 'editor_doc',
            'password': 'editor_doc',
            'email': 'editor_doc@example.viindoo.com',
            'groups_id': [(6, 0, [cls.group_internal.id, cls.group_editor_user.id])]
            })
        
        cls.editor_user_2 = Users.create({
            'name': 'Editor User 2',
            'login': 'editor_doc_2',
            'password': 'editor_doc_2',
            'email': 'editor_doc_2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.group_internal.id, cls.group_editor_user.id])]
            })
        
        cls.reviewer_user = Users.create({
            'name': 'Reviewer User',
            'login': 'reviewer_doc',
            'password': 'reviewer_doc',
            'email': 'reviewer_doc@example.viindoo.com',
            'groups_id': [(6, 0, [cls.group_internal.id, cls.group_reviewer_user.id])]
            })
        
        cls.reviewer_user_2 = Users.create({
            'name': 'Reviewer User 2',
            'login': 'reviewer_doc_2',
            'password': 'reviewer_doc_2',
            'email': 'reviewer_doc_2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.group_internal.id, cls.group_reviewer_user.id])]
            })
        
        cls.designer_user = Users.create({
            'name': 'Designer User',
            'login': 'designer_doc',
            'password': 'designer_doc',
            'email': 'designer_doc@example.viindoo.com',
            'groups_id': [(6, 0, [cls.group_internal.id, cls.group_designer_user.id])]
            })
        
        cls.designer_user_2 = Users.create({
            'name': 'Designer User 2',
            'login': 'designer_doc_2',
            'password': 'designer_doc_2',
            'email': 'designer_doc_2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.group_internal.id, cls.group_designer_user.id])]
            })
        
        cls.manager_user = Users.create({
            'name': 'Manager User',
            'login': 'manager_doc',
            'password': 'manager_doc',
            'email': 'manager_doc@example.viindoo.com',
            'groups_id': [(6, 0, [cls.group_internal.id, cls.group_manager_user.id])]
            })
        
        # Subjects data
        cls.subject_user = Category.create({
            'name': 'Odoo User Documentation', 
            'sequence': 5,
            'description': 'An introduction guides for Odoo end-user. Easily locate functional tutorials, helpful tips, and reference information for a wide array of apps and processes.',
            'type': 'subject',
            'document_type': 'link',
            })

        cls.subject_user_2 = Category.create({
            'name': 'Odoo User Documentation 2',
            'sequence': 5,
            'description': 'An introduction guides for Odoo end-user 2',
            'type': 'subject',
            'document_type': 'link',
            })

        # Sections data
        cls.section_applications = Category.create({
            'name': 'Applications',
            'parent_id': cls.subject_user.id,
            'sequence': 10,
            'type': 'section',
            'document_type': 'link',
            'css_section_item': 'col-md-3',
            })
        
        # Categories data
        cls.category_general = Category.create({
            'name': 'General',
            'parent_id': cls.section_applications.id,
            'sequence': 10,
            'type': 'category',
            'document_type': 'link',
            })

        # Categories data : No documentation
        cls.category_general_2 = Category.create({
            'name': 'General',
            'parent_id': cls.section_applications.id,
            'sequence': 10,
            'type': 'category',
            'document_type': 'link',
            })

        cls.category_general_3 = Category.create({
            'name': 'General',
            'parent_id': cls.subject_user_2.id,
            'sequence': 20,
            'type': 'category',
            'document_type': 'link',
        })
        # Docs data
        cls.doc = Document.create({
            'name': 'Activate the Developer (Debug) Mode',
            'category_id': cls.category_general.id,
            })
        cls.doc_2 = Document.create({
            'name': "Welcome To Summoner's Rift",
            'category_id': cls.category_general_3.id,
            })
        # Docs content data
        cls.doc_content = Content.create({
            'document_id': cls.doc.id,
            'fulltext': 'The Developer or Debug Mode gives you access to extra and advanced tools...',
            })
        cls.doc_content_2 = Content.create({
            'document_id': cls.doc_2.id,
            'fulltext': 'Introduction to the Angular Docs v20',
        })
        # Tags data
        cls.tag_1 = DocTag.create({'name': 'tag 1'})
        cls.tag_2 = DocTag.create({'name': 'tag 2'})
        cls.tag_3 = DocTag.create({'name': 'tag 3'})
