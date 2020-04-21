# Flow of Program:-
# 1. Clicking on Play button executes play()
# 2. play() starts a 3sec countdown and then makes all moleHole Buttons visible
# 3. Now we run a for loop which simulates a random MoleHole to become green each second. If the user clicks on any button, we call hammerDown() function
# 4. After the for loop is over, we call gameOver() to display final score and show a close button

import tkinter as tk
import random

root = tk.Tk() #app structure, all widgets are inside this
root.title('Whach a mole!')
score=0 # Keeps a track of final score
canvas=tk.Canvas(root,height=600,width=650,bg="#263D42") 
#canvas is used to set the width and height of our application
canvas.pack() #attaches canvas to the root in the next available row (items are centered)

# Frame is used to set the window's height and width
frame=tk.Frame(root,bg="#F5F5F5")
#rel is for relative, it is used for parameters like width,height x-margin and y-margin
frame.place(relheight=0.8,relwidth=0.8,relx=0.1,rely=0.1) # 0.8 = 80% and so on.. relx is marginX (left) and rely is top
textL=tk.StringVar()	
# StringVar is used to store a variable which can be used a string for a label/any other widget. Here I have used it for countdown
# You can avoid using StringVar but typecasting a variable to string for the countdown. 

# This label will display the countdown
label1=tk.Label(frame,font='Times 15 bold',textvariable=textL,fg='black')

# Function when you click on any moleHole button
def hammerDown(buttonX):
	global score # Tells method to use the global score instead of creating another local instance
	if buttonX['bg'] == "green":
		score=score+1
		print("score is ",score)
		buttonX['bg']='red'
	else:
		print("Miss")

# 3 buttons to represent Mole holes
button1=tk.Button(frame,padx="30",pady="30",bg="red",text=" ",command=lambda: hammerDown(button1))
button2=tk.Button(frame,padx="30",pady="30",bg="red",text=" ",command=lambda: hammerDown(button2))
button3=tk.Button(frame,padx="30",pady="30",bg="red",text=" ",command=lambda: hammerDown(button3))

# Method to start a countdown of 3..2..1..
def setLabel(textL,i):
	textL.set(i)
	if i>0:
		root.after(1000,lambda: setLabel(textL,i-1)) 
		#Here we cannot use time.sleep() or it will cause the mainloop to sleep
	else:
		textL.set("Whack em!")
		game()

#Method for play
def play():
	buttonPlay.destroy() # Destroy method clears the widget
	textL.set(3)
	label1.place(relx=0.42,rely=0.2) # For countdown 
	root.after(1000,lambda: setLabel(textL,2))

# Function to set a random moleHole to green background every 1 second
def simulateMoles(randomNumber):
	# Reset color of all mole holes
	button1['bg']='red'
	button2['bg']='red'
	button3['bg']='red'
	print("Random Number: ",randomNumber)
	if(randomNumber==1):
		button1['bg']='green' # To indicate the hole where a mole comes out
	if(randomNumber==2):
		button2['bg']='green'
	if(randomNumber==3):
		button3['bg']='green'

# Function to run when the game begins
def game():
	button1.place(relx=0.15,rely="0.45")
	button2.place(relx=0.45,rely="0.45")
	button3.place(relx=0.75,rely="0.45")
	for i in range (1,11):
		random.seed(i) # A new seed is required to generate a new random number
		root.after(i*1000,lambda: simulateMoles(random.choice([1,2,3])))
	root.after(12000,lambda: gameOver()) # If we do not add the 12sec delay then this will be executed before our for loop finishes

# Shows final score and exit button
def gameOver():
	label1.destroy()
	button1.destroy()
	button2.destroy()
	button3.destroy()
	finalResult = tk.Label(frame,text="Your score is: {}".format(score),font="Times 18 bold",pady="5")
	finalResult.place(relx=0.33,rely=0.4)
	buttonClose = tk.Button(frame,text="Close",padx="10",font="Times 22 bold",pady="5",bg="red",fg="white",command=closeGame)
	buttonClose.place(relx=0.4,rely=0.8)

# Called when you click on close button, it is used to close the game
def closeGame():
	root.destroy()

buttonPlay=tk.Button(frame,text="Play!",padx="10",font="Times 22 bold",pady="5",bg="green",fg="white",command=play)
buttonPlay.place(relx=0.4,rely=0.8) #40% margin for x and 80% for y

root.mainloop()	# This runs the Tkinter GUI