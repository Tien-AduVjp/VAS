odoo.define('to_website_affiliate.website_affiliate', function(require) {
    "use strict";
    require('web.dom_ready');
    var ajax = require('web.ajax');

    $('.copy_link_button').click(function() {
        var self = $(this);
        var link_tracker = self.closest('.link_tracker');
        $('.short_url_val', link_tracker).select();
        document.execCommand("Copy");
        var text = self.html();
        self.html('Copied')
        setTimeout(function() {
            self.html(text);
        }, 3000);
    });

    $('.edit_link_button').click(function() {
        var self = $(this);
        var link_tracker = self.closest('.link_tracker');
        link_tracker.addClass('editing');
        $('h4', link_tracker).addClass('hide');
        $('.link_title', link_tracker).removeClass('hide');
    });
    $('.save_link_button').click(function() {
        var self = $(this);
        var link_tracker = self.closest('.link_tracker');
        var new_name = $('.link_title', link_tracker).val();
        var new_medium = $('.link_medium_val', link_tracker).find(":selected").val();
        var new_medium_text = $('.link_medium_val', link_tracker).find(":selected").text();
        var new_source = $('.link_source_val', link_tracker).find(":selected").val();
        var new_source_text = $('.link_source_val', link_tracker).find(":selected").text();
        var link_id = self.data('id')
        if (new_name && new_name != '' && link_id) {
            ajax.post('/affiliate/update_link/' + link_id, { 'new_name': new_name, 'new_medium': new_medium, 'new_source': new_source })
                .then(function(result_data) {
                    if (result_data) {
                        $('h4', link_tracker).html(new_name).removeClass('hide');
                        $('.link_title', link_tracker).addClass('hide');
                        $('.medium', link_tracker).find('span').html(new_medium_text);
                        $('.source', link_tracker).find('span').html(new_source_text);
                        link_tracker.removeClass('editing');
                    }
                    else {
                        $('h4', link_tracker).removeClass('hide');
                        $('.link_title', link_tracker).val($('h4', link_tracker).html()).addClass('hide');
                        link_tracker.removeClass('editing');
                    }
                });
        }
    });
    $('.delete_link_button').click(function() {
        var self = $(this);
        var link_tracker = self.closest('.link_tracker');
        var link_id = self.data('id')
        if (link_id) {
            ajax.post('/affiliate/remove_link/' + link_id, {})
                .then(function(result_data) {
                    if (result_data) {
                        link_tracker.remove();
                    }
                });
        }
    });
});


