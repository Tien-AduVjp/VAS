odoo.define('web.ControlChartRenderer', function (require) {
    var GraphRenderer = require('web.GraphRenderer');

    return GraphRenderer.extend({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);

            this.rangeFields = params.rangeFields;
        },

        /**
         * Separate dataPoints coming from the read_group(s) into different datasets.
         * This function returns the parameters data and labels used to produce the charts.
         *
         * @private
         * @param {Object[]} dataPoints
         * @param {function} getLabel,
         * @param {function} getDatasetLabel, determines to which dataset belong a given data point
         * @param {function} [getDatasetDataLength], determines the initial section of the labels array
         *                    over which the datasets have to be completed. These sections only depend
         *                    on the datasets origins. Default is the constant function _ => labels.length.
         * @returns {Object} the parameter data used to instantiate the chart.
         */
        _prepareData: function (dataPoints) {
            var self = this;
            var labelMap = {};
            var labels = dataPoints.reduce(
                function (acc, dataPt) {
                    var label = self._getLabel(dataPt);
                    var labelKey = dataPt.resId + ':' + JSON.stringify(label);
                    var index = labelMap[labelKey];
                    if (index === undefined) {
                        labelMap[labelKey] = dataPt.labelIndex = acc.length;
                        acc.push(label);
                    } else {
                        dataPt.labelIndex = index;
                    }
                    return acc;
                },
                []
            );

            //add dataset range
            var newRangeDataset = function (datasetLabel, originIndex) {
                let data = new Array(self._getDatasetDataLength(originIndex, labels.length)).fill(0);
                return {
                    label: datasetLabel,
                    data: data,
                    originIndex: originIndex,
                    borderDash: [5, 5],
                    fill: false,
                };
            };

            var newDataset = function (datasetLabel, originIndex) {
                let data = new Array(self._getDatasetDataLength(originIndex, labels.length)).fill(0);
                return {
                    label: datasetLabel,
                    data: data,
                    originIndex: originIndex,
                };
            };

            // dataPoints --> datasets
            var datasets = _.values(dataPoints.reduce(
                function (acc, dataPt) {
                    var datasetLabel = self._getDatasetLabel(dataPt);
                    if (!(datasetLabel in acc)) {
                        if (dataPt['isRange']) {
                            acc[datasetLabel] = newRangeDataset(datasetLabel, dataPt.originIndex);
                        } else {
                            acc[datasetLabel] = newDataset(datasetLabel, dataPt.originIndex);
                        }
                    }
                    var labelIndex = dataPt.labelIndex;
                    acc[datasetLabel].data[labelIndex] = dataPt.value;
                    return acc;
                },
                {}
            ));

            // sort by origin
            datasets = datasets.sort(function (dataset1, dataset2) {
                return dataset1.originIndex - dataset2.originIndex;
            });

            return {
                datasets: datasets,
                labels: labels,
            };
        },
    });
})
