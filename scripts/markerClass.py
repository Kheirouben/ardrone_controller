#!/usr/bin/env python

from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
import rospy

class markerArrayRVIZ:
    def __init__(self,MAX,SCALE,COLOR,REFERENCEFRAME,PUBLISHER):
        self.targetMarkerArray = MarkerArray()
        self.targetCount = 0
        self.markerMax = MAX
        self.markerScale = SCALE
        self.markerColor = COLOR
        self.referenceFrame = REFERENCEFRAME
        self.publisher = PUBLISHER

    def addMarker(self,point):
        self.targetCount+=1
        if self.targetCount>self.markerMax:
            print 'marker dropped'
            self.dropMarker()
        # Construct new marker
        print 'New marker added, count = %d'%self.targetCount
        marker = Marker()
        marker.header.frame_id = self.referenceFrame
        marker.type = marker.SPHERE
        marker.action = marker.ADD
        marker.scale.x = self.markerScale
        marker.scale.y = self.markerScale
        marker.scale.z = self.markerScale
        marker.color.a = 1.0
        marker.color.r = self.markerColor[0]
        marker.color.g = self.markerColor[1]
        marker.color.b = self.markerColor[2]
        marker.pose.position.x = point[0]
        marker.pose.position.y = point[1]
        marker.pose.position.z = point[2]
        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 0.0
        # Add new marker to the array and publish the MarkerArray
        self.targetMarkerArray.markers.append(marker)

        # Renumber the marker IDs
        id = 0
        for m in self.targetMarkerArray.markers:
           m.id = id
           id += 1


        self.publisher.publish(self.targetMarkerArray)

    def dropMarker(self):
        self.targetMarkerArray.markers.pop(0)
        self.targetCount-=1


