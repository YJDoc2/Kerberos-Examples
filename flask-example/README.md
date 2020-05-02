# Flask Example

<hr />

This shows the usage of Kerberos_KDC class with a flask backend and Kerberos.min.js script in plain html-js frontend.

# Dependencies

This requires Python 3.8 and pipenv globally installed to work.
This is tested and also works with Python 3.7, but manual change of version in pipfiles will be required to make it work.

This depends on Flask, flask-cors and pycrypto modules to run.

The backend requires Ports 5000, 5001 and 5002 to be free on localhost.
This can be changed in individual Server python scripts, but then change of url in the script.js in static files in KDC folder will also be required.

# Explanation

The detailed explanation of how the code is set up and works is done through detailed commenting of code, which explains how the Kerberos classes are setup and how the working is done.

<strong>Comments only explain code related to Kerberos Module and library.Setup of flask and other things is not not explained.</strong>

Brief explanation is as follows:

In KDC folder, app python file sets up the Authentication Service and Ticket Granting Service using Kerberos_KDC class on port 5000.
The Tickets folder contains the server structures that have been already generated.If new Structures are to be generated, first un comment appropriate lines in app py file, then manually copy the newly generated A and B server structures in the data-servers/Tickets folders.
For generating new TGS_SERVER structure, simply delete the file from there.

The data-server contains two server scripts A and B.
The A server defines two different routes for two operations, while B has single route and uses parameters in encrypted request to decide which action to take.

# Running

The bash script start sh can be directly used to run all servers. In case pipenv is not installed, or some other route is to be taken for running, one can run the servers in steps as per done in shell script.
<strong>Note</strong> that even though after stopping the running script _sometimes_ the servers still keep running in background, though usually they will also stop with the script. In the case they don't, they will need to be manually stopped to free the bound ports on localhost.
