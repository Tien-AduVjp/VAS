odoo.define('viin_web_dashboard.ViinDashboardModel', function (require) {
    "use strict";

    var BasicModel = require('web.BasicModel');
    var Domain = require('web.Domain');
    var pyUtils = require('web.py_utils');

    var dataComparisonUtils = require('web.dataComparisonUtils');
    var computeVariation = dataComparisonUtils.computeVariation;

    /**
     * The ViinDashboardModel model is responsible for fetching and processing data from the
     * server.
     */
    var ViinDashboardModel = BasicModel.extend({

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

    	/**
         * @override
         */
        get: function () {
            var record = this._super.apply(this, arguments);

            record = this._copyDataPointValues(this.dataPoint, record);
            return record;
        },

    	/**
         * @override
         */
        load: async function (params) {
            var self = this;
            params.type = 'record';
            params.range = [];
            params.comparisonRange = [];
            params.comparison = false;
            params.variationData = {};
            params.comparisonData = {};
            params.timeRanges = {};
            this.loadParams = params;

            params.type = 'record';
            this.dataPoint = this._makeDataPoint(params);
            return this._load(this.dataPoint).then(() => self.dataPoint.id);
        },

        /**
         * @override
         */
        reload: function (id, options) {
    		var self = this;
            options = options || {};
            if (options.domain !== undefined) {
                this.dataPoint.domain = options.domain;
            }
            if (options.context !== undefined) {
                this.dataPoint.range = [];
                this.dataPoint.comparisonRange = [];
                this.dataPoint.comparison = false;
                var timeRanges = options.timeRanges;
                if (timeRanges) {
                    this.dataPoint.range = timeRanges.range || [];
                    this.dataPoint.comparisonRange = timeRanges.comparisonRange || [];
                    this.dataPoint.comparison = this.dataPoint.comparisonRange.length > 0;
                    this.dataPoint.context.timeRanges = timeRanges;
                    this.dataPoint.timeRanges = timeRanges
                }
            }
            return this._load(this.dataPoint).then(() => self.dataPoint.id);
        },

        _copyDataPointValues: function (src, des) {
            des.formulas = src.formulas || {};
            des.aggregates = src.aggregates || [];
            des.comparisonRange = src.comparisonRange || [];
            des.comparison = src.comparison || src.comparisonRange.length > 0;
            des.comparisonData = src.comparisonData;
            des.variationData = src.variationData;
            des.range = src.range || [];
            des.timeRanges = src.timeRanges;
            return des;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Evaluates formulas of the given dataPoint with its values.
    	 * Method determines whether a number is a finite, legal number.
         */
        _evalFormulasOfDataPoint: function (dataPoint) {
            _.each(dataPoint.formulas, function (formula, formulaID) {
    			try {
                    dataPoint.data[formulaID] = pyUtils.py_eval(formula.value, {
                        record: dataPoint.data
                    });
                    if (!isFinite(dataPoint.data[formulaID])) {
                        dataPoint.data[formulaID] = NaN;
                    }
                } catch (e) {
                    dataPoint.data[formulaID] = NaN;
                }

                if (dataPoint.comparison) {
                    try {
                        dataPoint.comparisonData[formulaID] = pyUtils.py_eval(formula.value, {
                            record: dataPoint.comparisonData
                        });
                        if (!isFinite(dataPoint.comparisonData[formulaID])) {
                            dataPoint.comparisonData[formulaID] = NaN;
                        }
                    } catch (e) {
                        dataPoint.comparisonData[formulaID] = NaN;
                    }
                }
            });
        },

        /**
         * @override
         */
        _load: function (dataPoint) {
            var self = this;

            // Prepare mapping for domain
            var domainMapping = {};
            var fieldsInfo = dataPoint.fieldsInfo.viin_dashboard;
            _.each(dataPoint.aggregates, function (aggName) {
                var domain = fieldsInfo[aggName].domain;
    			if (domainMapping[domain]) {
    				domainMapping[domain].push(aggName);
    			} else {
    				domainMapping[domain] = [aggName];
    			}
            });

            var defs = [];
            _.each(domainMapping, function (aggNames, domain) {
                var fields = _.map(
                    aggNames,
                    // e.g. "delay_delivery:avg(delay)", "cycle_time_delivery:avg(cycle_time)",...
                    (aggName) => aggName + ':' + fieldsInfo[aggName].group_operator + '(' + fieldsInfo[aggName].field + ')'
                    );

                defs.push(self._readGroup({
                    domain: self._prepareReadGroupDomain(domain, self.dataPoint.comparisonRange),
                    fields: fields,
                }).then((result) => _.extend(self.dataPoint.data, _.pick(result, aggNames))));

                if (dataPoint.comparison) {
                    defs.push(self._readGroup({
                        domain: self._prepareReadGroupDomain(domain, self.dataPoint.comparisonRange),
                        fields: fields,
                    }).then(function(result) {
                        self.dataPoint.comparisonData = self.dataPoint.comparisonData ? self.dataPoint.comparisonData : {}
                         _.extend(self.dataPoint.comparisonData, _.pick(result, aggNames))
                    }));
                }
            });

            return Promise.all(defs).then(function () {
                self._evalFormulasOfDataPoint(dataPoint);

    			dataPoint.comparisonData = {};
    			dataPoint.variationData = {};
                if (dataPoint.comparison) {
                    for (let d in dataPoint.data) {
                        dataPoint.variationData[d] = computeVariation(dataPoint.data[d], dataPoint.comparisonData[d]);
                    }
                }
                return dataPoint.id;
            });
        },

        /**
         * @override
         */
        _makeDataPoint: function (params) {
            var dataPoint = this._super.apply(this, arguments);

            dataPoint = this._copyDataPointValues(params, dataPoint);
            return dataPoint;
        },

        _prepareReadGroupDomain: function (range, aggDomain) {
            var rangeDomain = Domain.prototype.normalizeArray(new Domain(range).toArray());
            return Domain.prototype.normalizeArray(this.dataPoint.domain)
                .concat(aggDomain)
                .concat(rangeDomain);
        },

        _readGroup: function (args) {
            var readGroupArgs = _.extend({
                model: this.dataPoint.model,
                method: 'read_group',
                context: this.dataPoint.getContext(),
                groupBy: [],
                orderBy: [],
                lazy: true,
            }, args);
            return this._rpc(readGroupArgs).then((result) => _.mapObject(result[0], (res) => res || 0));
        }
    });

    return ViinDashboardModel;

});
