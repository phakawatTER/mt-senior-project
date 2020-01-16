import networkx as nx
import matplotlib
matplotlib.use("TKAgg")
import matplotlib.pyplot as plt
import matplotlib.backend_tools as tools
from backgrounds import backgrounds  # load background colors
import argparse
import math
import copy
from matplotlib.backend_bases import NavigationToolbar2
import json

### LOAD JSON FILE ###
with open("./subjects/em.json") as infile:
    em = json.load(infile)
with open("./subjects/mis.json") as infile:
    mis = json.load(infile)
with open("./subjects/scm.json") as infile:
    scm = json.load(infile)

parser = argparse.ArgumentParser()
parser.add_argument("--major","-m",required=False,help="this argument is used to specify major")
# parser.add_argument("--name","-n",required=False,help="this argument is used to specify the name to be display as title")
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
    HISTORY = [copy.deepcopy(scm.subject)] # DEEP COPY BECAUSE WE WANT TO COPY
print(f"CURRENT SCHOOL IS {SCHOOL}")
    
LEVEL_SUBTRACTION = 1
SIZE = plt.rcParams["figure.figsize"]
SIZE[0] = 15
SIZE[1] = 10
IS_FIRST = True
SCHOOL_NODE_SIZE = 1000
NORMAL_NODE_SIZE = 300

