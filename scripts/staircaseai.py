import Tkinter as tk
import rospy, roslaunch, math, logging, os
from geometry_msgs.msg import Twist, PointStamped
from std_msgs.msg import String
from threading import Thread
import dynamic_reconfigure.client
from clusterNode import *
from basicdronecontroller import droneStatus

class staircaseAI:
    ID = "AI"
    rvizStatus = 0
    detectionStatus = 0
    def __init__(self, master, CONTROLLER):
        """Initialize the AI class"""

        # GUI STUFF
        self.window = tk.Toplevel()
        self.window.title("AI Controller")
        img = tk.PhotoImage(file=CONTROLLER.PATH+'/media/ailogo.gif')
        self.window.tk.call('wm', 'iconphoto', self.window._w, img)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        # windowsize
        windowWidth = 570
        windowHeight = windowWidth/(1+math.sqrt(5))*2
        self.window.geometry("%dx%d%+d%+d" % (windowWidth, windowHeight, 550, 125)) # width, height, x-offset, y-offset
        # Grid size = 6x6 --> Unit size:
        uW=int(windowWidth/26)
        uH=int(windowHeight/200)
        # Define log widget
        logViewer = tk.Scrollbar(self.window)
        self.logText = tk.Text(self.window)
        self.logText.focus_set()
        logViewer.config(command=self.logText.yview)
        self.logText.config(yscrollcommand=logViewer.set,height=int(windowHeight/30))

        # Start controller and detection mechanism
        self.controller = CONTROLLER
        self.log('Controller started')

        self.detectionMarkerPublisher = rospy.Publisher('staircase_detectionmarker_visualization', MarkerArray, queue_size=10)
        self.goalMarkerPublisher = rospy.Publisher('staircase_goalmarker_visualization', MarkerArray, queue_size=10)
        self.tumComChannel = rospy.Publisher('/tum_ardrone/com', String, queue_size=10)
        self.cluster = clusterNode(self.log,self.detectionMarkerPublisher,self.goalMarkerPublisher,'t',150.0)
        self.targetSub = rospy.Subscriber('/pointcloudregistration/target', PointStamped, self.cluster.processPoints, queue_size=10)

        # Other GUI STUFF
        # Define titles
        titleLeft = tk.Label(self.window, text="AI Controller", font=("Helvetica", 18))
        titleRightUp = tk.Label(self.window, text="Launch and Visualization", font=("Helvetica", 18))
        titleDown = tk.Label(self.window, text="Log", font=("Helvetica", 18))
        # Define buttons (LEFT)
        scanBtn     = tk.Button(self.window,text="Scan Envrionment",command=self.initializeAI)
        takeoverBtn = tk.Button(self.window,text="AI Takeover",command=self.goAI)
        goBtn       = tk.Button(self.window,text="Go",command=self.goAI)
        returnBtn   = tk.Button(self.window,text="Return",command=self.close)
        stopBtn     = tk.Button(self.window,text="Stop",command=self.stopAI)
        # Define buttons (RIGHT)
        detectionBtn= tk.Button(self.window,text="Launch detection",command=self.launchPointcloudregistration)
        ardroneDriverBtn= tk.Button(self.window,text="Launch driver",command=self.launchArdroneDriver)
        self.rvizBtnText = tk.StringVar(); self.rvizBtnText.set("Launch RVIZ")
        rvizBtn   = tk.Button(self.window,textvariable=self.rvizBtnText,command=self.launchRVIZ)
        updateClusterBtn   = tk.Button(self.window,text="Update Cluster",command=self.cluster.update)
        resetClusterBtn = tk.Button(self.window,text="Reset Cluster",command=self.cluster.reset)

        # Place titles and buttons in grid
        titleLeft.grid(row=0,column=0,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)
        scanBtn.grid(row=1,column=0,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)
        takeoverBtn.grid(row=2,column=0,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)
        goBtn.grid(row=3,column=0,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        returnBtn.grid(row=3,column=1,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        stopBtn.grid(row=3,column=2,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        

        titleRightUp.grid(row=0,column=3,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)
        detectionBtn.grid(row=1,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        ardroneDriverBtn.grid(row=1,column=5,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        rvizBtn.grid(row=2,column=3,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)
        updateClusterBtn.grid(row=3,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        resetClusterBtn.grid(row=3,column=5,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)

        titleDown.grid(row=4,column=0,columnspan=6,sticky=tk.N+tk.E+tk.S+tk.W)
        self.logText.grid(row=5,column=0,columnspan=6,sticky=tk.N+tk.E+tk.W)

        self.log('AI initialized and ready to roll')

    def log(self,string):
        """Puts text in the logscreen of the AI GUI"""
        self.logText.insert(1.0,string+'\n')

    def launchRVIZ(self):
        """Launch rviz with the custom setup that is used in ardrone_controller together with launchStaticTf()"""
        if self.rvizStatus==1:
            self.rvizProcess.stop()
            self.launchStaticTf(0)
            self.rvizBtnText.set("Launch RVIZ")
            self.rvizStatus=0
            self.log('RVIZ is stopped')
        else:
            self.launchStaticTf(1)
            xmlFile = self.controller.PATH+'/model/ardrone2.xml'
            rospy.set_param('robot_description', open(xmlFile,'r').read())
            rospy.set_param('/use_sim_time',True)
            node = roslaunch.core.Node('rviz','rviz','rviz_ardrone','','','-d $(find ardrone_controller)/launch/staircasedetection.rviz')
            launch = roslaunch.scriptapi.ROSLaunch()
            launch.start()
            self.rvizProcess = launch.launch(node)
            self.rvizBtnText.set("Stop RVIZ")
            self.rvizStatus=1
            self.log('RVIZ is started')

    def launchStaticTf(self,toggle):
        """Launch the tf static transform node from the body of the ardrone to the camera axis. If the argument is 0, the static transform is stopped."""
        if toggle==0:
            self.staticTfProcess.stop()
            self.log('Static Tf is stopped')
        else:
            node = roslaunch.core.Node('tf','static_transform_publisher','tf_cam_to_base_ardrone','','','0.210 0 0.0 -0.5 0.5 -0.5 0.5 tum_base_link tum_base_frontcam 100')
            launch = roslaunch.scriptapi.ROSLaunch()
            launch.start()
            self.staticTfProcess = launch.launch(node)
            self.log('Static Tf is started')

    def launchPointcloudregistration(self):
        """Launch pointcloudregistration with all its dependend nodes: Image Rectifier and LSD_SLAM"""
        if self.detectionStatus==0:
            # Launch image rectifier node
            node = roslaunch.core.Node('image_proc','image_proc','image_proc_ardrone','/ardrone/front')
            launch = roslaunch.scriptapi.ROSLaunch()
            launch.start()
            self.imageRectifyProcess = launch.launch(node)
            # Launch lsd_slam_core
            node = roslaunch.core.Node('lsd_slam_core','live_slam','lsd_slam_core_ardrone','','','image:=/ardrone/front/image_rect camera_info:=/ardrone/front/camera_info')
            launch = roslaunch.scriptapi.ROSLaunch()
            launch.start()
            self.lsdslamProcess = launch.launch(node)
            # Reconfigure lsd_slam_core
            dynConfLSDSLAM = dynamic_reconfigure.client.Client('lsd_slam_core_ardrone')
            params = { 'minUseGrad' : 15, 'cameraPixelNoise' : 30 }
            config = dynConfLSDSLAM.update_configuration(params)
            client = dynamic_reconfigure.client.Client('lsd_slam_core_ardrone')
            # Launch pointcloudregistration
            node = roslaunch.core.Node('pointcloudregistration','registrar','registrar','','','image:=/ardrone/front/image_rect')
            launch = roslaunch.scriptapi.ROSLaunch()
            launch.start()
            self.detectionProcess = launch.launch(node)

            self.detectionStatus=1
            self.log('Detection node is started')
        else:
            self.detectionProcess.stop()
            self.lsdslamProcess.stop()
            self.imageRectifyProcess.stop()
            self.detectionStatus=0
            self.log('Detection node is shut down')

    def launchArdroneDriver(self):
        # Launch lsd_slam_core
        node = roslaunch.core.Node('ardrone_autonomy','ardrone_driver','ardrone_driver','','','-ip 192.168.2.165')
        launch = roslaunch.scriptapi.ROSLaunch()
        launch.start()
        self.ardroneDriverProcess = launch.launch(node)
        dynConfArdroneDriver = dynamic_reconfigure.client.Client('ardrone_driver')
        params = { 'navdata_demo' : False, 'realtime_navdata' : True, 'realtime_video' : True, 'looprate' : 30, 'altitude_max' : 10000 }
        config = dynConfArdroneDriver.update_configuration(params)
        client = dynamic_reconfigure.client.Client('ardrone_driver')
        # Launch tum_ardrone
        node = roslaunch.core.Node('tum_ardrone','drone_stateestimation','drone_stateestimation_ardrone')
        launch = roslaunch.scriptapi.ROSLaunch()
        launch.start()
        self.droneStateestimationProcess = launch.launch(node)
        node = roslaunch.core.Node('tum_ardrone','drone_autopilot','drone_autopilot_ardrone')
        launch = roslaunch.scriptapi.ROSLaunch()
        launch.start()
        self.droneAutopilotProcess = launch.launch(node)
        node = roslaunch.core.Node('tum_ardrone','drone_gui','drone_gui_ardrone')
        launch = roslaunch.scriptapi.ROSLaunch()
        launch.start()
        self.droneGuiProcess = launch.launch(node)

    def stopAI(self):
        command = 'c stop'
        self.tumComChannel.publish(command)

    def goAI(self):
        self.log('Sending command to the drone')
        if len(self.cluster.targetPoint)!=0:
            commands = []
            commands.append('c clearCommands')
            commands.append('c goto %f %f %f 0' % (self.cluster.targetPoint[0],self.cluster.targetPoint[1],self.cluster.targetPoint[2]))
            # Publish commands
            for i in range(0,len(commands)):
                self.tumComChannel.publish(commands[i])

    def initializeAI(self):
        self.log('Initializing AI')
        if self.controller.status == droneStatus.Flying or self.controller.status == droneStatus.GotoHover or self.controller.status == droneStatus.Hovering:
            self.log('Drone is already in the air')
        else:
            self.log('Sending commands to the drone')
            commands = []
            commands.append('f reset')
            commands.append('c autoInit 1000 800 4000 0.3')
            commands.append('c setReference $POSE$')
            commands.append('c setInitialReachDist 0.2')
            commands.append('c setStayWithinDist 0.3')
            commands.append('c setStayTime 3')
            commands.append('c lockScaleFP')
            commands.append('c goto 0 0 0 0')
            commands.append('c start')
            # Publish commands
            for i in range(0,len(commands)):
                self.tumComChannel.publish(commands[i])

        

    def close(self):
        """Close the AI GUI interface"""
        self.detectionMarkerPublisher.unregister()
        self.goalMarkerPublisher.unregister()
        self.targetSub.unregister()
        self.window.destroy()
        if self.rvizStatus==1:
            self.rvizProcess.stop()
            self.staticTfProcess.stop()
        if self.detectionStatus==1:
            self.detectionProcess.stop()
            self.lsdslamProcess.stop()
            self.imageRectifyProcess.stop()

        rospy.loginfo("AI Controller is destroyed")