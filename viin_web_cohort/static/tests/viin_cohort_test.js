odoo.define('vin_web_cohort.viin_cohort_test', function(require) {
	var ViinCohortView = require('viin_web_cohort.ViinCohortView');
	var testUtils = require('viin_web_cohort.test_utils');
	var session = require('web.session');
	var sample_cohort_data = require('viin_web_cohort.sample_cohort_data');

	var createViinCohortView = testUtils.createViinCohortView;

	function _preventScroll(ev) {
		ev.stopImmediatePropagation();
	}

	function timeout(ms) {
		return new Promise(resolve => setTimeout(resolve, ms));
	}

	QUnit.module('Views', {
		beforeEach: function() {
			window.addEventListener('scroll', _preventScroll, true);
			session.uid = -1; // TO CHECK
			this.data = {
				lead: {
					fields: {
						id: { string: "ID", type: "integer" },
						date_deadline: { string: "Date Deadline", type: "datetime" },
						create_date: { string: "Create Date", type: "datetime" },
						name: { string: "name", type: "char" },
						email_from: { string: "Email From", type: "char" },
						city: { string: 'City', type: 'char' },
						activity_date_deadline: { string: 'Planned End Date', type: 'datetime' },
						planned_revenue: { string: 'Planned Revenue', type: 'float', store: true },
						probability: { string: 'Probability', type: 'float' },
						user_id: { string: "User", type: "many2one", relation: 'user', default: session.uid },
						write_date: { string: 'Write Date', type: "datetime" },
						company_id: { string: "Company", type: "many2one", relation: "company" },
						priority: {
							string: "Priority", type: "selection", selection: [
								['0', 'Low'],
								['1', 'Medium'],
								['2', 'High'],
								['3', 'Very High'],
							]
						},
						date_closed: { string: 'Closed Date', type: 'datetime' }
					},
					records: [
						{
							"id": 25,
							"date_deadline": false,
							"create_date": "2021-08-16 07:30:58",
							"name": "Modern Open Space",
							"email_from": "henry@elight.com",
							"city": "Buenos Aires",
							"activity_date_deadline": "2021-08-17",
							"planned_revenue": 4500,
							"probability": 60,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "2",
							"date_closed": false,
						},
						{
							"id": 21,
							"date_deadline": false,
							"create_date": "2021-08-16 07:30:58",
							"name": "Office Design and Architecture",
							"email_from": "ready.mat28@example.com",
							"city": "Birmingham",
							"activity_date_deadline": "2021-08-21",
							"planned_revenue": 9000,
							"probability": 91.67,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "2",
							'date_closed': false
						},
						{
							"id": 20,
							"date_deadline": false,
							"create_date": "2021-08-10 07:30:57",
							"name": "Distributor Contract",
							"email_from": "john.b@tech.info",
							"phone": "+1 312 349 2324",
							"city": "Chicago",
							"activity_date_deadline": "2021-08-18",
							"planned_revenue": 19800,
							"probability": 100,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "2",
							"date_closed": "2021-08-17 07:30:58"
						},
						{
							"id": 16,
							"date_deadline": "2021-08-24",
							"create_date": "2021-08-15 07:30:57",
							"name": "Global Solutions: Furnitures",
							"email_from": "ready.mat28@example.com",
							"phone": "(803)-873-6126",
							"city": "Liverpool",
							"activity_date_deadline": "2021-08-19",
							"planned_revenue": 3800,
							"probability": 90,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "2",
							"date_closed": false
						},
						{
							"id": 32,
							"date_deadline": "2021-08-31",
							"create_date": "2021-06-17 07:30:58",
							"name": "Quote for 600 Chairs",
							"email_from": "ErikNFrench@armyspy.com",
							"phone": false,
							"city": "Chevy Chase",
							"activity_date_deadline": false,
							"planned_revenue": 22500,
							"probability": 20,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "1",
							"date_closed": false
						},
						{
							"id": 31,
							"date_deadline": "2021-08-31",
							"create_date": "2021-07-17 07:30:58",
							"name": "Quote for 150 carpets",
							"email_from": "ErikNFrench@armyspy.com",
							"phone": false,
							"city": "Chevy Chase",
							"activity_date_deadline": false,
							"planned_revenue": 40000,
							"probability": 10,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "1",
							"date_closed": false
						},
						{
							"id": 22,
							"date_deadline": false,
							"create_date": "2021-08-09 07:30:58",
							"name": "5 VP Chairs",
							"email_from": "azure.Interior24@example.com",
							"phone": "(870)-931-0505",
							"city": "Fremont",
							"activity_date_deadline": "2021-08-15",
							"planned_revenue": 5600,
							"probability": 30,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "1",
							"date_closed": false
						},
						{
							"id": 15,
							"date_deadline": "2021-08-24",
							"create_date": "2021-08-16 07:30:57",
							"name": "Info about services",
							"email_from": "virginie@agrolait.com",
							"phone": "+32 10 588 558",
							"city": "Wavre",
							"activity_date_deadline": "2021-08-18",
							"planned_revenue": 25000,
							"probability": 30,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "1",
							"date_closed": false
						},
						{
							"id": 13,
							"date_deadline": "2021-08-31",
							"create_date": "2021-08-16 07:30:57",
							"name": "Quote for 12 Tables",
							"email_from": "willmac@rediffmail.example.com",
							"phone": false,
							"city": "Melbourne",
							"activity_date_deadline": "2021-08-20",
							"activity_summary": "Meeting to go over pricing information.",
							"planned_revenue": 40000,
							"probability": 10,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "1",
							"date_closed": false
						},
						{
							"id": 24,
							"date_deadline": false,
							"create_date": "2021-08-10 07:30:58",
							"name": "Need 20 Desks",
							"email_from": "info@mycompany.net",
							"phone": false,
							"city": "Lima",
							"activity_date_deadline": "2021-08-19",
							"planned_revenue": 60000,
							"probability": 90,
							"user_id": 2,
							"write_date": "2021-08-17 07:31:00",
							"company_id": 1,
							"priority": "0",
							"date_closed": false
						}
					],
					check_access_rights: function() {
						return Promise.resolve(true);
					},
				},
				company: {
					fields: {
						id: { string: "ID", type: "integer" },
						name: { string: "name", type: "char" },
						display_name: { string: "Display Name", type: "char" },
					},
					records: [
						{ id: 1, name: "Chicago Company", display_name: "Chicago Company" },
						{ id: 2, name: "San Fransisco Company", display_name: "San Fransisco Company" },
					]
				},
				user: {
					fields: {
						id: { string: "ID", type: "integer" },
						name: { string: "Name", type: "char" },
						display_name: { string: "Displayed name", type: "char" },
					},
					records: [
						{ id: session.uid, display_name: "user 1" },
						{ id: 4, display_name: "user 4" },
						{ id: 2, display_name: "Michell" },
					]
				},
			};
		},
		afterEach: function() {
			window.removeEventListener('scroll', _preventScroll, true);
		},
	}, function() {
		QUnit.module('ViinCohortView');

		var archs = {
			"lead,false,form":
				'<form>' +
				'<field name="name"/>' +
				'</form>',
			"lead,1,form":
				'<form>' +
				'</form>',
		};

		odoo.session_info = {};
		odoo.session_info.user_context = {};

		QUnit.test('simple rendering web cohort', async function(assert) {
			assert.expect(3);
			var viin_cohort = await createViinCohortView({
				View: ViinCohortView,
				model: 'lead',
				data: this.data,
				arch: '<viin_cohort string="Opportunities" ' +
					'start_date="create_date" stop_date="date_closed" interval="week" ' +
					'mode="churn" />',
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					return this._super.apply(this, arguments);
				},
				viewOptions: {},
			});
			await timeout(1000);
			assert.equal(viin_cohort.$('.viin_cohort_interval_button').length, 4, 'should have 4 button day, week, month, year');
			assert.equal(viin_cohort.$('.viin_cohort_row').length, 4, 'show have 4 data row');
			assert.equal(viin_cohort.$('.viin_cohort_interval_button.active').data('interval'), 'week', 'show have 4 data row');
			viin_cohort.destroy();
		});

		QUnit.test('check data display in cohort', async function(assert) {
			assert.expect(5)
			var viin_cohort = await createViinCohortView({
				View: ViinCohortView,
				model: 'lead',
				data: this.data,
				arch: '<viin_cohort string="Opportunities" ' +
					'start_date="create_date" stop_date="date_closed" interval="week" ' +
					'mode="churn" />',
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					return this._super.apply(this, arguments);
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			var row1Col2Val = $('.viin_cohort_row').eq(0).find('.viin_cohort_cell_value').eq(1).text();
			row1Col2Val = row1Col2Val.trim();
			assert.equal(row1Col2Val, '1.0', 'The 2nd column of 1st row should have value of 1.0');
			var row2Col2Val = $('.viin_cohort_row').eq(1).find('.viin_cohort_cell_value').eq(1).text();
			row2Col2Val = row2Col2Val.trim();
			assert.equal(row2Col2Val, '1.0', 'The 2nd column of 2nd row should have value of 1.0');

			var row3Col2Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(1).text();
			row3Col2Val = row3Col2Val.trim();
			assert.equal(row3Col2Val, '4.0', 'The 2nd column of 3rd row should have value of 4.0');

			var row4Col2Val = $('.viin_cohort_row').eq(3).find('.viin_cohort_cell_value').eq(1).text();
			row4Col2Val = row4Col2Val.trim();
			assert.equal(row4Col2Val, '4.0', 'The 2nd column of 4th row should have value of 4.0');

			var row3Col4Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(3).text();
			row3Col4Val = row3Col4Val.trim();
			assert.equal(row3Col4Val, '25%', 'The 4th column of 3rd row should have value of 25%');
			viin_cohort.destroy();
		});

		QUnit.test('check redirect to list', async function(assert) {
			assert.expect(1)
			var viin_cohort = await createViinCohortView({
				View: ViinCohortView,
				model: 'lead',
				data: this.data,
				arch: '<viin_cohort string="Opportunities" ' +
					'start_date="create_date" stop_date="date_closed" interval="week" ' +
					'mode="churn" />',
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						return Promise.resolve(sample_cohort_data.get_cohort_data_week());
					}
					return this._super.apply(this, arguments);
				},
				intercepts: {
					do_action: function(event) {
						assert.deepEqual(event.data.action.domain, [
							"&",
							"&",
							["create_date", ">=", "2021-08-08 22:00:00"],
							["create_date", "<", "2021-08-15 22:00:00"],
							"&",
							["type", "=", "opportunity"],
							["user_id", "=", 2]
						], 'should send the correct data to redirect to list')
					},
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			await testUtils.dom.click($('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(0));
			viin_cohort.destroy();
		});

		QUnit.test('click month internal button', async function(assert) {
			assert.expect(4)
			var viin_cohort = await createViinCohortView({
				View: ViinCohortView,
				model: 'lead',
				data: this.data,
				arch: '<viin_cohort string="Opportunities" ' +
					'start_date="create_date" stop_date="date_closed" interval="week" ' +
					'mode="churn" />',
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						if (args.interval == 'month') {
							return Promise.resolve(sample_cohort_data.get_cohort_data_month());
						} else {
							return Promise.resolve(sample_cohort_data.get_cohort_data_week());
						}
					}
					return this._super.apply(this, arguments);
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			await testUtils.dom.click(viin_cohort.$('.viin_cohort_interval_button').eq(2));
			await timeout(2000);
			var row1Col2Val = $('.viin_cohort_row').eq(0).find('.viin_cohort_cell_value').eq(1).text();
			row1Col2Val = row1Col2Val.trim();
			assert.equal(row1Col2Val, '1.0', 'The 2nd column of 1st row should have value of 1.0');
			var row2Col2Val = $('.viin_cohort_row').eq(1).find('.viin_cohort_cell_value').eq(1).text();
			row2Col2Val = row2Col2Val.trim();
			assert.equal(row2Col2Val, '1.0', 'The 2nd column of 2nd row should have value of 1.0');

			var row3Col2Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(1).text();
			row3Col2Val = row3Col2Val.trim();
			assert.equal(row3Col2Val, '8.0', 'The 2nd column of 3rd row should have value of 8.0');

			var row3Col4Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(3).text();
			row3Col4Val = row3Col4Val.trim();
			assert.equal(row3Col4Val, '12.5%', 'The 4th column of 3rd row should have value of 12.5%');
			viin_cohort.destroy();
		});

		QUnit.test('click year internal button', async function(assert) {
			assert.expect(2)
			var viin_cohort = await createViinCohortView({
				View: ViinCohortView,
				model: 'lead',
				data: this.data,
				arch: '<viin_cohort string="Opportunities" ' +
					'start_date="create_date" stop_date="date_closed" interval="week" ' +
					'mode="churn" />',
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						if (args.interval == 'year') {
							return Promise.resolve(sample_cohort_data.get_cohort_data_year());
						} else {
							return Promise.resolve(sample_cohort_data.get_cohort_data_week());
						}
					}
					return this._super.apply(this, arguments);
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			await testUtils.dom.click(viin_cohort.$('.viin_cohort_interval_button').eq(3));
			await timeout(2000);
			var row1Col2Val = $('.viin_cohort_row').eq(0).find('.viin_cohort_cell_value').eq(1).text();
			row1Col2Val = row1Col2Val.trim();
			assert.equal(row1Col2Val, '10.0', 'The 2nd column of 1st row should have value of 1.0');

			var row1Col3Val = $('.viin_cohort_row').eq(0).find('.viin_cohort_cell_value').eq(2).text();
			row1Col3Val = row1Col3Val.trim();
			assert.equal(row1Col3Val, '10%', 'The 3rd column of 1st row should have value of 10%');
			viin_cohort.destroy();
		});

		QUnit.test('when select measure', async function(assert) {
			assert.expect(3)
			var viin_cohort = await createViinCohortView({
				View: ViinCohortView,
				model: 'lead',
				data: this.data,
				arch: '<viin_cohort string="Opportunities" ' +
					'start_date="create_date" stop_date="date_closed" interval="week" ' +
					'mode="churn" />',
				archs: archs,
				mockRPC: function(route, args) {
					if (route == '/web/viin_cohort/get_data') {
						if (args.interval == 'week' && args.measure == '__count__') {
							return Promise.resolve(sample_cohort_data.get_cohort_data_week());
						} else {
							return Promise.resolve(sample_cohort_data.get_cohort_data_planned_revenue());
						}
					}
					return this._super.apply(this, arguments);
				},
				viewOptions: {},
			}, { positionalClicks: true });
			await timeout(1000);
			await testUtils.dom.click(viin_cohort.$('.dropdown-toggle.viin_cohort_btn'));
			await timeout(1000);
			// Select planned_revenue field
			await testUtils.dom.click(viin_cohort.$(".viin_cohort_measures_list .viin_cohort_btn[data-field='planned_revenue']"));
			await timeout(2000);

			var row3Col4Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(3).text();
			row3Col4Val = row3Col4Val.trim();
			assert.equal(row3Col4Val, '22.2%', 'The 4th column of 3rd row should have value of 22.2%');

			var row3Col5Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(4).text();
			row3Col5Val = row3Col5Val.trim();
			assert.equal(row3Col5Val, '22.2%', 'The 5th column of 3rd row should have value of 22.2%');

			var row3Col6Val = $('.viin_cohort_row').eq(2).find('.viin_cohort_cell_value').eq(5).text();
			row3Col6Val = row3Col6Val.trim();
			assert.equal(row3Col6Val, '22.2%', 'The 6th column of 3rd row should have value of 22.2%');

			viin_cohort.destroy();
		});
	});
});
