Installation
============

1. Navigate to Apps
2. Find with keyword 'to_fleet_driver'
3. Install it as usual then you are done

Instructions
============

1. Manage Drivers
	* Navigate to 'Fleet > Drivers > Drivers'
	* Hit Create button to create a new driver. A dirver record comes with the following information
		* Address: It is an odoo partner profile. When a partner is selected, Odoo will try to:
			* Fill the Name field of the driver with the name of the selected partner
			* Search Employee directory to see if the partner is also an employee of the company's. If yes, the found employee will be filled into the driver's Employee field.
		* Employee:
			* If the Employee field is left empty, Odoo will consider the driver is an external person who is not an employee.
			* If Odoo found that the partner selected in the Address field is an employee, it will fill the associated employee to this field
		* Date of Birth: this is a related field, which is related to the partner specified in the Address field.
		* License: contain the list of driver licenses which can be created an monitored in the Licenses menu (Fleet > Drivers > Licenses)
2. Manage Driver Licenses:
	* Navigate to 'Fleet > Drivers > Licenses' to see all the licenses list. Here you have some predefined filters for your quick search:
		* Expired in 30 days: show all the licenses that will be expired in 30 days
		* Expired in 7 days: show all the licenses that will be expired in 7 days
		* Expired: show all the licenses that is already expired
	* Hit Create button to create a new driver license. A dirver license comes with the following information:
		* Legal Number: the legal number of the driver license
		* Class: the class of the license. For example, if you are in US, you can create classes according to the wiki page https://en.wikipedia.org/wiki/Driver%27s_licenses_in_the_United_States
		* Driver: the driver who owns the license
		* Date Issued: the date on which the license was issued
		* Expiry: the date on which the license is considered as expired. Leave it empty for a non-expiring license
		* Issued by: the entity that issued the license. It is an Odoo partner record.
