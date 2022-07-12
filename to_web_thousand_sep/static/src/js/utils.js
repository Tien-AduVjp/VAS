odoo.define('to_web_thousand_sep.utils', function (require) {
    'use strict';

    var core = require('web.core');

    var formatNumber = function (value) {
        /**
         * Represent a number in language-sensitive format.
         * Example: 1000000 => 1,000,000
         *
         * @param value: a number to format
         * @return {string}
         */
        var thousandsSep = core._t.database.parameters.thousands_sep || ',';
        var decimalSep = core._t.database.parameters.decimal_point || '.';
        var str = String(value).trim();
        var sign = str.startsWith('-') ? '-' : '';
        // remove all characters except number and decimal separator
        str = str.replace(new RegExp('[^' + decimalSep + '\\d]', 'g'), '');
        // if the string starts with decimal separators, remove them
        str = str.replace(new RegExp('^\\' + decimalSep + '*'), '')
        // insert thousand separators
        str = str.replace(/\B(?=((\d{3})+(?!\d)))/g, thousandsSep);
        // remove invalid characters after the first decimal separator
        var splits = str.split(decimalSep);
        if (splits.length > 1) {
            str = splits[0] + decimalSep + splits[1].replace(new RegExp('\\' + thousandsSep, 'g'), '');
        }
        // restore sign
        str = sign + str;
        return str
    };

    /**
     * Same as formatNumber() but for a formula (new in Odoo 13).
     * Example: "= 1000 + 2000" will be formatted as "= 1,000 + 2,000"
     *
     * @param {string} formula
     * @return {string}
     */
    var formatFormula = function (formula) {
        if (!formula.startsWith('=')) {
            return formatNumber(formula);
        }
        var str = '';
        for (let v of formula.split(new RegExp(/([-+*/()^=\s])/g))) {
            if (!['+', '-', '*', '/', '(', ')', '^', '='].includes(v) && v.trim()) {
                v = formatNumber(v);
            }
            str += v;
        }
        return str;
    }

    var parseNumber = function (value) {
        /**
         * Get number value from its language-sensitive representation.
         * Example: 1,000,000 => 1000000
         *
         * @param {string} value: a string that represents a number
         * @return {number}
         */
        var thousandsSep = core._t.database.parameters.thousands_sep || ',';
        var decimalSep = core._t.database.parameters.decimal_point || '.';
        var str = value;
        // remove all thousands separators
        str = str.replace(new RegExp('\\' + thousandsSep, 'g'), '');
        // remove language-dependent decimal separator with the standard separator (.)
        str = str.replace(decimalSep, '.');
        return Number(str);
    }

    return {
        formatNumber: formatNumber,
        formatFormula: formatFormula,
        parseNumber: parseNumber
    }
})
