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
        aiCtrlBtn = tk.Button(self.frame, text = 'Staircase AI', width = 25, command = self.startAICtrl)
        # Labels
        self.var1 = tk.StringVar()
        labelCfg = tk.Label(self.frame, text="Select controller")
        
        # Grid placement of all the GUI elements
        labelCfg.grid(row=0,column=0,columnspan=2)

        ctrlBtnKey.grid(row=1,column=0,sticky=tk.W)
        ctrlBtnGam.grid(row=2,column=0,sticky=tk.W)
        ctrlBtnAI.grid(row=3,column=0,sticky=tk.W)

        keyCtrlBtn.grid(row=1,column=1)
        gameCtrlBtn.grid(row=2,column=1)
        aiCtrlBtn.grid(row=3,column=1)

    def startKeyCtrl(self):
        self.app1 = keyboardController(self.controller)

    def startGameCtrl(self):
        self.app2 = gamepadController(self.controller)

    def startAICtrl(self):
        self.app3 = staircaseAI(self.controller)

    def toggleController(self,controller):
        if not rospy.is_shutdown():
            self.controller.controllerSelect = controller
            rospy.loginfo("Controller is set to: "+self.controller.controllerSelect)
        else:
            print "ERROR: rospy.is_shutdown == 1"
            sys.exit(0)

    def close(self):
        try:
            self.app1.close()
        except:
            pass
        try:
            self.app2.close()
        except:
            pass
        try:
            self.app3.close()
        except:
            pass