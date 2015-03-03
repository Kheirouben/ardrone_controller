#!/usr/bin/env python

import Tkinter as tk

import roslib; roslib.load_manifest('ardrone_controller')
import os
import rospy, roslaunch, sys, select, termios, tty, commands
from std_msgs.msg import String
from geometry_msgs.msg import Twist      # for sending commands to the drone
from sensor_msgs.msg import Joy

from drone_controller import BasicDroneController
# from keyboard_controller import keyboardController


class KeyMapping(object):
    PitchForward     = "e"
    PitchBackward    = "d"
    RollLeft         = "s"
    RollRight        = "f"
    YawLeft          = "j"
    YawRight         = "l"
    IncreaseAltitude = "i"
    DecreaseAltitude = "k"
    Takeoff          = "t"
    Land             = "y"
    Emergency        = "u"
    Exit             = "C" # Shift + C to exit the program


class keyboardController:
    ID = "Keyboard"
    pitch = 0
    roll = 0
    yaw_velocity = 0 
    z_velocity = 0
    counter = 0
    def __init__(self, master):
        self.master = master
        self.newWindow = tk.Toplevel()
        self.newWindow.title("Keyboard Controller")
        self.newWindow.geometry("%dx%d%+d%+d" % (300, 280, 250, 125))
        self.frame = tk.Frame(self.master)
        self.frame.bind("<Key>", self.key)
        self.frame.bind("<Button-1>", self.callback)
        self.frame.pack()

        tk.Label(self.newWindow, text="\n\n---------------------\n|  "+KeyMapping.PitchForward+"    "+KeyMapping.Takeoff+KeyMapping.Land+KeyMapping.Emergency+"    "+KeyMapping.IncreaseAltitude+"  |\n| "+KeyMapping.RollLeft+KeyMapping.PitchBackward+KeyMapping.RollRight+"          "+KeyMapping.YawLeft+KeyMapping.DecreaseAltitude+KeyMapping.YawRight+" |\n---------------------\n\n "+KeyMapping.PitchForward+KeyMapping.PitchBackward+": Pitch\n "+KeyMapping.RollLeft+KeyMapping.RollRight+": Roll\n "+KeyMapping.IncreaseAltitude+KeyMapping.DecreaseAltitude+": Height\n "+KeyMapping.YawLeft+KeyMapping.YawRight+": Yaw\n\n "+KeyMapping.Takeoff+": Takeoff\n "+KeyMapping.Land+": Land\n "+KeyMapping.Emergency+": Emergency", justify=tk.LEFT).pack()
        

    def key(self,event):
        key = event.char
        if key != '':
            self.counter = 0
            if key == KeyMapping.Takeoff:
                CONTROLLER.SendTakeoff()
            elif key == KeyMapping.Land:
                CONTROLLER.SendLand()
            elif key == KeyMapping.Emergency:
                CONTROLLER.SendEmergency()
            else:
                if key == KeyMapping.PitchForward:
                    self.pitch += 1
                elif key == KeyMapping.PitchBackward:
                    self.pitch += -1
                elif key == KeyMapping.RollLeft:
                    self.roll += 1
                elif key == KeyMapping.RollRight:
                    self.roll += -1
                elif key == KeyMapping.YawLeft:
                    self.yaw_velocity += 1
                elif key == KeyMapping.YawRight:
                    self.yaw_velocity += -1
                elif key == KeyMapping.IncreaseAltitude:
                    self.z_velocity += 1
                elif key == KeyMapping.DecreaseAltitude:
                    self.z_velocity += -1
                elif key == KeyMapping.Exit:
                    rospy.signal_shutdown('Great Flying!')
                    sys.exit(1)
                else:
                    print "Not a configured key"
        else:
            if self.counter == 4:
                self.pitch = 0
                self.roll = 0
                self.yaw_velocity = 0 
                self.z_velocity = 0
                self.counter+=1
            elif self.counter<4:
                self.counter+=1
        CONTROLLER.SetCommand(self.roll, self.pitch, self.yaw_velocity, self.z_velocity,self.ID)

    def callback(self,event):
        self.frame.focus_set()


