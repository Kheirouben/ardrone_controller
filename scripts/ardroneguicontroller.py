import Tkinter as tk
import rospy, sys

from gamepadcontroller import *
from basicdronecontroller import *
from keyboardcontroller import *
from staircaseai import *

class ardroneGUIController:
    def __init__(self, root, CONTROLLER):
        self.master = root
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.controller = CONTROLLER
        # Select the current Controller
        v = tk.StringVar()
        v.set("0") # initialize
        ctrlBtnKey = tk.Radiobutton(self.frame, text="Keyboard", variable=v, value=1, command=lambda: self.toggleController("Keyboard"))
        ctrlBtnGam = tk.Radiobutton(self.frame, text="Gamepad", variable=v, value=2, command=lambda: self.toggleController("Gamepad"))
        ctrlBtnAI  = tk.Radiobutton(self.frame, text="AI", variable=v, value=3, command=lambda: self.toggleController("AI"))
        # Start buttons for the controllers
        keyCtrlBtn = tk.Button(self.frame, text = 'Keyboard controller', width = 25, command = self.startKeyCtrl)
        gameCtrlBtn = tk.Button(self.frame, text = 'Gamepad controller', width = 25, command = self.startGameCtrl)
        relayCtrlBtn = tk.Button(self.frame, text = 'Staircase AI', width = 25, command = self.startAICtrl)
        # Labels
        self.var1 = tk.StringVar()
        labelCfg = tk.Label(self.frame, textvariable=self.var1)
        self.var1.set("Select controller")
        self.var2 = tk.StringVar()
        labelParam = tk.Label(self.frame, textvariable=self.var2)
        self.var2.set("Set AR Drone Parameters (Set doesn't work yet)")
        # Image
        photo = tk.PhotoImage(file=self.controller.PATH+"/media/ardrone.gif")
        pictureLabel = tk.Label(self.frame, image=photo)
        pictureLabel.photo = photo
        # Parameter entries
        self.sva = []
        self.paramAR = ("Max Altitude [mm]", "Min Altitude [mm]", "Max Vertical Speed [mm/sec]", "Max Yaw Speed [rad/sec]", "Max Euler Angle [rad/sec]", "No Shell [0/1]", "Outdoor [0/1]")
        self.namespace = "/ardrone_driver/"
        self.paramARRos = (self.namespace+"altitude_max",self.namespace+"altitude_min",self.namespace+"control_vz_max",self.namespace+"control_yaw",self.namespace+"euler_angle_max",self.namespace+"flight_without_shell",self.namespace+"outdoor")
        for f in self.paramAR:
            i = len(self.sva)
            self.sva.append(tk.StringVar())
            tk.Label(self.frame, text=f).grid(column=0, row=i+5)
            tk.Entry(self.frame, width=6, textvariable=self.sva[i]).grid(column=1, row=i+5)
        # Parameter buttons
        getParamBtn = tk.Button(self.frame, text = 'Get Parameters', width = 25, command = self.getParameters)
        setParamBtn = tk.Button(self.frame, text = 'Set Parameters', width = 25, command = self.setParameters)
        
        # Grid placement of all the GUI elements
        labelCfg.grid(row=0,column=0,columnspan=2)

        ctrlBtnKey.grid(row=1,column=0,sticky=tk.W)
        ctrlBtnGam.grid(row=2,column=0,sticky=tk.W)
        ctrlBtnAI.grid(row=3,column=0,sticky=tk.W)

        keyCtrlBtn.grid(row=1,column=1)
        gameCtrlBtn.grid(row=2,column=1)
        relayCtrlBtn.grid(row=3,column=1)

        labelParam.grid(row=4,column=0,columnspan=2)

        getParamBtn.grid(row=12, column=0)
        setParamBtn.grid(row=12, column=1)

        pictureLabel.grid(row=0, column=2, rowspan=13, columnspan=1, sticky=tk.E)

    def getParameters(self):
        for i in range(len(self.paramARRos)):
            self.sva[i].set(rospy.get_param(self.paramARRos[i]))

    def setParameters(self):
        for i in range(len(self.paramARRos)):
            if i==3 or i==4:
                rospy.set_param(self.paramARRos[i], float(self.sva[i].get()))
            else:
                rospy.set_param(self.paramARRos[i], int(self.sva[i].get()))

    def startKeyCtrl(self):
        self.app = keyboardController(self.master, self.controller)

    def startGameCtrl(self):
        self.app = gamepadController(self.master, self.controller)

    def startAICtrl(self):
        self.app = staircaseAI(self.master, self.controller)

    def toggleController(self,controller):
        if not rospy.is_shutdown():
            self.controller.controllerSelect = controller
            rospy.loginfo("Controller is set to: "+self.controller.controllerSelect)
        else:
            print "ERROR: rospy.is_shutdown == 1"
            sys.exit(0)

    def close(self):
        try:
            self.app.close()
        except:
            pass