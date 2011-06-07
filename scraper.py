import urllib2
import html5lib 
from html5lib import treebuilders
import re
import os
import stemmer
from collections import defaultdict
from math import sqrt

def scrape_links():
  index_links = []
  followlink = ''
  for i in range(4):
    #TODO get titles of posts
    try:
      c = urllib2.urlopen('http://news.ycombinator.com%s' % followlink)
    except urllib2.URLError:
      pass
    #contents = c.read()
    links = re.findall(r'title"><a href="(.+?)"', c.read()) #? changes + to non-greedy
    for link in links[:-1]:
      #print link
      if 'pdf' != link[-3:]:
        index_links.append(link)
    followlink = links[-1]

  #print '\n'.join(index_links) 
  return index_links

def download_pages():
  links = scrape_links()

  print '\n'.join(links) 
  i=0
  for link in links:
    try:
      print link
      c = urllib2.urlopen(link)
      data = c.read()
      f = open('pages/'+str(i), 'w')
      i+=1
      f.write(data)
      f.close()
    except Exception:
      pass

def index():
  doc_terms = parsepage()
  #term_freq = {}
  term_freq = []
  allterms = {}
  count = 0
  for doc, terms in doc_terms.items():
    freq = defaultdict(lambda: 0)
    for term in terms:
      freq[term] += 1
      if term not in allterms:
        allterms[term]=count
        count += 1
    #term_freq[doc] = freq
    term_freq.append(freq)

  #allterms = dict(enumerate(allterms))
  return (allterms, term_freq)
  
def simmatrix():
  matrix = []
  allterms, term_freq = index()
  print (len(allterms))

  for i in range(len(term_freq)):
    tmp = []
    vec1 = create_vec(term_freq[i], allterms)
    for j in range(i+1,len(term_freq)):
      vec2 = create_vec(term_freq[j], allterms)
      #print vec1,vec2
      tmp.append(pearson_sim(vec1, vec2))
    matrix.append(tmp)
  print matrix
  return matrix
    	  
def create_vec(tf_dict, allterms):
  vec = [0]*len(allterms)
  for key,value in tf_dict.items():
  	vec[allterms[key]] = value
  return vec


#pearson correl unoptimized
def pearson_sim(vec1, vec2):
  n = len(vec1)
  sum1 = sum(vec1)
  sum2 = sum(vec2)
  mean1 = float(sum1) / n
  mean2 = float(sum2) / n
  vec1_centered = [x - mean1 for x in vec1]
  vec2_centered = [y - mean2 for y in vec2]
  dotprod = sum([vec1_centered[i] * vec2_centered[i] for i in range(n)])
  stddevs_prod = (sqrt(sum([x*x for x in vec1_centered])) * sqrt(sum([y*y for y in vec2_centered])))
  return dotprod / stddevs_prod if stddevs_prod else 0

def parsepage():
  #get stopwords; remove newline char
  parsed_html = {}
  stopwords = [word[:-1] for word in open('stopwords.txt')]
  pstemmer = stemmer.PorterStemmer()
  

  htmldocs = os.listdir('page/') #grap all html docs and parse them
  words = re.compile(r'\W*') #split on non words
  for htmldoc in htmldocs:
    html = open('page/'+htmldoc, 'r').readlines();
    #its deprecated...i know
    try:
      print htmldoc
      p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('beautifulsoup'))
      tree = p.parse(html)
    except:
      print 'error parsing %s' % htmldoc
      continue

    data = [p.text.lower() for p in tree.findAll('p')]
    unstemmed_words = [word for word in words.split(''.join(data)) 
                            if word != '' and word not in stopwords]
    stemmed_words = [pstemmer.stem(word,0,len(word)-1) for word in unstemmed_words]
    parsed_html[int(htmldoc)] = stemmed_words
  #print parsed_html
  return parsed_html

if __name__ == '__main__':
	#index()
	simmatrix()
