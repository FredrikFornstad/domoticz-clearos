The Domoticz basic software package, that is distributed for free under GNU GPL 3 in ClearOS, contains all of the (relevant) upstream code with some minor modifications:

1. To comply with ClearOS requirements on file structure (FHS), the program code is placed in /usr/share/domoticz and userdata is found in /var/domoticz.
   As a side effect, a number of parameters MUST be passed to domoticz at startup or it will fail:
	a. -wwwroot /var/domoticz/www
	b. -dbase /var/domoticz/domoticz.db
	c. -userdata /var/domoticz/
	d. -sslcert /var/domoticz/server_cert.pem
	e. -ssldhparm /var/domoticz/server_cert.pem
   The easiest way to start domoticz is to execute the /usr/share/domoticz/run-domoticz script that will start domoticz manually with the domoticz default parameters.
   You may want to change/add parameters. Do not execute /usr/share/domoticz/domoticz directly as root as that will mess up file ownerships. You have been warned.

2. If you want to run Domoticz as a daemon in the background (recommended), you will need to create your own daemon script.
   Use domoticz as the daemon name (in other words make sure the file name is domoticz.service when using systemd) and execute it as user domoticz.

3. In order to successfully run Domoticz in ClearOS, you will, depending on your setup and your needs, need to configure ClearOS
   in such a way that domoticz can access system resources and that you do not expose your system unprotected to the Internet.
   Important: Do not forget to enable password protection!

4. Software updates from within the Domoticz management interface does not work. New stable releases will be released in ClearOS with some delay.

5. Finally, in the ClearOS Marketplace you can find app-domoticz. This is a separate paid app that automatically installs,
   configures and manage the running of the Domoticz software. If you feel that the manual configuration described above is not for you,
   then please consider to buy the app. For each purchase 5 USD will be donated to domoticz.com .
