odoo.define('viin_hr_timesheet_timer.timesheet_timer', function(require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    var registry = require('web.field_registry');

    var CountupTimer = basic_fields.FieldDateTime.extend({

        init: function() {
            this._super.apply(this, arguments);
            this.timeGap = 0.0;
        },

        destroy: function() {
            this._super.apply(this, arguments);
            clearTimeout(this.timer);
        },

        willStart: function() {
            var self = this;
            if (self.value instanceof moment) {
                self.timeGap = (new Date() - self.value.toDate()) / (3600 * 1000);
            }
            return Promise.all([this._super.apply(this, arguments)]);
        },

        // every second add 1 to the duration
        _startTimeCounter: function() {
            var self = this;
            if (self.value instanceof moment) {
                this.timer = setTimeout(function() {
                    self.timeGap += 1 / 3600;
                    self._startTimeCounter();
                }, 1000);
                const hours = parseInt(self.timeGap);
                const floatMinutes = (self.timeGap - hours) * 60;
                const minutes = parseInt(floatMinutes);
                const seconds = parseInt((floatMinutes - minutes) * 60);
                const text = _.str.sprintf("%02d:%02d:%02d", hours, minutes, seconds);
                const $timeText = $('<span>', { text });
                this.$el.empty().append($timeText);
            } else {
                clearTimeout(this.timer);
            }
        },

        _render: function() {
            this._startTimeCounter();
        },
    });

    registry.add('countup_timer', CountupTimer);
});
