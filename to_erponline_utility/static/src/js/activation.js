odoo.define('to_erponline_utility.activation_systray', function (require) {
    'use strict';

    var session = require('web.session');
    var core = require('web.core');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var config = require('web.config');

    var ActivationMenu = Widget.extend({
        xmlDependencies: ['/to_erponline_utility/static/src/xml/activation.xml'],
        template: 'activation_systray_button',
        events: {
            'click .activation_button': '_onActivationClick'
        },

        init: function () {
            this._super.apply(this, arguments);
            this.trial_activated = session.trial_activated;
            this.isMobile = config.device.isMobile;
        },

        _onActivationClick: function (event) {
            event.preventDefault();
            this._showActivationDialog();
        },

        _showActivationDialog: function () {
            var stopDate = moment.utc(session.stop_date);
            var now = moment();
            var duration = moment.duration(stopDate.diff(now));
            $(core.qweb.render('activation_modal', {
                activation_warning: session.activation_warning,
                trial_activated: session.trial_activated,
                duration: duration,
                activation_email: session.activation_email,
                trial_days: session.trial_days,
            })).appendTo($('body')).modal('show').on('hidden.bs.modal', function (e) {
                $(this).remove();
            });
        },
    });

    if (session.activation_warning) {
        SystrayMenu.Items.push(ActivationMenu);
    }

    return ActivationMenu;
})
