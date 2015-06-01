import Tkinter as tk
import rospy, roslaunch, math, logging, os
from geometry_msgs.msg import Twist, PointStamped
from std_msgs.msg import String
from threading import Thread
import dynamic_reconfigure.client
from clusterNode import *
from basicdronecontroller import droneStatus
from lsd_slam_core.srv import *
from settingviewer import *

class staircaseAI:
    ID = "AI"
    # Initialize status parameters
    ardroneDriverStatus = 0
    tumArdroneStatus = 0
    detectionNodeStatus = 0
    RVIZStatus = 0
    LSDSLAMViewerStatus = 0
    rqtImageViewerStatus = 0
    
    def __init__(self, CONTROLLER):
        """Initialize the AI class"""

        # GUI STUFF
        self.window = tk.Toplevel()
        self.window.title("AI Controller")
        img = tk.PhotoImage(file=CONTROLLER.PATH+'/media/ailogo.gif')
        self.window.tk.call('wm', 'iconphoto', self.window._w, img)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        # windowsize
        #windowWidth = 1130
        #windowHeight = windowWidth/(1+math.sqrt(5))*2
        #self.window.geometry("%dx%d%+d%+d" % (windowWidth, windowHeight, 550, 125)) # width, height, x-offset, y-offset
        # Grid size = 6x6 --> Unit size:
        #uW=int(windowWidth/26)
        #uH=int(windowHeight/200)
        
        # Define log widget
        self.logText = tk.Text(self.window)
        self.logText.focus_set()
        self.logText.config(height=10)
        # Define detection widget
        self.detectionText = tk.Text(self.window)
        self.detectionText.focus_set()
        self.detectionText.config(height=10)
        # Early definition of target label indicator --> pass on to cluster
        self.targetLockedText = tk.StringVar()

        # Start controller and detection mechanism
        self.controller = CONTROLLER
        self.log('Controller started')

        self.detectionMarkerPublisher = rospy.Publisher('staircase_detectionmarker_visualization', MarkerArray, queue_size=10)
        self.goalMarkerPublisher = rospy.Publisher('staircase_goalmarker_visualization', MarkerArray, queue_size=10)
        self.tumComPublisher = rospy.Publisher('/tum_ardrone/com', String, queue_size=10)
        self.cluster = clusterNode(self.targetLockedText, self.logDet,self.detectionMarkerPublisher, self.goalMarkerPublisher,'t',1.0,10)
        self.targetSub = rospy.Subscriber('/pointcloudregistration/target', PointStamped, self.cluster.processPoints, queue_size=10)

        # Other GUI STUFF
        # Define titles
        titleTopLeft = tk.Label(self.window, text="AI Controller", font=("Helvetica", 16))
        titleTopCenter = tk.Label(self.window, text="Toggle ON/OFF", font=("Helvetica", 16))
        titleTopRight = tk.Label(self.window, text="Status", font=("Helvetica", 16))
        titleCenterLeft = tk.Label(self.window, text="Staircase Guidance", font=("Helvetica", 16))
        titleBottomLeft = tk.Label(self.window, text="Detection", font=("Helvetica", 16))
        titleBottomRight = tk.Label(self.window, text="Log", font=("Helvetica", 16))

        # Define buttons (LEFT)
        settingsBtn = tk.Button(self.window,text='Settings',command=self.viewSettings)
        initBtn     = tk.Button(self.window,text="Initialize",command=self.initializeAI)
        stopBtn     = tk.Button(self.window,text="Stop",command=self.stopAI)
        
        resetEKFBtn = tk.Button(self.window,text="Reset EKF",command=self.resetEKF)
        resetPTAMBtn = tk.Button(self.window,text="Reset PTAM",command=self.resetPTAM)
        initLSDSLAMBtn = tk.Button(self.window,text="Re-init LSD-SLAM",command=self.initLSDSLAM)

        takeoffBtn = tk.Button(self.window,text="Takeoff",command= lambda: self.controller.sendtakeoff(self.ID))
        landBtn = tk.Button(self.window,text="Land",command= lambda: self.controller.sendLand(self.ID))
        emergencyBtn = tk.Button(self.window,text="Emergency",command= lambda: self.controller.sendEmergency(self.ID))

        self.commandEntryText = tk.StringVar()
        commandEntry = tk.Entry(self.window,textvariable=self.commandEntryText)
        self.commandEntryText.set('tum_ardrone command. e.g. "c goto 0 0 0 0"')
        sendCommandBtn = tk.Button(self.window,text="Send Command",command=self.sendCommand)        

        goBtn       = tk.Button(self.window,text="Go",command=self.goAI)
        updateClusterBtn   = tk.Button(self.window,text="Update Cluster",command=self.cluster.update)
        resetClusterBtn = tk.Button(self.window,text="Reset Cluster",command=self.cluster.reset)

        # Define buttons and labels (RIGHT)
        ardroneDriverBtn = tk.Button(self.window,text="Launch AR.Drone driver",command=self.launchArdroneDriver)
        self.ardroneDriverLbl = tk.Label(self.window,text="OFF", fg="red")

        tumArdroneBtn = tk.Button(self.window,text="Launch TUM ARDRONE",command=self.launchTumArdrone)
        self.tumArdroneLbl = tk.Label(self.window,text="OFF", fg="red")
        
        detectionNodeBtn = tk.Button(self.window,text="Launch detection node",command=self.launchDetectionNode)
        self.detectionNodeLbl = tk.Label(self.window,text="OFF", fg="red")
        
        RVIZBtn = tk.Button(self.window,text="Launch RVIZ",command=self.launchRVIZ)
        self.RVIZLbl = tk.Label(self.window,text="OFF", fg="red")
        
        LSDSLAMViewerBtn = tk.Button(self.window,text="Launch LSD-SLAM Viewer",command=self.launchLSDSLAMViewer)
        self.LSDSLAMViewerLbl = tk.Label(self.window,text="OFF", fg="red")
        
        rqtImageViewerBtn = tk.Button(self.window,text="Launch RQT Image Viewer",command=self.launchrqtImageViewer)
        self.rqtImageViewerLbl = tk.Label(self.window,text="OFF", fg="red")
        
        targetLockedStaticLbl = tk.Label(self.window,text="Target Locked")
        targetLockedLbl = tk.Label(self.window,textvariable=self.targetLockedText); self.targetLockedText.set('NO')
        
        # Place titles, labels, entries and buttons in grid
        titleTopLeft.grid(row=0,column=0,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)
        titleTopCenter.grid(row=0,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        titleTopRight.grid(row=0,column=4,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        titleCenterLeft.grid(row=5,column=0,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)
        titleBottomLeft.grid(row=8,column=0,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)
        titleBottomRight.grid(row=8,column=3,columnspan=2,sticky=tk.N+tk.E+tk.S+tk.W)

        settingsBtn.grid(row=1,column=0,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        initBtn.grid(row=1,column=1,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        stopBtn.grid(row=1,column=2,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)

        resetEKFBtn.grid(row=2,column=0,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        resetPTAMBtn.grid(row=2,column=1,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        initLSDSLAMBtn.grid(row=2,column=2,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)

        takeoffBtn.grid(row=3,column=0,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        landBtn.grid(row=3,column=1,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        emergencyBtn.grid(row=3,column=2,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        
        commandEntry.grid(row=4,column=0,columnspan=2,sticky=tk.N+tk.E+tk.S+tk.W)
        sendCommandBtn.grid(row=4,column=2,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)

        goBtn.grid(row=6,column=0,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        updateClusterBtn.grid(row=6,column=1,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        resetClusterBtn.grid(row=6,column=2,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)

        self.detectionText.grid(row=9,column=0,rowspan=1,columnspan=3,sticky=tk.N+tk.E+tk.S+tk.W)

        ardroneDriverBtn.grid(row=1,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.ardroneDriverLbl.grid(row=1,column=4,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)

        tumArdroneBtn.grid(row=2,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.tumArdroneLbl.grid(row=2,column=4,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        
        detectionNodeBtn.grid(row=3,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.detectionNodeLbl.grid(row=3,column=4,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        
        RVIZBtn.grid(row=4,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.RVIZLbl.grid(row=4,column=4,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        
        LSDSLAMViewerBtn.grid(row=5,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.LSDSLAMViewerLbl.grid(row=5,column=4,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        
        rqtImageViewerBtn.grid(row=6,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        self.rqtImageViewerLbl.grid(row=6,column=4,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        
        targetLockedStaticLbl.grid(row=7,column=3,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)
        targetLockedLbl.grid(row=7,column=4,columnspan=1,sticky=tk.N+tk.E+tk.S+tk.W)

        self.logText.grid(row=9,column=3,rowspan=1,columnspan=2,sticky=tk.N+tk.E+tk.S+tk.W)


        self.launcher = roslaunch.scriptapi.ROSLaunch()
        self.launcher.start()

        self.log('AI initialized and ready to roll')

        if self.controller.controllerSelect!=self.ID:
            self.log('Please select the AI as the current controller in the previous window')

    def log(self,string):
        """Puts text in the logscreen of the AI GUI"""
        self.logText.insert(1.0,string+'\n')

    def logDet(self,string):
        """Puts text in the logscreen of the AI GUI"""
        self.detectionText.insert(1.0,string+'\n')


    def launchRVIZ(self):
        """Launch rviz with the custom setup that is used in ardrone_controller together with launchStaticTf()"""
        if self.RVIZStatus==0:
            xmlFile = self.controller.PATH+'/model/ardrone2.xml'
            rospy.set_param('robot_description', open(xmlFile,'r').read())
            #rospy.set_param('/use_sim_time',True)
            node = roslaunch.core.Node('rviz','rviz','rviz_ardrone','','','-d $(find ardrone_controller)/launch/staircasedetection.rviz')
            self.RVIZProcess = self.launcher.launch(node)
            self.RVIZStatus=1
            self.RVIZLbl.configure(fg='blue',text='ON')
            self.log('RVIZ is started')
        else:
            self.RVIZProcess.stop()
            self.RVIZStatus=0
            self.RVIZLbl.configure(fg='red',text='OFF')
            self.log('RVIZ is stopped')

    def launchDetectionNode(self):
        """Launch pointcloudregistration with all its related nodes: Static TF transform, Image Rectifier and LSD_SLAM"""
        if self.detectionNodeStatus==0:
            # Launch image rectifier node
            node = roslaunch.core.Node('image_proc','image_proc','image_proc_ardrone','/ardrone/front')
            self.imageRectifyProcess = self.launcher.launch(node)
            # Launch lsd_slam_core
            node = roslaunch.core.Node('lsd_slam_core','live_slam','lsd_slam_core_ardrone','','','image:=/ardrone/front/image_rect camera_info:=/ardrone/front/camera_info')
            self.lsdslamProcess = self.launcher.launch(node)
            # Reconfigure lsd_slam_core
            dynConfLSDSLAM = dynamic_reconfigure.client.Client('lsd_slam_core_ardrone')
            params = { 'minUseGrad' : 15, 'cameraPixelNoise' : 30 }
            config = dynConfLSDSLAM.update_configuration(params)
            client = dynamic_reconfigure.client.Client('lsd_slam_core_ardrone')
            # Launch pointcloudregistration
            node = roslaunch.core.Node('pointcloudregistration','registrar','pointcloudregistration','','','image:=/ardrone/front/image_rect')
            self.detectionProcess = self.launcher.launch(node)

            self.detectionNodeStatus=1
            self.detectionNodeLbl.configure(fg='blue',text='ON')
            self.log('Detection node is started')
        else:
            self.detectionProcess.stop()
            self.lsdslamProcess.stop()
            self.imageRectifyProcess.stop()
            
            self.detectionNodeStatus=0
            self.detectionNodeLbl.configure(fg='red',text='OFF')
            self.log('Detection node is shut down')

    def launchArdroneDriver(self):
        if self.ardroneDriverStatus==0:
            # Launch ardrone_driver
            node = roslaunch.core.Node('ardrone_autonomy','ardrone_driver','ardrone_driver','','','-ip 192.168.2.165 _realtime_navdata:=True _navdata_demo:=0 _looprate:=30 _realtime_video:=False _altitude_max:=10000')
            self.ardroneDriverProcess = self.launcher.launch(node)
            self.ardroneDriverLbl.configure(fg='blue',text='ON')
            self.ardroneDriverStatus=1
        else:
            self.ardroneDriverProcess.stop()
            self.ardroneDriverLbl.configure(fg='red',text='OFF')
            self.ardroneDriverStatus=0

    def launchTumArdrone(self):
        if self.tumArdroneStatus==0:
            # Launch tum_ardrone
            node = roslaunch.core.Node('tum_ardrone','drone_stateestimation','drone_stateestimation_ardrone')
            self.droneStateestimationProcess = self.launcher.launch(node)
            node = roslaunch.core.Node('tum_ardrone','drone_autopilot','drone_autopilot_ardrone','','','_agressiveness:=0.7')
            self.droneAutopilotProcess = self.launcher.launch(node)
            node = roslaunch.core.Node('tum_ardrone','drone_gui','drone_gui_ardrone')
            self.droneGuiProcess = self.launcher.launch(node)
            self.tumArdroneLbl.configure(fg='blue',text='ON')
            self.tumArdroneStatus=1
            # Launch Static TF transform
            node = roslaunch.core.Node('tf','static_transform_publisher','tf_cam_to_base_ardrone','','','0.210 0 0.0 -0.5 0.5 -0.5 0.5 tum_base_link tum_base_frontcam 10')
            self.staticTfProcess = self.launcher.launch(node)
        else:
            self.staticTfProcess.stop()
            self.droneStateestimationProcess.stop()
            self.droneAutopilotProcess.stop()
            self.droneGuiProcess.stop()
            self.tumArdroneLbl.configure(fg='red',text='OFF')
            self.tumArdroneStatus=0

    def launchLSDSLAMViewer(self):
        if self.LSDSLAMViewerStatus==0:
            # Launch the lsd-slam viewer
            node = roslaunch.core.Node('lsd_slam_viewer','viewer','lsd_slam_viewer_ardrone')
            self.LSDSLAMViewerProcess = self.launcher.launch(node)
            self.LSDSLAMViewerLbl.configure(fg='blue',text='ON')
            self.LSDSLAMViewerStatus=1
        else:
            self.LSDSLAMViewerProcess.stop()
            self.LSDSLAMViewerLbl.configure(fg='red',text='OFF')
            self.LSDSLAMViewerStatus=0

    def launchrqtImageViewer(self):
        if self.rqtImageViewerStatus==0:
            # Launch the rqt image viewer
            node = roslaunch.core.Node('rqt_image_view','rqt_image_view','rqt_image_view_ardrone')
            self.rqtImageViewerProcess = self.launcher.launch(node)
            self.rqtImageViewerLbl.configure(fg="blue",text="ON")
            self.rqtImageViewerStatus=1
        else:
            self.rqtImageViewerProcess.stop()
            self.rqtImageViewerLbl.configure(fg="red",text="OFF")
            self.rqtImageViewerStatus=0

    def sendCommand(self):
        command = self.commandEntryText.get()
        self.tumComPublisher.publish(command)
        self.log('The command: '+command+' is sent to the drone')

    def stopAI(self):
        commands = []
        commands.append('c stop')
        commands.append('c clearCommands')
        for i in range(0,len(commands)):
            self.tumComPublisher.publish(commands[i])
        self.log('Commands are flushed and drone is stopped')

    def goAI(self):
        self.log('Sending the drone to the target.')
        if len(self.cluster.targetPoint)!=0:
            commands = []
            commands.append('c clearCommands')
            commands.append('c setReference 0 0 0 0')
            commands.append('c goto %f %f %f 0' % (self.cluster.targetPoint[1],self.cluster.targetPoint[0],self.cluster.targetPoint[2]))
            # Publish commands
            for i in range(0,len(commands)):
                self.tumComPublisher.publish(commands[i])

    def resetEKF(self):
        commands = []
        commands.append('c stop')
        commands.append('c clearCommands')
        commands.append('f reset')
        for i in range(0,len(commands)):
            self.tumComPublisher.publish(commands[i])
        self.cluster.reset()
        self.log('EKF is resetted')
        self.logDet('Cluster is resetted, points are flushed')

    def resetPTAM(self):
        commands = []
        commands.append('c stop')
        commands.append('c clearCommands')
        commands.append('p reset')
        for i in range(0,len(commands)):
            self.tumComPublisher.publish(commands[i])
        self.log('PTAM is resetted')

    def resetLSDSLAM(self):
        rospy.wait_for_service('resetlsd')
        try:
            serviceCall = rospy.ServiceProxy('resetlsd', ResetLSD)
            response = serviceCall(True)
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e
        self.log('LSD-SLAM is resetted')


    def initLSDSLAM(self):
        commands = []
        #commands.append('c clearCommands')
        #commands.append('c setReference 0 0 0 0')
        commands.append('c goto 0.5 0 0 0')
        commands.append('c goto -0.5 0 0 0')
        commands.append('c goto 0.5 0 0 0')
        commands.append('c goto -0.5 0 0.5 0')
        commands.append('c goto 0.5 0 0.5 0')
        commands.append('c goto 0 0 0 0')
        for i in range(0,len(commands)):
            self.tumComPublisher.publish(commands[i])
        rospy.sleep(2.0)
        self.resetLSDSLAM()

    def initializeAI(self):
        self.log('Initializing AI')
        if self.controller.status == droneStatus.Flying or self.controller.status == droneStatus.GotoHover or self.controller.status == droneStatus.Hovering:
            self.log('Drone is already in the air')
        elif self.controller.status == droneStatus.Emergency:
            self.log('Drone is in emergency status. Please click the emergency button.')
        else:
            self.log('Sending commands to the drone')
            commands = []
            # commands.append('c stop')
            # commands.append('c clearCommands')
            # commands.append('f reset')
            # commands.append('c autoInit 1000 800 1000 0.3')
            # commands.append('c setReference $POSE$')
            # #commands.append('c setReference 0 0 0 0')
            # commands.append('c setInitialReachDist 0.2')
            # commands.append('c setStayWithinDist 0.3')
            # commands.append('c setStayTime 3')
            # #commands.append('c lockScaleFP')
            # commands.append('c goto 0 0 0.5 0')
            # commands.append('c goto 0 0 0 0')
            # commands.append('c start')
            commands.append('c setReference $POSE$')
            commands.append('c setInitialReachDist 0.2')
            commands.append('c setStayWithinDist 0.3')
            commands.append('c setStayTime 2')
            commands.append('c lockScaleFP')
            commands.append('c goto 0 0 0 0')
            
            # Publish commands
            for i in range(0,len(commands)):
                self.tumComPublisher.publish(commands[i])

    def takeoff(self):
        self.takeoffPublisher.publish(Empty)
    
    def viewSettings(self):
        self.settingsApp = settingViewer(self.controller)


    def close(self):
        """Close the AI GUI interface"""
        self.detectionMarkerPublisher.unregister()
        self.goalMarkerPublisher.unregister()
        self.targetSub.unregister()
        self.tumComPublisher.unregister()
        self.window.destroy()
        if self.RVIZStatus==1:
            self.RVIZProcess.stop()
        if self.detectionNodeStatus==1:
            self.detectionProcess.stop()
            self.lsdslamProcess.stop()
            self.imageRectifyProcess.stop()
            
        if self.tumArdroneStatus==1:
            self.droneStateestimationProcess.stop()
            self.droneAutopilotProcess.stop()
            self.droneGuiProcess.stop()
            self.staticTfProcess.stop()
        if self.ardroneDriverStatus==1:
            self.ardroneDriverProcess.stop()
        if self.LSDSLAMViewerStatus==1:
            self.LSDSLAMViewerProcess.stop()
        if self.rqtImageViewerStatus==1:
            self.rqtImageViewerProcess.stop()

        rospy.loginfo("AI Controller is destroyed")
