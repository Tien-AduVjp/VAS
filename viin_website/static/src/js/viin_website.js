odoo.define('viin_website.navbar', function(require) {
    'use strict';

    var websiteNavbar = require('website.navbar');

    websiteNavbar.WebsiteNavbar.include({
        events: _.extend({}, websiteNavbar.WebsiteNavbar.prototype.events || {}, {
            'click .fa.fa-th.o_menu_toggle': '_onClickMenuToggle',
        }),

        /**
         * When users click to the application apps switcher on website,
         * they will be redirected to the back office
         */
        _onClickMenuToggle: function(e) {
            e.preventDefault();
            var $button = $(e.currentTarget);
            var $spinner = $('<i/>', { 'class': 'fa fa-spinner fa-pulse'});
            $button.removeClass('fa-th').append($spinner);
            $(window.location).attr('href', '/web');

        },
    });
});
