odoo.define('viin_mobile.ThreadWindow', function (require){
    "use strict";
        
    var MailThreadWindow = require('mail.ThreadWindow');

    MailThreadWindow.include({
        events: _.extend({}, MailThreadWindow.prototype.events, {
            'click .o_thread_window_expand_mobile': '_onClickExpandMobile',
        }),

        _onClickExpandMobile: _.debounce(function (ev) {
            var self = this;
            ev.preventDefault();
            if (this._isDocumentThread()) {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: this._thread.getDocumentModel(),
                    views: [[false, 'form']],
                    res_id: this._thread.getDocumentID(),
                });
            } else {
                this.do_action('mail.action_discuss', {
                    clear_breadcrumbs: false,
                    active_id: this.hasThread() ? this._getThreadID() : undefined,
                    on_reverse_breadcrumb: function () {
                        var mailBus = self.call('mail_service', 'getMailBus');
                        if (mailBus) {
                            mailBus.trigger('discuss_open', false);
                        }
                    },
                });
            }
            this.close();
        }, 1000, true),

        _isDocumentThread: function(){
            return this.hasThread() && this._thread.getType() === 'document_thread';
        },
	});
    
})
