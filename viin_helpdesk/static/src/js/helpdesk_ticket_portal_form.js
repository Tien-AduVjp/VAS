odoo.define('viin_helpdesk.helpdesk_ticket_portal_form', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.TeamDescription = publicWidget.Widget.extend({
        selector: '.js_helpdesk_ticket_portal_form',
        events: {
            'change select': '_onchangeTeam',
            'click button#submit': '_onSubmit',
        },

        /**
        * @override
        */
        start: function() {
            this._onchangeTeam();
            return this._super();
        },

        check_error_fields: function(error_fields) {
            var form_valid = true;
            // Loop on all fields
            this.$target.find('.form-field').each(function(k, field) {
                var $field = $(field);
                var field_name = $field.find('.col-form-label').attr('for');

                // Validate inputs for this field
                var inputs = $field.find('.o_website_form_input:not(#editable_select)');
                var invalid_inputs = inputs.toArray().filter(function(input, k, inputs) {
                    return !input.checkValidity();
                });

                // Update field color if invalid or erroneous
                $field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
                if (invalid_inputs.length || error_fields[field_name]) {
                    $field.addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid')
                    if (_.isString(error_fields[field_name])) {
                        $field.popover({ content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top' });
                        // update error message and show it.
                        $field.data("bs.popover").config.content = error_fields[field_name];
                        $field.popover('show');
                    }
                    form_valid = false;
                }
            });
            return form_valid;
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onchangeTeam: function() {
            var self = this;
            var team = $('select[name="team_id"] option:selected');

            this._rpc({
                model: 'helpdesk.team',
                method: 'get_description_of_team',
                args: [[+team.val()]],
            }).then(function(result) {
                var description = self.$target.find('.helpdesk-team-description');
                if (result[0].description) {
                    $(description).find('span').text(result[0].description);
                    description.removeClass('d-none');
                } else {
                    description.addClass('d-none');
                }
            });
        },

        /**
        * handle button submit click event
        * @private
        */
        _onSubmit: function(e) {
            e.preventDefault();  // Prevent the default submit behavior

            if (!this.check_error_fields({})) {
                return false;
            }

            var self = this;
            // Prepare form inputs
            this.form_fields = this.$target.serializeArray();
            $.each(this.$target.find('input[type=file]'), function(outer_index, input) {
                $.each($(input).prop('files'), function(index, file) {
                    // Index field name as ajax won't accept arrays of files
                    // when aggregating multiple files into a single field value
                    self.form_fields.push({
                        name: input.name + '[' + outer_index + '][' + index + ']',
                        value: file
                    });
                });
            });
            // Serialize form inputs into a single object
            // Aggregate multiple values into arrays
            var form_values = {};
            _.each(this.form_fields, function(input) {
                if (input.name in form_values) {
                    // If a value already exists for this field,
                    // we are facing a x2many field, so we store
                    // the values in an array.
                    if (input.name == '' || Array.isArray(form_values[input.name])) {
                        form_values[input.name].push(input.value);
                    } else {
                        form_values[input.name] = [form_values[input.name], input.value];
                    }
                } else {
                    if (input.value !== '') {
                        form_values[input.name] = input.value;
                    }
                }
            });
            // Post form and handle result
            ajax.post(this.$target.attr('action'), form_values)
                .then(function(result_data) {
                    result_data = JSON.parse(result_data);
                    if (!result_data.id) {
                        // Failure, the server didn't return the created record ID
                        $(window.location).attr('href', '/my/tickets');
                    } else {
                        // Success, redirect or update status
                        $(window.location).attr('href', '/my/tickets/' + result_data.id);

                        // Reset the form
                        self.$target[0].reset();
                    }
                })
                .guardedCatch(function() {
                    $(window.location).attr('href', '/my/tickets');
                });;
        },

    });
});
