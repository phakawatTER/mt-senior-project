import sys
from tkinter import *
from graph import Render
class GraphFrame:
    def __init__(self,major=None,master=None):
        if not major:
            major = "SCM"
        major = major.upper()
        self.app = Tk()
        self.app.wm_title(f"Management Techonology ({major})")
        self.graph = Render(major=major,master=self.app)
        self.search_text = StringVar(self.app)
        self.addSearchFrame()
        self.addToolFrame()
        self.graph.canvas.get_tk_widget().pack(side=BOTTOM)
        def on_closing():
            self.graph.plt.close()
            self.app.destroy()
        self.app.protocol("WM_DELETE_WINDOW",on_closing)
        if not master:
            self.app.mainloop()
        
        
    def addSearchFrame(self):
        frame = Frame(self.app)
        frame.pack(side=TOP)
        label = Label(frame,text="Search for:")
        label.pack(side=LEFT)
        entry = Entry(frame,textvariable=self.search_text)
        entry.pack(side=LEFT)
        button = Button(frame,text="Search",command=self.search)
        button.pack(side=RIGHT)
        result_frame = Frame(self.app)
        result_frame.pack(side=TOP)
        self.search_result = Label(result_frame,text="")
        self.search_result.pack()
        entry.bind("<Return>",self.search)
        
    def addToolFrame(self):
        frame = Frame(self.app)
        frame.pack(side=TOP)
        _home = Button(frame,text="reset",command=self.graph.home)
        _home.pack(side=LEFT)
        _back = Button(frame,text="prev",command=self.graph.back)
        _back.pack(side=LEFT)
        _forward = Button(frame,text="next",command=self.graph.forward)
        _forward.pack(side=LEFT)
    
    def search(self,*args,**kwargs):
        print(self.search_text.get())
        self.graph.search_text = self.search_text.get()
        self.graph.searchSubject(self.search_text.get())
        total_matched = len(self.graph.total_matched)
        if total_matched > 0 and self.search_text.get() != "":
            self.search_result.configure(text=f"Result for \"{self.search_text.get()}\". Found {total_matched} result(s)",fg="red")            
            self.search_result.pack()
        else:
            self.search_result.pack_forget()
    
if __name__ == "__main__":
    GraphFrame()