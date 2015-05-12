import Tkinter as tk
import rospy, roslaunch, math
from geometry_msgs.msg import Twist, PointStamped

class staircaseAI:
    ID = "AI"
    def __init__(self, master, CONTROLLER):
        self.window = tk.Toplevel()
        self.window.title("AI Controller")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        # windowsize
        windowWidth = 800
        windowHeight = windowWidth/(1+math.sqrt(5))*2
        self.window.geometry("%dx%d%+d%+d" % (windowWidth, windowHeight, 550, 125)) # width, height, x-offset, y-offset
        # Grid size = 6x6 --> Unit size:
        uW=int(windowWidth/60)
        uH=int(windowHeight/300)
        # GUI STUFF
        # Define titles
        titleLeft = tk.Label(self.window, text="AI Controller")
        titleRightUp = tk.Label(self.window, text="Visualization")
        titleRightDown = tk.Label(self.window, text="Log")
        # Define buttons (LEFT)
        scanBtn     = tk.Button(self.window,text="Scan Envrionment",width=3*uW,height=uH,command=self.close)
        takeoverBtn = tk.Button(self.window,text="AI Takeover",width=3*uW,height=uH,command=self.close)
        goBtn       = tk.Button(self.window,text="Go",width=uW,height=uH,command=self.close)
        returnBtn   = tk.Button(self.window,text="Return",width=uW,height=uH,command=self.close)
        stopBtn     = tk.Button(self.window,text="Stop",width=uW,height=uH,command=self.close)
        # Define buttons (RIGHT)
        targetBtn   = tk.Button(self.window,text="Targets",width=uW,height=uH,command=self.close)
        obstacleBtn = tk.Button(self.window,text="Obstacles",width=uW,height=uH,command=self.close)
        trailBtn    = tk.Button(self.window,text="Trail",width=uW,height=uH,command=self.close)

        # Place titles and buttons in grid
        titleLeft.grid(row=0,column=0,columnspan=3)
        scanBtn.grid(row=1,column=0,columnspan=3)
        takeoverBtn.grid(row=2,column=0,columnspan=3)
        goBtn.grid(row=3,column=0,columnspan=1)
        returnBtn.grid(row=3,column=1,columnspan=1)
        stopBtn.grid(row=3,column=2,columnspan=1)

        titleRightUp.grid(row=0,column=3,columnspan=3)
        targetBtn.grid(row=1,column=3,columnspan=1)
        obstacleBtn.grid(row=1,column=4,columnspan=1)
        trailBtn.grid(row=1,column=5,columnspan=1)

        titleRightDown.grid(row=2,column=3,columnspan=3)



        # Start 
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.sub = rospy.Subscriber("ardrone_thesis/ai_cmd_vel", Twist, self.callbackRelay)

        #tk.Label(self.window, text="\n\nThis tool forwards Twist messages from\n\n'ardrone_thesis/ai_cmd_vel'\n\nTo\n\n'cmd_vel'", justify=tk.LEFT).pack()
        
        
        self.controller = CONTROLLER

    def callbackRelay(self,data):
        rospy.loginfo("Relaying message: %s",data)
        if self.controller.controllerSelect == self.ID:
            if not rospy.is_shutdown():
                self.pub.publish(data)
        else:
            print "ERROR: AI Controller access denied. Current controller is "+self.controller.controllerSelect

    def close(self):
        self.pub.unregister()
        self.sub.unregister()
        self.window.destroy()
        rospy.loginfo("AI Controller is destroyed")