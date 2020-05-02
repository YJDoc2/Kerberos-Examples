# Kerberos Examples

A repository containing usage examples for Kerberos JS module and Python Library.

## About

This contains two examples about how to use the Kerberos JS Module and Python library.
The Module and library can be found as :
<a href='https://github.com/YJDoc2/Kerberos-JS-Module'>Kerberos JS Module</a>
<a href='https://github.com/YJDoc2/Kerberos-Python-Library'>Kerberos Python Library</a>

<strong>Note</strong> that neither of these implement the protocol on low c-like level. These only provide Classes that can be used over some other protocol.Which means that neither of them set up any kind of Server or client and that has to be by use of some other means.

The explanation of working of them is done in the respective repositories and not repeated here.The API documentation can be found there as well.

Both examples demonstrate usage of these over HTTP protocol.

Both also show that JS module and library can be used with each other, and there is not a constraint to use same language module/library on Server and client side.

This repository contains two examples in two folders, whose explanation and working is in the respective README files in the respective folders. Basic explanation is given below.

## Building

<strong>NOTE : for reducing the size of repository, as well as of redundant copies, the actual module/library folder were linked using symlinks while development. Before running, replace all Kerberos symlinks with Kerberos python library, and Kerberos-JS symlink with Kerberos JS module.</strong>

## Flask Example

This uses Flask backend and a plain html-js frontend.
The Kerberos_KDC class is used on single server to handle both Authentication as well as Ticket Granting Services.This also handles display of the single front end page.

A second Server acts as a server to be protected by this, and uses Server class.

In front end Kerberos.min.js script is used to access the Client class, and external dependency of axios is used to make AJAX requests to backend servers.

## Node Example

This uses NodeJS with ExpressJS backend and tkinter GUI based client side.

Here Two distinct servers listening on two different ports handle the Authentication Service and Ticket Granting Service.
One uses KerberosAS class and other used KerberosTGS class.

A third Server on different port acts as a server to be protected by this, and uses Server class.

This shows that the AS and TGS can be set up on different servers, and does the same work as KDC class.

On client side, Tkinter GUI uses Python library Client class.
