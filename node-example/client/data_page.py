import tkinter as tk
import requests
import common
import time
import random

#? It may be possible that by the time our request sent to a server using Kerberos reches it,
#? the ticket that we sent is gets expired , in edge cases.
#? So we use a error delta here so than in refresh ticket function below if the remaining time for ticket's expiry is
#? less than this we first take a fresh ticket and then make the request.
errDelta = 5000

#! Most of tkinter code and design is done after https://pythonprogramming.net/change-show-new-frame-tkinter/
bookInput = None
buttonGet = None
buttonSend = None
text = None


#* A helper function to check if we have the required ticket,
#* and if it is expired/close to expiry , take a new one
#? name is the name of server we want the ticket for
#? the ricket is saved in client by the 'name' and
#? the response that is sent along with the ticket is decrypted and seved by name 'dec{name}'
#? so for a server A, the ticket will be saved with name 'A' and decrypted response saved with name 'decA'
def refreshTicket(name):

    #? First try to get the ticket and decoded response , the get function returns None if the required name is not found
    ticket = common.client.get_ticket(name)
    decTicket = common.client.get_ticket(f'dec{name}')

    #? If ticket is not found or it is close to expiry , ask TGS for a new ticket
    if ticket == None or decTicket['timestamp'] + decTicket['lifetime'] < int(time.time()*1000) - 5000:
        #* get response we got when logging in
        auth = common.client.get_ticket('decAuth')
        req = {}
        req['uid1'] = auth['uid1']
        req['uid2'] = auth['uid2']
        req['rand'] = random.randint(0,10000)
        req['target'] = name
        # TODO CHANGE REQ STRUCT
        #* encrypt request with key provided in auth ticket
        encReq = common.client.encrypt_req(req,auth['key'])
        #* make actual http request
        res = requests.post('http://localhost:5002',data={'req':encReq,'tgt':common.client.get_ticket('tgt'),'user':common.username})
        data = res.json()
        res.close()
        if not data['success']:
            raise Exception(data['err'])
        else:
            #* If successful save the encrypted ticket we got and save the response we got along with it after decryption
            resDec = common.client.decrypt_res(data['res'],auth['key'])
            common.client.save_ticket(name,data['ticket'])
            common.client.save_ticket(f'dec{name}',resDec)

    #* Here we now have the ticket saved in client
    return


class Data_Page(tk.Frame):
    def __init__(self,parent,controller):
        global buttonGet,buttonSend,bookInput,text
        #* Display setup
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
        global buttonGet,buttonSend,bookInput,text
        #* First clear the error
        self.err.config(text = '')

        #* make sure we have the ticket
        refreshTicket('Books')
        req = {}
        req['rand'] = random.randint(0,10000)
        req['user'] = common.username

        #* Ticket which is encrypted and can be decrypted only by the respective server and TGS
        ticket = common.client.get_ticket('Books')

        #* response we got with ticket giving us key to encrypt our request (data not http) to send to server
        decT = common.client.get_ticket('decBooks')

        #* encrypt the req(data, not http) with key given in response alogn with ticket
        strEncReq = common.client.encrypt_req(req,decT['key'],decT['init_val'])
        #* make actual http request to server
        res = requests.post('http://localhost:5003/data',data={'req':strEncReq,'ticket':ticket,'user':common.username},timeout = 1)
        data = res.json()
        res.close()
        txt = ''

        if data['success']:
            #* if succeded decryt the response (data not http)
            decRes = common.client.decrypt_res(data['res'],decT['key'],decT['init_val'])
            #* show data to user
            for i,b in enumerate(decRes):
                txt += f'Book {i+1} : {b}\n'

            text.delete('1.0',tk.END)
            text.insert(tk.INSERT,txt)
        else:
            #* show error
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