odoo.define('to_sale_subscription.sale_subscription_tour', function(require) {
"use_strict";

var core = require('web.core');
var tour = require('web_tour.tour');

var _t = core._t;

tour.register('to_sale_subscription_tour', {
	url: "/web",
}, [tour.STEPS.SHOW_APPS_MENU_ITEM, {
	content: _t('Get started by clicking here to recur billing via subscription management'),
	trigger: '.o_app[data-menu-xmlid="to_sale_subscription.menu_sale_subscription_root"]',
	position: 'bottom',
},
{
	content: _t('Click here to config your subscription templates'),
	trigger: '.dropdown-toggle[data-menu-xmlid="to_sale_subscription.menu_sale_subscription_config"]',
	position: 'bottom',
},
{
	content: _t('Click to create <b>your first subscription template</b> here'),
	trigger: '.o_menu_entry_lvl_2[data-menu-xmlid="to_sale_subscription.menu_template_of_subscription"]',
	position: 'top',
},
{
	content: _t('Now create a new subscription template.'),
	trigger: 'div .o_list_button_add',
	extra_trigger: 'button.o_list_button_add',
	position: 'bottom',
	width: 200,
},
{
	content: _t('Now you can enter a name for this subscription template.<br/><i>(e.g. Office Cleaning Monthly)</i>'),
	trigger: 'div.oe_title input',
	extra_trigger: '.o_form_editable',
	position: 'right',
	width: 200,
	run: "text ERPOnline Monthly ### TOUR DATA ###",
},
{
	content: _t('In the Invoice field, choose the recurrence for this subscription template.<br/><i>(e.g. 1 time per month)</i>'),
	trigger: 'select.field_rule_type',
	extra_trigger: '.o_form_editable',
	position: 'right',
	width: 200,
},
{
	content: _t('Click on Save button to save this template and you can assign this subscription template to different subscription products.'),
	trigger: '.o_form_button_save',
	position: 'bottom',
},
{
	content: _t('Let\'s go to the Subscription Products menu to create our first subscription product'),
	trigger: '.dropdown-toggle[data-menu-xmlid="to_sale_subscription.menu_sale_subscription"]',
	position: 'bottom',
},
{
	content: _t('Create a new subscription product here'),
	trigger: '.o_menu_entry_lvl_2[data-menu-xmlid="to_sale_subscription.menu_sale_subscription_product"]',
	position: 'top',
},
{
	content: _t('Go ahead and create a new subscription product'),
	trigger: '.o_list_button_add',
	position: 'right',
	width: 200,
},
{
	content: _t('Now you can enter a name for this subscription product.<br/><i>(e.g. Office Cleaning Monthly)</i>'),
	trigger: 'input.o_field_widget[name="name"]',
	position: 'right',
	width: 200,
	run: "text ERPOnline SAAS Monthly ### TOUR DATA ###",
},
{
	content: _t('Link this subscription product to a subscription template in this tab'),
	trigger: 'li.page_sales a',
	extra_trigger: '.o_form_editable',
	position: 'top',
},
{
	content: _t('Link this subscription product to a subscription template in this tab'),
	trigger: '.o_form_editable .o_field_many2one[name="subscription_template_id"]',
	extra_trigger: '.o_form_editable',
	position: 'bottom',
	run: function (actions) {
        actions.text("TOUR DATA", this.$anchor.find("input"));
    },
},
{
    trigger: ".ui-menu-item > a",
    auto: true,
    in_modal: false,
},
{
	content: _t('Save and you\'re all set!<br/>Simply sell this product to create a subscription automatically or create a subscription manually from Sales/Subscription app!'),
	trigger: '.o_form_button_save',
	position: 'bottom',
},
// requires focus
{
	trigger: '.o_form_button_save',
	position: 'bottom',
}]);
	return {};
});
