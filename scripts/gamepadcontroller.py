import commands, rospy, roslaunch
from sensor_msgs.msg import Joy
import Tkinter as tk

class gamepadController:
    # Get joystick controller
    device = commands.getoutput('ls /dev/input/js*')

    # define the default mapping between joystick buttons and their corresponding actions
    buttonEmergency = 0
    buttonLand      = 1
    buttonTakeoff   = 2

    # define the default mapping between joystick axes and their corresponding directions
    axisRoll        = 0
    axisPitch       = 1
    axisYaw         = 3
    axisZ           = 4

    # define the default scaling to apply to the axis inputs. useful where an axis is inverted
    scaleRoll       = 1.0
    scalePitch      = 1.0
    scaleYaw        = 1.0
    scaleZ          = 1.0

    
    def __init__(self, CONTROLLER):
    	self.ID = "Gamepad"
        self.window = tk.Toplevel()
        self.window.title("Gamepad Controller")
        img = tk.PhotoImage(file=CONTROLLER.PATH+'/media/gamepadlogo.gif')
        self.window.tk.call('wm', 'iconphoto', self.window._w, img)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        
        self.controller = CONTROLLER

        photo = tk.PhotoImage(file=self.controller.PATH+"/media/gamepad2.gif")
        pictureLabel = tk.Label(self.window, image=photo)
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
        self.buttonEmergency = int (   rospy.get_param("~buttonEmergency",self.buttonEmergency) )
        self.buttonLand      = int (   rospy.get_param("~buttonLand",self.buttonLand) )
        self.buttonTakeoff   = int (   rospy.get_param("~buttonTakeoff",self.buttonTakeoff) )
        self.axisRoll        = int (   rospy.get_param("~axisRoll",self.axisRoll) )
        self.axisPitch       = int (   rospy.get_param("~axisPitch",self.axisPitch) )
        self.axisYaw         = int (   rospy.get_param("~axisYaw",self.axisYaw) )
        self.axisZ           = int (   rospy.get_param("~axisZ",self.axisZ) )
        self.scaleRoll       = float ( rospy.get_param("~scaleRoll",self.scaleRoll) )
        self.scalePitch      = float ( rospy.get_param("~scalePitch",self.scalePitch) )
        self.scaleYaw        = float ( rospy.get_param("~scaleYaw",self.scaleYaw) )
        self.scaleZ          = float ( rospy.get_param("~scaleZ",self.scaleZ) )

        # subscribe to the /joy topic and handle messages of type Joy with the function ReceiveJoystickMessage
        self.subJoystick = rospy.Subscriber('/joy', Joy, self.ReceiveJoystickMessage)

    # handles the reception of joystick packets
    def ReceiveJoystickMessage(self,data):
        if data.buttons[self.buttonEmergency]==1:
            rospy.loginfo("Emergency Button Pressed")
            self.controller.sendEmergency(self.ID)
        elif data.buttons[self.buttonLand]==1:
            rospy.loginfo("Land Button Pressed")
            self.controller.sendLand(self.ID)
        elif data.buttons[self.buttonTakeoff]==1:
            rospy.loginfo("Takeoff Button Pressed")
            self.controller.sendTakeoff(self.ID)
        else:
            self.controller.setCommand(data.axes[self.axisRoll]/self.scaleRoll,data.axes[self.axisPitch]/self.scalePitch,data.axes[self.axisYaw]/self.scaleYaw,data.axes[self.axisZ]/self.scaleZ, self.ID)
    
    def close(self):
        rospy.loginfo("Gamepad Controller is destroyed")
        try:
            self.process.stop()
        except AttributeError:
            print 'Process could not be stopped'
        self.window.destroy()