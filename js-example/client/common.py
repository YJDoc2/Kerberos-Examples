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

def login():
    global username,password,usernameIp,passIp,client
    username = usernameIp.get()
    password = passIp.get()
    hash = SHA256.new()
    hash.update(password.encode('ascii'))
    pass_hash = hash.hexdigest().encode('ascii')[:32]

    rand = random.randint(0,10000)
    
    
    res = requests.post('http://localhost:5001',data={'username':username,'rand':rand})
    data = res.json()
    try:
        if not data['success']:
            print(data['err'])
            return False
        else:
            client = KClient(pass_hash.decode('ascii'))
            auth = client.decrypt_res(data['auth'],pass_hash)
            client.save_ticket('decAuth',auth)
            client.save_ticket('auth',data['auth'])
            client.save_ticket('tgt',data['tgt'])
            return True
    except:
        print('Invalid Password')
        return