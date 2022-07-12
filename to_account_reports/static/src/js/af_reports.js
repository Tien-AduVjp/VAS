odoo.define('to_account_reports.af_report_generic', function (require) {
'use strict';

var core = require('web.core');
var Context = require('web.Context');
var AbstractAction = require('web.AbstractAction');

var field_utils = require('web.field_utils');

var Dialog = require('web.Dialog');
var datepicker = require('web.datepicker');
var session = require('web.session');

var CrashManager = require('web.CrashManager');
var WarningDialog = CrashManager.WarningDialog;

var Many2ManyFilters = require('to_account_reports.AFFilters');

var _t = core._t;
var QWeb = core.qweb;

var ARWidget = AbstractAction.extend({
    hasControlPanel: true,

    events: {
        'input .o_af_reports_filter_input': 'filter_accounts',
        'click .o_af_reports_summary': 'edit_report_summary',
        'click .js_af_report_save_summary': 'save_report_summary',
        'click .o_af_reports_footnote_icons': 'delete_fn',

		'click [action]': 'trigger_action',

        'click .o_af_reports_load_more span': 'load_more',
        'click .js_af_reports_add_footnote': 'add_edit_fn',
        'click .js_af_report_foldable': 'toggle_fold_unfold',
    },

    custom_events: {
    	'value_changed': function(ev) {
		 	var self = this;
		 	self.rp_options.analytic_accounts = ev.data.analytic_accounts;
		 	self.rp_options.analytic_tags = ev.data.analytic_tags;
			self.rp_options.accounts = ev.data.accounts;
			self.rp_options.partners = ev.data.partners;
			self.rp_options.partner_ids = ev.data.partner_ids;
         	self.rp_options.partner_categories = ev.data.partner_categories;
         	return self.reload_report().then(function () {
				self.$sv_buttons.find('.account_analytic_filter').click();
     			self.$sv_buttons.find('.partners_filter').click();
				self.$sv_buttons.find('.accounts_filter').click();
 			});
 		},
    },

    init: function(parent, action) {
        this.actionManager = parent;
        this.rp_model = action.context.model;
        if (this.rp_model === undefined) {
            this.rp_model = 'account.report';
        }
        this.financial_id = false;
        if (action.context.id) {
            this.financial_id = action.context.id;
        }
        this.odoo_context = action.context;
        this.rp_options = action.options || false;
        this.ignore_session = action.ignore_session;
        if ((action.ignore_session === 'read' || action.ignore_session === 'both') !== true) {
            var persist_key = 'report:'+this.rp_model+':'+this.financial_id+':'+session.company_id;
            this.rp_options = JSON.parse(sessionStorage.getItem(persist_key)) || this.rp_options;
        }
        return this._super(...arguments);
    },
    start: function() {
        var self = this;
        var extra_info = this._rpc({
                model: self.rp_model,
                method: 'get_rp_informations',
                args: [self.financial_id, self.rp_options],
                context: self.odoo_context,
            })
            .then(function(result){
                return self.parse_rp_informations(result);
            });
        return Promise.all([extra_info, this._super.apply(this, arguments)]).then(function() {
            self.render();
        });
    },
    persist_options: function() {
        if ((this.ignore_session === 'write' || this.ignore_session === 'both') !== true) {
            var persist_key = 'report:'+this.rp_model+':'+this.financial_id+':'+session.company_id;
            sessionStorage.setItem(persist_key, JSON.stringify(this.rp_options));
        }
    },
	parse_rp_informations: function(values) {
        this.rp_options = values.options;
        this.odoo_context = values.context;
        this.report_manager_id = values.report_manager_id;
        this.footnotes = values.footnotes;
        this.buttons = values.buttons;

        this.main_html = values.main_html;
        this.$sv_buttons = $(values.searchview_html);
        this.persist_options();
    },
    do_show: function() {
        this._super(...arguments);
        this.update_c_p();
    },
    update_c_p: function() {
        if (!this.$buttons) {
            this.renderBtns();
        }
        var status = {
            cp_content: {
                $buttons: this.$buttons,
                $searchview_buttons: this.$sv_buttons,
                $pager: this.$pager,
                $searchview: this.$searchview,
            },
        };
        return this.updateControlPanel(status, {clear: true});
    },
    reload_report: function() {
        var self = this;
        return this._rpc({
                model: this.rp_model,
                method: 'get_rp_informations',
                args: [self.financial_id, self.rp_options],
                context: self.odoo_context,
            })
            .then(function(result){
                self.parse_rp_informations(result);
                return self.render();
            });
    },
    render: function() {
        var self = this;
        this.render_tmp();
        this.render_fns();
        this.render_sv_buttons();
        this.update_c_p();
        this.$('.js_af_report_foldable').each(function() {
            if(!$(this).data('unfolded')) {
                self.fold($(this));
            }
        });
    },
    render_tmp: function() {
        this.$('.o_content').html(this.main_html);
        this.$('.o_content').find('.o_af_reports_summary_edit').hide();
        this.$('[data-toggle="tooltip"]').tooltip();
        this._add_rp_line_classes();
    },
    _add_rp_line_classes: function() {
        var el = this.$el[0];
        var report_lines = el.getElementsByClassName('o_af_report_line');
        for (var l=0; l < report_lines.length; l++) {
            var line = report_lines[l];
            var unfolded = line.dataset.unfolded;
            if (unfolded === 'True') {
                line.parentNode.classList.add('o_js_af_report_parent_row_unfolded');
            }
        }
        this.$('tr[data-parent-id]').addClass('o_js_af_report_inner_row');
     },
    filter_accounts: function(e) {
        var self = this;
        var query = e.target.value.trim().toLowerCase();
        this.filterOn = false;
        this.$('.o_af_reports_level2').each(function(index, el) {
            var $accountReportLineFoldable = $(el);
            var line_id = $accountReportLineFoldable.find('.o_af_report_line').data('id');
            var $childs = self.$('tr[data-parent-id="'+line_id+'"]');
            var lineText = $accountReportLineFoldable.find('.af_report_line_name')
                .contents().get(0).nodeValue
                .trim();

            var queryFound = lineText.split(' ').some(function (str) {
                return str.toLowerCase().startsWith(query);
            });

            $accountReportLineFoldable.toggleClass('o_af_reports_filtered_lines', !queryFound);
            $childs.toggleClass('o_af_reports_filtered_lines', !queryFound);

            if (!queryFound) {
                self.filterOn = true;
            }
        });
        if (this.filterOn) {
            this.$('.o_af_reports_level1.total').hide();
        }
        else {
            this.$('.o_af_reports_level1.total').show();
        }
        this.rp_options['filter_accounts'] = query;
        this.render_fns();
    },
    selected_column: function(e) {
        var self = this;
        if (self.rp_options.selected_column !== undefined) {
            var col_number = Array.prototype.indexOf.call(e.currentTarget.parentElement.children, e.currentTarget) + 1;
            if (self.rp_options.selected_column && self.rp_options.selected_column == col_number) {
                self.rp_options.selected_column = -col_number;
            } else {
                self.rp_options.selected_column = col_number;
            }
            self.reload_report()
        }
    },
    render_sv_buttons: function() {
        var self = this;
        var $datepickers = this.$sv_buttons.find('.js_af_report_datetimepicker');
        var options = {
            locale : moment.locale(),
            format : 'L',
            icons: {
                date: "fa fa-calendar",
            },
        };

        _.each(this.$sv_buttons.find('.js_format_date'), function(dt) {
            var date_value = $(dt).html();
            $(dt).html((new moment(date_value)).format('ll'));
        });

        _.each(self.rp_options, function(k) {
            if (k!== null && k.filter !== undefined) {
                self.$sv_buttons.find('[data-filter="'+k.filter+'"]').addClass('selected');
            }
        });

        _.each(this.$sv_buttons.find('.js_af_report_bool_filter'), function(k) {
            $(k).toggleClass('selected', self.rp_options[$(k).data('filter')]);
        });

        _.each(this.$sv_buttons.find('.js_af_report_choice_filter'), function(k) {
            $(k).toggleClass('selected', (_.filter(self.rp_options[$(k).data('filter')], function(el){return ''+el.id == ''+$(k).data('id') && el.selected === true;})).length > 0);
        });

        $('.js_af_reports_one_choice_filter', this.$sv_buttons).each(function (i, el) {
            var $el = $(el);
            var ids = $el.data('member-ids');
            $el.toggleClass('selected', _.every(self.rp_options[$el.data('filter')], function (member) {
                if(typeof member.id == 'number'){
                  return member.selected === (ids.indexOf(member.id) > -1);
                } else {
                  return true;
                }
            }));
        });

        _.each(this.$sv_buttons.find('.js_af_reports_one_choice_filter'), function(k) {
            $(k).toggleClass('selected', ''+self.rp_options[$(k).data('filter')] === ''+$(k).data('id'));
        });

		$datepickers.each(function () {
            var name = $(this).find('input').attr('name');
            var val = $(this).data('default-value');
            $(this).datetimepicker(options);
            var date = new datepicker.DateWidget(options);
            date.replace($(this)).then(function () {
                date.$el.find('input').attr('name', name);
                if (val) {
                    date.setValue(moment(val));
                }
            });
        });

		this.$sv_buttons.find('.js_foldable_trigger').click(function (event) {
            $(this).toggleClass('o_closed_menu o_open_menu');
            self.$sv_buttons.find('.o_foldable_menu[data-filter="'+$(this).data('filter')+'"]').toggleClass('o_closed_menu');
        });

        this.$sv_buttons.find('.js_af_report_date_filter').click(function (event) {
            self.rp_options.date.filter = $(this).data('filter');
            var error = false;
            if ($(this).data('filter') === 'custom') {
                var date_from = self.$sv_buttons.find('.o_datepicker_input[name="date_from"]');
                var date_to = self.$sv_buttons.find('.o_datepicker_input[name="date_to"]');
                if (date_from.length > 0){
                    error = date_from.val() === "" || date_to.val() === "";
                    self.rp_options.date.date_from = field_utils.parse.date(date_from.val());
                    self.rp_options.date.date_to = field_utils.parse.date(date_to.val());
                }
                else {
                    error = date_to.val() === "";
                    self.rp_options.date.date_to = field_utils.parse.date(date_to.val());
                }
            }
            if (error) {
                new WarningDialog(self, {
                    title: _t("Odoo Warning"),
                }, {
                    message: _t("Date cannot be empty")
                }).open();
            } else {
                self.reload_report();
            }
        });

        this.$sv_buttons.find('.js_af_report_bool_filter').click(function (event) {
            var option_value = $(this).data('filter');
            self.rp_options[option_value] = !self.rp_options[option_value];
            if (option_value === 'unfold_all') {
                self.unfold_all(self.rp_options[option_value]);
            }
            self.reload_report();
        });

        this.$sv_buttons.find('.js_af_report_choice_filter').click(function (event) {
            var option_value = $(this).data('filter');
            var option_id = $(this).data('id');
            _.filter(self.rp_options[option_value], function(el) {
                if (''+el.id == ''+option_id){
					if (option_value === 'multi_company' && el.selected === true) {
						return;
					}
                    if (el.selected === undefined || el.selected === null){el.selected = false;}
                    el.selected = !el.selected;
                } else if (option_value === 'ir_filters' || option_value === 'multi_company'){
                    el.selected = false;
                }
                return el;
            });
            self.reload_report();
        });

        this.$sv_buttons.find('.js_af_reports_one_choice_filter').click(function (event) {
            self.rp_options[$(this).data('filter')] = $(this).data('id');
            self.reload_report();
        });

        this.$sv_buttons.find('.js_af_report_date_cmp_filter').click(function (event) {
            self.rp_options.comparison.filter = $(this).data('filter');
            var error = false;
            var number_period = $(this).parent().find('input[name="periods_number"]');
            self.rp_options.comparison.number_period = (number_period.length > 0) ? parseInt(number_period.val()) : 1;
            if ($(this).data('filter') === 'custom') {
                var date_from = self.$sv_buttons.find('.o_datepicker_input[name="date_from_cmp"]');
                var date_to = self.$sv_buttons.find('.o_datepicker_input[name="date_to_cmp"]');
                if (date_from.length > 0) {
                    error = date_from.val() === "" || date_to.val() === "";
                    self.rp_options.comparison.date_from = field_utils.parse.date(date_from.val());
                    self.rp_options.comparison.date_to = field_utils.parse.date(date_to.val());
                }
                else {
                    error = date_to.val() === "";
                    self.rp_options.comparison.date_to = field_utils.parse.date(date_to.val());
                }
            }
            if (error) {
                new WarningDialog(self, {
                    title: _t("Odoo Warning"),
                }, {
                    message: _t("Date cannot be empty")
                }).open();
            } else {
                self.reload_report();
            }
        });

        this.$sv_buttons.find('.js_af_reports_analytic_auto_complete').select2();
        if (self.rp_options.analytic) {
            self.$sv_buttons.find('[data-filter="analytic_accounts"]').select2("val", self.rp_options.analytic_accounts);
            self.$sv_buttons.find('[data-filter="analytic_tags"]').select2("val", self.rp_options.analytic_tags);
        }

        this.$sv_buttons.find('.js_af_reports_analytic_auto_complete').on('change', function(){
            self.rp_options.analytic_accounts = self.$sv_buttons.find('[data-filter="analytic_accounts"]').val();
            self.rp_options.analytic_tags = self.$sv_buttons.find('[data-filter="analytic_tags"]').val();
            return self.reload_report().then(function(){
                self.$sv_buttons.find('.account_analytic_filter').click();
            })
        });

		this.$sv_buttons.find('.js_af_reports_accounts_auto_complete').select2();
        if (self.rp_options.account_all) {
            self.$sv_buttons.find('[data-filter="accounts"]').select2("val", self.rp_options.accounts);
        }

        this.$sv_buttons.find('.js_af_reports_accounts_auto_complete').on('change', function(){
            self.rp_options.accounts = self.$sv_buttons.find('[data-filter="accounts"]').val();
            return self.reload_report().then(function(){
                self.$sv_buttons.find('.accounts_filter').click();
            })
        });

		this.$sv_buttons.find('.js_af_reports_partners_auto_complete').select2();
        if (self.rp_options.partner_all) {
            self.$sv_buttons.find('[data-filter="partners"]').select2("val", self.rp_options.partners);
        }

        this.$sv_buttons.find('.js_af_reports_partners_auto_complete').on('change', function(){
            self.rp_options.partners = self.$sv_buttons.find('[data-filter="partners"]').val();
            return self.reload_report().then(function(){
                self.$sv_buttons.find('.partners_filter').click();
            })
        });

        if (this.rp_options.partner) {
            if (!this.Many2ManyFilters) {
                var fields = {};
                if ('partner_ids' in this.rp_options) {
                    fields['partner_ids'] = {
                        label: _t('Partners'),
                        modelName: 'res.partner',
                        value: this.rp_options.partner_ids.map(Number),
                    };
                }
                if ('partner_categories' in this.rp_options) {
                    fields['partner_categories'] = {
                        label: _t('Tags'),
                        modelName: 'res.partner.category',
                        value: this.rp_options.partner_categories.map(Number),
                    };
                }
                if (!_.isEmpty(fields)) {
                    this.Many2ManyFilters = new Many2ManyFilters(this, fields);
                    this.Many2ManyFilters.appendTo(this.$sv_buttons.find('.js_account_partner_m2m'));
                }
            } else {
                this.$sv_buttons.find('.js_account_partner_m2m').append(this.Many2ManyFilters.$el);
            }
        }

        if (this.rp_options.analytic) {
            if (!this.Many2ManyFilters) {
                var fields = {};
                if (this.rp_options.analytic_accounts) {
                    fields['analytic_accounts'] = {
                        label: _t('Accounts'),
                        modelName: 'account.analytic.account',
                        value: this.rp_options.analytic_accounts.map(Number),
                    };
                }
                if (this.rp_options.analytic_tags) {
                    fields['analytic_tags'] = {
                        label: _t('Tags'),
                        modelName: 'account.analytic.tag',
                        value: this.rp_options.analytic_tags.map(Number),
                    };
                }
                if (!_.isEmpty(fields)) {
                    this.Many2ManyFilters = new Many2ManyFilters(this, fields);
                    this.Many2ManyFilters.appendTo(this.$sv_buttons.find('.js_account_analytic_m2m'));
                }
            } else {
                this.$sv_buttons.find('.js_account_analytic_m2m').append(this.Many2ManyFilters.$el);
            }
        }

		if (this.rp_options.account_all) {
            if (!this.Many2ManyFilters) {
                var fields = {};
                fields['accounts'] = {
                    label: _t('Accounts'),
                    modelName: 'account.account',
                    value: this.rp_options.accounts.map(Number),
                };
                if (!_.isEmpty(fields)) {
                    this.Many2ManyFilters = new Many2ManyFilters(this, fields);
                    this.Many2ManyFilters.appendTo(this.$sv_buttons.find('.js_accounts_m2m'));
                }
            } else {
                this.$sv_buttons.find('.js_accounts_m2m').append(this.Many2ManyFilters.$el);
            }
        }

		if (this.rp_options.partner_all) {
            if (!this.Many2ManyFilters) {
                var fields = {};
                fields['partners'] = {
                    label: _t('Partners'),
                    modelName: 'res.partner',
                    value: this.rp_options.partners.map(Number),
                };
                if (!_.isEmpty(fields)) {
                    this.Many2ManyFilters = new Many2ManyFilters(this, fields);
                    this.Many2ManyFilters.appendTo(this.$sv_buttons.find('.js_partners_m2m'));
                }
            } else {
                this.$sv_buttons.find('.js_partners_m2m').append(this.Many2ManyFilters.$el);
            }
        }
    },
    renderBtns: function() {
        var self = this;
        this.$buttons = $(QWeb.render("toAccountReports.buttons", {buttons: this.buttons}));
        _.each(this.$buttons.siblings('button'), function(el) {
            $(el).click(function() {
                self.$buttons.attr('disabled', true);
                return self._rpc({
                        model: self.rp_model,
                        method: $(el).attr('action'),
                        args: [self.financial_id, self.rp_options],
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
	format_date: function(date) {
        var date_format = 'YYYY-MM-DD';
        return date.format(date_format);
    },
    save_report_summary: function(e) {
        var self = this;
        var text = $(e.target).siblings().val().replace(/[ \t]+/g, ' ');
        return this._rpc({
                model: 'account.report.manager',
                method: 'write',
                args: [this.report_manager_id, {summary: text}],
                context: this.odoo_context,
            })
            .then(function(result){
                self.$el.find('.o_af_reports_summary_edit').hide();
                self.$el.find('.o_af_reports_summary').show();
                if (!text) {
                    var $content = $("<input type='text' class='o_input' name='summary'/>");
                    $content.attr('placeholder', _t('Click to add summary'));
                } else {
                    var $content = $('<span />').text(text).html(function (i, value) {
                        return value.replace(/\n/g, '<br>\n');
                    });
                }
                return $(e.target).parent().siblings('.o_af_reports_summary').find('> .o_af_report_summary').html($content);
            });
    },
	edit_report_summary: function(e) {
        var $textarea = $(e.target).parents('.o_af_reports_body').find('textarea[name="summary"]');
        var height = Math.max($(e.target).parents('.o_af_reports_body').find('.o_af_report_summary').height(), 100);
        var text = $textarea.val().replace(new RegExp('<br />', 'g'), '\n');
        $textarea.height(height);
        $textarea.val(text);
        $(e.target).parents('.o_af_reports_body').find('.o_af_reports_summary_edit').show();
        $(e.target).parents('.o_af_reports_body').find('.o_af_reports_summary').hide();
        $(e.target).parents('.o_af_reports_body').find('textarea[name="summary"]').focus();
    },
    render_fns: function() {
        var self = this;
        var $dom_footnotes = self.$el.find('.js_af_report_line_footnote:not(.folded)');
        $dom_footnotes.html('');
        var number = 1;
        var footnote_to_render = [];
        _.each($dom_footnotes, function(el) {
            if ($(el).parents('.o_af_reports_filtered_lines').length > 0) {
                return;
            }
            var line_id = $(el).data('id');
            var footnote = _.filter(self.footnotes, function(footnote) {return ''+footnote.line === ''+line_id;});
            if (footnote.length !== 0) {
                $(el).html('<sup><b class="o_af_reports_footnote_sup"><a href="#footnote'+number+'">'+number+'</a></b></sup>');
                footnote[0].number = number;
                number += 1;
                footnote_to_render.push(footnote[0]);
            }
        });
        return this._rpc({
                model: this.rp_model,
                method: 'get_html_footnotes',
                args: [self.financial_id, footnote_to_render],
                context: self.odoo_context,
            })
            .then(function(result){
                return self.$el.find('.js_af_report_footnotes').html(result);
            });
    },
    delete_fn: function(e) {
        var self = this;
        var footnote_id = $(e.target).parents('.footnote').data('id');
        return this._rpc({
                model: 'account.report.footnote',
                method: 'unlink',
                args: [footnote_id],
                context: this.odoo_context,
            })
            .then(function(result){
                self.footnotes = _.filter(self.footnotes, function(element) {
                    return element.id !== footnote_id;
                });
                return self.render_fns();
            });
    },
	add_edit_fn: function(e) {
        var self = this;
        var line_id = $(e.target).data('id');
        var existing_footnote = _.filter(self.footnotes, function(footnote) {
            return ''+footnote.line === ''+line_id;
        });
        var text = '';
        if (existing_footnote.length !== 0) {
            text = existing_footnote[0].text;
        }
        var $content = $(QWeb.render('toAccountReports.footnote_dialog', {text: text, line: line_id}));
        var save = function() {
            var footnote_text = $('.js_af_reports_footnote_note').val().replace(/[ \t]+/g, ' ');
            if (!footnote_text && existing_footnote.length === 0) {return;}
            if (existing_footnote.length !== 0) {
                if (!footnote_text) {
                    return self.$el.find('.footnote[data-id="'+existing_footnote[0].id+'"] .o_af_reports_footnote_icons').click();
                }
                return this._rpc({
                        model: 'account.report.footnote',
                        method: 'write',
                        args: [existing_footnote[0].id, {text: footnote_text}],
                        context: this.odoo_context,
                    })
                    .then(function(result){
                        _.each(self.footnotes, function(footnote) {
                            if (footnote.id === existing_footnote[0].id){
                                footnote.text = footnote_text;
                            }
                        });
                        return self.render_fns();
                    });
            }
            else {
                return this._rpc({
                        model: 'account.report.footnote',
                        method: 'create',
                        args: [{line: line_id, text: footnote_text, manager_id: self.report_manager_id}],
                        context: this.odoo_context,
                    })
                    .then(function(result){
                        self.footnotes.push({id: result, line: line_id, text: footnote_text});
                        return self.render_fns();
                    });
            }
        };
        new Dialog(this, {title: _t('Annotate'), size: 'medium', $content: $content, buttons: [{text: 'Save', classes: 'btn-primary', close: true, click: save}, {text: 'Cancel', close: true}]}).open();
    },
    toggle_fold_unfold: function(e) {
        var self = this;
        if ($(e.target).hasClass('caret') || $(e.target).parents('.o_af_reports_footnote_sup').length > 0){return;}
        e.stopPropagation();
        e.preventDefault();
        var line = $(e.target).parents('td');
        if (line.length === 0) {line = $(e.target);}
        var method = line.data('unfolded') === 'True' ? this.fold(line) : this.unfold(line);
        Promise.resolve(method).then(function() {
            self.render_fns();
            self.persist_options();
        });
    },
    fold: function(line) {
        var self = this;
        var line_id = line.data('id');
        line.find('.fa-caret-down').toggleClass('fa-caret-right fa-caret-down');
        line.toggleClass('folded');
        $(line).parent('tr').removeClass('o_js_af_report_parent_row_unfolded');
        var $lines_to_hide = this.$el.find('tr[data-parent-id="'+line_id+'"]');
        var index = self.rp_options.unfolded_lines.indexOf(line_id);
        if (index > -1) {
            self.rp_options.unfolded_lines.splice(index, 1);
        }
        if ($lines_to_hide.length > 0) {
            line.data('unfolded', 'False');
            $lines_to_hide.find('.js_af_report_line_footnote').addClass('folded');
            $lines_to_hide.hide();
            _.each($lines_to_hide, function(el){
                var child = $(el).find('[data-id]:first');
                if (child) {
                    self.fold(child);
                }
            })
        }
        return false;
    },
    unfold: function(line) {
        var self = this;
        var line_id = line.data('id');
        line.toggleClass('folded');
        self.rp_options.unfolded_lines.push(line_id);
        var $lines_in_dom = this.$el.find('tr[data-parent-id="'+line_id+'"]');
        if ($lines_in_dom.length > 0) {
            $lines_in_dom.find('.js_af_report_line_footnote').removeClass('folded');
            $lines_in_dom.show();
            line.find('.fa-caret-right').toggleClass('fa-caret-right fa-caret-down');
            line.data('unfolded', 'True');
            this._add_rp_line_classes();
            return true;
        }
        else {
            return this._rpc({
                    model: this.rp_model,
                    method: 'get_html',
                    args: [self.financial_id, self.rp_options, line.data('id')],
                    context: self.odoo_context,
                })
                .then(function(result){
                    $(line).parent('tr').replaceWith(result);
                    self._add_rp_line_classes();
                });
        }
    },
    load_more: function (ev) {
        var $line = $(ev.target).parents('td');
        var id = $line.data('id');
        var offset = $line.data('offset') || 0;
        var progress = $line.data('progress') || 0;
        var remaining = $line.data('remaining') || 0;
        var options = _.extend({}, this.rp_options, {lines_offset: offset, lines_progress: progress, lines_remaining: remaining});
        var self = this;
        this._rpc({
                model: this.rp_model,
                method: 'get_html',
                args: [this.financial_id, options, id],
                context: this.odoo_context,
            })
            .then(function (result){
                var $tr = $line.parents('.o_af_reports_load_more');
                $tr.after(result);
                $tr.remove();
                self._add_rp_line_classes();
            });
    },
    unfold_all: function(bool) {
        var self = this;
        var lines = this.$el.find('.js_af_report_foldable');
        self.rp_options.unfolded_lines = [];
        if (bool) {
            _.each(lines, function(el) {
                self.rp_options.unfolded_lines.push($(el).data('id'));
            });
        }
    },
    trigger_action: function(e) {
        e.stopPropagation();
        var self = this;
        var action = $(e.target).attr('action');
        var id = $(e.target).parents('td').data('id');
        var params = $(e.target).data();
        var context = new Context(this.odoo_context, params.actionContext || {}, {active_id: id});

        params = _.omit(params, 'actionContext');
        if (action) {
            return this._rpc({
                    model: this.rp_model,
                    method: action,
                    args: [this.financial_id, this.rp_options, params],
                    context: context.eval(),
                })
                .then(function(result){
                    return self.do_action(result);
                });
        }
    },
});

core.action_registry.add('af_report_generic', ARWidget);

return ARWidget;

});
