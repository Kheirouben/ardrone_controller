#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import PointStamped


def talker():
    pub = rospy.Publisher('/pointcloudregistration/target', PointStamped, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(15) # 10hz
    m = PointStamped()
    m.header.frame_id = '/tum_base_frontcam'
    while not rospy.is_shutdown():
        m.header.stamp = rospy.Time.now()
        m.point.x = 0.0
        m.point.y = 1.0
        m.point.z = 1.0
        log_str = "Send point to /pointcloudregistration/target"
        rospy.loginfo(log_str)
        pub.publish(m)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass