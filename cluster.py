from math import sqrt
from collections import defaultdict

class Clustring:

  def __init__(self):
    pass

  def hcluster(self, allterms, doc_term_index):
    """
      Performs hierarchical agglomerative clustering based on centroids.
    """
    #create term vectors; allwords length dimensions
    term_vecs = [(doc_id, create_vec(terms, allterms)) for doc_id, terms in doc_term_index.items()]
    
    clusters = [] #list of all clusters
    mapping = {}
    distances = {} #cache
    non_leaf_id = -1

    #create initial clusters with doc->clustID mapping
    for i in range(len(doc_term_index)):
      new_cluster = Cluster(id=i, vec=term_vecs[i][1])
      mapping[i] = term_vecs[i][0]
      clusters.append(new_cluster)

    #loop until all clusters are formed into one
    while len(clusters) > 1:
      leastsofar  = 99
      least_item = (0,1)

      #take advantage of the symmetry of distances between pairs
      for i in xrange(len(clusters)):
        clust1 = clusters[i]
        for j in xrange(i+1, len(clusters)):
          clust2 = clusters[j]
          #used cache here instead of sim matrix bc of constant insertions/deletions
          if (clust1.id, clust2.id) not in distances:
            distances[(clust1.id, clust2.id)] = pearson_sim(clust1.vec, clust2.vec)
          dist = distances[(clust1.id, clust2.id)]

          if dist < leastsofar:
            least_item = (i, j)
            leastsofar = dist
        
      #find the dimension values for the newly created vector; 
      #in this class it is the centroid of the two closest pairs of clusters
      centroid = merge(clusters[least_item[0]].vec, clusters[least_item[1]].vec)
      new_cluster = Cluster(id=non_leaf_id, vec=centroid, l_child=clusters[least_item[0]], 
                            r_child=clusters[least_item[1]], distance=dist)

      #always delete closest to end of list first to avoid key errors
      del clusters[least_item[1]]
      del clusters[least_item[0]]
      clusters.append(new_cluster)
      non_leaf_id -= 1

    #return the root of the clusters tree along with the mapping from
    #clustid to docid
    return (clusters[0], mapping)


  def merge(self, vec1, vec2):
    #return centroid/average of two vectors
    return [(vec1[i]+vec2[i])/2 for i in range(len(vec1))]


  def subclusters(self, cluster, threshold):
    """ 
        Identify senscial clusters based on of the distance id of a cluster
        is below the specified threshold
    """

    if cluster.distance < threshold:
      return [cluster]
    else:
      clust_right = None
      clust_left = None

      if cluster.l_child != None:
        clust_left = subclusters(cluster.l_child, threshold)
      if cluster.r_child != None:
        clust_right = subclusters(cluster.r_child, threshold)
      
      #returns list of relevant subclusters
      return clust_left + clust_right


  def display(self, cluster, mapping, n=0):
    #preorder traversal
    for i in range(n): print ' ',
    if cluster.id < 0:
      print '-'
    else:
      print mapping[cluster.id]

    #if (cluster.l_child == None or cluster.r_child == None):
    #	print mapping[cluster.id]
    #else:
    if cluster.l_child != None: display(cluster.l_child, mapping,n=n+1)
    #print cluster.id
    if cluster.r_child != None: display(cluster.r_child, mapping,n=n+1)


  #def simmatrix(self):
  #  matrix = []
  #  #matrix = {}
  #  allterms, doc_term_index = index()
  #  print (len(allterms))

  #  #take advantage of the symmetry of the matrix
  #  for i in xrange(len(doc_term_index)):
  #    tmp = []
  #    vec1 = create_vec(doc_term_index[i], allterms)
  #    for j in xrange(i+1,len(doc_term_index)):
  #      vec2 = create_vec(doc_term_index[j], allterms)
  #      #print vec1,vec2
  #      tmp.append(pearson_sim(vec1, vec2))
  #    matrix.append(tmp)
  #  print matrix
  #  return (matrix,doc_term_index)
          
  def create_vec(self, tf_dict, allterms):
    """ Creates term vectors """

    vec = [0]*len(allterms)
    for key,value in tf_dict.items():
      vec[allterms[key]] = value
    return vec


  def pearson_sim(self, vec1, vec2):
    """ Pearson Correl unoptimized """

    n = len(vec1)
    sum1 = sum(vec1)
    sum2 = sum(vec2)
    mean1 = float(sum1) / n
    mean2 = float(sum2) / n
    vec1_centered = [x - mean1 for x in vec1] #remove average from vecs
    vec2_centered = [y - mean2 for y in vec2]
    dotprod = sum([vec1_centered[i] * vec2_centered[i] for i in xrange(n)])
    stddevs_prod = (sqrt(sum([x*x for x in vec1_centered])) * sqrt(sum([y*y for y in vec2_centered])))

    #since similarity and distance are inverses of each other
    return 1 - (dotprod / stddevs_prod if stddevs_prod else 0)

class Cluster:
  def __init__(self, vec=0, l_child=None, r_child=None, id=None, distance=0):
    self.vec = vec
    self.l_child = l_child
    self.r_child = r_child
    self.distance = distance
    self.id = id

if __name__ == '__main__':
  clusters,mapping = hcluster()
  c = subclusters(clusters[0], 0.8)
  print '##################'
  for x in c:
    display(x, mapping)
    print '***'
