from sys import platform as sys_pf
import json
import copy
import math
import argparse
import matplotlib
if sys_pf == 'darwin':
    matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.widgets as widgets
import matplotlib.backend_tools as tools
import matplotlib.pyplot as plt
from sys import platform as sys_pf
import networkx as nx
import tkinter as tk
import os
import matplotlib.patches as mpatches


current_dir = os.path.dirname(__file__)


LEVEL_SUBTRACTION = 1
SIZE = plt.rcParams["figure.figsize"]
SIZE[0] = 14
SIZE[1] = 7.5
IS_FIRST = True
SCHOOL_NODE_SIZE = 2000
NODE_SIZE_MULTIPLIER = 250
SCHOOL_NODE_COLOR = "#bada55"
TYPE_COLORS = {
    "Free Elective": "#FA8072",
    "General": "#50d0ff",
    "Senior Project":"#ff0000"
}

class Render:
    def __init__(self,major="MIS",name="Management Techonology (MIS)",master=None):
        ### LOAD SUBJECTS FROM JSON FILES ###
        with open(os.path.join(current_dir,"subjects","{}.json".format(major.lower()))) as infile:
            subject_data = json.load(infile)
        self.plt = plt
        if not major:
            major = "SCM"
        major = major.upper()
        globals()["MAJOR"] = major
        self.SCHOOL = name
        self.HISTORY = [copy.deepcopy(subject_data["subjects"])]
        self.total_matched = []
        self.HISTORY_INDEX = 0
        self.master = master
        self.subjects = []
        self.NODE_COORDINATES = {}
        self.SUBJECT_PATHS = {}
        self.FIRST = True
        self.search_box = None
        self.search_text = ""

        # PLOT CONFIGURATION
        plt.rcParams["figure.figsize"] = SIZE
        plt.subplots_adjust(
            left=0.0,  # the left side of the subplots of the figure
            right=1.0,  # the right side of the subplots of the figure
            bottom=0.0,  # the bottom of the subplots of the figure
            top=1.0,  # the top of the subplots of the figure
        )
        plot = plt.figure(1)  # REFERENCE TO CURRENT PLOT
        # SET CALLBACK FUNCTION FOR PLOT ON CLICK
        self.draw()
        if not master:
            plot.canvas.mpl_connect('button_press_event',self.removeNodeOnClick)
            plt.show()
        else:
            # self.app = tk.Tk()
            self.canvas = FigureCanvasTkAgg(plot, master)
            # self.canvas.get_tk_widget().pack(side='bottom', fill='both', expand=1) # ERROR Tk.
            self.canvas.mpl_connect('button_press_event',self.removeNodeOnClick)
            # self.app.mainloop()

    def destroy_plot(self):
        self.plt.close()

    ### END CLASS INIT ###
     # BACK BUTTON CALLBACK FUNCTION
    def back(self,*args, **kwargs):
        self.search_text = ""
        if self.HISTORY_INDEX > 0:
            self.HISTORY_INDEX -= 1
            self.redraw()

    # FORWARD BUTTON CALLBACK FUNCTION
    def forward(self,*args, **kwargs):
        self.search_text = ""
        if self.HISTORY_INDEX < len(self.HISTORY)-1:
            self.HISTORY_INDEX += 1
            self.redraw()

    def home(self,*args, **kwargs):
        self.search_text = ""
        self.HISTORY_INDEX = 0
        self.redraw()

    def redraw(self):
        plt.clf()
        self.draw()
        if self.master:
            self.canvas.draw()
        else:
            plt.pause(0.00001)

    # CALLBACK FUNCTION FOR GRAPH ON CLICK
    def removeNodeOnClick(self, event):
        coords = self.NODE_COORDINATES
        subjects = self.subjects
        clickx = event.xdata  # X COORDINATE
        clicky = event.ydata  # Y COORDINATE
        targetName = ""
        matched = []
        minDistance = None
        targetName = None
        # CALCULATE EUCLIDEAN DISTANCE
        for subject in coords:
            try:
                location = coords[subject]
                x = location[0]
                y = location[1]
                distance = math.pow(
                    math.pow((x-clickx), 2) + math.pow((y-clicky), 2), 0.5)
                if distance < 0.5:
                    matched.append((subject, distance))

            except Exception:
                pass

        for (s, d) in matched:
            if not minDistance or d < minDistance:
                targetName = s
                minDistance = d

        # IF EUCLIDEAN DISTANCE MATCH WITH SOME NODE SO DELETE THAT NODE
        # AND ALSO REMOVE ITS HEIRS
        if targetName:
            if not tk.messagebox.askyesno("Remove subject node",f"Do you want to remove {targetName} ?"):
                return
            remain_subjects = []
            tmp_target = [targetName]
            iteration = 0
            while len(tmp_target) > 0:
                target = tmp_target.pop()
                for d in subjects:
                    try:
                        if target != d["subject"] and target not in d["prerequisite"]:
                            if d in remain_subjects:
                                # print("HIT CONTINUE")
                                continue
                            if iteration == 0:
                                remain_subjects.append(d)
                        else:
                            remain_subjects = [
                                d for d in remain_subjects if d["subject"] != target]
                            if target == d["subject"]:
                                continue
                            tmp_target.append(d["subject"])
                    except Exception as err:
                        if iteration == 0:
                            remain_subjects.append(d)
                iteration += 1
            if str(remain_subjects) != str(self.HISTORY[len(self.HISTORY)-1]):
                self.HISTORY.append(subjects)
                self.HISTORY.append(remain_subjects)
            self.HISTORY_INDEX = len(self.HISTORY)-1
            self.redraw()
        ######***** END ON CLICK CALLBACK FUNCTION *****######
        
    # Draw everything
    def draw(self):
        
        global MAJOR

        # add legend to plot
        general = mpatches.Patch(color=TYPE_COLORS["General"], label='General Subject')
        free_elective = mpatches.Patch(color=TYPE_COLORS["Free Elective"], label='Free Elective')
        senior = mpatches.Patch(color=TYPE_COLORS["Senior Project"], label='Senior Project')
        plt.legend(handles=[general,free_elective,senior])

        G = nx.DiGraph()
        # HISTORY STACK ON GIVEN CURRENT HISTORY INDEX
        self.subjects = self.HISTORY[self.HISTORY_INDEX]
        rootNodes = []  # LIST OF ALL PARENT NODES
        childNodes = []  # LIST OF ALL CHILD NODES
        noNextSubjects = []
        NODE_CHILD_COUNTS = {}
        ROOT_LEVEL = 0
        PREV_LEVEL_Y_RIGHT = -4  # Y COORDINATE OF PREV ROOT LEVEL
        PREV_LEVEL_Y_LEFT = 0
        COUNT_RIGHT_NODES = 0
        # STRING TO BE DISPLAYED ON SCHOOL NODE
        SCHOOL_LABEL = self.SCHOOL.replace(" ", "\n")

        # FILTER ROOT NODE
        for node in copy.deepcopy(self.subjects):
            try:
                if len(node["prerequisite"]) == 0:
                    rootNodes.append(node)
            except:
                rootNodes.append(node)

        # FILTER CHILD NODE ** NODE THAT HAS PREREQUISITE
        for node in copy.deepcopy(self.subjects):
            try:
                if len(node["prerequisite"]) > 0:
                    childNodes.append(node)
            except:
                pass

        # sorting for subject that doesnt have วิชาต่อ
        for node in rootNodes:
            subject = node["subject"]
            should_append = True
            for n in childNodes:
                if subject in n["prerequisite"]:
                    should_append = False
                    break
            if(should_append):
                noNextSubjects.append(subject)

        if self.FIRST:
            LEVELS = len(rootNodes)  # total root nodes (length of array)
            self.NODE_COORDINATES[SCHOOL_LABEL] = (0, -(LEVELS/2))
            G.add_node(SCHOOL_LABEL, pos=(0, -(LEVELS/2)), weight=10,
                       color=SCHOOL_NODE_COLOR, text=SCHOOL_LABEL)  # ADD SCHOOL NODE
        else:
            G.add_node(SCHOOL_LABEL, pos=self.NODE_COORDINATES[SCHOOL_LABEL], weight=10,
                       color=SCHOOL_NODE_COLOR, text=SCHOOL_LABEL)  # ADD SCHOOL NODE
        # childNodes variable is an array of nodes that have prerequisite
        # rootNodes variable is an array of nodes that do not have prerequisite
        # LOOP OVER ROOT NODES ARRAY
        for node in (rootNodes):
            has_no_next = False
            subject = node["subject"]  # SUBJECT NAME (ROOT NAME)
            weight = 1  # Default value for weight
            subject_type = "General"
            if "weight" in node:  # if weight is already set so use that value
                weight = node["weight"]
            if "type" in node:
                subject_type = node["type"]

            if subject in noNextSubjects:
                has_no_next = True
            if self.FIRST:
                PARENT_CURRENT_Y = ROOT_LEVEL
                if not has_no_next: # IS RIGHT SIDE
                    PARENT_CURRENT_Y = PREV_LEVEL_Y_RIGHT
                    # PARENT_CURRENT_X = 1 + math.pow(-1, abs(COUNT_RIGHT_NODES))*0.2
                    PARENT_CURRENT_X = 1 
                    COUNT_RIGHT_NODES += 1
                else: # IS LEFT SIDE
                    PARENT_CURRENT_Y = PREV_LEVEL_Y_LEFT
                    # PARENT_CURRENT_X = -1 + math.pow(-1, abs(ROOT_LEVEL))*0.2
                    PARENT_CURRENT_X = -1 
                self.NODE_COORDINATES[subject] = (
                    PARENT_CURRENT_X, PARENT_CURRENT_Y)
                self.SUBJECT_PATHS[subject] = []
                Y_COORDINATES = [PARENT_CURRENT_Y]
                # ADD ROOT NODE TO GRAPH
                G.add_node(
                    subject,
                    pos=(PARENT_CURRENT_X, PARENT_CURRENT_Y),
                    text=f"{subject}({weight})",
                    color=TYPE_COLORS[subject_type]
                )
            else:
                G.add_node(
                    subject,
                    pos=self.NODE_COORDINATES[subject],
                    text=f"{subject}({weight})",
                    color=TYPE_COLORS[subject_type]
                )
            # ADD EDGE FROM ROOT NODE TO SCHOOL NODE
            G.add_edge(SCHOOL_LABEL, subject, weight=weight,
                       root=SCHOOL_LABEL, color=TYPE_COLORS[subject_type])
            PARENTS = [subject]
            while True:
                parent = PARENTS.pop(0)  # POP FIRST ELEMENT OF PARENTS
                parent_child_x = []
                parent_child_y = []
                index = 0  # INDEX
                if parent not in NODE_CHILD_COUNTS:
                    NODE_CHILD_COUNTS[parent] = 0
                for child in childNodes:
                    # CHECK IF PARENT HAS ANY CHILDREN
                    # AND IF SUBJECT IS INTERSECT WITH CURRENT MAJOR eg. EM ,SCM ,MIS
                    if parent in child["prerequisite"] and MAJOR in child["school"]:
                        NODE_CHILD_COUNTS[parent] += 1
                        _subject = child["subject"]
                        _weight = 1  # Default value for weight
                        _subject_type = "General"
                        if "weight" in child:  # if weight is already set so use that value
                            _weight = child["weight"]
                        if "type" in child:
                            _subject_type = child["type"]

                        for l, p in enumerate(child["prerequisite"], start=0):
                            if p == parent:
                                _prereq = child["prerequisite"].pop(l)
                                break
                        if _prereq in self.NODE_COORDINATES:
                            if self.FIRST:
                                # COORDINATE OF THIS NODE PARENT
                                PARENT_COORDINATES = self.NODE_COORDINATES[_prereq]
                                PARENT_TYPE = [node["type"] for node in self.subjects if node["subject"] == _prereq][0]
                                
                                # X COORDINATE
                                # CURRENT_X = round(PARENT_COORDINATES[0] + \
                                #     2+math.pow(-1, abs(index))*0.2,2)
                                CURRENT_X = round(PARENT_COORDINATES[0] +2,2)
                                CURRENT_Y = round(PARENT_COORDINATES[1] -index,2) # Y COORDINATE

                                pos = (CURRENT_X, CURRENT_Y)
                                ## sorting for overlappeds coordinates ##
                                coords = [self.NODE_COORDINATES[key]
                                          for key in self.NODE_COORDINATES if key != SCHOOL_LABEL]
                                ## matched coordinates list
                                matched = [
                                    c for c in coords if str(c) == str(pos)]
                                if len(matched) != 0: # if overlapped coordinate
                                    matched = [
                                    c for c in coords if c[0]==pos[0] and c[1] <= pos[1] ]
                                    matched_y = matched[len(matched)-1][1] - 1
                                    CURRENT_Y = matched_y
                                if CURRENT_Y in parent_child_y:
                                    CURRENT_Y -= 1
                                pos = (CURRENT_X, CURRENT_Y)
                                    
                                ## if subjec is not in node coordinates dict then put it in...
                                if _subject not in self.NODE_COORDINATES:
                                    self.NODE_COORDINATES[_subject] = pos
                                self.SUBJECT_PATHS[subject].append(_subject)
                                Y_COORDINATES.append(CURRENT_Y)
                                
                            else:
                                CURRENT_X = self.NODE_COORDINATES[_subject][0]
                                CURRENT_Y = self.NODE_COORDINATES[_subject][1]
                                pos = (CURRENT_X, CURRENT_Y)
                            # ADD NODE TO GRAPH
                            if _subject not in G.nodes():
                                G.add_node(
                                    _subject, pos=pos, text=f"{_subject}({_weight})", color=TYPE_COLORS[_subject_type])
                            # ADD EDGE FROM PARENT TO CHILD NODE
                            G.add_edge(_prereq, _subject, weight=_weight,
                                       root=subject, color=TYPE_COLORS[_subject_type])
                            # PUSH NEW PARENT TO THE LIST
                            PARENTS.append(_subject)
                            index += 1

                # IF THERE'S NO ELEMENTS IN PARENTS LIST ; BREAK THE LOOP
                if len(PARENTS) == 0:
                    break
            #### END WHILE LOOP ####
            if not self.FIRST:
                continue

            ROOT_LEVEL -= LEVEL_SUBTRACTION
            if not has_no_next:
                # UPDATE LEVEL OF ROOT NODE
                if len(Y_COORDINATES) == 0:
                    PREV_LEVEL_Y_RIGHT = PREV_LEVEL_Y_RIGHT - LEVEL_SUBTRACTION  # UPDATE PREVIOUS Y COORDINATE
                else:
                    minY = min(Y_COORDINATES)
                    PREV_LEVEL_Y_RIGHT = minY - LEVEL_SUBTRACTION
            else:
                PREV_LEVEL_Y_LEFT -= 1
        # END FOR LOOP

        self.FIRST = False
        labels = {}
        for index, data in enumerate(G.nodes(data=True), start=0):
            subject = data[0]
            attributes = data[1]
            labels[subject] = attributes["text"]

            # skip index=0 because it's school node ,everthing's already set for it
            if index == 0:
                continue
            weight = NODE_CHILD_COUNTS[subject]
            if weight > 3:
                weight = 3
            elif weight == 0:
                weight = 1
                attributes["weight"] = weight
                
            ## searched matched!
            if self.search_text.upper() in subject and self.search_text != "":
                attributes["color"] = "red"
                weight = 5
            attributes["weight"] = weight

        pos = nx.get_node_attributes(G, 'pos')

        # # DRAW NODES
        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=[d["color"] for (p, d) in G.nodes(data=True)],
            node_size=[d["weight"] *
                       NODE_SIZE_MULTIPLIER for (p, d) in G.nodes(data=True)],
            alpha=0.7,
            linewidths=1
        )
        # DRAW SCHOOL EDGES
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=G.edges(),
            edge_color=[d["color"] for (u, v, d) in G.edges(data=True)],
            alpha=0.80
        )
        # DRAW LABELS
        nx.draw_networkx_labels(
            G,
            pos,
            font_size=7.5,
            font_weight="bold"
            # labels=labels,
        )

        plt.title(f"School of {self.SCHOOL}")  # SET TITLE
        plt.gcf().canvas.set_window_title(
            f"School of {self.SCHOOL}")  # SET WINDOW TITLE
        plt.axis("off")  # TURN OFF AXIS
        if not self.master:
            self.search_box = widgets.TextBox(
                plt.axes([0.075, 0.05, 0.05, 0.025]),
                'Search for:',
                initial=self.search_text,
                label_pad=0.05,
            )
            self.search_box.on_submit(self.searchSubject)
            self.search_box.on_text_change(self.setSearchBoxText)
        
    # END DRAW FUNCTION

    # ON TEXT CHANGE CALLBACK FUNCTION
    def setSearchBoxText(self, text):
        self.search_text = text

    # FUNCTIONS SEARCH
    def searchSubject(self, text):
        text = text.upper()
        roots = []
        appended_subjects = []
        paths = []
        roots = [root for root in self.SUBJECT_PATHS if any(text in s for s in self.SUBJECT_PATHS[root]) or text in root]
        # print(roots)
        while len(roots) > 0:
            current_root = roots.pop()
            for s in self.HISTORY[0]:
                if s["subject"] == current_root:
                    paths.append(s)
                    break
            for child in self.SUBJECT_PATHS[current_root]:
                if child not in appended_subjects:
                    paths.append(
                        [s for s in self.HISTORY[0] if s["subject"] == child].pop(0))
                    appended_subjects.append(child)
        if len(paths) == 0:
            self.HISTORY_INDEX = 0
        else:
            self.total_matched = [s["subject"] for s in paths if text in s["subject"]]
            self.HISTORY.append(paths)
            self.HISTORY_INDEX = len(self.HISTORY)-1
        self.redraw()
    # END FUNCTION SEARCH


# CALLED CLASS "render" WHEN IT IS MAIN PROCESS
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--major", "-m", required=False,
                    help="this argument is used to specify major")
    args = vars(parser.parse_args())
    MAJOR = "MIS"
    if args["major"]:
        MAJOR = args["major"].upper()
    Render(major=MAJOR)
