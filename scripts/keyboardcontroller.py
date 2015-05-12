import Tkinter as tk
import rospy
#from basicdronecontroller import *
from ardrone_gui_controller import *

class keyMapping(object):
    pitchForward     = "e"
    pitchBackward    = "d"
    rollLeft         = "s"
    rollRight        = "f"
    yawLeft          = "j"
    yawRight         = "l"
    increaseAltitude = "i"
    decreaseAltitude = "k"
    takeoff          = "t"
    land             = "y"
    emergency        = "u"
    exit             = "C" # Shift + C to exit the program


class keyboardController:
    pitch = 0
    roll = 0
    yaw_velocity = 0 
    z_velocity = 0
    counter = 0
    def __init__(self, master, CONTROLLER):
        self.ID = "Keyboard"
        self.newWindow = tk.Toplevel()
        self.newWindow.title("Keyboard Controller")
        self.newWindow.geometry("%dx%d%+d%+d" % (300, 280, 250, 125))
        self.newWindow.bind("<Key>", self.key)
        self.newWindow.bind("<KeyRelease>", self.onkeyrelease)
        # self.newWindow.bind("<Button-1>", self.callback)
        tk.Label(self.newWindow, text="\n\n---------------------\n|  "+keyMapping.pitchForward+"    "+keyMapping.takeoff+keyMapping.land+keyMapping.emergency+"    "+keyMapping.increaseAltitude+"  |\n| "+keyMapping.rollLeft+keyMapping.pitchBackward+keyMapping.rollRight+"          "+keyMapping.yawLeft+keyMapping.decreaseAltitude+keyMapping.yawRight+" |\n---------------------\n\n "+keyMapping.pitchForward+keyMapping.pitchBackward+": pitch\n "+keyMapping.rollLeft+keyMapping.rollRight+": Roll\n "+keyMapping.increaseAltitude+keyMapping.decreaseAltitude+": Height\n "+keyMapping.yawLeft+keyMapping.yawRight+": Yaw\n\n "+keyMapping.takeoff+": takeoff\n "+keyMapping.land+": Land\n "+keyMapping.emergency+": Emergency", justify=tk.LEFT).pack()
        self.controller= CONTROLLER

        
    def onkeyrelease(self,event):
        self.pitch = 0
        self.roll = 0
        self.yaw_velocity = 0 
        self.z_velocity = 0
        self.controller.setCommand(self.roll, self.pitch, self.yaw_velocity, self.z_velocity,self.ID)

    def key(self,event):
        key = event.char
        if key != '':
            #self.counter = 0
            if key == keyMapping.takeoff:
                self.controller.sendtakeoff(self.ID)
            elif key == keyMapping.land:
                self.controller.sendLand(self.ID)
            elif key == keyMapping.emergency:
                self.controller.sendEmergency(self.ID)
            else:
                if key == keyMapping.pitchForward:
                    self.pitch += 1
                elif key == keyMapping.pitchBackward:
                    self.pitch += -1
                elif key == keyMapping.rollLeft:
                    self.roll += 1
                elif key == keyMapping.rollRight:
                    self.roll += -1
                elif key == keyMapping.yawLeft:
                    self.yaw_velocity += 1
                elif key == keyMapping.yawRight:
                    self.yaw_velocity += -1
                elif key == keyMapping.increaseAltitude:
                    self.z_velocity += 1
                elif key == keyMapping.decreaseAltitude:
                    self.z_velocity += -1
                elif key == keyMapping.exit:
                    rospy.signal_shutdown('Great Flying!')
                    sys.exit(1)
                else:
                    print "ERROR: Not a configured key"

        self.controller.setCommand(self.roll, self.pitch, self.yaw_velocity, self.z_velocity,self.ID)
