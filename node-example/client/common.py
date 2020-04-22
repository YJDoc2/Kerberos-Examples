import tkinter as tk
import random
from Crypto.Hash import SHA256
from Kerberos.kerberso_client import Client as  KClient
import requests

username =''
password =''

usernameIp = None
passIp = None

client = None


auth_err = None

def login():
    global username,password,usernameIp,passIp,client
    username = usernameIp.get()
    password = passIp.get()

    if username.strip() == '' or password.strip() == '':
        auth_err.config(text = 'Please Fill all details')
        return False


    hash = SHA256.new()
    hash.update(password.encode('ascii'))
    pass_hash = hash.hexdigest().encode('ascii')[:32]

    rand = random.randint(0,10000)
    
    
    res = requests.post('http://localhost:5001',data={'username':username,'rand':rand})
    data = res.json()
    try:
        if not data['success']:
            auth_err.config(text = data['err'])
            return False
        else:
            client = KClient(pass_hash.decode('ascii'))
            auth = client.decrypt_res(data['auth'],pass_hash)
            client.save_ticket('decAuth',auth)
            client.save_ticket('auth',data['auth'])
            client.save_ticket('tgt',data['tgt'])
            return True
    except:
        auth_err.config(text = 'Invalid Password')
        return False