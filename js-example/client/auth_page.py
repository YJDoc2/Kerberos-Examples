import tkinter as tk
from data_page import Data_Page
import common

class Auth_Page(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text='Login',font='Times 20')
        label.pack(pady=10,padx=10)

        
        common.usernameIp = tk.Entry(self,bg='white',fg='black',font='Times 20')
        common.passIp = tk.Entry(self,bg='white',show='*',fg='black',font='Times 20')

        common.usernameIp.place(relx = 0.3,rely = 0.3)
        common.passIp.place(relx = 0.3,rely = 0.5)

        btnLogin = tk.Button(self,text = 'Login',padx="10",pady="5",bg='green',fg='white',font='Times 20',command=lambda : common.login() and controller.show_frame(Data_Page) )
        btnLogin.place(relx=0.4,rely=0.7)



        