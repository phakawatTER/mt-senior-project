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
    
THEME_COLOR = "#ffffff"
TITLE_COLOR = "#000"
PROCESSES = []
class Control:
    def __init__(self):
        self.app = Tk()
        self.app.title("MT Senior Project")
        # self.app.attributes("-alpha",0.8)
        self.app.resizable(False,False)
        self.toplevel = None
        self.yscroll = 0
        self.mainframe=Frame(self.app,bg=THEME_COLOR)
        self.TKVARS = []
        self.mainframe.grid(row=0,column=0)
        self.canvas=Canvas(self.mainframe,bg=THEME_COLOR,width=750,height=500)
        self.tkvar = StringVar(self.app)
        self.choices = {
            "Management Techonology (MIS)", "Management Techonology (SCM)", "Engineering Management (EM)"}
        self.subject_types = {
            "General",
            "Free Elective"
        }
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
            tkVar1 = StringVar()
            tkVar1.set(s["subject"])
            tkVar2 = StringVar(0)
            tkVar3 = StringVar()
            tkVar3.set("General")
            if "weight" in s:
                tkVar2.set(s["weight"])
            if "type" in s:
                tkVar3.set(s["type"])
            self.TKVARS.append((tkVar1,tkVar2,tkVar3))
        
        self.vbar=Scrollbar(self.mainframe,orient=VERTICAL)
        self.vbar.pack(side=RIGHT,fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vbar.set)
        self.canvas.bind_all("<MouseWheel>",self._on_mousewheel)
        self.addframe()
        self.canvas.pack()
        self.app.mainloop()
        
    def _on_mousewheel(self,event):
        self.canvas.yview_scroll(int(-1*(event.delta)), "units")
        
    def addframe(self):
        self.frame = Frame(self.canvas,bg=THEME_COLOR)
        # Dictionary with options
        Label(self.frame, text=f"Select School",bg=THEME_COLOR,fg=TITLE_COLOR).grid(row=0, column=1, sticky="N")
        self.schoolOptions = OptionMenu(self.frame, self.tkvar, *self.choices)
        self.schoolOptions.configure(bg=THEME_COLOR)
        self.schoolOptions.grid(row=1, column=1, sticky="N")
        Label(self.frame,text="Subject",bg=THEME_COLOR,fg=TITLE_COLOR).grid(row=2,column=1,sticky="N")
        Label(self.frame,text="Weight",bg=THEME_COLOR,fg=TITLE_COLOR).grid(row=2,column=2,sticky="N")
        Label(self.frame,text="Type",bg=THEME_COLOR,fg=TITLE_COLOR).grid(row=2,column=3,sticky="N")
        self.app.update()
        row_size = self.schoolOptions.winfo_height()
        self.button_1 = Button(self.frame, text='View Path',highlightbackground=THEME_COLOR,
                               command=lambda: self.renderGraph())
        self.button_1 . grid(row=1, column=2, sticky="N")
        ### ADD SCROLLBAR
        # # Update content 
        self.updateEditFrame()
        self.canvas.create_window((0,0),window=self.frame,anchor="nw")
        self.canvas.configure(scrollregion=(0,0,500,(row_size+3)*len(self.subjects)))
    
    def updateEditFrame(self):
        row = 3
        for index,s in enumerate(self.subjects,start=0):
            row += index
            Button(self.frame,text="remove",highlightbackground=THEME_COLOR,command=lambda s=index:self.removeRow(s))\
                .grid(row=row,column=0,sticky="N")
            subject_entry = Entry(self.frame,textvariable=self.TKVARS[index][0],highlightbackground=THEME_COLOR)
            subject_entry.grid(row=row, column=1, sticky="N")
            weight_entry = Entry(self.frame,textvariable=self.TKVARS[index][1], width=20,highlightbackground=THEME_COLOR)
            weight_entry.grid(row=row, column=2,sticky="N")
            subject_type_option = OptionMenu(self.frame, self.TKVARS[index][2], *self.subject_types)
            subject_type_option.grid(row=row, column=3,sticky="N")
            Button(self.frame,text="edit preq.",highlightbackground=THEME_COLOR,command=lambda s=index:self.addTopLevel(s))\
                .grid(row=row,column=4,sticky="N")
        addBtn = Button(self.frame,text="+add",highlightbackground=THEME_COLOR,command=lambda:self.addRow())
        addBtn.grid(column=0,row=row+1)
        updateBtn = Button(self.frame,text="update",highlightbackground=THEME_COLOR,command=lambda:self.update())
        updateBtn.grid(column=1,row=row+1)
        
        
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
            tkVar1 = StringVar()
            tkVar1.set(s["subject"])
            tkVar2 = StringVar(0)
            tkVar3 = StringVar()
            tkVar3.set("General")
            if "weight" in s:
                tkVar2.set(s["weight"])
            if "type" in s:
                tkVar3.set(s["type"])
            self.TKVARS.append((tkVar1,tkVar2,tkVar3))
        self.updateFrame()
        
    def addRow(self):
        self.subjects.append({
            "subject":"",
            "school":[self.MAJOR.upper()]
        })
        TYPE = StringVar()
        TYPE.set("General")
        self.TKVARS.append((StringVar(),StringVar(),TYPE))
        self.updateFrame()
        
    def removeRow(self,index):
        self.TKVARS.pop(index)
        self.subjects.pop(index)
        self.updateFrame()
    
        
    def updateFrame(self):
        for index,l in enumerate(self.frame.grid_slaves(),start=0):
            l.destroy()
        self.addframe()
        
    def update(self):
        for index,s in enumerate(self.subjects,start=0):
            s["subject"] = self.TKVARS[index][0].get()
            if self.TKVARS[index][1].get() != "":
                s["weight"] = int(self.TKVARS[index][1].get())
            else:
                s["weight"] = 1
            s["type"] = self.TKVARS[index][2].get()
        globals()[self.MAJOR] = {"subjects":self.subjects}
        with open(f"./subjects/{self.MAJOR}.json","w") as json_file:
            json.dump(globals()[self.MAJOR],json_file)
        
    def renderGraph(self):
        # proc = Process(target=os.system,args=(f"python3.6 graph.py --major {self.MAJOR}",))
        proc = Process(target=os.system,args=(f"python3 graph.py --major {self.MAJOR}",))
        PROCESSES.append(proc)
        proc.daemon = True
        proc.start()
        
        
if __name__=="__main__":
    Control()