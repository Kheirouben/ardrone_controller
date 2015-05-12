#!/usr/bin/env python

import Tkinter as tk
import roslib
roslib.load_manifest('ardrone_controller')

from ardroneguicontroller import *

if __name__ == '__main__':
    rospy.init_node('ardrone_gui_controller')
    CONTROLLER = basicDroneController()
    root = tk.Tk()
    root.title('AR Drone GUI Controller')
    app = ardroneGUIController(root, CONTROLLER)
    root.mainloop()
