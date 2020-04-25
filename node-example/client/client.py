import tkinter as tk

from auth_page import Auth_Page
from data_page import Data_Page

#! Client GUI Page
#! Most of tkinter code and design is done after https://pythonprogramming.net/change-show-new-frame-tkinter/

class Client(tk.Tk):
    def __init__(self,*args,**kwargs):
        #* Display setup
        tk.Tk.__init__(self,*args,**kwargs)
        
        container = tk.Frame(self)

        container.pack(side='top',fill='both',expand=True)
        container.grid_rowconfigure(0, weight=1,minsize=480)
        container.grid_columnconfigure(0, weight=1,minsize=650)

        self.frames = {}
        for F in (Auth_Page,Data_Page):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(Auth_Page)

    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

#! NOTE the client in following is not Kerberos client but the client GUI class above
app = Client()
app.title('Kerberos Example')
app.mainloop()