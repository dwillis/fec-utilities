#!/usr/bin/python
"""
Scraping the FEC's news releases to produce an RSS feed using regular expressions. Based on a script by Sam Ruby. The RSS feed is produced using print statements and is RSS 0.91. Recent changes to the script include support for relative urls and the elimination of extraneous whitespace. Running this script using versions of Python before 2.3 require importing sre as re and resetting the maximum recursion limit.

The MIT License

Copyright (c) 2008 Derek Willis

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
__author__ = "Derek Willis <dwillis@gmail.com>"
__date__ = "$Date: 2008/05/19 $"
__version__ = "$Revision: 2.2 $"

import re
import urllib
import sys
import string
import urlparse
import datetime

# set up needed variables

date = datetime.date.today()
year = date.year
base_url = 'http://www.fec.gov/press/press%s/' % year
url = base_url + '%sNewsReleases.shtml' % year
file = 'fecnews.rss'


# read the content of the FEC's press page

try:
  page=urllib.urlopen(url).read()
except IOError:
  page=''
except AssertionError:
  page=''

# set up the top of the RSS feed.

rss="""<?xml version="1.0" encoding="ISO-8859-1"?>
<rss version="0.91">
	<channel>
		<title>FEC News</title>
		<link>http://www.fec.gov/</link>
		<description>Press releases and announcements</description>
		<language>en-us</language>
"""
		
#define regular expression to grab link, date and title from FEC news
#releases page, using DOTALL to find multiline text. Since urls are
#internal, we need to add a prefix to the link for the RSS feed.

news = re.compile("""valign=.top.>(.*?\d\d\d\d).</td>.*?<td.valign=.top.><a href=.(.*?).>(.*?)</a>.?</td>.*?</tr>""", re.DOTALL)

#remove additional whitespace like linebreaks and returns from HTML code.
page = ' '.join(page.split())

#find first 10 matches
matches = news.findall(page)
matches = matches[:10]

#unpack tuple of matches and add to rss feed
for (date, link, title) in matches:
            rss+="\n<item>\n<date>%s</date><title>%s</title><link>%s</link>\n</item>\n" % (date,title,urlparse.urljoin(base_url,link))

#close rss feed                
rss+="""
	</channel>
</rss>
"""

# if we successfully read the FEC page, write the RSS out to file
if page:
  fh=open(file,'w')
  fh.write(rss) 
  fh.close()