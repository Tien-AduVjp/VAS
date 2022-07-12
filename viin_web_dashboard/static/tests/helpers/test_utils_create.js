odoo.define('viin_web_dashboard.test_utils_create', function(require) {
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
	var testUtilsMock = require('viin_web_dashboard.test_utils_mock');
	var Widget = require('web.Widget');
	var testUtilsCreate = require('web.test_utils_create');


	/**
	 * Similar as createView, but specific for viin dashboard views. Some viin dashboard
	 * tests need to trigger positional clicks on the DOM produced by viin dashboard.
	 * Those tests must use this helper with option positionalClicks set to true.
	 * This will move the rendered viin dashboard to the body (required to do positional
	 * clicks).
	 *
	 * @param {Object} params see @createView
	 * @param {Object} [options]
	 * @param {boolean} [options.positionalClicks=false]
	 * @returns {Promise<ViinDashboardController>}
	 */
	async function createViinDashboardView(params, options) {
		var viin_dashboard = await testUtilsCreate.createView(params);
		if (!options || !options.positionalClicks) {
			return viin_dashboard;
		}
		var $view = $('#qunit-fixture').contents();
		$view.prependTo('body');
		var destroy = viin_dashboard.destroy;
		viin_dashboard.destroy = function() {
			$view.remove();
			destroy();
		};
		await concurrency.delay(0);
		return viin_dashboard;
	}

	testUtilsCreate.createViinDashboardView = createViinDashboardView;
	return testUtilsCreate;

});
