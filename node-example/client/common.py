import tkinter as tk
import random
from Crypto.Hash import SHA256
from Kerberos.kerberos_client import Client as  KClient
import requests

#? Common variables that are shared in both data and login page

#* actual username and password
username =''
password =''

#* Tkinter Input widgets for username and password
usernameIp = None
passIp = None

#* Kerberos Client
client = None

#* Error display label in Auth Page
auth_err = None


def login():
    global username,password,usernameIp,passIp,client
    #* We get username and password entered by user
    username = usernameIp.get()
    password = passIp.get()

    #* Sanity Checks , show error if username or input field is empty
    if username.strip() == '' or password.strip() == '':
        auth_err.config(text = 'Please Fill all details')
        return False


    #* Produce the user specific key from the password, exactly same as it is done on server
    hash = SHA256.new()
    hash.update(password.encode('ascii'))
    pass_hash = (hash.hexdigest().encode('ascii')[:32]).decode()

    #* eandom number to be sent with request
    rand = random.randint(0,10000)
    
    #* Actual request for auth and TGT
    res = requests.post('http://localhost:5001',data={'username':username,'rand':rand})
    data = res.json()
    if not data['success']:
            #* error in getting auth & TGT
            #! NOTE This does not mean that password in correct as that can be known only if the decryption of auth fails
            #! This can mean some other error has occured on server side, such as no user found 
            auth_err.config(text = data['err'])
            return False
    else:
        try:
            #* If successded then create client and decode and save the auth ticket & TGT
            client = KClient()
            auth = client.decrypt_res(pass_hash,data['auth'])
            #* save decode auth ticket
            client.save_ticket('decAuth',auth)
            #* save original auth ticket
            client.save_ticket('auth',data['auth'])
            #* save Ticket Granting Ticket
            client.save_ticket('tgt',data['tgt'])
            return True
        except Exception as e:
            #* if any error in decryption, it means that the password provided was incorrect
            auth_err.config(text = 'Invalid Password')
            return False