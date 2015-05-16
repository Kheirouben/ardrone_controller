import sys, math, numpy, rospy, tf
from geometry_msgs.msg import PointStamped
from markerClass import *

# -- The Point class represents points in n-dimensional space
class Point:
    # Instance variables
    # self.coords is a list of coordinates for this Point
    # self.n is the number of dimensions this Point lives in (ie, its space)
    # self.reference is an object bound to this Point
    # Initialize new Points
    def __init__(self, coords, reference=None):
        self.coords = coords
        self.n = len(coords)
        self.reference = reference
    # Return a string representation of this Point
    def __repr__(self):
        return str(self.coords)


# -- The Cluster class represents clusters of points in n-dimensional space
class Cluster:
    # Instance variables
    # self.points is a list of Points associated with this Cluster
    # self.n is the number of dimensions this Cluster's Points live in
    # self.centroid is the sample mean Point of this Cluster
    # Initialize new Clusters
    def __init__(self, points):
        # We forbid empty Clusters (they don't make mathematical sense!)
        if len(points) == 0: raise Exception("ILLEGAL: EMPTY CLUSTER")
        self.points = points
        self.n = points[0].n
        # We also forbid Clusters containing Points in different spaces
        # Ie, no Clusters with 2D Points and 3D Points
        for p in points:
            if p.n != self.n: raise Exception("ILLEGAL: MULTISPACE CLUSTER")
        # Figure out what the centroid of this Cluster should be
        self.centroid = self.calculateCentroid()
    # Return a string representation of this Cluster
    def __repr__(self):
        return str(self.points)
    # Update function for the K-means algorithm
    # Assigns a new list of Points to this Cluster, returns centroid difference
    def update(self, points):
        old_centroid = self.centroid
        self.points = points
        self.centroid = self.calculateCentroid()
        return self.getDistance(old_centroid, self.centroid)
    # Calculates the centroid Point - the centroid is the sample mean Point
    # (in plain English, the average of all the Points in the Cluster)
    def calculateCentroid(self):
        centroid_coords = []
        # For each coordinate:
        for i in range(self.n):
            # Take the average across all Points
            centroid_coords.append(0.0)
            for p in self.points:
                centroid_coords[i] = centroid_coords[i]+p.coords[i]
            centroid_coords[i] = centroid_coords[i]/len(self.points)
        # Return a Point object using the average coordinates
        return Point(centroid_coords)
    # Return the single-linkage distance between this and another Cluster
    def getSingleDistance(self, cluster):
        ret = self.getDistance(self.points[0], cluster.points[0])
        for p in self.points:
            for q in cluster.points:
                distance = self.getDistance(p, q)
                if distance < ret: ret = distance
        return ret
    # Return the complete-linkage distance between this and another Cluster
    def getCompleteDistance(self, cluster):
        ret = self.getDistance(self.points[0], cluster.points[0])
        for p in self.points:
            for q in cluster.points:
                distance = self.getDistance(p, q)
                if distance > ret: ret = distance
        return ret
    # Return the centroid-linkage distance between this and another Cluster
    def getCentroidDistance(self, cluster):
        return self.getDistance(self.centroid, cluster.centroid)
    # Return the fusion of this and another Cluster
    def fuse(self, cluster):
        # Forbid fusion of Clusters in different spaces
        if self.n != cluster.n: raise Exception("ILLEGAL FUSION")
        points = self.points
        points.extend(cluster.points)
        return Cluster(points)

    # -- Get the Euclidean distance between two Points
    def getDistance(self, a, b):
        # Forbid measurements between Points in different spaces
        if a.n != b.n: raise Exception("ILLEGAL: NON-COMPARABLE POINTS")
        # Euclidean distance between a and b is sqrt(sum((a[i]-b[i])^2) for all i)
        ret = 0.0
        for i in range(a.n):
            ret = ret+pow((a.coords[i]-b.coords[i]), 2)
        return math.sqrt(ret)

