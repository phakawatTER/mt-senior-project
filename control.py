from tkinter import *
import tkinter as ttk
from threading import Thread
import os
from multiprocessing import Process
import sys 

class Control:
    def __init__(self):
        self.root = Tk()
        self.root.title("MT SENIOR PROJECT")
        self.root.resizable(False,False)
        # Add a grid
        self.mainframe = Frame(self.root)
        
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.pack(pady=100, padx=100)

        # Create a Tkinter variable
        self.tkvar = StringVar(self.root)

        # Dictionary with options
        self.choices = {
            "Management Techonology (MIS)", "Management Techonology (SCM)", "Engineering Management (EM)"}
        self.tkvar.set("Management Techonology (MIS)")  # set the default option

        self.popupMenu = OptionMenu(self.mainframe, self.tkvar, *self.choices)
        Label(self.mainframe, text="Choose School").grid(row=1, column=1)
        self.popupMenu.grid(row=2, column=1)
        self.button_1 = Button(self.mainframe, text='Search',
                               width=19, command=lambda: self.renderGraph())
        # self.button_1.configure(highlightbackground="green",background="green")
        self.button_1 . grid(row=3, column=1)

        # on change dropdown value
        def change_dropdown(*args):
            pass
            # print(self.tkvar.get())

        # link function to change dropdown
        self.tkvar.trace('w', change_dropdown)
        self.root.mainloop()

    def renderGraph(self):
        print(self.tkvar.get())
        split = self.tkvar.get().split()
        MAJOR = split[2].replace("(","").replace(")","")
        proc = Process(target=os.system,args=(f"python3.6 graph.py --major {MAJOR}",))
        proc.start()
if __name__ == "__main__":
    control = Control()
