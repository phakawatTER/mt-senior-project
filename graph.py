import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backend_tools as tools
import matplotlib.widgets as widgets
import argparse
import math
import copy
from matplotlib.backend_bases import NavigationToolbar2
import json

### LOAD SUBJECTS FROM JSON FILES ###
with open("./subjects/em.json") as infile:
    em = json.load(infile)
with open("./subjects/mis.json") as infile:
    mis = json.load(infile)
with open("./subjects/scm.json") as infile:
    scm = json.load(infile)

parser = argparse.ArgumentParser()
parser.add_argument("--major","-m",required=False,help="this argument is used to specify major")
args = vars(parser.parse_args())
MAJOR = args["major"]
if MAJOR:
    MAJOR = MAJOR.upper()
    
HISTORY = []
HISTORY_INDEX = 0
SCHOOL = ""
if MAJOR == "SCM":
    SCHOOL = "Management Techonology (SCM)"
    HISTORY = [copy.deepcopy(scm["subjects"])] # DEEP COPY BECAUSE WE WANT TO COPY ARRAY INSIDE DICTIONARY
elif MAJOR == "EM":
    SCHOOL = "Engineering Management (EM)"
    HISTORY = [copy.deepcopy(em["subjects"])] # DEEP COPY BECAUSE WE WANT TO COPY ARRAY INSIDE DICTIONARY
elif MAJOR == "MIS":
    SCHOOL="Management Techonology (MIS)"
    HISTORY = [copy.deepcopy(mis["subjects"])] # DEEP COPY BECAUSE WE WANT TO COPY ARRAY INSIDE DICTIONARY
elif not MAJOR:
    MAJOR = "SCM"
    SCHOOL = "Management Techonology (SCM)"
    HISTORY = [copy.deepcopy(scm["subjects"])] # DEEP COPY BECAUSE WE WANT TO COPY
print(f"CURRENT SCHOOL IS {SCHOOL}")
    
LEVEL_SUBTRACTION = 1
SIZE = plt.rcParams["figure.figsize"]
SIZE[0] = 14
SIZE[1] = 7.5
IS_FIRST = True
SCHOOL_NODE_SIZE = 2000
NODE_SIZE_MULTIPLIER = 160
SCHOOL_NODE_COLOR = "#660099"
TYPE_COLORS = {
    "Free Elective":"#00ff38",
    "General":"#50d0ff"
}


