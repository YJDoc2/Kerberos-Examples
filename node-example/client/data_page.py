import tkinter as tk
import requests
import common
import time
import random

errDelta = 5000

#! Most of tkinter code and design is done after https://pythonprogramming.net/change-show-new-frame-tkinter/
bookInput = None
buttonGet = None
buttonSend = None
text = None


def refreshTicket(name):
    ticket = common.client.get_ticket(name)
    decTicket = common.client.get_ticket(f'dec{name}')
    if ticket == None or decTicket['timestamp'] + decTicket['lifetime'] < int(time.time()*1000) - 5000:
        auth = common.client.get_ticket('decAuth')
        req = {}
        req['uid1'] = auth['uid1']
        req['uid2'] = auth['uid2']
        req['rand'] = random.randint(0,10000)
        req['target'] = name
        encReq = common.client.encrypt_req(req,auth['key'])
        res = requests.post('http://localhost:5002',data={'req':encReq,'tgt':common.client.get_ticket('tgt'),'user':common.username})
        data = res.json()
        res.close()
        if not data['success']:
            raise Exception(data['err'])
        else:
            resDec = common.client.decrypt_res(data['res'],auth['key'])
            common.client.save_ticket(name,data['ticket'])
            common.client.save_ticket(f'dec{name}',resDec)

    return


class Data_Page(tk.Frame):
    def __init__(self,parent,controller):
        global buttonGet,buttonSend,bookInput,text
        tk.Frame.__init__(self,parent)
        bookInput = tk.Entry(self,bg='white',fg='black',font='Times 20')
        bookInput.place(relx = 0.3,rely = 0.6)
        buttonGet = tk.Button(self,text = 'Get Data',padx="10",pady="5",bg='green',fg='white',font='Times 22 bold',command=self.get_data)
        buttonGet.place(relx = 0.2,rely=0.7)

        buttonSend = tk.Button(self,text = 'Send Data',padx="10",pady="5",bg='green',fg='white',font='Times 22 bold',command=self.send_data)
        buttonSend.place(relx = 0.6,rely=0.7)

        self.err = tk.Label(self,text = '',font = 'Times 20',fg = '#ff0000')
        self.err.place(relx=0.3,rely=0.85)

        text = tk.Text(self,height = 15,width=50,font='Times 10')
        text.place(relx=0.2,rely=0.05)

    def get_data(self):
        self.err.config(text = '')
        global buttonGet,buttonSend,bookInput,text
        refreshTicket('Books')
        req = {}
        req['rand'] = random.randint(0,10000)
        req['user'] = common.username
        ticket = common.client.get_ticket('Books')
        decT = common.client.get_ticket('decBooks')
        strEncReq = common.client.encrypt_req(req,decT['key'],decT['init_val'])
        res = requests.post('http://localhost:5003/data',data={'req':strEncReq,'ticket':ticket,'user':common.username},timeout = 1)
        data = res.json()
        res.close()
        txt = ''
        if data['success']:
            decRes = common.client.decrypt_res(data['res'],decT['key'],decT['init_val'])
            for i,b in enumerate(decRes):
                txt += f'Book {i+1} : {b}\n'

            text.delete('1.0',tk.END)
            text.insert(tk.INSERT,txt)
        else:
            self.err.config(text = data['err'])
            return
            
        

    def send_data(self):
        global buttonGet,buttonSend,bookInput
        self.err.config(text = '')
        book = bookInput.get().strip()
        if book == '':
            self.err.config(text = 'Please fill input for data')
            return

        refreshTicket('Books')
        req = {'book':book}
        req['rand'] = random.randint(0,10000)
        ticket = common.client.get_ticket('Books')
        decT = common.client.get_ticket('decBooks')
        strEncReq = common.client.encrypt_req(req,decT['key'],decT['init_val'])
        res = requests.post('http://localhost:5003/add',data={'req':strEncReq,'ticket':ticket,'user':common.username},timeout = 1)
        data = res.json()
        res.close()
        if data['success']:
            decRes = common.client.decrypt_res(data['res'],decT['key'],decT['init_val']) 
            #print(decRes) # {}
            bookInput.delete(0,tk.END)
        else:
            self.err.config(text = data['err'])
            return