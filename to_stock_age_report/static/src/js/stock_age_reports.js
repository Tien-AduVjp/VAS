odoo.define('to_stock_age_report.af_stock_age_report', function (require) {
'use strict';

var core = require('web.core');
var AbstractAction = require('web.AbstractAction');
var Dialog = require('web.Dialog');
var datepicker = require('web.datepicker');
var session = require('web.session');
var field_utils = require('web.field_utils');
var WarningDialog = require('web.CrashManager').WarningDialog;

var QWeb = core.qweb;
var _t = core._t;

var stockReportsWidget = AbstractAction.extend({
    hasControlPanel: true,

    init: function(parent, action) {
        this.actionManager = parent;
        this.report_model = action.context.model;
        if (this.report_model === undefined) {
            this.report_model = 'stock.report.abstract';
        }
        this.financial_id = false;
        if (action.context.id) {
            this.financial_id = action.context.id;
        }
        this.odoo_context = action.context;
        this.report_options = action.options || false;
        this.ignore_session = action.ignore_session;
        if ((action.ignore_session === 'read' || action.ignore_session === 'both') !== true) {
            var persist_key = 'report:'+this.report_model+':'+this.financial_id+':'+session.company_id;
            this.report_options = JSON.parse(sessionStorage.getItem(persist_key)) || this.report_options;
        }
        return this._super.apply(this, arguments);
    },
    start: function() {
        var self = this;
        var extra_info = this._rpc({
                model: self.report_model,
                method: 'get_report_informations',
                args: [self.financial_id, self.report_options],
                context: self.odoo_context,
            })
            .then(function(result){
		 	return self.parse_reports_informations(result);
            });

        return Promise.all([extra_info, this._super.apply(this, arguments)]).then(function() {
            self.render();
        });
    },

       parse_reports_informations: function(values) {
        this.report_options = values.options;
        this.odoo_context = values.context;
        this.report_manager_id = values.report_manager_id;
        this.buttons = values.buttons;

        this.main_html = values.main_html;
        this.$searchview_buttons = $(values.searchview_html);
        this.persist_options();
    },
    persist_options: function() {
        if ((this.ignore_session === 'write' || this.ignore_session === 'both') !== true) {
            var persist_key = 'report:'+this.report_model+':'+this.financial_id+':'+session.company_id;
            sessionStorage.setItem(persist_key, JSON.stringify(this.report_options));
        }
    },
    // We need this method to rerender the control panel when going back in the breadcrumb
    do_show: function() {
        this._super.apply(this, arguments);
        this.update_cp();
    },
    // Updates the control panel and render the elements that have yet to be rendered
    update_cp: function() {
        if (!this.$buttons) {
            this.renderButtons();
        }
        var status = {
            cp_content: {
                $buttons: this.$buttons,
                $searchview_buttons: this.$searchview_buttons,
                $pager: this.$pager,
                $searchview: this.$searchview,
            },
        };
        return this.updateControlPanel(status, {clear: true});
    },
    reload: function() {
        var self = this;
        return this._rpc({
                model: this.report_model,
                method: 'get_report_informations',
                args: [self.financial_id, self.report_options],
                context: self.odoo_context,
            })
            .then(function(result){
                self.parse_reports_informations(result);
                return self.render();
            });
    },
    render: function() {
        var self = this;
        this.render_template();
        this.render_searchview_buttons();
        this.update_cp();
    },
    render_template: function() {
        this.$('.o_content').html(this.main_html);
    },

    _onChangeExpectedDate: function (event) {
        var self = this;
        var targetID = parseInt($(event.target).attr('data-id'));
        var parentID = parseInt($(event.target).attr('parent-id').split("_")[1]);
        var $content = $(QWeb.render("paymentDateForm", {target_id: targetID}));
        var paymentDatePicker = new datepicker.DateWidget(this);
        paymentDatePicker.appendTo($content.find('div.o_af_reports_payment_date_picker'));
        var save = function () {
            return this._rpc({
                model: 'res.partner',
                method: 'change_expected_date',
                args: [[parentID], {
                    move_line_id: parseInt($content.find("#target_id").val()),
                    expected_pay_date: paymentDatePicker.getValue(),
                }],
            }).then(function() {
                self.reload();
            });
        };
        new Dialog(this, {
            title: 'Odoo',
            size: 'medium',
            $content: $content,
            buttons: [{
                text: _t('Save'),
                classes: 'btn-primary',
                close: true,
                click: save
            },
            {
                text: _t('Cancel'),
                close: true
            }]
        }).open();
    },
    render_searchview_buttons: function() {
        var self = this;
        // bind searchview buttons/filter to the correct actions
        var $datetimepickers = this.$searchview_buttons.find('.js_af_report_datetimepicker_period');
        var options = { // Set the options for the datetimepickers
            locale : moment.locale(),
            format : 'L',
            icons: {
                date: "fa fa-calendar",
            },
        };
        // attach datepicker
        $datetimepickers.each(function () {
            var name = $(this).find('input').attr('name');
            var defaultValue = $(this).data('default-value');
            $(this).datetimepicker(options);
            var dt = new datepicker.DateWidget(options);
            dt.replace($(this)).then(function () {
                dt.$el.find('input').attr('name', name);
                if (defaultValue) {
                    dt.setValue(moment(defaultValue));
                }
            });
        });
        // format date that needs to be show in user lang
        _.each(this.$searchview_buttons.find('.js_format_date'), function(dt) {
            var date_value = $(dt).html();
            $(dt).html((new moment(date_value)).format('ll'));
        });

        _.each(self.report_options, function(k) {
            if (k!== null && k.filter !== undefined) {
                self.$searchview_buttons.find('[data-filter="'+k.filter+'"]').addClass('selected');
            }
        });
        _.each(this.$searchview_buttons.find('.js_af_report_choice_filter'), function(k) {
            $(k).toggleClass('selected', (_.filter(self.report_options[$(k).data('filter')], function(el){return ''+el.id == ''+$(k).data('id') && el.selected === true;})).length > 0);
        });
        $('.js_af_reports_one_choice_filter', this.$searchview_buttons).each(function (i, el) {
            var $el = $(el);
            var ids = $el.data('member-ids');
            $el.toggleClass('selected', _.every(self.report_options[$el.data('filter')], function (member) {
                // only look for actual ids, discard separators and section titles
                if(typeof member.id == 'number'){
                  // true if selected and member or non member and non selected
                  return member.selected === (ids.indexOf(member.id) > -1);
                } else {
                  return true;
                }
            }));
        });
        this.$searchview_buttons.find('.js_af_report_date_filter').click(function (event) {
            self.report_options.date.filter = $(this).data('filter');
            var error = false;
            if ($(this).data('filter') === 'custom') {
                var date_from = self.$searchview_buttons.find('.o_datepicker_input[name="date_from"]');
                var date_to = self.$searchview_buttons.find('.o_datepicker_input[name="date_to"]');
                if (date_from.length > 0){
                    error = date_from.val() === "" || date_to.val() === "";
                    self.report_options.date.date_from = field_utils.parse.date(date_from.val());
                    self.report_options.date.date_to = field_utils.parse.date(date_to.val());
                }
                else {
                    error = date_to.val() === "";
                    self.report_options.date.date_to = field_utils.parse.date(date_to.val());
                }
            }
            if (error) {
                new WarningDialog(self, {
                    title: _t("Odoo Warning"),
                }, {
                    message: _t("Date cannot be empty")
                }).open();
            } else {
                self.reload();
            }
        });

	  this.$searchview_buttons.find('.js_af_report_period_filter').click(function (event) {
            self.report_options.periods.filter = $(this).data('filter');
            if ($(this).data('filter') == 'period-custom') {
		        self.report_options.periods.period_length = parseInt($('#period-length').val());
		        self.report_options.periods.number_of_period = parseInt($('#number-of-period').val());
		        self.report_options.periods.date = field_utils.parse.date($('.datetimepicker-input').val());
			  if (self.report_options.periods.period_length < 1 || self.report_options.periods.number_of_period < 1)
				alert(_t("'Period Length' or 'Number of periods' value error"))
			  else
		        	self.reload();
            }

        });
	  $('#af-product-category', this.$searchview_buttons).change(function () {
		var product_categoy = $(this).val();
		$('#af-product-id option').remove();
		$("#af-product-id").append('<option value="all">All</option>');
		$.each( self.report_options.product_category, function(i,product_categories) {
			if (product_categoy == product_categories.id || product_categoy == '1'){
				$.each(product_categories.product, function(i,product) {
					$("#af-product-id").append('<option value=' + product.id  + '>' + product.name + '</option>');
				});
			}
		});
	  });

	  $('#warehouse-id', this.$searchview_buttons).change(function () {
		var warehouse_id = parseInt($('#warehouse-id').val());
		$('#location-id option').remove();
		$("#location-id").append('<option value="all">All</option>');
		$.each( self.report_options.locations, function(i,location) {
			if (warehouse_id == parseInt(location['warehouse_id'])){
				$("#location-id").append('<option value=' + location['id']  + '>' + location['name'] + '</option>');
			}
		});
	  });

	  this.$searchview_buttons.find('.js_af_report_product_filter').click(function (event) {
	        self.report_options.current_product.product_category_id = parseInt($('#af-product-category').val());
	        self.report_options.current_product.product_id = parseInt($('#af-product-id').val());
	        self.reload();
        });
	  this.$searchview_buttons.find('.af_report_warehouse_location').click(function (event) {
	        self.report_options.current_warehouse_location.warehouse_id = parseInt($('#warehouse-id').val());
	        self.report_options.current_warehouse_location.location_id = parseInt($('#location-id').val());
	        self.reload();
        });
        $('.js_af_report_choice_filter', this.$searchview_buttons).click(function () {
            var option_value = $(this).data('filter');
            var option_member_ids = $(this).data('member-ids') || [];
            var option_id = $(this).data('id');
            var is_selected = $(this).hasClass('selected');

            _.each(self.report_options[option_value], function (el) {
                // if group was selected, we want to uncheck all
                el.selected = !is_selected && (option_member_ids.indexOf(Number(el.id)) > -1);
            });
            _.filter(self.report_options[option_value], function(el) {
                if (''+el.id == ''+option_id){
                    if (el.selected === undefined || el.selected === null)
                        {
                            el.selected = false;
                        }
                    el.selected = !el.selected

                } else if (option_value === 'ir_filters') {
                    el.selected = false;
                }
                return el;
            });

            self.reload();
        });


    },
    format_date: function(moment_date) {
        var date_format = 'YYYY-MM-DD';
        return moment_date.format(date_format);
    },
    renderButtons: function() {
        var self = this;
        this.$buttons = $(QWeb.render("toStockAgeReport.buttons", {buttons: this.buttons}));
        // bind actions
        _.each(this.$buttons.siblings('button'), function(el) {
            $(el).click(function() {
                self.$buttons.attr('disabled', true);
                return self._rpc({
                        model: self.report_model,
                        method: $(el).attr('action'),
                        args: [self.financial_id, self.report_options],
                        context: self.odoo_context,
                    })
                    .then(function(result){
                        var doActionProm = self.do_action(result);
                        self.$buttons.attr('disabled', false);
                        return doActionProm;
                    })
                    .guardedCatch(function() {
                        self.$buttons.attr('disabled', false);
                    });
            });
        });
        return this.$buttons;
    },

});

core.action_registry.add('af_stock_age_report', stockReportsWidget);

return stockReportsWidget;

});
