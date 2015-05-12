#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PointStamped
count=0
def callback(data):
    global count
    rospy.loginfo(rospy.get_caller_id() + "I heard (%f,%f,%f)", data.point.x, data.point.y, data.point.z)
    count+=1
    
def listener():
    
    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/pointcloudregistration/target", PointStamped, callback)
    print count

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()