class Render:
    global MAJOR,SCHOOL_NODE_SIZE,SCHOOL
    def __init__(self):
        self.subjects = []
        self.NODE_COORDINATES = {}
        self.SUBJECT_PATHS = {}
        self.FIRST = True
        self.search_box = None
        self.search_text = ""
        self.fig,self.ax = plt.subplots()
        # BACK BUTTON CALLBACK FUNCTION
        def back(*args, **kwargs):
            global HISTORY_INDEX
            self.search_text = ""
            if HISTORY_INDEX > 0:
                HISTORY_INDEX -= 1
                self.redraw()

        # FORWARD BUTTON CALLBACK FUNCTION
        def forward(*args, **kwargs):
            global HISTORY_INDEX
            self.search_text = ""
            if HISTORY_INDEX < len(HISTORY)-1:
                HISTORY_INDEX += 1
                self.redraw()
                
        def home(*args, **kwargs):
            global HISTORY_INDEX
            self.search_text = ""
            HISTORY_INDEX = 0
            self.redraw()
                
        NavigationToolbar2.back = back
        NavigationToolbar2.forward = forward
        NavigationToolbar2.home = home
        
        
        # PLOT CONFIGURATION
        plt.rcParams["figure.figsize"] = SIZE
        plt.subplots_adjust(
            left = 0.0,  # the left side of the subplots of the figure
            right = 1.0 ,  # the right side of the subplots of the figure
            bottom = 0.0 , # the bottom of the subplots of the figure
            top = 0.94    , # the top of the subplots of the figure
        )
        
        plot = plt.figure(1) # REFERENCE TO CURRENT PLOT
        # fig.set_facecolor("#d4d4d4") # SET BACKGROUND COLOR
        # SET CALLBACK FUNCTION FOR PLOT ON CLICK
        plot.canvas.mpl_connect('button_press_event', lambda e:self.removeNodeOnClick(event=e,
                coords=self.NODE_COORDINATES,subjects=self.subjects))
        self.draw() 
        plt.show() # SHOT PLOT
    ### END CLASS INIT ###
        
    def redraw(self):
        # self.ax.clear()
        # plt.cla()
        plt.clf()
        self.draw()
        plt.pause(0.00001)
    
        
    # CALLBACK FUNCTION FOR GRAPH ON CLICK
    def removeNodeOnClick(self,event,coords={},subjects=[]):
        global HISTORY_INDEX
        clickx = event.xdata # X COORDINATE
        clicky = event.ydata # Y COORDINATE
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
                distance = math.pow(math.pow((x-clickx), 2) + math.pow((y-clicky), 2), 0.5)
                if distance < 0.5:
                    matched.append((subject,distance))
                
            except Exception:
                pass
            
        for (s,d) in matched:
            if not minDistance or d < minDistance:
                targetName = s
                minDistance = d
            
                        
        # IF EUCLIDEAN DISTANCE MATCH WITH SOME NODE SO DELETE THAT NODE
        # AND ALSO REMOVE ITS HEIRS
        if targetName:
            print(targetName)
            remain_subjects = []
            tmp_target = [targetName]
            iteration = 0
            while len(tmp_target)>0:
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
                            remain_subjects = [d for d in remain_subjects if d["subject"]!=target]
                            if target == d["subject"]:
                                continue
                            tmp_target.append(d["subject"])
                    except Exception as err:
                        if iteration == 0:
                            remain_subjects.append(d)
                iteration += 1
            if str(remain_subjects) != str(HISTORY[len(HISTORY)-1]):
                HISTORY.append(subjects)
                HISTORY.append(remain_subjects)
            HISTORY_INDEX = len(HISTORY)-1
            self.redraw()
        ######***** END ON CLICK CALLBACK FUNCTION *****######
        
    # Draw everything
    def draw(self):
        G = nx.DiGraph()
        self.subjects = HISTORY[HISTORY_INDEX]  # HISTORY STACK ON GIVEN CURRENT HISTORY INDEX
        rootNodes = [] # LIST OF ALL PARENT NODES
        childNodes = [] # LIST OF ALL CHILD NODES
        NODE_CHILD_COUNTS = {}
        ROOT_LEVEL = 0
        PREV_LEVEL_Y = 0 # Y COORDINATE OF PREV ROOT LEVEL
        SCHOOL_LABEL = SCHOOL.replace(" ","\n") # STRING TO BE DISPLAYED ON SCHOOL NODE

        # FILTER ROOT NODE
        for node in copy.deepcopy(self.subjects):
            if "prerequisite" not in node:
                rootNodes.append(node)
        # FILTER CHILD NODE ** NODE THAT HAS PREREQUISITE
        for node in copy.deepcopy(self.subjects):
            if "prerequisite" in node:
                childNodes.append(node)
        if self.FIRST:
            LEVELS = len(rootNodes)  # total root nodes (length of array)
            self.NODE_COORDINATES[SCHOOL_LABEL] = (-2, -(LEVELS/2))
            G.add_node(SCHOOL_LABEL, pos=(-2, -(LEVELS/2)),weight=10,color=SCHOOL_NODE_COLOR,text=SCHOOL_LABEL)  # ADD SCHOOL NODE
        else:
            G.add_node(SCHOOL_LABEL, pos=self.NODE_COORDINATES[SCHOOL_LABEL],weight=10,color=SCHOOL_NODE_COLOR,text=SCHOOL_LABEL)  # ADD SCHOOL NODE

        # childNodes variable is an array of nodes that have prerequisite
        # rootNodes variable is an array of nodes that do not have prerequisite
        # LOOP OVER ROOT NODES ARRAY
        for node in (rootNodes):
            subject = node["subject"]  # SUBJECT NAME (ROOT NAME)
            weight = 1 ## Default value for weight
            subject_type = "General"
            if "weight" in node: ## if weight is already set so use that value
                weight = node["weight"]
            if "type" in node:
                subject_type = node["type"]
            
                
            if self.FIRST:
                PARENT_CURRENT_Y = ROOT_LEVEL
                PARENT_CURRENT_Y = PREV_LEVEL_Y
                PARENT_CURRENT_X = 1 + math.pow(-1,abs(ROOT_LEVEL))*0.07
                self.NODE_COORDINATES[subject] = (PARENT_CURRENT_X, PARENT_CURRENT_Y)
                self.SUBJECT_PATHS[subject] = []
                Y_COORDINATES = [PARENT_CURRENT_Y]
                # ADD ROOT NODE TO GRAPH
                G.add_node(
                    subject,
                    pos=(1+math.pow(-1,abs(ROOT_LEVEL))*0.07,PREV_LEVEL_Y),
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
            G.add_edge(SCHOOL_LABEL, subject, weight=weight,root=SCHOOL_LABEL,color=SCHOOL_NODE_COLOR)
            PARENTS = [subject]
            while True:
                parent = PARENTS.pop(0)  # POP FIRST ELEMENT OF PARENTS
                index = 0  # INDEX
                if parent not in NODE_CHILD_COUNTS:
                    NODE_CHILD_COUNTS[parent] = 0
                for child in childNodes:
                    # CHECK IF PARENT HAS ANY CHILDREN
                    # AND IF SUBJECT IS INTERSECT WITH CURRENT MAJOR eg. EM ,SCM ,MIS
                    if parent in child["prerequisite"] and MAJOR in child["school"]:
                        NODE_CHILD_COUNTS[parent] += 1
                        _subject = child["subject"]
                        _weight = 1 ## Default value for weight
                        _subject_type = "General"
                        if "weight" in child: ## if weight is already set so use that value
                            _weight = child["weight"]
                        if "type" in child: 
                            _subject_type = child["type"]
                        
                        for l,p in enumerate(child["prerequisite"],start=0):
                            if p == parent:
                                _prereq = child["prerequisite"].pop(l)
                                break
                        if _prereq in self.NODE_COORDINATES:
                            if self.FIRST:
                                # COORDINATE OF THIS NODE PARENT
                                PARENT_COORDINATES = self.NODE_COORDINATES[_prereq]
                                CURRENT_X = PARENT_COORDINATES[0] + 2+math.pow(-1,abs(index))*0.2 # X COORDINATE
                                CURRENT_Y = PARENT_COORDINATES[1] + \
                                    (-index)  # Y COORDINATE
                                
                                pos = (CURRENT_X,CURRENT_Y)
                                ## sorting for overlappeds coordinates ##
                                coords = [self.NODE_COORDINATES[key] for key in self.NODE_COORDINATES if key!=SCHOOL_LABEL]
                                matched = [c for c in coords if str(c) == str(pos)]
                                if len(matched) != 0:
                                    CURRENT_Y -= 1
                                    pos = (CURRENT_X,CURRENT_Y)
                                if _subject not in self.NODE_COORDINATES:
                                    self.NODE_COORDINATES[_subject] = pos
                                self.SUBJECT_PATHS[subject].append(_subject)
                                Y_COORDINATES.append(CURRENT_Y)
                            else:
                                CURRENT_X = self.NODE_COORDINATES[_subject][0]
                                CURRENT_Y = self.NODE_COORDINATES[_subject][1]
                                pos = (CURRENT_X,CURRENT_Y)
                            # ADD NODE TO GRAPH
                            if _subject not in G.nodes():
                                G.add_node(_subject, pos=pos,text=f"{_subject}({_weight})",color=TYPE_COLORS[_subject_type])
                            # ADD EDGE FROM PARENT TO CHILD NODE
                            G.add_edge(_prereq, _subject, weight=_weight,root=subject,color=TYPE_COLORS[_subject_type])
                            PARENTS.append(_subject)  # PUSH NEW PARENT TO THE LIST
                            index += 1
                
                # IF THERE'S NO ELEMENTS IN PARENTS LIST ; BREAK THE LOOP
                if len(PARENTS) == 0:
                    break
            #### END WHILE LOOP ####
            if not self.FIRST:
                continue
            

            ROOT_LEVEL -= LEVEL_SUBTRACTION
            # UPDATE LEVEL OF ROOT NODE
            if len(Y_COORDINATES) == 0:
                PREV_LEVEL_Y = PREV_LEVEL_Y - LEVEL_SUBTRACTION # UPDATE PREVIOUS Y COORDINATE
            else:
                minY = min(Y_COORDINATES)
                PREV_LEVEL_Y = minY - LEVEL_SUBTRACTION
        ## END FOR LOOP

                
        self.FIRST = False   
        labels={}
        for index,data in enumerate(G.nodes(data=True),start=0):
            subject = data[0]
            attributes = data[1]
            labels[subject] = attributes["text"]
                
            ## skip index=0 because it's school node ,everthing's already set for it
            if index == 0: 
                continue
            weight = NODE_CHILD_COUNTS[subject]
            if weight > 3 and self.search_text.upper() != subject:
                weight = 3
            elif weight == 0 and self.search_text.upper() != subject:
                weight = 0.25
                attributes["weight"] = weight
                continue
            elif self.search_text.upper() == subject:
                weight = 3
            attributes["weight"] = weight

            
        pos = nx.get_node_attributes(G, 'pos')

        # # DRAW NODES
        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=[d["color"] for (p,d) in G.nodes(data=True)],
            node_size=[d["weight"] * NODE_SIZE_MULTIPLIER for (p,d) in G.nodes(data=True)],
            alpha=0.7,
            linewidths=1
        )
        # DRAW SCHOOL EDGES
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=G.edges(),
            edge_color=[d["color"] for (u,v,d) in G.edges(data=True)],
            alpha=0.80
        )
        # DRAW LABELS
        nx.draw_networkx_labels(
            G,
            pos,
            font_size=5,
            # labels=labels,
        )
       
        plt.title(f"School of {SCHOOL}") # SET TITLE
        plt.gcf().canvas.set_window_title(f"School of {SCHOOL}") # SET WINDOW TITLE
        plt.axis("off") # TURN OFF AXIS
        self.search_box = widgets.TextBox(
            plt.axes([0.075, 0.05, 0.05, 0.025]), 
            'Search for:', 
            initial=self.search_text,
            label_pad=0.05,
        )
        self.search_box.on_submit(self.searchSubject)
        self.search_box.on_text_change(self.setSearchBoxText)
    ### END DRAW FUNCTION
    
    ## ON TEXT CHANGE CALLBACK FUNCTION
    def setSearchBoxText(self,text):
        self.search_text = text
        
    ## FUNCTIONS SEARCH
    def searchSubject(self,text):
        global HISTORY,HISTORY_INDEX
        text = text.upper()
        roots = []
        appended_subjects = []
        paths = []
        for root in self.SUBJECT_PATHS :
            if text in self.SUBJECT_PATHS[root]:
                roots.append(root)
            elif text == root:
                roots.append(root)
                break
        while len(roots) > 0:
            current_root = roots.pop()
            for s in HISTORY[0]:
                if s["subject"] == current_root:
                    paths.append(s)
                    break
            for child in self.SUBJECT_PATHS[current_root]:
                if child not in appended_subjects:
                    paths.append([s for s in HISTORY[0] if s["subject"]==child].pop(0))
                    appended_subjects.append(child)
        if len(paths) == 0:
            HISTORY_INDEX = 0
        else:
            HISTORY.append(paths)
            HISTORY_INDEX = len(HISTORY)-1
        self.redraw()
    ## END FUNCTION SEARCH
        

# CALLED CLASS "render" WHEN IT IS MAIN PROCESS
if __name__=="__main__":
    Render()