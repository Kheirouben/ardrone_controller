#!/usr/bin/env python

import roslib; roslib.load_manifest('ardrone_controller')
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
from geometry_msgs.msg import PointStamped
from std_msgs.msg import String
import rospy, math, tf

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + " I heard (%f,%f,%f)", data.point.x, data.point.y, data.point.z)
    data.header.stamp = rospy.Time()
    print data.header.stamp
    marker = Marker()
    marker.header.frame_id = "/map"
    marker.type = marker.SPHERE
    marker.action = marker.ADD
    marker.scale.x = .1
    marker.scale.y = .1
    marker.scale.z = .1
    marker.color.a = 1.0
    marker.color.r = 0.0
    marker.color.g = 1.0
    marker.color.b = 0.0
    #marker.pose.orientation.w = 1.0
    global tf_listener
    worldPoint = tf_listener.transformPoint('/map',data)
    marker.pose.position.x = worldPoint.point.x
    marker.pose.position.y = worldPoint.point.y
    marker.pose.position.z = worldPoint.point.z
    marker.pose.orientation.x = 0.0
    marker.pose.orientation.y = 0.0
    marker.pose.orientation.z = 0.0
    marker.pose.orientation.w = 0.0
    # We add the new marker to the MarkerArray, removing the oldest
    # marker from it when necessary
    global count, MARKERS_MAX, MarkerArray
    if(count > MARKERS_MAX):
       markerArray.markers.pop(0)

    markerArray.markers.append(marker)

    # Renumber the marker IDs
    id = 0
    for m in markerArray.markers:
       m.id = id
       id += 1
    
    publisher.publish(markerArray)

    count += 1


def targetListener():
    rospy.Subscriber("/pointcloudregistration/target", PointStamped, callback)
    rospy.spin()


class rvizMarkers(object):
    def __init__(self):
        self.targetMarkerArray = MarkerArray()
        self.targetCount = 0
        self.obstacleMarkerArray = MarkerArray()
        self.obstacleCount = 0
        self.markerMax = 50
        self.markerScale = 0.1
        self.referenceFrame = '/map'

    def plotMarkerArray(self,pointStamped,arrayID):
        marker = Marker()
        marker.header.frame_id = self.referenceFrame
        marker.type = marker.SPHERE
        marker.action = marker.ADD
        marker.scale.x = .1
        marker.scale.y = .1
        marker.scale.z = .1
        marker.color.a = 1.0
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0

    def plotSingleMarker(self,pointStamped,color):
        marker = Marker()
        marker.header.frame_id = self.referenceFrame
        marker.type = marker.SPHERE
        marker.action = marker.ADD
        marker.scale.x = .1
        marker.scale.y = .1
        marker.scale.z = .1
        marker.color.a = 1.0
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0



if __name__=="__main__":
    topic = 'staircase_detection_visualization'
    publisher = rospy.Publisher(topic, MarkerArray, queue_size=10)

    rospy.init_node('listener')

    markerArray = MarkerArray()

    count = 0
    MARKERS_MAX = 50
    
    tf_listener = tf.TransformListener()

    targetListener()