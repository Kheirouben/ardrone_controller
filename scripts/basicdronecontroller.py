import Tkinter as tk
import roslib, rospy, rospkg, os
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from ardrone_autonomy.msg import Navdata


class droneStatus(object):
    Emergency = 0
    Inited    = 1
    Landed    = 2
    Flying    = 3
    Hovering  = 4
    Test      = 5
    TakingOff = 6
    GotoHover = 7
    Landing   = 8
    Looping   = 9

class basicDroneController(object):
    controllerSelect = "None"

    def __init__(self):
        # Holds the current drone status
        self.status = -1
        rospack = rospkg.RosPack()
        self.PATH = rospack.get_path('ardrone_controller')
        self.COMMAND_PERIOD = 100 #ms
        # Subscribe to the /ardrone/navdata topic, of message type navdata, and call self.receiveNavdata when a message is received
        self.subNavdata = rospy.Subscriber('/ardrone/navdata',Navdata,self.receiveNavdata, queue_size=10) 
        
        # Allow the controller to publish to the /ardrone/takeoff, land and reset topics
        self.pubLand    = rospy.Publisher('/ardrone/land',Empty, queue_size=10)
        self.pubtakeoff = rospy.Publisher('/ardrone/takeoff',Empty, queue_size=10)
        self.pubReset   = rospy.Publisher('/ardrone/reset',Empty, queue_size=10)
        
        # Allow the controller to publish to the /cmd_vel topic and thus control the drone
        self.pubCommand = rospy.Publisher('/cmd_vel',Twist, queue_size=10)
        
        # Setup regular publishing of control packets
        self.command = Twist()
        self.commandTimer = rospy.Timer(rospy.Duration(self.COMMAND_PERIOD/1000.0),self.sendCommand)

        # Land the drone if we are shutting down
        rospy.on_shutdown(self.landBeforeExit)

    def receiveNavdata(self,navdata):
        # Although there is a lot of data in this packet, we're only interested in the state at the moment    
        self.status = navdata.state

    def sendtakeoff(self,ID):
        # Send a takeoff message to the ardrone driver
        # Note we only send a takeoff message if the drone is landed - an unexpected takeoff is not good!
        if(self.status == droneStatus.Landed and ID==self.controllerSelect):
            self.pubtakeoff.publish(Empty())

    def sendLand(self,ID):
        # Send a landing message to the ardrone driver
        # Note we send this in all states, landing can do no harm
        if(ID==self.controllerSelect):
            self.pubLand.publish(Empty())

    def sendEmergency(self,ID):
        # Send an emergency (or reset) message to the ardrone driver
        if(ID==self.controllerSelect):
            self.pubReset.publish(Empty())

    def setCommand(self,roll=0,pitch=0,yaw_velocity=0,z_velocity=0,ID="None"):
        # Called by the main program to set the current command
        if ID == self.controllerSelect:
            self.command.linear.x  = pitch
            self.command.linear.y  = roll
            self.command.linear.z  = z_velocity
            self.command.angular.z = yaw_velocity
        else:
            print "ERROR: "+ID+" Controller access denied. Current controller is "+self.controllerSelect

    def sendCommand(self,event):
        # The previously set command is then sent out periodically if the drone is flying
        if self.status == droneStatus.Flying or self.status == droneStatus.GotoHover or self.status == droneStatus.Hovering:
            self.pubCommand.publish(self.command)

    def landBeforeExit(self):
        self.sendLand(self.controllerSelect)