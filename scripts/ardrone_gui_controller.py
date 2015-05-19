#!/usr/bin/env python

import Tkinter as tk
import roslib, rospy
roslib.load_manifest('ardrone_controller')

from ardroneguicontroller import *

def quit():
    app.close()
    rospy.loginfo('Exiting ardrone_controller')
    try:
        root.destroy()
    except rospy.ROSInterruptException:
        print 'ROS exited'
    else:
        pass

if __name__ == '__main__':
    rospy.init_node('ardrone_gui_controller')
    CONTROLLER = basicDroneController()
    root = tk.Tk()
    root.title('AR Drone GUI Controller')
    img = tk.PhotoImage(file=CONTROLLER.PATH+'/media/softwarelogo.gif')
    root.tk.call('wm', 'iconphoto', root._w, img)
    app = ardroneGUIController(root, CONTROLLER)
    root.protocol("WM_DELETE_WINDOW", quit)
    root.mainloop()
