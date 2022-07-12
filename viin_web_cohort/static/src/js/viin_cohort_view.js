odoo.define('viin_web_cohort.ViinCohortView', function (require) {
    'use strict';

    var AbstractView = require('web.AbstractView');
    var ViinCohortModel = require('viin_web_cohort.ViinCohortModel');
    var ViinCohortRenderer = require('viin_web_cohort.ViinCohortRenderer');
    var ViinCohortController = require('viin_web_cohort.ViinCohortController');
    var view_registry = require('web.view_registry');

    var core = require('web.core');
    var _t = core._t;
    var _lt = core._lt;

    const intervalObj = {
        day: _lt('Day'),
        week: _lt('Week'),
        month: _lt('Month'),
        year: _lt('Year'),
    };

    var ViinCohortView = AbstractView.extend({
        display_name: _lt('Cohort'),
        icon: 'fa-signal',
        viewType: 'viin_cohort',
        searchMenuTypes: ['filter', 'timeRange', 'favorite'],
        config: Object.assign({}, AbstractView.prototype.config, {
            Model: ViinCohortModel,
            Renderer: ViinCohortRenderer,
            Controller: ViinCohortController,
        }),

        /**
         * @override
         */
        init: function (viewInfo, params) {
            this._super(...arguments);
            var attrs = this.arch.attrs;
            if (!attrs.start_date || !attrs.stop_date) {
                throw new Error(_lt('start_date or stop_date attribute has not been defined.'));
            }
            var measureObj = {};
            Object.entries(this.fields).forEach(fields => {
                const [fieldName, fieldValue] = fields;
                if (fieldValue.store === true && fieldName !== 'id' && ['integer', 'float', 'monetary'].includes(fieldValue.type)) {
                    measureObj[fieldName] = fieldValue.string;
                }
            });
            this.rendererParams.measures = Object.assign({}, measureObj, {__count__: _t('Count')});
            this.rendererParams.intervals = intervalObj;
            this.controllerParams.measures = measureObj;
            this.controllerParams.intervals = intervalObj;
            this.controllerParams.title = params.title || attrs.string || _t('Untitled');

            function _findView(views, viewType) {
                if (views === undefined) {
                    return [false, viewType];
                }
                const contextViewId = viewType === 'list' ? views.context.list_view_id : views.context.form_view_id;
                const viewResult = _.findWhere(views.views, {type: viewType});
                const viewId = contextViewId || (viewResult ? viewResult.viewID : false);
                return [viewId, viewType];
            }

            this.controllerParams.views = [_findView(params.action, 'list'), _findView(params.action, 'form')];

        },

        /**
         * @override
         */
        _updateMVCParams: function () {
            this._super(...arguments);
            var context = this.loadParams.context;
            var attrs = this.arch.attrs;
            // Load params
            this.loadParams.mode = context.cohort_mode || attrs.mode || 'retention';
            this.loadParams.timeline = context.cohort_timeline || attrs.timeline || 'forward';
            this.loadParams.startDate = context.cohort_start_date || attrs.start_date;
            this.loadParams.stopDate = context.cohort_stop_date || attrs.stop_date;
            this.loadParams.measure = context.cohort_measure || attrs.measure || '__count__';
            this.loadParams.interval = context.cohort_interval || attrs.interval || 'day';
            // Renderer params
            this.rendererParams.mode = this.loadParams.mode;
            this.rendererParams.timeline = this.loadParams.timeline;
            this.rendererParams.startDateString = this.fields[this.loadParams.startDate].string;
            this.rendererParams.stopDateString = this.fields[this.loadParams.stopDate].string;
            // Controller params
            this.controllerParams.startDateString = this.rendererParams.startDateString;
            this.controllerParams.stopDateString = this.rendererParams.stopDateString;
            this.controllerParams.timeline = this.rendererParams.timeline;
        },
    });

    view_registry.add('viin_cohort', ViinCohortView);

    return ViinCohortView;

});
