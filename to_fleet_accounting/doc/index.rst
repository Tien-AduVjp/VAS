Installation
============

1. Navigate to Apps
2. Find with keyword 'to_fleet_accounting'
3. Install it as usual then you are done

Instructions
============

Concepts
--------

1. Vehicle Cost: this is a native model offered by the Fleet application to record costs related to your vehicles with Fleet application

Usages
------

1. Record vehicle costs in Fleet application then invoice them
	* Vehicle costs can be recorded via either
		* Vehicles Contracts (Fleet > Vehicles > Vehicles Contracts). You must specify a vendor if you want to get them invoiced later
		* Vehicles Fuel Logs (Fleet > Vehicles > Vehicles Fuel Logs). You must specify a vendor if you want to get them invoiced later
		* Vehicles Services Logs (Fleet > Vehiles > Vehicles Services Logs). You must specify a vendor if you want to get them invoiced later
		* Vehicle Costs (Fleet > Vehicles > Vehicle Costs). You must specify a vendor if you want to get them invoiced later. You must have manager rights to access this menu
	* Get the costs invoiced
		* Navigate to either of the list views of the following
			* Vehicles Fuel Logs
			* Vehicles Services Logs
			* Vehicle Costs
		* Search for items that you want to have invoiced. You can use the filter "To Invoice" to find out all the items that have not invoiced yet.
		* Check the select box to see the Action menu at the top of the list
		* Click the Action menu to see "Invoice Vehicle Costs" in the Dropdown.
		* Click on that menu entry to see a window to ask you to do either of the following
			* Create and View Invoices: This will create invoices and drive you to the invoice list view containing the invoices that have been created. All the vehicle costs of the same vendor will be put in the same invoice
			* Create Invoice: This will create invoice but keep you stay at the current view
			* Cancel: do nothing.
2. Distribute Vendor Bills to vehicles. This feature is also known as "Create vehicle Costs from a vendor bill"
	* Create a vendor bill
	* Add some lines to the bill and save the bill
		* If you would like to have vehicle and costs encoded in analytics accounting, you can specify analytics accounts for the lines
	* At the last right column of the lines table, you will see bus icons which should be in yellow color to indicated that the invoice expense has not been distributed to any vehicle of yours.
	* Click on the icon to see the Vehicle Cost Allocation/Distribution Wizard, which will help you distribute the bill line's amount to your vehicles
	* Upon validation of the bill,
		* Vehicle Costs will be created according to what you have specified in the Vehicle Cost Distribution Wizard
		* Invoice's journal items of a distributed invoice line will link to their corresponding vehicle cost and vehicle for future analysis in journal entries analysis and reports
		* If an analytic account is specified on the distributed line, analytics move lines created will also contain information about the vehicle
3. Report and Analysis
	* Links
		* Journal Entries related to vehicle costs also link to vehicles
		* Vehicle Costs that have been invoiced will link to invoice
	* Journal Entries Analysis
		* Accountants now can analyze the costs related to vehicles over the time
	* Ready to integrated with other accounting reports. Check out other related applications of ours to find more
