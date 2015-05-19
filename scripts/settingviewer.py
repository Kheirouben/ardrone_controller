import Tkinter as tk

class settingViewer:
    def __init__(self,CONTROLLER):
        self.window = tk.Toplevel()
        self.window.title("Setting Viewer")
        img = tk.PhotoImage(file=CONTROLLER.PATH+'/media/settingslogo.gif')
        self.window.tk.call('wm', 'iconphoto', self.window._w, img)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        

        self.settings = {
            'ARDRONE DRIVER':'-ip 192.168.2.165\nrealtime_navdata = True\nnavdata_demo = False\nlooprate = 30ms\nrealtime_video = False\naltitude_max = 10000mm',
            'TUM ARDRONE':'agressiveness=0.5',
            'STATIC TRANSFORM PUBLISHER':'Period = 10ms',
            'LSD-SLAM':'minUseGrad = 15\ncameraPixelNoise = 30',
            'CLUSTERING':'Distance = centroid distance\nThreshold = 1m\nCluster size = 10',
            'DETECTION':'/// Minimal distance to camera sensor in liveframe that will be considered.\nfloat minZ=0.1f;\n/// Maximal distance from camera sensor in liveframe that will be considered.\nfloat    maxZ=2.0f;\n/// Factor that determines the size of depth image with respect to the visual image.\nfloat scaleDepthImage = 3.0f;\n/// The size of the structuring element in x direction\nfloat struct_x=3;\n/// The size of the structuring element in y direction\nfloat struct_y=2;\nfloat gauss_sigma=2.0f;\nint gauss_size=5;\ndouble maxAngle = 8.0;\n/// minimum number of lines to withhold candidate\nunsigned int minLines = 5;\n/// minimum angle to be a stair\nfloat minStairAngle=0.35f;\n/// maximum angle to be a stair\nfloat maxStairAngle=1.3f;\n/// if the variance of a point in the keyframe is lower than this value it is withheld\nfloat scaledDepthVarTH = 0.01;\n/// the number of neighbours a point needs to be valid\nint minNearSupport = 5;\n/// cut-off after this\ndouble lastFrameTime = 1e15;',
        }
        self.packageList = []
        for k in range(len(self.settings)):
            self.packageList.append(self.settings.keys()[k])

        self.var1 = tk.StringVar()
        drop = tk.OptionMenu(self.window,self.var1,*self.packageList,command=self.updateSettingLabel)
        drop.config(width=30)
        drop.grid(row=0,column=0,columnspan=1,sticky=tk.N)

        self.var2 = tk.StringVar()
        settingLabel = tk.Label(self.window,textvariable=self.var2,height=26,width=65,bg='white',justify=tk.LEFT,anchor=tk.NW,padx=20,pady=8)
        settingLabel.grid(row=0,column=1,columnspan=1)

        self.var1.set(self.settings.keys()[0])
        self.var2.set(self.settings.values()[0])

    def updateSettingLabel(self,arg):
        newlabel = self.settings[self.var1.get()]
        self.var2.set(newlabel)

        
    def close(self):
        """Close the Settings viewer interface"""
        self.window.destroy()