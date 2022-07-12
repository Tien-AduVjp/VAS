odoo.define('web.ControlChartModel', function (require) {
    var GraphModel = require('web.GraphModel');

    return GraphModel.extend({
        load: function (params) {
            this.rangeFields = params.rangeFields;

            return this._super.apply(this, arguments);
        },

        /**
         * Fetch and process graph data.  It is basically a(some) read_group(s)
         * with correct fields for each domain.  We have to do some light processing
         * to separate date groups in the field list, because they can be defined
         * with an aggregation function, such as my_date:week.
         *
         * @override
         * @private
         * @returns {Promise}
         */
        _loadGraph: function () {
            var self = this;
            this.chart.dataPoints = [];
            var groupBy = this.chart.processedGroupBy;
            var fields = _.map(groupBy, function (groupBy) {
                return groupBy.split(':')[0];
            });

            //Add rangeFields to fields to load data from database
            fields = [...new Set(fields.concat(this.rangeFields))];

            if (this.chart.measure !== '__count__') {
                if (this.fields[this.chart.measure].type === 'many2one') {
                    fields = fields.concat(this.chart.measure + ":count_distinct");
                } else {
                    fields = fields.concat(this.chart.measure);
                }
            }

            var context = _.extend({fill_temporal: true}, this.chart.context);
            var defs = [];

            this.chart.domains.forEach(function (domain, originIndex) {
                defs.push(self._rpc({
                    model: self.modelName,
                    method: 'read_group',
                    context: context,
                    domain: domain,
                    fields: fields,
                    groupBy: groupBy,
                    lazy: false,
                }).then(self._processData.bind(self, originIndex)));
            });
            return Promise.all(defs);
        },

        /**
         * Since read_group is insane and returns its result on different keys
         * depending of some input, we have to normalize the result.
         * Each group coming from the read_group produces a dataPoint
         *
         * @todo This is not good for race conditions.  The processing should get
         *  the object this.chart in argument, or an array or something. We want to
         *  avoid writing on a this.chart object modified by a subsequent read_group
         *
         * @override
         * @private
         * @param {number} originIndex
         * @param {any} rawData result from the read_group
         */
        _processData: function (originIndex, rawData) {
            var self = this;
            var isCount = this.chart.measure === '__count__';
            var labels;

            function getLabels(dataPt) {
                return self.chart.processedGroupBy.map(function (field) {
                    return self._sanitizeValue(dataPt[field], field.split(":")[0]);
                });
            }

            rawData.forEach(function (dataPt) {
                labels = getLabels(dataPt);
                var count = dataPt.__count || dataPt[self.chart.processedGroupBy[0] + '_count'] || 0;
                var value = isCount ? count : dataPt[self.chart.measure];
                if (value instanceof Array) {
                    // when a many2one field is used as a measure AND as a grouped
                    // field, bad things happen.  The server will only return the
                    // grouped value and will not aggregate it.  Since there is a
                    // name clash, we are then in the situation where this value is
                    // an array.  Fortunately, if we group by a field, then we can
                    // say for certain that the group contains exactly one distinct
                    // value for that field.
                    value = 1;
                }

                //add range point
                if (self.rangeFields)
                    self.rangeFields.forEach(function (rangeField) {
                        let label = self.fields[rangeField].string;
                        self.chart.dataPoints.push({
                            isRange: true,
                            resId: dataPt[self.chart.groupBy[0]] instanceof Array ? dataPt[self.chart.groupBy[0]][0] : -1,
                            count: count,
                            value: dataPt[rangeField],
                            labels: [labels[0], label],
                            originIndex: originIndex,
                        });
                    });

                self.chart.dataPoints.push({
                    resId: dataPt[self.chart.groupBy[0]] instanceof Array ? dataPt[self.chart.groupBy[0]][0] : -1,
                    count: count,
                    value: value,
                    labels: labels,
                    originIndex: originIndex,
                });
            });
        },
    });
})
