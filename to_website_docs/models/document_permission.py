class DocumentPermission():
    """
        Get permission of document
        Read is checked from rule
        write: assigned user, manager, administrator and supervisor
        unlink: assigned user (draft only), manager, administrator and supervisor
        create: members, manager, administrator and supervisor
        approve: can approve
    """
    create = False
    write = False
    approve = False
    unlink = False
    parent = None

    def load_category(self, category, user):
        self.parent = category
        if user.has_group('to_website_docs.group_website_doc_manager'):
            self.create = True
            self.write = True
            self.unlink = True
            self.approve = True
        elif user.has_group('to_website_docs.group_website_doc_reviewer'):
            self.create = True
            self.write = True
            self.approve = True

    def load_document(self, document, user):
        self.parent = document
        if user.has_group('to_website_docs.group_website_doc_reviewer'):
            self.create = True
            self.write = True
            self.unlink = True
            self.approve = True
        elif user.has_group('to_website_docs.group_website_doc_editor'):
            self.create = True
            self.write = True
            self.unlink = True

    def load_document_content(self, content, user):
        self.parent = content
        if user.has_group('to_website_docs.group_website_doc_reviewer'):
            self.create = True
            self.write = True
            self.unlink = True
            self.approve = True
        elif user.has_group('to_website_docs.group_website_doc_editor'):
            self.create = True
            self.write = True
            self.unlink = True
