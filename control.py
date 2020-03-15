import json
import os
from multiprocessing import Process
import copy
from graph import Render
from tkinter import *
from sys import platform
from tkinter import messagebox
current_directory = os.path.dirname(__file__)
data_dir = os.path.join(current_directory,"subjects")
### LOAD JSON FILE ###
for file in os.listdir(data_dir):
    name,ext = os.path.splitext(file)
    if ext == ".json":
        try:
            with open(os.path.join(data_dir,file)) as infile:
                globals()[name] = json.load(infile)
        except:
            pass
        
THEME_COLOR = "#ffffff"
TITLE_COLOR = "#000"

class Control:
    def __init__(self):
        self.app = Tk()
        self.app.title("MT Senior Project")
        self.app.resizable(False, False)
        self.graphframe = None
        self.search_matched = False
        self.matched_index = []
        self.yscroll = 0
        self.mainframe = Frame(self.app, bg=THEME_COLOR)
        self.TKVARS = []
        self.mainframe.grid(row=2)
        self.canvas = Canvas(
            self.mainframe, bg=THEME_COLOR, height=350)
        self.tkvar = StringVar(self.app)
        ## list of school in SIIT
        self.choices = {
            "Management Techonology (MIS)", 
            "Management Techonology (SCM)", 
            "Engineering Management (EM)",
            "Information Technology (IT)",
            "Industrial Engineering (IE)",
            "Mechinical Engineering (ME)",
            "Electrical Engineering (EE)",
            "Computer Engineering (CPE)",
            "Civil Engineering (CE)",
            "Chemical Engineering (ChE)",
            
        }
        self.year_choices = {"year 1", "year 2", "year 3", "year 4"}
        self.subject_types = {
            "General",
            "Free Elective",
            "Senior Project"
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

        self.load_subject_data()
        self.add_head()
        self.addframe()
        self.add_bottom()
        self.vbar = Scrollbar(self.mainframe, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.hbar = Scrollbar(self.mainframe, orient=HORIZONTAL)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.hbar.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=self.vbar.set,
                           xscrollcommand=self.hbar.set)
        # vertical mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_y)
        # horizontal mousewheel
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel_x)
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

    def _on_mousewheel_y(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta)), "units")

    def _on_mousewheel_x(self, event):
        self.canvas.xview_scroll(int(-1*(event.delta)), "units")

    def _search_submit(self, *args, **kwargs):
        search_text = self.search_text.get().lower()
        self.matched_index = [index for index, subject in enumerate(
            self.subjects, start=0) if search_text in subject["subject"].lower()]
        if len(self.matched_index) > 0:
            if(search_text != ""):
                self.search_result_label.configure(
                    text=f"Result for \"{self.search_text.get()}\". Found {len(self.matched_index)} result(s)", fg="red")
            else:
                self.search_result_label.configure(text="")
            self.search_matched = True
        else:
            self.search_result_label.configure(text="")
            self.search_matched = False
        self.updateFrame()

    def add_head(self):
        frame = Frame(self.app)
        frame.grid(row=0)
        Label(frame, text=f"Select School", bg=THEME_COLOR,
              fg=TITLE_COLOR).grid(row=1, column=1, sticky="E")
        self.search_frame = Frame(frame, bg=THEME_COLOR)
        self.search_frame.grid(row=2, column=1, columnspan=3)

        # SEARCH BOX WIDGET
        self.search_text = StringVar(self.app)
        Label(self.search_frame, text=f"Search for", bg=THEME_COLOR,
              fg=TITLE_COLOR).grid(row=2, column=1)
        search_box = Entry(self.search_frame, textvariable=self.search_text)
        search_box.grid(row=2, column=2)
        search_box.bind("<Return>", self._search_submit)
        self.search_result_label = Label(self.search_frame, text="", bg=THEME_COLOR,
                                         fg=TITLE_COLOR)
        self.search_result_label.grid(row=3, columnspan=2, column=1)

        self.schoolOptions = OptionMenu(frame, self.tkvar, *self.choices)
        self.schoolOptions.configure(bg=THEME_COLOR)
        self.schoolOptions.grid(row=1, column=2, sticky="NESW")

        self.row_size = self.schoolOptions.winfo_height()
        self.button_1 = Button(frame, text='View Path', bg="#318ee8", fg="#000",
                               command=lambda: self.renderGraph())
        self.button_1 . grid(row=1, column=3, sticky="W")
        frame2 = Frame(self.app)
        frame2.grid(row=1,sticky="EW")
        Label(frame2, text="", bg=THEME_COLOR,width=8,
            fg=TITLE_COLOR).grid(row=3, column=1,sticky="W")
        Label(frame2, text="Subject", bg=THEME_COLOR,width=10,
            fg=TITLE_COLOR).grid(row=3, column=2,sticky="W")
        Label(frame2, text="Weight", bg=THEME_COLOR,width=8,
            fg=TITLE_COLOR).grid(row=3, column=3,sticky="W")
        Label(frame2, text="Type", bg=THEME_COLOR,width=15,
            fg=TITLE_COLOR).grid(row=3, column=4,sticky="W")
        Label(frame2, text="Add Prerequisite", bg=THEME_COLOR,width=12,
            fg=TITLE_COLOR).grid(row=3, column=5,sticky="E")

    def add_bottom(self):
        # BOTTOM SECTION
        self.bottom_frame = Frame(self.app)
        self.bottom_frame.grid(row=3)
        addBtn = Button(self.bottom_frame, text="+ new subject", bg="#88c878",fg="#000",
                        highlightbackground=THEME_COLOR, command=lambda: self.addRow())
        addBtn.grid(column=0, row=1)
        updateBtn = Button(self.bottom_frame, text="update", bg="#318ee8",fg="#000",
                           highlightbackground=THEME_COLOR, command=lambda: self.update())
        updateBtn.grid(column=1, row=1)

    def addframe(self):
        self.frame = Frame(self.canvas, bg=THEME_COLOR)
        self.input_frame = Frame(self.frame)
        self.input_frame.grid(row=4, column=1, columnspan=4)
        # ADD SCROLLBAR
        # # Update content
        self.addInputFrame()
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.app.update()
        self.canvas.configure(width=self.frame.winfo_width())
        self.updateScrollRegion()

    def addInputFrame(self):
        render_list = [i for i in range(0, len(self.TKVARS))]
        if self.search_matched:
            render_list = self.matched_index
        for pos,index in enumerate(render_list,start=0):
            self.addInputChildFrame(index)

    def addInputChildFrame(self, index):
        input_group_frame = Frame(self.input_frame)
        input_group_frame.grid(row=index+1, column=0, sticky="EW")

        Button(input_group_frame, text="remove", bg="#e6245c", fg="#000", highlightbackground=THEME_COLOR, command=lambda s=index: self.removeRow(s))\
            .grid(row=index+1, column=0, sticky="N")
        subject_entry = Entry(
            input_group_frame, textvariable=self.TKVARS[index][0], highlightbackground=THEME_COLOR)
        subject_entry.grid(row=index+1, column=1, sticky="N")
        self.TKVARS[index][0].trace("w",lambda name,_index,mode,var=self.TKVARS[index][0]:self.capitalize_input(var))
        subject_entry.configure(width=10)
        weight_entry = Entry(
            input_group_frame, textvariable=self.TKVARS[index][1], width=20, highlightbackground=THEME_COLOR)
        weight_entry.grid(row=index+1, column=2, sticky="N")
        self.TKVARS[index][1].trace("w",lambda name,_index,mode,var=self.TKVARS[index][1]:self.numeric_input(var))
        weight_entry.configure(width=5)
        subject_type_option = OptionMenu(
            input_group_frame, self.TKVARS[index][2], *self.subject_types)
        subject_type_option.configure(width=15)
        subject_type_option.grid(row=index+1, column=3, sticky="N")

        ## Prerequisite subjects
        prerequisite_frame = Frame(input_group_frame)
        prerequisite_frame.grid(row=index+1, column=4)
        # loop over preqrequsiite list
        for i, var in enumerate(self.TKVARS[index][3], start=0):
            current_row = index+i+1
            prereq_input = Entry(prerequisite_frame, textvariable=var)
            prereq_input.configure(width=8)
            prereq_input.grid(row=current_row, column=1, sticky="W", padx=31.5)
            Button(prerequisite_frame, text="x",command=lambda target=(index, i): self.remove_prerequsite(target)).grid(
                row=current_row, column=0, sticky="W", columnspan=2)
            # var.trace("w",lambda name,_index,mode,var=var:self.capitalize_input(var))
        current_row = (index+1) + len(self.TKVARS[index][3])
        Button(input_group_frame, text="+ prerequisite", command=lambda _index=index: self.add_prerequisite(_index)).grid(
            row=current_row, column=4, sticky="w")
        
    # callback  function to automatically capitalize input
    def capitalize_input(*args):
        sv = args[1]
        sv.set(sv.get().upper())
    
    def numeric_input(*args):
        sv = args[1]
        try:
            current_char = sv.get()[-1]
            if not current_char.isnumeric():
                messagebox.showinfo("Input Error","Please enter numeric input...")
                current_char = "0"
        except:
            current_char = "0"
        sv.set(current_char)
        
    # add empty prerequisite entry to input frame
    def add_prerequisite(self, index):
        self.TKVARS[index][3].append("")
        self.updateFrame()

    # remove prerequisite entry
    def remove_prerequsite(self, target):
        i, j = target
        subject = self.subjects[i]["subject"]
        if len(self.TKVARS[i][3][j].get()) > 0:
            if messagebox.askokcancel(
                    "Prerequisite of {}".format(subject), "Do you want to remove {}?".format(self.TKVARS[i][3][j].get())):
                self.TKVARS[i][3].pop(j)
                self.updateFrame()
        else:
            self.TKVARS[i][3].pop(j)
            self.updateFrame()

    def load_subject_data(self):
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

            prerequisite = []
            if "prerequisite" in s:
                for prereq in s["prerequisite"]:
                    var = prereq
                    prerequisite.append(var)

            self.TKVARS.append((tkVar1, tkVar2, tkVar3, prerequisite))

    def setSubjects(self):
        self.subjects = copy.deepcopy(globals()[self.MAJOR]["subjects"])
        self.TKVARS = []
        self.search_matched = False
        self.matched_index = []
        self.load_subject_data()
        self.updateFrame()

    def addRow(self):
        self.subjects.append({
            "subject": "",
            "school": [self.MAJOR.upper()]
        })
        s_type = StringVar(self.app)
        s_type.set("General")
        weight = StringVar(self.app)
        weight.set(1)
        self.TKVARS.append((StringVar(self.app), weight,
                            s_type, []))
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
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def updateFrame(self, index=None):
        for i, item in enumerate(self.input_frame.winfo_children(), start=0):
            item.grid_forget()
            item.destroy()
        if self.search_matched:
            self.matched_index = []
            for _index, s in enumerate(self.subjects, start=0):
                subject = s["subject"]
                if self.search_text.get().lower() in subject.lower():
                    self.matched_index.append(_index)

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
            s["prerequisite"] = [pre.get() for pre in self.TKVARS[index]
                                 [3] if len(pre.get()) > 0]
        globals()[self.MAJOR] = {"subjects": self.subjects}

        with open(f"./subjects/{self.MAJOR}.json", "w") as json_file:
            json.dump(globals()[self.MAJOR], json_file)

    def renderGraph(self):
        Render(major=self.MAJOR)


if __name__ == "__main__":
    Control()
