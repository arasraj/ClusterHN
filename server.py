import tornado.httpserver
import tornado.ioloop
import tornado.web

from retriever import Retriever
from cluster import Clustering


class MainHandler(tornado.web.RequestHandler):
  def get(self):
    html = '<html><body><h3>HN Cluster groups</h3>'
    r = Retriever()
    allwords, index, doc_to_title = r.retrieve()
    c = Clustering()
    root, cluster_doc_map = c.hcluster(allwords, index)
    relevant_clusters = c.subclusters(root, 0.85)
    print '##################'
    singles = []
    for cluster in relevant_clusters:
      item_c = c.subcluster_items(cluster, cluster_doc_map, doc_to_title)
      if len(item_c) == 1: singles.append(item_c[0]); continue
      for item in item_c:
        html += '<a href="%s">%s</a><br>' % (doc_to_title[cluster_doc_map[item]][1],
                                             doc_to_title[cluster_doc_map[item]][0])
      html += '<hr><br><br>'
    html += '<h3>Single clusters</h3>'
    for item in singles:
      html += '<a href="%s">%s</a><br>' % (doc_to_title[cluster_doc_map[item]][1],
                                            doc_to_title[cluster_doc_map[item]][0])
    html += '</body></html>'

    self.write(html)

application = tornado.web.Application([(r'/hn', MainHandler),])

if __name__ == "__main__":
  print 'HN Cluster loaded....'
  print 'Starting web server...'
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8888)
  tornado.ioloop.IOLoop.instance().start()
