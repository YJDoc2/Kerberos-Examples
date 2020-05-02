# Node Example

This shows the usage of KerberosAS class and KerberosTGS class on two distinct server to handle the Authentication and Ticket Granting Services. This uses NodeJS with ExpressJs in backend and a python Tkinter GUI client.

<strong>Note</strong> that the setup for the Tkinter GUI program done in client is probably not the best way to do it, and can be done in better way.

The GUI programing is done with help of Tkinter Documentation and <a href='https://pythonprogramming.net/change-show-new-frame-tkinter/'>a tutorial on pythonprogramming.net</a>

# Dependencies

This requires Python 3.8 and pipenv globally installed to work.

This is tested and also works with Python 3.7, but manual change of version in pipfiles will be required to make it work.

This requires appropriate Tkinter libraries to be installed for the Client GUI to work.

This also requires NodeJS globally installed.

The backend requires Ports 5001, 5002 and 5003 to be free on localhost.
This can be changed in individual Server scripts, but then change of url in Functions in Python Client scripts will also be required.

# Explanation

The detailed explanation of how the code is set up and works is done through detailed commenting of code, which explains how the Kerberos classes are setup and how the working is done.

<strong>Comments only explain code related to Kerberos Module and library. Setup of Express, Tkinter and other things is not not explained.</strong>

Brief explanation is as follows:

In the Servers folder, AS.js and TGS.js set up servers on port 5001 and 5002 to handle Authentication Service and Ticket Granting Service respectively.

BookServer.js sets up the third server on port 5003 which acts as the server that is protected by kerberos.

the python Tkinter GUI client uses requests module to make requests to servers.

# Running

This has two inbuilt user profiles :<br />
username u1 with password pass1<br />
username u2 with password pass2<br />

The bash script start sh can be directly used to run all servers. In case pipenv is not installed, or some other route is to be taken for running, one can run the servers in steps as per done in shell script.
<strong>Note</strong> that even though after stopping the running script _sometimes_ the servers still keep running in background, though usually they will also stop with the script. In the case they don't, they will need to be manually stopped to free the bound ports on localhost.
