import json
import os
from multiprocessing import Process
import sys
import copy
from editsubject import EditSubject
from graphframe import GraphFrame
from tkinter import *
from tkinter import messagebox
### LOAD JSON FILE ###
with open("./subjects/em.json") as infile:
    em = json.load(infile)
with open("./subjects/mis.json") as infile:
    mis = json.load(infile)
with open("./subjects/scm.json") as infile:
    scm = json.load(infile)

THEME_COLOR = "#ffffff"
TITLE_COLOR = "#000"


class Control:
    def __init__(self):
        self.app = Tk()
        self.app.title("MT Senior Project")
        # self.app.attributes("-alpha",0.8)
        self.app.resizable(False, False)
        self.editsubject_toplevel = None
        self.graphframe = None
        self.search_matched = False
        self.matched_index = []
        self.yscroll = 0
        self.mainframe = Frame(self.app, bg=THEME_COLOR)
        self.TKVARS = []
        self.mainframe.grid(row=0, column=0)
        self.canvas = Canvas(
            self.mainframe, bg=THEME_COLOR, height=500)
        self.tkvar = StringVar(self.app)
        self.choices = {
            "Management Techonology (MIS)", "Management Techonology (SCM)", "Engineering Management (EM)"}
        self.year_choices = {"year 1", "year 2", "year 3", "year 4"}
        self.subject_types = {
            "General",
            "Free Elective"
        }
        # set the default option
        self.tkvar.set("Management Techonology (MIS)")

        self.selected_year = StringVar(self.app)
        self.selected_year.set("year 1")

        self.subjects = copy.deepcopy(mis["subjects"])
        self.MAJOR = "mis"

        def change_dropdown(*args):
            split = self.tkvar.get().split()
            self.MAJOR = split[2].replace("(", "").replace(")", "")
            self.MAJOR = self.MAJOR.lower()
            self.app.after(1, lambda: self.setSubjects())
        # link function to change dropdown
        self.tkvar.trace('w', change_dropdown)

        for s in self.subjects:
            tkVar1 = StringVar(self.app)
            tkVar1.set(s["subject"])
            tkVar2 = StringVar(0)
            tkVar3 = StringVar(self.app)
            tkVar3.set("General")
            if "weight" in s:
                tkVar2.set(s["weight"])
            if "type" in s:
                tkVar3.set(s["type"])
            self.TKVARS.append((tkVar1, tkVar2, tkVar3))
        self.addframe()
        self.vbar = Scrollbar(self.mainframe, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.pack()

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                try:
                    self.graphframe.app.destroy()
                    self.graphframe.graph.plt.close()
                except:
                    pass
                self.app.destroy()
        self.app.protocol("WM_DELETE_WINDOW", on_closing)
        self.app.mainloop()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta)), "units")

    def _search_submit(self, *args, **kwargs):
        search_text = self.search_text.get().lower()
        self.matched_index = [index for index, subject in enumerate(globals(
        )[self.MAJOR.lower()]["subjects"], start=0) if search_text in subject["subject"].lower()]
        if len(self.matched_index) > 0:
            if(search_text != ""):
                self.search_result_label.configure(text=f"Result for \"{self.search_text.get()}\". Found {len(self.matched_index)} result(s)",fg="red")
            else:
                self.search_result_label.configure(text="")
            self.search_matched = True
        else:
            self.search_result_label.configure(text="")
            self.search_matched = False
        self.updateFrame()

    def addframe(self):
        self.frame = Frame(self.canvas, bg=THEME_COLOR)
        Label(self.frame, text=f"Select School", bg=THEME_COLOR,
              fg=TITLE_COLOR).grid(row=1, column=1, sticky="E")
        self.search_frame = Frame(self.frame, bg=THEME_COLOR)
        self.search_frame.grid(row=2, column=1, columnspan=3)
        self.input_frame = Frame(self.frame)
        self.input_frame.grid(row=4, column=1, columnspan=4)
        self.bottom_frame = Frame(self.frame)
        self.bottom_frame.grid(row=5, column=1, columnspan=4)

        # SEARCH BOX WIDGET
        self.search_text = StringVar(self.app)
        Label(self.search_frame, text=f"Search for", bg=THEME_COLOR,
              fg=TITLE_COLOR).grid(row=2, column=1)
        search_box = Entry(self.search_frame, textvariable=self.search_text)
        search_box.grid(row=2, column=2)
        search_box.bind("<Return>", self._search_submit)
        self.search_result_label = Label(self.search_frame, text="", bg=THEME_COLOR,
              fg=TITLE_COLOR)
        self.search_result_label.grid(row=3, columnspan=2,column=1)

        # BOTTOM SECTION
        addBtn = Button(self.bottom_frame, text="+add", bg="#88c878", fg=THEME_COLOR,
                        highlightbackground=THEME_COLOR, command=lambda: self.addRow())
        addBtn.grid(column=0, row=1)
        updateBtn = Button(self.bottom_frame, text="update", bg="#318ee8", fg="#fff",
                           highlightbackground=THEME_COLOR, command=lambda: self.update())
        updateBtn.grid(column=1, row=1)

        self.schoolOptions = OptionMenu(self.frame, self.tkvar, *self.choices)
        self.schoolOptions.configure(bg=THEME_COLOR)
        self.schoolOptions.grid(row=1, column=2, sticky="NESW")
        Label(self.frame, text="Subject", bg=THEME_COLOR,
              fg=TITLE_COLOR).grid(row=3, column=1, sticky="N")
        Label(self.frame, text="Weight", bg=THEME_COLOR,
              fg=TITLE_COLOR).grid(row=3, column=2, sticky="N")
        Label(self.frame, text="Type", bg=THEME_COLOR,
              fg=TITLE_COLOR).grid(row=3, column=3, sticky="N")
        self.row_size = self.schoolOptions.winfo_height()
        self.button_1 = Button(self.frame, text='View Path', bg="#318ee8", fg="#fff",
                               command=lambda: self.renderGraph())
        self.button_1 . grid(row=1, column=3, sticky="W")
        # ADD SCROLLBAR
        # # Update content
        self.addInputFrame()
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.app.update()
        self.canvas.configure(width=self.frame.winfo_width())
        self.updateScrollRegion()

    def addInputFrame(self):
        for index in range(0, len(self.subjects)):
            self.addInputChildFrame(index)

    def addInputChildFrame(self, row):
        input_group_frame = Frame(self.input_frame)
        input_group_frame.grid(row=row, column=0, sticky="N")
        Button(input_group_frame, text="remove", bg="#e6245c", fg="white", highlightbackground=THEME_COLOR, command=lambda s=row: self.removeRow(s))\
            .grid(row=row, column=0, sticky="N")
        subject_entry = Entry(
            input_group_frame, textvariable=self.TKVARS[row][0], highlightbackground=THEME_COLOR)
        subject_entry.grid(row=row, column=1, sticky="N")
        weight_entry = Entry(
            input_group_frame, textvariable=self.TKVARS[row][1], width=20, highlightbackground=THEME_COLOR)
        weight_entry.grid(row=row, column=2, sticky="N")
        subject_type_option = OptionMenu(
            input_group_frame, self.TKVARS[row][2], *self.subject_types)
        subject_type_option.configure(width=20)
        subject_type_option.grid(row=row, column=3, sticky="N")
        Button(input_group_frame, text="edit prerequisite", bg="#88c878", fg="#fff", highlightbackground=THEME_COLOR, command=lambda s=row: self.openEditPreqWindow(s))\
            .grid(row=row, column=4, sticky="N")

    def openEditPreqWindow(self, index):
        # pass
        try:
            if self.editsubject_toplevel is None or not self.editsubject_toplevel.window.winfo_exists():
                self.editsubject_toplevel = EditSubject(
                    self.app, self.subjects[index], self.MAJOR)
            else:
                self.editsubject_toplevel.window.lift(self.app)
        except Exception as err:
            print(err)
            self.editsubject_toplevel = EditSubject(
                self.app, self.subjects[index], self.MAJOR)

    def setSubjects(self):
        self.subjects = copy.deepcopy(globals()[self.MAJOR]["subjects"])
        self.TKVARS = []
        self.search_matched = False
        self.matched_index = []
        for s in self.subjects:
            tkVar1 = StringVar(self.app)
            tkVar1.set(s["subject"])
            tkVar2 = StringVar(0)
            tkVar3 = StringVar(self.app)
            tkVar3.set("General")
            if "weight" in s:
                tkVar2.set(s["weight"])
            if "type" in s:
                tkVar3.set(s["type"])
            self.TKVARS.append((tkVar1, tkVar2, tkVar3))
        self.updateFrame()

    def addRow(self):
        self.subjects.append({
            "subject": "",
            "school": [self.MAJOR.upper()]
        })
        type = StringVar(self.app)
        type.set("General")
        weight = StringVar(self.app)
        weight.set(1)
        self.TKVARS.append((StringVar(self.app), weight, type))

        self.addInputChildFrame(len(self.TKVARS)-1)
        self.updateScrollRegion()
        self.canvas.yview_moveto(self.frame.winfo_height())

    def removeRow(self, index):
        subject = self.subjects[index]["subject"]
        if subject != "":
            if not messagebox.askokcancel("Remove", f"Do you want to remove \"{subject}\""):
                return
        self.TKVARS.pop(index)
        self.subjects.pop(index)
        self.updateFrame(index=index)

    def updateScrollRegion(self):
        self.app.update()
        self.canvas.configure(scrollregion=(
            0, 0, 500, self.frame.winfo_height()))

    def updateFrame(self, index=None):

        for i, item in enumerate(self.input_frame.winfo_children(), start=0):
            if self.search_matched:
                item.grid_forget()
                if i == index:
                    item.destroy()
            else:
                if i == index:
                    item.grid_forget()
                    item.destroy()
                    break
                elif index == None:
                    item.grid_forget()
                    item.destroy()
        if self.search_matched:
            try:
                for idx,i in enumerate(self.matched_index,start=0):
                    if index == i :
                        self.matched_index.pop(idx)
                        break
                for idx,i in enumerate(self.matched_index,start=0):
                    if i>=index :
                        self.matched_index[idx] = self.matched_index[idx] - 1
                        
            except Exception as err:
                pass
            if len(self.matched_index) == 0:
                self.search_matched = False
            print(str(self.matched_index))
        for i, item in enumerate(self.input_frame.winfo_children(), start=0):
            if self.search_matched and i not in self.matched_index :
                continue
            widgets = item.winfo_children()
            remove_button = widgets[0]
            edit_preq_button = widgets[4]
            remove_button.configure(command=lambda s=i: self.removeRow(s))
            edit_preq_button.configure(
                command=lambda s=i: self.openEditPreqWindow(s))
            item.grid()

        if index == None and not self.search_matched:
            self.addInputFrame()

        # update scroll region
        self.updateScrollRegion()

    def update(self):
        if not messagebox.askokcancel("Update", f"Do you want to update major \"{self.MAJOR.upper()}\""):
            return
        for index, s in enumerate(self.subjects, start=0):
            s["subject"] = self.TKVARS[index][0].get()
            if self.TKVARS[index][1].get() != "":
                s["weight"] = int(self.TKVARS[index][1].get())
            else:
                s["weight"] = 1
            s["type"] = self.TKVARS[index][2].get()
        globals()[self.MAJOR] = {"subjects": self.subjects}

        with open(f"./subjects/{self.MAJOR}.json", "w") as json_file:
            json.dump(globals()[self.MAJOR], json_file)

    def renderGraph(self):
        try:
            self.graphframe.app.destroy()
        except:
            pass
        self.graphframe = GraphFrame(major=self.MAJOR.upper(), master=self.app)
        self.graphframe.app.mainloop()


if __name__ == "__main__":
    Control()