class gamepadController:
    ID = "Gamepad"
    # Get joystick controller
    device = commands.getoutput('ls /dev/input/js*')

    # define the default mapping between joystick buttons and their corresponding actions
    ButtonEmergency = 0
    ButtonLand      = 1
    ButtonTakeoff   = 2

    # define the default mapping between joystick axes and their corresponding directions
    AxisRoll        = 0
    AxisPitch       = 1
    AxisYaw         = 3
    AxisZ           = 4

    # define the default scaling to apply to the axis inputs. useful where an axis is inverted
    ScaleRoll       = 1.0
    ScalePitch      = 1.0
    ScaleYaw        = 1.0
    ScaleZ          = 1.0

    
    def __init__(self, master):
        self.master = master
        self.newWindow = tk.Toplevel()
        self.newWindow.title("Gamepad Controller")
        self.newWindow.protocol("WM_DELETE_WINDOW", self.close)
        
        # Configure GUI
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        photo = tk.PhotoImage(file=PATH+"gamepad.gif")
        pictureLabel = tk.Label(self.newWindow, image=photo)
        pictureLabel.photo = photo
        pictureLabel.pack()

        # Start Joy node
        rospy.set_param("joy_node/dev", self.device)
        package = 'joy'
        executable = 'joy_node'
        node = roslaunch.core.Node(package, executable)

        launch = roslaunch.scriptapi.ROSLaunch()
        launch.start()

        self.process = launch.launch(node)
        print "Joynode started =",self.process.is_alive()

        # Next load in the parameters from the launch-file
        self.ButtonEmergency = int (   rospy.get_param("~ButtonEmergency",self.ButtonEmergency) )
        self.ButtonLand      = int (   rospy.get_param("~ButtonLand",self.ButtonLand) )
        self.ButtonTakeoff   = int (   rospy.get_param("~ButtonTakeoff",self.ButtonTakeoff) )
        self.AxisRoll        = int (   rospy.get_param("~AxisRoll",self.AxisRoll) )
        self.AxisPitch       = int (   rospy.get_param("~AxisPitch",self.AxisPitch) )
        self.AxisYaw         = int (   rospy.get_param("~AxisYaw",self.AxisYaw) )
        self.AxisZ           = int (   rospy.get_param("~AxisZ",self.AxisZ) )
        self.ScaleRoll       = float ( rospy.get_param("~ScaleRoll",self.ScaleRoll) )
        self.ScalePitch      = float ( rospy.get_param("~ScalePitch",self.ScalePitch) )
        self.ScaleYaw        = float ( rospy.get_param("~ScaleYaw",self.ScaleYaw) )
        self.ScaleZ          = float ( rospy.get_param("~ScaleZ",self.ScaleZ) )

        # subscribe to the /joy topic and handle messages of type Joy with the function ReceiveJoystickMessage
        self.subJoystick = rospy.Subscriber('/joy', Joy, self.ReceiveJoystickMessage)

    # handles the reception of joystick packets
    def ReceiveJoystickMessage(self,data):
        if data.buttons[self.ButtonEmergency]==1:
            rospy.loginfo("Emergency Button Pressed")
            CONTROLLER.SendEmergency()
        elif data.buttons[self.ButtonLand]==1:
            rospy.loginfo("Land Button Pressed")
            CONTROLLER.SendLand()
        elif data.buttons[self.ButtonTakeoff]==1:
            rospy.loginfo("Takeoff Button Pressed")
            CONTROLLER.SendTakeoff()
        else:
            CONTROLLER.SetCommand(data.axes[self.AxisRoll]/self.ScaleRoll,data.axes[self.AxisPitch]/self.ScalePitch,data.axes[self.AxisYaw]/self.ScaleYaw,data.axes[self.AxisZ]/self.ScaleZ, self.ID)
    
    def close(self):
        print "Shutting down the joy_node"
        self.process.stop()
        self.subJoystick.unregister()
        self.newWindow.destroy()

