odoo.define('viin_web_cohort.ViinCohortRenderer', function (require) {
    'use strict';

    var AbstractRenderer = require('web.AbstractRenderer');
    var field_utils = require('web.field_utils');

    var core = require('web.core');
    var QWeb = core.qweb;

    var ViinCohortRenderer = AbstractRenderer.extend({
        className: 'viin_cohort_view',
        events: Object.assign({}, AbstractRenderer.prototype.events, {
            'click .viin_cohort_row': '_onRowClicked',
        }),

        /**
         * @override
         */
        init: function (parent, state, params) {
            this._super(...arguments);
            this.measures = params.measures;
            this.intervals = params.intervals;
            this.mode = params.mode;
            this.timeline = params.timeline;
            this.startDateString = params.startDateString;
            this.stopDateString = params.stopDateString;
            this.timeRangeLabel = params.timeRangeLabel;
            this.comparisonTimeRangeLabel = params.comparisonTimeRangeLabel;
        },

        /**
         * @override
         */
        updateState: function (state, params) {
            if (params.context !== undefined) {
                this.timeRangeLabel = undefined;
                this.comparisonTimeRangeLabel = undefined;
                var timeRangeMenuData = params.context.timeRangeMenuData;
                if (timeRangeMenuData) {
                    this.timeRangeLabel = timeRangeMenuData.timeRangeLabel;
                    this.comparisonTimeRangeLabel = timeRangeMenuData.comparisonTimeRangeLabel;
                }
            }
            return this._super(...arguments);
        },

        // Private method

        /**
         * @override
         */
        _render: function () {
            var self = this;
            this.$el.empty();
            // display No content helper if there are no data
            if (!this._hasContent()) {
                this.$el.append(QWeb.render('View.NoContentHelper'));
                return this._super(...arguments);
            }
            this.$el.append(QWeb.render('ViinCohortView', {
                formatFloat: this._formatFloat,
                formatPercentage: this._formatPercentage,
                comparisonReport: this.state.comparisonReport,
                interval: this.intervals[this.state.interval],
                timeline: this.timeline,
                report: this.state.report,
                mode: this.mode,
                measure: this.measures[this.state.measure],
                startDateString: this.startDateString,
                stopDateString: this.stopDateString,
                timeRangeLabel: this.timeRangeLabel,
                comparisonTimeRangeLabel: this.comparisonTimeRangeLabel,
            }));
            this.$('.viin_cohort_highlight.viin_cohort_cell_value').tooltip({
                title: function () {
                    return QWeb.render('ViinCohortView.tooltip', {
                        measure: self.measures[self.state.measure],
                        period: $(this).data('period'),
                        count: $(this).data('count'),
                    });
                },
            });
            return this._super(...arguments);
        },

        _hasContent: function () {
            return this.state.report.rows.length || (this.state.comparisonReport && this.state.comparisonReport.rows.length);
        },

        _formatFloat: function (value) {
            return field_utils.format.float(value, null, {digits: [69, 1]});
        },

        _formatPercentage: function (value) {
            return field_utils.format.percentage(value, null, {digits: [69, 2]});
        },

        // Handlers

        _onRowClicked: function (e) {
            var $currentRow = $(e.target);
            if (!$currentRow.hasClass('viin_cohort_cell_value')) {
                return;
            }
            var currentRowData = $(e.currentTarget).data();
            var currentRowIndex = currentRowData.row;
            var currentColIndex = $currentRow.data().col;
            var currentRow = currentRowData.type === 'data' ? this.state.report.rows[currentRowIndex] : this.state.comparisonReport.rows[currentRowIndex];
            var currentRowDomain = currentRow ? currentRow.domain : [];
            var currentCell = currentRow ? currentRow.columns[currentColIndex] : false;
            var currentCellDomain = currentCell ? currentCell.domain : [];
            var domain = [...currentRowDomain, ...currentCellDomain];
            if (currentCellDomain.length) {
                domain.unshift('&');
            }
            if (domain.length) {
                this.trigger_up('cell_clicked', {domain: domain});
            }
        },
    });

    return ViinCohortRenderer;

});
