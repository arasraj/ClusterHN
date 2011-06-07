import urllib2
import re

def scrape():
  c = urllib2.urlopen('http://news.ycombinator.com')
  #contents = c.read()
  links = re.findall(r'title"><a href="(.+?)"', c.read()) #? changes + to non-greedy
  followlink = links[-1]
  print '\n'.join(links)
  print followlink
  


if __name__ == '__main__':
	scrape()
