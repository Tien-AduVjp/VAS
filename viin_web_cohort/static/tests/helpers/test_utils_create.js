odoo.define('viin_web_cohort.test_utils_create', function (require) {
"use strict";

/**
 * Create Test Utils
 *
 * This module defines various utility functions to help creating mock widgets
 *
 * Note that all methods defined in this module are exported in the main
 * testUtils file.
 */
var concurrency = require('web.concurrency');
var dom = require('web.dom');
var testUtilsMock = require('viin_web_cohort.test_utils_mock');
var Widget = require('web.Widget');
var testUtilsCreate = require('web.test_utils_create');


/**
 * Similar as createView, but specific for viin cohort views. Some viin cohort
 * tests need to trigger positional clicks on the DOM produced by viin cohort.
 * Those tests must use this helper with option positionalClicks set to true.
 * This will move the rendered viin cohort to the body (required to do positional
 * clicks).
 *
 * @param {Object} params see @createView
 * @param {Object} [options]
 * @param {boolean} [options.positionalClicks=false]
 * @returns {Promise<ViinCohortController>}
 */
async function createViinCohortView(params, options) {
    var viin_cohort = await testUtilsCreate.createView(params);
    if (!options || !options.positionalClicks) {
        return viin_cohort;
    }
    var $view = $('#qunit-fixture').contents();
    $view.prependTo('body');
    var destroy = viin_cohort.destroy;
    viin_cohort.destroy = function () {
        $view.remove();
        destroy();
    };
    await concurrency.delay(0);
    return viin_cohort;
}

testUtilsCreate.createViinCohortView = createViinCohortView;
return testUtilsCreate;

});
