import json
from tkinter import *
class EditSubject:

    def __init__(self,app,subject,major):
        self.major = major
        self.new_requisites = []
        self.new_rows = []
        self.PREREQUISITES = []
        self.IS_ROOT = True
        self.subject_data = subject
        self.subject = self.subject_data["subject"]
        self.window = Toplevel(app)
        self.window.title(f"Edit \"{self.subject}\" Preq.")
        self.window.resizable(False,False)
        self.frame = Frame(self.window)
        self.frame.pack()
        try:
            for (index,preq) in enumerate(self.subject_data["prerequisite"],start=1):
                tkVar = StringVar()
                tkVar.set(preq)
                self.PREREQUISITES.append(tkVar)
        except Exception as err:
            pass
        self.editFrameComponent()
        
    def editFrameComponent(self):
        try:
            if "prerequisite" in self.subject_data or len(self.subject_data["prerequisite"])>0:
                self.IS_ROOT = not self.IS_ROOT
        except Exception as err:
            pass
        Label(self.frame,text=f"Edit Prerequsiite of {self.subject}").grid(column=1,row=0,sticky="nesw")
        start_row = 1
                
        for index,tkVar in enumerate(self.PREREQUISITES,start=1):
            start_row = start_row + 1
            e = Entry(self.frame,textvariable=tkVar)
            e.grid(column=1,row=start_row)
            remove = Button(self.frame,command=lambda s=index-1:self.removeNewRow(s),text="remove")
            remove.grid(column=0,row=start_row)
        
        addBtn = Button(self.frame,text="+add",command=lambda :self.addEmptyRow())
        addBtn.grid(column=0,row=start_row+1)
        confirmBtn = Button(self.frame,text="update",command=lambda :self.update())
        confirmBtn.grid(column=1,row=start_row+1)
        
    def addEmptyRow(self):
        tkVar = StringVar()
        tkVar.set("")
        self.PREREQUISITES.append(tkVar)
        self.frame.pack_forget()
        self.frame.pack()
        self.editFrameComponent()
        
    def removeNewRow(self,index):
        self.PREREQUISITES.pop(index)
        for l in self.frame.grid_slaves():
            l.destroy()
        self.editFrameComponent()
        
    def update(self):
        prerequisite = []
        for e in self.PREREQUISITES:
            prerequisite.append(e.get())
        ### READ JSON FILE ###
        with open(f"./subjects/{self.major}.json") as json_file:
            data = json.load(json_file)
        # print(data["subjects"][self.subject])
        for index,s in enumerate(data["subjects"],start=0):
            subject = s["subject"]
            if(subject == self.subject):
                self.subject_data["prerequisite"] = \
                    [preq.get() for preq in  self.PREREQUISITES]
                data["subjects"][index]["prerequisite"] = \
                    [preq.get() for preq in  self.PREREQUISITES]
                if len(self.PREREQUISITES )==0:
                    del data["subjects"][index]["prerequisite"]
                    del self.subject_data["prerequisite"]
        ### WRITE JSON FILE ###
        with open(f"./subjects/{self.major}.json","w") as json_file:
            json.dump(data,json_file)