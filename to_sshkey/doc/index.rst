Installation
============

1. Install paramiko into your Odoo server. Read this page to learn more on how to install paramiko: http://www.paramiko.org/installing.html
2. Upload this module to an addons path that is registered with your Odoo instance. Do not forget to apply appropriate permission to the module's files
3. Login to your Odoo instance with an administrator account
4. Navigate to Apps
5. Find with keyword 'to_sshkey'
6. Install it as usual then you are done

Instructions
============

Usages
------

1. Access Rights
	* There are two access groups added upon installation of this module:
		* SSH Keys Users: The user in this group will have access to his own SSH Keys only.
		* SSH Key Managers: The user in this group will have access to all SSH Keys stored in your Odoo.
2. Add your SSH Keys: your SSH Keys can be added in your 'My Profile' page
