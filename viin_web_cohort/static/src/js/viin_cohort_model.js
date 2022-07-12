odoo.define('viin_web_cohort.ViinCohortModel', function (require) {
    'use strict';

    var AbstractModel = require('web.AbstractModel');

    var ViinCohortModel = AbstractModel.extend({

        // Public Methods

        /**
         * @override
         */
        get: function () {
            return this.data;
        },

        /**
         * @override
         */
        load: function (params) {
            this.modelName = params.modelName;
            this.measure = params.measure;
            this.interval = params.interval;
            this.startDate = params.startDate;
            this.stopDate = params.stopDate;
            this.domain = params.domain;
            this.mode = params.mode;
            this.timeline = params.timeline;
            this.timeRange = params.timeRange || [];
            this.comparison = params.comparison;
            this.comparisonTimeRange = params.comparisonTimeRange || [];
            this.context = params.context;
            this.data = {
                measure: this.measure,
                interval: this.interval,
            };
            return this._loadCohortData();
        },

        reload: function (handle, params) {
            if (params.context !== undefined) {
                this.timeRange = [];
                this.comparisonTimeRange = [];
                this.comparison = false;
                var timeRangeMenuData = params.context.timeRangeMenuData;
                if (timeRangeMenuData) {
                    this.timeRange = timeRangeMenuData.timeRange || [];
                    this.comparisonTimeRange = timeRangeMenuData.comparisonTimeRange || [];
                    this.comparison = this.comparisonTimeRange.length > 0;
                }
            }
            if ('measure' in params) {
                this.data.measure = params.measure;
            }
            if ('interval' in params) {
                this.data.interval = params.interval;
            }
            if ('domain' in params) {
                this.domain = params.domain;
            }
            return this._loadCohortData();
        },

        // Private Methods

        /**
         * Get Cohort Data.
         */

        _getCohortDataByDomain: function(domain) {
            return this._rpc({
                route: '/web/viin_cohort/get_data',
                params: {
                    model_name: this.modelName,
                    measure: this.data.measure,
                    interval: this.data.interval,
                    mode: this.mode,
                    timeline: this.timeline,
                    start_date: this.startDate,
                    stop_date: this.stopDate,
                    domain: domain,
                    ctx: this.context
                }
            });
        },

        _loadCohortData: function () {
            const self = this;
            var defs = [this._getCohortDataByDomain(this.domain.concat(this.timeRange))];
            if (this.comparison) {
                defs.push(this._getCohortDataByDomain(this.domain.concat(this.comparisonTimeRange)));
            }
            return Promise.all(defs).then(function () {
                let datas = arguments[0].slice();
                self.data.report = datas[0];
                self.data.comparisonReport = self.comparison ? datas[1] : undefined;
            });
        },
    });

    return ViinCohortModel;

});
