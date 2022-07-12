odoo.define('viin_web_dashboard.sample_cohort_data', function(require) {
	function get_cohort_data_week() {
		return {
			"rows": [
				{
					"date": "W25 2021",
					"value": 1,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-06-13 22:00:00"],
						["create_date", "<", "2021-06-20 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-06-20"]
							],
							"period": "13 Jun - 19 Jun"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-06-27"]
							],
							"period": "20 Jun - 26 Jun"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-04"]
							],
							"period": "27 Jun - 03 Jul"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-11"]
							],
							"period": "04 Jul - 10 Jul"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-18"]
							],
							"period": "11 Jul - 17 Jul"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-25"]
							],
							"period": "18 Jul - 24 Jul"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-01"]
							],
							"period": "25 Jul - 31 Jul"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-08"]
							],
							"period": "01 Aug - 07 Aug"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-15"]
							],
							"period": "08 Aug - 14 Aug"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-22"]
							],
							"period": "15 Aug - 21 Aug"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-29"]
							],
							"period": "22 Aug - 28 Aug"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-09-05"]
							],
							"period": "29 Aug - 04 Sep"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				},
				{
					"date": "W29 2021",
					"value": 1,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-07-11 22:00:00"],
						["create_date", "<", "2021-07-18 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-18"]
							],
							"period": "11 Jul - 17 Jul"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-25"]
							],
							"period": "18 Jul - 24 Jul"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-01"]
							],
							"period": "25 Jul - 31 Jul"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-08"]
							],
							"period": "01 Aug - 07 Aug"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-15"]
							],
							"period": "08 Aug - 14 Aug"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-22"]
							],
							"period": "15 Aug - 21 Aug"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-29"]
							],
							"period": "22 Aug - 28 Aug"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-09-05"]
							],
							"period": "29 Aug - 04 Sep"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				},
				{
					"date": "W33 2021",
					"value": 4,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-08-08 22:00:00"],
						["create_date", "<", "2021-08-15 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 4,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-15"]
							],
							"period": "08 Aug - 14 Aug"
						},
						{
							"value": 3,
							"churn_value": 1,
							"percentage": 25,
							"domain": [
								["date_closed", "<", "2021-08-22"]
							],
							"period": "15 Aug - 21 Aug"
						},
						{
							"value": 3,
							"churn_value": 1,
							"percentage": 25,
							"domain": [
								["date_closed", "<", "2021-08-29"]
							],
							"period": "22 Aug - 28 Aug"
						},
						{
							"value": 3,
							"churn_value": 1,
							"percentage": 25,
							"domain": [
								[
									"date_closed",
									"<",
									"2021-09-05"
								]
							],
							"period": "29 Aug - 04 Sep"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				},
				{
					"date": "W34 2021",
					"value": 4,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-08-15 22:00:00"],
						["create_date", "<", "2021-08-22 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						[
							"user_id",
							"=",
							2
						]
					],
					"columns": [
						{
							"value": 4,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-22"]
							],
							"period": "15 Aug - 21 Aug"
						},
						{
							"value": 4,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-29"]
							],
							"period": "22 Aug - 28 Aug"
						},
						{
							"value": 4,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-09-05"]
							],
							"period": "29 Aug - 04 Sep"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				}
			],
			"avg": {
				"avg_value": 2.5,
				"columns_avg": {
					"0": {
						"percentage": 0,
						"count": 4
					},
					"1": {
						"percentage": 25,
						"count": 4
					},
					"2": {
						"percentage": 25,
						"count": 4
					},
					"3": {
						"percentage": 25,
						"count": 3
					},
					"4": {
						"percentage": 0,
						"count": 2
					},
					"5": {
						"percentage": 0,
						"count": 2
					},
					"6": {
						"percentage": 0,
						"count": 2
					},
					"7": {
						"percentage": 0,
						"count": 2
					},
					"8": {
						"percentage": 0,
						"count": 1
					},
					"9": {
						"percentage": 0,
						"count": 1
					},
					"10": {
						"percentage": 0,
						"count": 1
					},
					"11": {
						"percentage": 0,
						"count": 1
					},
					"12": {
						"percentage": 0,
						"count": 0
					},
					"13": {
						"percentage": 0,
						"count": 0
					},
					"14": {
						"percentage": 0,
						"count": 0
					},
					"15": {
						"percentage": 0,
						"count": 0
					}
				}
			}
		};
	}

	function get_cohort_data_month() {
		return {
			"rows": [
				{
					"date": "June 2021",
					"value": 1,
					"domain": [
						"&",
						"&",
						[
							"create_date",
							">=",
							"2021-05-31 22:00:00"
						],
						[
							"create_date",
							"<",
							"2021-06-30 22:00:00"
						],
						"&",
						[
							"type",
							"=",
							"opportunity"
						],
						[
							"user_id",
							"=",
							2
						]
					],
					"columns": [
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-06-30"]
							],
							"period": "May 2021"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-30"]
							],
							"period": "June 2021"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-31"]
							],
							"period": "July 2021"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-09-30"]
							],
							"period": "August 2021"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				},
				{
					"date": "July 2021",
					"value": 1,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-06-30 22:00:00"],
						["create_date", "<", "2021-07-31 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-30"]
							],
							"period": "June 2021"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-30"]
							],
							"period": "July 2021"
						},
						{
							"value": 1,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-09-30"]
							],
							"period": "August 2021"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				},
				{
					"date": "August 2021",
					"value": 8,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-07-31 22:00:00"],
						["create_date", "<", "2021-08-31 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 7,
							"churn_value": 1,
							"percentage": 12.5,
							"domain": [
								["date_closed", "<", "2021-08-31"]
							],
							"period": "July 2021"
						},
						{
							"value": 7,
							"churn_value": 1,
							"percentage": 12.5,
							"domain": [
								["date_closed", "<", "2021-09-30"]
							],
							"period": "August 2021"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				}
			],
			"avg": {
				"avg_value": 3.3333333333333335,
				"columns_avg": {
					"0": {
						"percentage": 12.5,
						"count": 3
					},
					"1": {
						"percentage": 12.5,
						"count": 3
					},
					"2": {
						"percentage": 0,
						"count": 2
					},
					"3": {
						"percentage": 0,
						"count": 1
					},
					"4": {
						"percentage": 0,
						"count": 0
					},
					"5": {
						"percentage": 0,
						"count": 0
					},
					"6": {
						"percentage": 0,
						"count": 0
					},
					"7": {
						"percentage": 0,
						"count": 0
					},
					"8": {
						"percentage": 0,
						"count": 0
					},
					"9": {
						"percentage": 0,
						"count": 0
					},
					"10": {
						"percentage": 0,
						"count": 0
					},
					"11": {
						"percentage": 0,
						"count": 0
					},
					"12": {
						"percentage": 0,
						"count": 0
					},
					"13": {
						"percentage": 0,
						"count": 0
					},
					"14": {
						"percentage": 0,
						"count": 0
					},
					"15": {
						"percentage": 0,
						"count": 0
					}
				}
			}
		}
	}

	function get_cohort_data_year() {
		return {
			"rows": [
				{
					"date": "2021",
					"value": 10,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2020-12-31 23:00:00"],
						["create_date", "<", "2021-12-31 23:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 9,
							"churn_value": 1,
							"percentage": 10,
							"domain": [
								["date_closed", "<", "2021-12-31"]
							],
							"period": "2020"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				}
			],
			"avg": {
				"avg_value": 10,
				"columns_avg": {
					"0": {
						"percentage": 10,
						"count": 1
					},
					"1": {
						"percentage": 0,
						"count": 0
					},
					"2": {
						"percentage": 0,
						"count": 0
					},
					"3": {
						"percentage": 0,
						"count": 0
					},
					"4": {
						"percentage": 0,
						"count": 0
					},
					"5": {
						"percentage": 0,
						"count": 0
					},
					"6": {
						"percentage": 0,
						"count": 0
					},
					"7": {
						"percentage": 0,
						"count": 0
					},
					"8": {
						"percentage": 0,
						"count": 0
					},
					"9": {
						"percentage": 0,
						"count": 0
					},
					"10": {
						"percentage": 0,
						"count": 0
					},
					"11": {
						"percentage": 0,
						"count": 0
					},
					"12": {
						"percentage": 0,
						"count": 0
					},
					"13": {
						"percentage": 0,
						"count": 0
					},
					"14": {
						"percentage": 0,
						"count": 0
					},
					"15": {
						"percentage": 0,
						"count": 0
					}
				}
			}
		}
	}

	function get_cohort_data_planned_revenue() {
		return {
			"rows": [
				{
					"date": "W25 2021",
					"value": 22500,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-06-13 22:00:00"],
						["create_date", "<", "2021-06-20 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-06-20"]
							],
							"period": "13 Jun - 19 Jun"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-06-27"]
							],
							"period": "20 Jun - 26 Jun"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-04"]
							],
							"period": "27 Jun - 03 Jul"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-11"]
							],
							"period": "04 Jul - 10 Jul"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-18"]
							],
							"period": "11 Jul - 17 Jul"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-25"]
							],
							"period": "18 Jul - 24 Jul"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-01"]
							],
							"period": "25 Jul - 31 Jul"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-08"]
							],
							"period": "01 Aug - 07 Aug"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-15"]
							],
							"period": "08 Aug - 14 Aug"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-22"]
							],
							"period": "15 Aug - 21 Aug"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-29"]
							],
							"period": "22 Aug - 28 Aug"
						},
						{
							"value": 22500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-09-05"]
							],
							"period": "29 Aug - 04 Sep"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				},
				{
					"date": "W29 2021",
					"value": 40000,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-07-11 22:00:00"],
						["create_date", "<", "2021-07-18 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 40000,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-18"]
							],
							"period": "11 Jul - 17 Jul"
						},
						{
							"value": 40000,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-07-25"]
							],
							"period": "18 Jul - 24 Jul"
						},
						{
							"value": 40000,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-01"]
							],
							"period": "25 Jul - 31 Jul"
						},
						{
							"value": 40000,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-08"]
							],
							"period": "01 Aug - 07 Aug"
						},
						{
							"value": 40000,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-15"]
							],
							"period": "08 Aug - 14 Aug"
						},
						{
							"value": 40000,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-22"]
							],
							"period": "15 Aug - 21 Aug"
						},
						{
							"value": 40000,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-29"]
							],
							"period": "22 Aug - 28 Aug"
						},
						{
							"value": 40000,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-09-05"]
							],
							"period": "29 Aug - 04 Sep"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				},
				{
					"date": "W33 2021",
					"value": 89200,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-08-08 22:00:00"],
						["create_date", "<", "2021-08-15 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 89200,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-15"]
							],
							"period": "08 Aug - 14 Aug"
						},
						{
							"value": 69400,
							"churn_value": 19800,
							"percentage": 22.2,
							"domain": [
								["date_closed", "<", "2021-08-22"]
							],
							"period": "15 Aug - 21 Aug"
						},
						{
							"value": 69400,
							"churn_value": 19800,
							"percentage": 22.2,
							"domain": [
								["date_closed", "<", "2021-08-29"]
							],
							"period": "22 Aug - 28 Aug"
						},
						{
							"value": 69400,
							"churn_value": 19800,
							"percentage": 22.2,
							"domain": [
								["date_closed", "<", "2021-09-05"]
							],
							"period": "29 Aug - 04 Sep"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				},
				{
					"date": "W34 2021",
					"value": 78500,
					"domain": [
						"&",
						"&",
						["create_date", ">=", "2021-08-15 22:00:00"],
						["create_date", "<", "2021-08-22 22:00:00"],
						"&",
						["type", "=", "opportunity"],
						["user_id", "=", 2]
					],
					"columns": [
						{
							"value": 78500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-22"]
							],
							"period": "15 Aug - 21 Aug"
						},
						{
							"value": 78500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-08-29"]
							],
							"period": "22 Aug - 28 Aug"
						},
						{
							"value": 78500,
							"churn_value": 0,
							"percentage": 0,
							"domain": [
								["date_closed", "<", "2021-09-05"]
							],
							"period": "29 Aug - 04 Sep"
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						},
						{
							"value": "-",
							"churn_value": "-",
							"percentage": ""
						}
					]
				}
			],
			"avg": {
				"avg_value": 57550,
				"columns_avg": {
					"0": {
						"percentage": 0,
						"count": 4
					},
					"1": {
						"percentage": 22.2,
						"count": 4
					},
					"2": {
						"percentage": 22.2,
						"count": 4
					},
					"3": {
						"percentage": 22.2,
						"count": 3
					},
					"4": {
						"percentage": 0,
						"count": 2
					},
					"5": {
						"percentage": 0,
						"count": 2
					},
					"6": {
						"percentage": 0,
						"count": 2
					},
					"7": {
						"percentage": 0,
						"count": 2
					},
					"8": {
						"percentage": 0,
						"count": 1
					},
					"9": {
						"percentage": 0,
						"count": 1
					},
					"10": {
						"percentage": 0,
						"count": 1
					},
					"11": {
						"percentage": 0,
						"count": 1
					},
					"12": {
						"percentage": 0,
						"count": 0
					},
					"13": {
						"percentage": 0,
						"count": 0
					},
					"14": {
						"percentage": 0,
						"count": 0
					},
					"15": {
						"percentage": 0,
						"count": 0
					}
				}
			}
		};
	}

	return {
		get_cohort_data_week: get_cohort_data_week,
		get_cohort_data_month: get_cohort_data_month,
		get_cohort_data_year: get_cohort_data_year,
		get_cohort_data_planned_revenue: get_cohort_data_planned_revenue,
	}
});