class rosRelayer:
    ID = "AI"
    def __init__(self, master):
        self.master = master
        self.newWindow = tk.Toplevel()
        self.newWindow.title("AI Controller Relay")
        self.newWindow.protocol("WM_DELETE_WINDOW", self.close)

        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.sub = rospy.Subscriber("ardrone_thesis/ai_cmd_vel", Twist, self.callbackRelay)
        
        # Configure GUI
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        tk.Label(self.newWindow, text="\n\nThis tool forwards Twist messages from\n\n'ardrone_thesis/ai_cmd_vel'\n\nTo\n\n'cmd_vel'", justify=tk.LEFT).pack()
        self.newWindow.geometry("%dx%d%+d%+d" % (300, 180, 550, 125))
        


    def callbackRelay(self,data):
        rospy.loginfo("Relaying message: %s",data)
        if CONTROLLER.controllerSelect == self.ID:
            if not rospy.is_shutdown():
                self.pub.publish(data)
        else:
            print "ERROR: AI Controller access denied. Current controller is "+CONTROLLER.controllerSelect

    def close(self):
        self.pub.unregister()
        self.sub.unregister()
        self.newWindow.destroy()


class ardroneGUIController:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        # Select the current Controller
        v = tk.StringVar()
        v.set("0") # initialize
        ctrlBtnKey = tk.Radiobutton(self.frame, text="Keyboard", variable=v, value=1, command=lambda: self.toggleController("Keyboard"))
        ctrlBtnGam = tk.Radiobutton(self.frame, text="Gamepad", variable=v, value=2, command=lambda: self.toggleController("Gamepad"))
        ctrlBtnAI  = tk.Radiobutton(self.frame, text="AI", variable=v, value=3, command=lambda: self.toggleController("AI"))
        # Start buttons for the controllers
        self.keyCtrlBtn = tk.Button(self.frame, text = 'Keyboard controller', width = 25, command = self.startKeyCtrl)
        self.gameCtrlBtn = tk.Button(self.frame, text = 'Gamepad controller', width = 25, command = self.startGameCtrl)
        self.relayCtrlBtn = tk.Button(self.frame, text = 'AI relay', width = 25, command = self.startRelayCtrl)
        # Labels
        self.var1 = tk.StringVar()
        labelCfg = tk.Label(self.frame, textvariable=self.var1)
        self.var1.set("Select controller")
        self.var2 = tk.StringVar()
        labelParam = tk.Label(self.frame, textvariable=self.var2)
        self.var2.set("Set AR Drone Parameters")
        # Image
        photo = tk.PhotoImage(file=PATH+"ardrone.gif")
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

        self.keyCtrlBtn.grid(row=1,column=1)
        self.gameCtrlBtn.grid(row=2,column=1)
        self.relayCtrlBtn.grid(row=3,column=1)

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
        self.app = keyboardController(self.master)

    def startGameCtrl(self):
        self.app = gamepadController(self.master)

    def startRelayCtrl(self):
        self.app = rosRelayer(self.master)

    def toggleController(self,controller):
        if not rospy.is_shutdown():
            CONTROLLER.controllerSelect = controller
            rospy.loginfo("Controller is set to: "+CONTROLLER.controllerSelect)
        else:
            print "ERROR: rospy.is_shutdown == 1"
            sys.exit(0)

if __name__ == '__main__':
    PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
    rospy.init_node('ardrone_gui_controller')
    CONTROLLER = BasicDroneController()
    root = tk.Tk()
    root.title('AR Drone GUI Controller')
    #root.minsize(width=300, height=100)
    app = ardroneGUIController(root)
    root.mainloop()