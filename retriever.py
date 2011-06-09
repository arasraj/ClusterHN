import urllib2
import html5lib 
import re
import os
import stemmer
from collections import defaultdict
from html5lib import treebuilders


class Retriever:

  def __init__(self):
    pass

  def retrieve(self):
    #links = self.scrape_links()
    #self.download_pages(links)
    parsed_htmls = self.parser()
    allwords, index, doc_to_title = self.indexer(parsed_htmls)
    return allwords, index, doc_to_title
    
  
  def scrape_links(self):
    """
      Grab all links to news stories from HN.
      Only first 4 HN pages are scraped.
    """

    index_links = []
    followlink = ''
    for i in range(4):
      try:
        c = urllib2.urlopen('http://news.ycombinator.com%s' % followlink)
        contents = c.read()
      except urllib2.URLError:
        continue
      links = re.findall(r'title"><a href="(.+?)"', contents) #? changes + to non-greedy

      for link in links[:-1]:
        #print link
        if link[-3:] not in ['pdf', 'avi', 'mp4']:
          index_links.append(link)
      followlink = links[-1]

    #print '\n'.join(index_links) 
    return index_links


  def download_pages(self, links):
    """
      Follow all links obstained from scraping HN
      and write to disk for later processing.
    """

    i=0
    for link in links:
      try:
        c = urllib2.urlopen(link)
        data = c.read()
        f = open('pages/'+str(i), 'w')
        i+=1
        f.write('%s\n' % link)
        f.write(data)
        f.close()
      except Exception:
        pass


  def parser(self):
    """
      Here I use html5lib so parse the pages retrieved.
      I am using BeautifulSoup as my parser here and I know it 
      is deprecated.  I will change this soon...

      Content is taken only from <p> tags, so this could be a lot
      more robust. 

      All words are stemmed and stopwords are removed.
    """

    #get stopwords; remove newline char
    parsed_html = {}
    stopwords = [word[:-1] for word in open('stopwords.txt')]
    pstemmer = stemmer.PorterStemmer()
    

    htmldocs = os.listdir('pages/') #grap all html docs and parse them
    words_splitter = re.compile(r'\W*') #split on non words
    for htmldoc in htmldocs:
      f = open('pages/'+htmldoc, 'r')
      link = f.readline()
      html = f.readlines()

      try:
        print htmldoc
        p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('beautifulsoup'))
        tree = p.parse(html)
      except:
        os.remove(os.path.join('pages', htmldoc))
        print 'error parsing %s' % htmldoc
        continue

      title = tree.findAll('title')
      if title: title = title[0].text
      else: title = ''

      #grab text from p tags
      data = [p.text.lower() for p in tree.findAll('p')]
      #remove stopwords
      unstemmed_words = [word for word in words_splitter.split(''.join(data)) 
                              if word != '' and word not in stopwords]
      stemmed_words = [pstemmer.stem(word,0,len(word)-1) for word in unstemmed_words]
      parsed_html[(title,int(htmldoc),link)] = stemmed_words

    return parsed_html
    
  
  def indexer(self, doc_terms_dict):
    """
      Index all doc/html pages using vector space model.
      Dimensions are words (term frequencies).
    """

    term_freq = {}
    allterms = {}
    doc_titles = {}
    count = 0
    print ''
    for doc, terms in sorted(doc_terms_dict.items(), key=lambda doc: doc[1]): 
      doc_titles[doc[1]] = (doc[0], doc[2][:-1]) #get doc title, id, and link
      freq = defaultdict(lambda: 0)

      #get tf
      for term in terms:
        freq[term] += 1
        if term not in allterms:
          allterms[term]=count
          count += 1
      term_freq[doc[1]] = freq

    #allterms = dict(enumerate(allterms))
    return (allterms, term_freq, doc_titles)




