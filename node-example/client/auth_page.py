import tkinter as tk
from data_page import Data_Page
import common

#! Most of tkinter code and design is done after https://pythonprogramming.net/change-show-new-frame-tkinter/
class Auth_Page(tk.Frame):
    def __init__(self,parent,controller):
        #* Display setup

        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text='Login',font='Times 20')
        label.pack(pady=10,padx=10)

        
        common.usernameIp = tk.Entry(self,bg='white',fg='black',font='Times 20')
        common.passIp = tk.Entry(self,bg='white',show='*',fg='black',font='Times 20')

        common.usernameIp.place(relx = 0.3,rely = 0.2)
        common.passIp.place(relx = 0.3,rely = 0.4)

        common.auth_err = tk.Label(self,text = '',font = 'Times 20',fg = '#ff0000')
        common.auth_err.place(relx=0.3,rely=0.7)
        
        #? We set the callback for button click to first check for login, and if it is successful, then only change the page
        btnLogin = tk.Button(self,text = 'Login',padx="10",pady="5",bg='green',fg='white',font='Times 20',command=lambda : common.login() and controller.show_frame(Data_Page) )
        btnLogin.place(relx=0.4,rely=0.5)



        