# Import classes
import random
from clusterClass import *

# -- Create a random Point in n-dimensional space
def makeRandomPoint(n, lower, upper):
    coords = []
    for i in range(n): coords.append(random.uniform(lower, upper))
    return Point(coords)

# -- Main function
def main(args):
    num_points, n, lower, upper = 20, 3, -200, 200
    #k, kmeans_cutoff = 3, 0.5
    # Create num_points random Points in n-dimensional space, print them
    #print "\nPOINTS:"
    points = []
    for i in range(num_points):
        p = makeRandomPoint(n, lower, upper)
        points.append(p)

    # Cluster the points using the agglomerative algorithm

    linkage, agglo_cutoff, verbosity = 't', 150.0, 0
    targetPoint = agglomerativeClustering(points,linkage,agglo_cutoff,verbosity)
    print '\nTarget set to ', targetPoint,'\n'   
    
# -- The following code executes upon command-line invocation
if __name__ == "__main__": main(sys.argv)