class Render:
    global MAJOR,SCHOOL_NODE_SIZE,NORMAL_NODE_SIZE,SCHOOL
    def __init__(self):
        
        self.subjects = []
        self.NODE_COORDINATES = {}
        self.NODE_SIZES = []
        # BACK BUTTON CALLBACK FUNCTION
        def back(*args, **kwargs):
            global HISTORY_INDEX
            # print(f"HIT HERE :LENGHT {len(HISTORY)}")
            if HISTORY_INDEX > 0:
                HISTORY_INDEX -= 1
                self.rerender()

        # FORWARD BUTTON CALLBACK FUNCTION
        def forward(*args, **kwargs):
            global HISTORY_INDEX
            if HISTORY_INDEX < len(HISTORY)-1:
                HISTORY_INDEX += 1
                self.rerender()
                
        def home(*args,**kwargs):
            global HISTORY_INDEX
            HISTORY_INDEX = 0
            self.rerender()
                
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
        self.draw()
        fig = plt.figure(1) # REFERENCE TO CURRENT PLOT
        fig.set_facecolor("#000000") # SET BACKGROUND COLOR
        # SET CALLBACK FUNCTION FOR PLOT ON CLICK
        fig.canvas.mpl_connect('button_press_event', lambda e:self.removeNodeOnClick(event=e,
                coords=self.NODE_COORDINATES,subjects=self.subjects)) 
        plt.show() # SHOT PLOT
    ### END CLASS INIT ###
        
    def rerender(self):
        plt.clf()
        plt.cla()
        self.draw()
        plt.pause(0.00001)
        
    # CALLBACK FUNCTION FOR GRAPH ON CLICK
    def removeNodeOnClick(self,event,coords={},subjects=[]):
        global HISTORY_INDEX
        clickx = event.xdata # X COORDINATE
        clicky = event.ydata # Y COORDINATE
        print(f"{clickx},{clicky}")
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
                distance = math.pow(math.pow((x-clickx), 2) +
                                    math.pow((y-clicky), 2), 0.5)
                if distance < 0.25:
                    matched.append((subject,distance))
                
            except Exception:
                pass
            
        for (s,d) in matched:
            if not minDistance or d < minDistance:
                targetName = s
                minDistance = d
            
                        
        # IF EUCLIDEAN DISTANCE MATCH WITH SOME NODE SO DELETE THAT NODE
        if targetName != "":
            print(f"remove {targetName}")
            removed = [
                course for course in subjects if course["subject"] != targetName]
            removed = copy.deepcopy(removed)
            HISTORY.append(removed)
            HISTORY_INDEX = len(HISTORY)-1
            self.rerender()
        ######***** END ON CLICK CALLBACK FUNCTION *****######
        
    
    # Draw everything
    def draw(self):
        G = nx.DiGraph()
        self.subjects = HISTORY[HISTORY_INDEX]  # HISTORY STACK ON GIVEN CURRENT HISTORY INDEX
        self.NODE_COORDINATES = {} # COORDINATES OF ALL NODES
        self.NODE_SIZES = [] # MAPPED NODE SIZE LIST
        rootNodes = [] # LIST OF ALL PARENT NODES
        childNodes = [] # LIST OF ALL CHILD NODES
        ROOT_LEVEL = 0 
        COLOR_MAP = [] # MAPPED NODE COLOR LIST
        ROOT_NODE_COLORS = [] # ROOT NODE COLOR LIST
        PREV_LEVEL_Y = 0 # Y COORDINATE OF PREV ROOT LEVEL
        SCHOOL_LABEL = "" # STRING TO BE DISPLAYED ON SCHOOL NODE
        for index,s in enumerate(SCHOOL.split(" "),start=0):
            SCHOOL_LABEL += f"{s}"
            if index < len(SCHOOL.split(" "))-1:
                SCHOOL_LABEL += "\n"

        # FILTER ROOT NODE
        for node in copy.deepcopy(self.subjects):
            if "prerequisite" not in node:
                rootNodes.append(node)
        LEVELS = len(rootNodes)  # total root nodes (length of array)
        G.add_node(SCHOOL_LABEL, pos=(-2, -int(LEVELS/2)))  # ADD SCHOOL NODE
        self.NODE_SIZES.append(SCHOOL_NODE_SIZE)
        COLOR_MAP.append(backgrounds[len(backgrounds)-1]) # APPEND LAST COLOR OF THE LIST TO BE COLOR OF ROOT NODE

        # FILTER CHILD NODE ** NODE THAT HAS PREREQUISITE
        for node in copy.deepcopy(self.subjects):
            if "prerequisite" in node:
                childNodes.append(node)

        # childNodes variable is an array of nodes that have prerequisite
        # rootNodes variable is an array of nodes that do not have prerequisite

        # LOOP OVER ROOT NODES ARRAY
        for node in rootNodes:
            subject = node["subject"]  # SUBJECT NAME (ROOT NAME)
            NODE_COLOR = backgrounds[abs(ROOT_LEVEL)%len(backgrounds)]
            COLOR_MAP.append(NODE_COLOR)
            ROOT_NODE_COLORS.append({"root":subject,"color":NODE_COLOR})
            # ADD ROOT NODE TO GRAPH
            G.add_node(subject, pos=(1+math.pow(-1,abs(ROOT_LEVEL))*0.07, PREV_LEVEL_Y))
            # ADD EDGE FROM ROOT NODE TO SCHOOL NODE
            G.add_edge(SCHOOL_LABEL, subject, weight=5,root=SCHOOL_LABEL)
            PARENT_CURRENT_Y = ROOT_LEVEL
            PARENT_CURRENT_Y = PREV_LEVEL_Y
            PARENT_CURRENT_X = 1 + math.pow(-1,abs(ROOT_LEVEL))*0.07
            self.NODE_COORDINATES[subject] = (PARENT_CURRENT_X, PARENT_CURRENT_Y)
            self.NODE_SIZES.append(NORMAL_NODE_SIZE)
            PARENTS = [subject]
            Y_COORDINATES = []
            while True:
                parent = PARENTS.pop(0)  # POP FIRST ELEMENT OF PARENTS
                offsetY = 0.5  # Y COORDINATE OFFSET
                index = 0  # INDEX
                for child in childNodes:
                    # CHECK IF PARENT HAS ANY CHILDREN
                    # AND IF SUBJECT IS INTERSECT WITH CURRENT MAJOR eg. EM ,SCM ,MIS
                    if parent in child["prerequisite"] and MAJOR in child["school"]:
                        _subject = child["subject"]
                        for l,p in enumerate(child["prerequisite"],start=0):
                            if p == parent:
                                _prereq = child["prerequisite"].pop(l)
                                print(_prereq)
                                break
                        
                        if _prereq in self.NODE_COORDINATES:
                            # COORDINATE OF THIS NODE PARENT
                            PARENT_COORDINATES = self.NODE_COORDINATES[_prereq]
                            CURRENT_X = PARENT_COORDINATES[0] + 2+math.pow(-1,abs(ROOT_LEVEL))*0.2 # X COORDINATE
                            CURRENT_Y = PARENT_COORDINATES[1] + \
                                (offsetY-1*index)  # Y COORDINATE
                            Y_COORDINATES.append(CURRENT_Y)
                            if _subject not in self.NODE_COORDINATES:
                                COLOR_MAP.append(NODE_COLOR)
                            self.NODE_COORDINATES[_subject] = (CURRENT_X, CURRENT_Y)
                            self.NODE_SIZES.append(NORMAL_NODE_SIZE)
                            # ADD NODE TO GRAPH
                            G.add_node(_subject, pos=(CURRENT_X, CURRENT_Y))
                            # ADD EDGE FROM PARENT TO CHILD NODE
                            G.add_edge(_prereq, _subject, weight=3,root=subject)
                            PARENTS.append(_subject)  # PUSH NEW PARENT TO THE LIST
                            index += 1
                
                # IF THERE'S NO ELEMENTS IN PARENTS LIST ; BREAK THE LOOP
                if len(PARENTS) == 0:
                    break
            #### END WHILE LOOP ####

            ROOT_LEVEL -= LEVEL_SUBTRACTION
            # UPDATE LEVEL OF ROOT NODE
            if len(Y_COORDINATES) == 0:
                PREV_LEVEL_Y = PREV_LEVEL_Y - LEVEL_SUBTRACTION # UPDATE PREVIOUS Y COORDINATE
            else:
                minY = min(Y_COORDINATES)
                PREV_LEVEL_Y = minY - LEVEL_SUBTRACTION
            
        pos = nx.get_node_attributes(G, 'pos')
        while(len(G)<len(COLOR_MAP)):
            COLOR_MAP.pop()
        # print(G.edges)
        # DRAW NODES
        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=COLOR_MAP,
            node_size=self.NODE_SIZES,
            alpha=0.5,
            linewidths=2
        )
        # DRAW LABELS
        nx.draw_networkx_labels(G, pos, font_weight="bold",font_color="#FFFFFF",
                                font_size=7)
        child_edges = {}
        # SORT FOR CHILD EDGES
        for (u,v,d) in G.edges(data=True):
            
            root = d["root"]
            if root == MAJOR:
                continue
            if root not in child_edges:
                child_edges[root] = [(u,v)]
            else:
                child_edges[root].append((u,v))
        # DRAW CHILD EDGES
        for d in ROOT_NODE_COLORS:
            color = d["color"]
            root = d["root"]
            if root not in child_edges:
                continue
            edges = child_edges[root]
            nx.draw_networkx_edges(G, pos, edgelist=edges, width=2,edge_color=color,alpha=0.25)
            
            
        # EDGES FROM SCHOOL TO ROOT SUBJECTS
        school_edges = [(u, v)
                        for (u, v, d) in G.edges(data=True) if d["weight"] == 5]
        # # EDGES TO SUBJECTS THAT HAVE 3 CREDITS
        # credit3_edges = [(u, v)
        #                  for (u, v, d) in G.edges(data=True) if d["weight"] == 3]
        # # EDGES TO SUBJECTS THAT HAVE 2 CREDITS
        # credit2_edges = [(u, v)
        #                  for (u, v, d) in G.edges(data=True) if d["weight"] == 2]
        # # EDGES TO SUBJECTS THAT HAVE 1 CREDITS
        # credit1_edges = [(u, v)
        #                  for (u, v, d) in G.edges(data=True) if d["weight"] == 1]
        # # DRAW SCHOOL EDGES
        nx.draw_networkx_edges(G, pos, edgelist=school_edges, width=2.5,edge_color="#ee3a6a",alpha=0.25)
        # # DRAW 3 CREDIT EDGES
        # nx.draw_networkx_edges(G, pos, edgelist=credit3_edges, width=3,edge_color="#6200E1",alpha=0.25)
        # # DRAW 2 CREDIT EDGES
        # nx.draw_networkx_edges(G, pos, edgelist=credit2_edges, width=2,edge_color="#FFFFFF",alpha=1.00)
        # # DRAW 1 CREDIT EDGES
        # nx.draw_networkx_edges(G, pos, edgelist=credit1_edges, width=1,edge_color="#ffffff",alpha=1.00)
        
        plt.axis("off") # TURN OFF AXIS
        title_obj = plt.title(f"School of {SCHOOL}") # SET TITLE
        plt.gcf().canvas.set_window_title(f"School of {SCHOOL}") # SET WINDOW TITLE
        plt.setp(title_obj, color='#FFFFFF') 
 
# CALLED CLASS "render" WHEN IT IS MAIN PROCESS
if __name__=="__main__":
    Render()
