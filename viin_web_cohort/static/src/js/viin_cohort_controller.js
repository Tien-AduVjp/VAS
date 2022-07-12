odoo.define('viin_web_cohort.ViinCohortController', function (require) {
    'use strict';

    var AbstractController = require('web.AbstractController');
    var session = require('web.session');
    var config = require('web.config');
    var framework = require('web.framework');

    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    var ViinCohortController = AbstractController.extend({

        custom_events: Object.assign({}, AbstractController.prototype.custom_events, {
            'cell_clicked': '_onCellClicked',
        }),

        /**
         * @override
         */
        init: function (parent, model, renderer, params) {
            this._super(...arguments);
            this.title = params.title;
            this.measures = params.measures;
            this.intervals = params.intervals;
            this.views = params.views;
            this.timeline = params.timeline;
            this.startDateString = params.startDateString;
            this.stopDateString = params.stopDateString;
        },

        // Public method

        /**
         * @override
         */
        renderButtons: function ($node) {
            if ($node.length > 0) {
                this.$buttons = $(qweb.render('ViinCohortView.buttons', {
                    measures: _.sortBy(_.pairs(this.measures), measure => measure[1].toLowerCase()),
                    intervals: this.intervals,
                    isMobile: config.device.isMobile
                })).appendTo($node);
                this.$measureList = this.$buttons.find('.viin_cohort_measures_list');
                this._updateCPButtons();
                this.$buttons.on('click', '.viin_cohort_btn', this._onButtonClick.bind(this));
            }
        },

        /**
         * @override
         */
        getOwnedQueryParams: function () {
            const state = this.model.get();
            return {
                context: {
                    cohort_measure: state.measure,
                    cohort_interval: state.interval,
                }
            };
        },

        // Private method

        /**
         * @override
         */
        _update: function () {
            this._updateCPButtons();
            return this._super(...arguments);
        },

        _downloadExcelReport: function () {
            var data = this.model.get();
            data = Object.assign({}, data, {
                title: this.title,
                measure_string: this.measures[data.measure] || _t('Count'),
                interval_string: this.intervals[data.interval].toString(),
                timeline: this.timeline,
                start_date_string: this.startDateString,
                stop_date_string: this.stopDateString,
            });
            framework.blockUI();
            session.get_file({
                url: '/web/viin_cohort/export',
                data: {data: JSON.stringify(data)},
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
        },

        /**
         * Match the display of control panel buttons with current state
         */
        _updateCPButtons: function () {
            if (!this.$buttons) {
                return;
            }
            var state = this.model.get();

            var empty = !state.report.rows.length && (!state.comparisonReport || !state.comparisonReport.rows.length);
            this.$buttons.find('.viin_cohort_download_xls').toggleClass('d-none', empty);

            var cohortIntervalBtn = `.viin_cohort_interval_button[data-interval=${state.interval}]`;
            if (config.device.isMobile) {
                var $cohortIntervalBtnActive = this.$buttons.find(cohortIntervalBtn);
                this.$buttons.find('.dropdown_cohort_content').text($cohortIntervalBtnActive.text());
            }
            this.$buttons.find('.viin_cohort_interval_button').removeClass('active');
            this.$buttons.find(cohortIntervalBtn).addClass('active');
            _.each(this.$measureList.find('.dropdown-item'), measureItem => {
                const $measureItem = $(measureItem);
                $measureItem.toggleClass('selected', $measureItem.data('field') === state.measure);
            });
        },

        // Handlers

        /**
         * Handle click event on a button from the cohort view.
         */
        _onButtonClick: function (e) {
            var $button = $(e.currentTarget);
            if ($button.hasClass('viin_cohort_interval_button')) {
                this.update({interval: $button.data('interval')});
            } else if ($button.hasClass('viin_cohort_download_xls')) {
                this._downloadExcelReport();
            } else if ($button.closest('.viin_cohort_measures_list').length) {
                e.preventDefault();
                e.stopPropagation();
                this.update({measure: $button.data('field')});
            }
        },

        _doActionViewDetail: function (domain) {
            const action = {
                name: this.title,
                type: 'ir.actions.act_window',
                res_model: this.modelName,
                views: this.views,
                domain: domain,
            };
            this.do_action(action);
        },
        /**
         * Open corresponding view when clicked on a cohort cell
         */
        _onCellClicked: function (e) {
            this._doActionViewDetail(e.data.domain);
        },
    });

    return ViinCohortController;

});
