import os
from multiprocessing import Process
import sys 
from editsubject import EditSubject
from tkinter import *
import json

### LOAD JSON FILE ###
with open("./subjects/em.json") as infile:
    em = json.load(infile)
with open("./subjects/mis.json") as infile:
    mis = json.load(infile)
with open("./subjects/scm.json") as infile:
    scm = json.load(infile)
    

class Control:
    def __init__(self):
        self.app = Tk()
        self.app.title("MT Senior Project")
        self.app.resizable(False,False)
        self.toplevel = None
        self.yscroll = 0
        self.mainframe=Frame(self.app)
        self.TKVARS = []
        self.mainframe.grid(row=0,column=0)
        self.canvas=Canvas(self.mainframe,bg='#ffffff',width=500,height=500)
        self.tkvar = StringVar(self.app)
        self.choices = {
            "Management Techonology (MIS)", "Management Techonology (SCM)", "Engineering Management (EM)"}
        self.tkvar.set("Management Techonology (MIS)")  # set the default option
        self.subjects = mis["subjects"]
        self.MAJOR = "mis"
        def change_dropdown(*args):
            split = self.tkvar.get().split()
            self.MAJOR = split[2].replace("(","").replace(")","")
            self.app.after(1,lambda : self.setSubjects())
        # link function to change dropdown
        self.tkvar.trace('w', change_dropdown)
        
        for s in self.subjects:
            tkVar = StringVar()
            tkVar.set(s["subject"])
            self.TKVARS.append(tkVar)
        
        self.vbar=Scrollbar(self.mainframe,orient=VERTICAL)
        self.vbar.pack(side=RIGHT,fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vbar.set)
        self.addframe()
        self.canvas.pack()
        self.app.mainloop()
        
    def addframe(self):
        self.frame = Frame(self.canvas)
        # Dictionary with options
        Label(self.frame, text=f"Select School to Edit").grid(row=0, column=1, sticky="N")
        self.popupMenu2 = OptionMenu(self.frame, self.tkvar, *self.choices)
        self.popupMenu2.grid(row=1, column=1, sticky="N")
        self.app.update()
        row_size = self.popupMenu2.winfo_height()
        self.button_1 = Button(self.frame, text='Search',
                               width=19, command=lambda: self.renderGraph())
        self.button_1 . grid(row=1, column=2, sticky="N")
        ### ADD SCROLLBAR
        # # Update content 
        self.updateEditFrame()
        self.canvas.create_window((0,0),window=self.frame,anchor="nw")
        self.canvas.configure(scrollregion=(0,0,500,(row_size+2)*len(self.subjects)))
    
    def updateEditFrame(self):
        start_row = 0
        for index,s in enumerate(self.subjects,start=0):
            start_row = index
            Button(self.frame,text="remove",command=lambda s=index:self.removeRow(s))\
                .grid(row=index+2,column=0,sticky="N")
            e = Entry(self.frame,textvariable=self.TKVARS[index])
            e.grid(row=index+2, column=1, sticky="N")
            Button(self.frame,text="add preq.",command=lambda s=index:self.addTopLevel(s))\
                .grid(row=index+2,column=2,sticky="N")
        addBtn = Button(self.frame,text="+add",command=lambda:self.addRow())
        addBtn.grid(column=0,row=start_row+3)
        updateBtn = Button(self.frame,text="update",command=lambda:self.update())
        updateBtn.grid(column=1,row=start_row+3)
        
        
    def addTopLevel(self,index):
        try:
            if self.toplevel is None or not self.toplevel.window.winfo_exists():
                self.toplevel = EditSubject(self.app,self.subjects[index],self.MAJOR)
            else:
                self.toplevel.window.lift(self.app)
        except Exception as err:
            print(err)
            self.toplevel = EditSubject(self.app,self.subjects[index],self.MAJOR)
        
    def setSubjects(self):
        if self.MAJOR == "MIS":
            self.subjects = mis["subjects"]
        elif self.MAJOR == "SCM":
            self.subjects = scm["subjects"]
        elif self.MAJOR == "EM":
            self.subjects = em["subjects"]
        
        self.TKVARS = []
        for s in self.subjects:
            tkVar = StringVar()
            tkVar.set(s["subject"])
            self.TKVARS.append(tkVar)
        self.updateFrame()
        
    def addRow(self):
        self.subjects.append({
            "subject":"",
            "school":[self.MAJOR.upper()]
        })
        self.TKVARS.append(StringVar())
        self.updateFrame()
        
    def removeRow(self,index):
        self.TKVARS.pop(index)
        self.subjects.pop(index)
        self.updateFrame()
    
        
    def updateFrame(self):
        for l in self.frame.grid_slaves():
            l.destroy()
        self.addframe()
        
    def update(self):
        subjects = [e.get() for e in self.TKVARS]
        for index,s in enumerate(self.subjects,start=0):
            s["subject"] = subjects[index]
        globals()[self.MAJOR] = {"subjects":self.subjects}
        with open(f"./subjects/{self.MAJOR}.json","w") as json_file:
            json.dump(globals()[self.MAJOR],json_file)
        
    def renderGraph(self):
        proc = Process(target=os.system,args=(f"python3.6 graph.py --major {self.MAJOR}",))
        proc.start()
        
        
if __name__=="__main__":
    Control()