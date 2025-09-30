In order to run the app, you must install Python.

You must also install flask. Installing flask using pip from the command line will ensure that you do not miss any dependencies. No dependencies other than flask's dependencies are required for this app.

This app must be started from the command line in admin mode. Navigate to the directory folder containing the __init__.py file, and use the following command:

flask --app FJTickets init-db

This will initialise the SQLite database, but it will not contain any data when initialised.

In order to start the app, enter the command

flask --app FJTickets run

The output on the command line will tell you what IP address to navigate to.
It will usually be 127.0.0.1:5000

Going to the command line and pressing ctrl-c will end the program.
