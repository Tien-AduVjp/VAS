/*
Temporarily fix Restricted Editor unable to save blog post, page view
Ticket: https://viindoo.com/web#active_id=6231&cids=1&id=6231&model=helpdesk.ticket&menu_id=
TODO: Check and remove this part if this bug has been fixed in 15
*/

odoo.define('viin_website_page_access_right.editor', function (require) {
    'use strict';

    const WysiwygMultizone = require('web_editor.wysiwyg.multizone');

    WysiwygMultizone.include({
        willStart() {
            return this._super(...arguments).then(() => {
                if (!this.hasOwnProperty('isDesigner')) {
                    return this._rpc({
                        model: 'res.users',
                        method: 'has_group',
                        args: ['website.group_website_designer']
                    }).then(isDesigner => {
                        this.isDesigner = isDesigner;
                    });
                }
            });
        },
        _saveElement(outerHTML, recordInfo, editable) {
            // Skip content related to website.menu before restricted editor saving content to avoid permission errors.
            if (!this.isDesigner && editable
                && $('html').data('mainObject').includes('website.page')
                && editable.dataset.oeModel === 'website.menu') {
                return Promise.resolve();
            }
            return this._super(...arguments);
        }
    });
});