# -- Return a distance matrix which captures distances between all Clusters
class clusterNode:
    def __init__(self,targetLABEL,LOG,detectionPUB,goalPUB,linkage,agglo_cutoff,AMOUNTOFPOINTS):
        """Initialize point clustering class"""
        # Initialize agglomerative clustering parameters
        self.linkage = linkage
        self.agglo_cutoff = agglo_cutoff
        self.verbosity = 1
        # Initialize variables
        self.pointArray = []
        self.maxAmountOfPoints = AMOUNTOFPOINTS # maximum amount of points in the array
        self.targetLocked = 0
        self.targetPoint = []
        self.targetLabel = targetLABEL
        # Initialize rosnode
        self.tf_listener = tf.TransformListener()

        self.log = LOG
        # Create markers
        self.targetMarkers = markerArrayRVIZ(self.maxAmountOfPoints,0.1,[1,0,0],'/map',detectionPUB)
        self.goalMarker = markerArrayRVIZ(1,0.5,[0,1,0],'/map',goalPUB)
        self.log('ClusterNode initialized: listening to detection output')
        
    def reset(self):
        self.targetPoint = []
        self.pointArray = []
        self.targetLocked = 0
        self.targetLabel.set('NO')
        self.log('ClusterNode will be reset with the next detected point')

    def update(self):
        self.targetPoint = []
        self.targetLocked = 0
        self.targetLabel.set('NO')
        self.log('ClusterNode will be updated with the next detected point')

    def processPoints(self,pointStamped):
        """Process incoming points. Project to '/map' coordinates and puts them into an array"""
        #pointStamped.header.stamp = rospy.Time()
        nP = self.tf_listener.transformPoint('/map',pointStamped) # new Point
        self.pointArray.append(Point([nP.point.x,nP.point.y,nP.point.z]))
        self.targetMarkers.addMarker([nP.point.x,nP.point.y,nP.point.z])
        # If the point array has the maximum amount of points
        if len(self.pointArray)>self.maxAmountOfPoints:
            self.pointArray = self.pointArray[1:][:]
            # Call the cluster function if the maximum amount of points is reached
            if self.targetLocked==0:
                self.targetPoint = self.agglomerativeClustering(self.pointArray,self.linkage,self.agglo_cutoff,self.verbosity)
                self.goalMarker.addMarker(self.targetPoint)
                self.targetLocked = 1
                message = 'Agglomerative clustering produced goal:'+str(self.targetPoint)
                self.log(str(message))
                self.targetLabel.set('YES')
                print '\nTarget set to ', self.targetPoint,'\n'

    # -- Returns the central position of the biggest Cluster (agglomerative clustering)
    def agglomerativeClustering(self, points, linkage, cutoff, verbosity):
        #
        stopClustering = 0
        while not stopClustering:
            # Currently, we only allow single, complete, or average linkage
            if not linkage in [ 's', 'c', 't' ]: raise Exception("INVALID LINKAGE")
            # Create singleton Clusters, one for each Point
            clusters = []
            for p in points: clusters.append(Cluster([p]))
            # Set the min_distance between Clusters to zero
            min_distance = 0
            # Loop until the break statement is made
            while (True):
                # Compute a distance matrix for all Clusters
                distances = self.makeDistanceMatrix(clusters, linkage)
                # Find the key for the Clusters which are closest together
                if len(distances.keys())==0:
                    print 'The solution is a single cluster'
                    break
                min_key = distances.keys()[0]
                min_distance = distances[min_key]
                for key in distances.keys():
                    if distances[key] < min_distance:
                        min_key = key
                        min_distance = distances[key]
                # If the min_distance is bigger than the cutoff, terminate the loop
                # Otherwise, agglomerate the closest clusters
                if min_distance > cutoff or len(clusters) == 1: break
                else:
                    c1, c2 = clusters[min_key[0]], clusters[min_key[1]]
                    clusters.remove(c1)
                    clusters.remove(c2)
                    clusters.append(c1.fuse(c2))

            clustersSize = numpy.array([])
            for k in range(0,len(clusters)): clustersSize=numpy.append(clustersSize,len(clusters[k].points))

            if sum(clustersSize==max(clustersSize))==1: # Check if there is only 1 cluster with maximum size
                biggestCluster = numpy.where(clustersSize==max(clustersSize))[0]
                clusterCenter = numpy.array([0.0,0.0,0.0])
                for k in clusters[biggestCluster].points:
                    clusterCenter+=numpy.array(k.coords)
                clusterCenter = clusterCenter/float(max(clustersSize))
                if verbosity==1:
                    print '\nAgglomerative cluster algorithm formed '+str(len(clusters))+' clusters from '+str(sum(clustersSize))+' points'
                    print '  The biggest cluster contains '+str(max(clustersSize))+' points'
                    print '  The mean coordinate of that cluster is '
                    print '  (', clusterCenter[0],',',clusterCenter[1],',',clusterCenter[2],')\n'
                stopClustering = 1
            else:
                if verbosity==1:
                    print '\nAgglomerative cluster algorithm formed '+str(len(clusters))+' clusters from '+str(sum(clustersSize))+' points'
                    print '  Did not find a singular top cluster'
                # Soften the cutoff criterium by 5% to create larger clusters
                cutoff=cutoff*1.05

        
        # Return the list of Clusters
        return clusterCenter

    def makeDistanceMatrix(self, clusters, linkage):
        ret = dict()
        for i in range(len(clusters)):
            for j in range(len(clusters)):
                if j == i: break
                if linkage == 's':
                    ret[(i,j)] = clusters[i].getSingleDistance(clusters[j])
                elif linkage == 'c':
                    ret[(i,j)] = clusters[i].getCompleteDistance(clusters[j])
                elif linkage == 't':
                    ret[(i,j)] = clusters[i].getCentroidDistance(clusters[j])
                else: raise Exception("INVALID LINKAGE")
        return ret






