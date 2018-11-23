from tkinter import *


def foo():
    print("Learn")


def bar():
    print("Play")


def center_window(w=300, h=200):
    # get screen width and height
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    # calculate position x, y
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))


lightGrey = '#f7f7f7'
grey = '#c9cace'

root = Tk()
root.configure(background=grey)
root.title("Tetromino")
root.geometry('480x280+0+0')
root.resizable(0,0)
# center_window(500, 300)
#
# label = Label(root, text="Choose setting", bg=grey)
#
#
# learn_button = Button(root, text="Learn", width=16 ,highlightbackground=grey, command=foo)
# play_button = Button(root, text="play", width=16, highlightbackground=grey, command=bar)
#
# learn_button.place(x=50, y=120)
# play_button.place(x=300, y=120)
# label.place(x=195, y=50)
# root.mainloop()
