#!/usr/bin/python
"""
Library of functions to process and handle Federal Election Commission data
available from http://www.fec.gov and its FTP site, ftp://ftp.fec.gov.

The MIT License

Copyright (c) 2008 Derek Willis

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Modified by:
Ben Welsh
Los Angeles
May 28, 2008

"""
__author__ = "Derek Willis <dwillis@gmail.com>"
__date__ = "$Date: 2008/05/19 $"
__version__ = "$Revision: 2.2 $"

import re
import urllib
import sys
import string
import urlparse
import time
import datetime

def latest_news():
    """
    Scrape the FEC's news releases to produce an RSS feed using
    regular expressions.
        
    The script supports relative urls and the elimination of
    extraneous whitespace, and produces an RSS 2.0 feed.
    
    Running this script using versions of Python before 2.3 require importing
    sre as re and resetting the maximum recursion limit.
    
    Based on a script by Sam Ruby. 
    
    Usage from within Python shell: 
    from fec import latest_news
    latest_news()
    """
    # set up needed variables
    date = datetime.date.today()
    year = date.year
    base_url = 'http://www.fec.gov/press/press%s/' % year
    url = base_url + '%sNewsReleases.shtml' % year
    file = 'fecnews.xml'

    # read the content of the FEC's press page
    try:
      page=urllib.urlopen(url).read()
    except IOError:
      page=''
    except AssertionError:
      page=''
    
    #define regular expression to grab link, date and title from FEC news
    #releases page, using DOTALL to find multiline text. Since urls are
    #internal, we need to add a prefix to the link for the RSS feed.
    news = re.compile("""valign=.top.>(.*?\d\d\d\d).?</td>.*? +
                      <td.valign=.top.>.*?<a href=.(.*?).>(.*?)</a>.*? +
                      </td>.*?</tr>""", re.DOTALL)

    #remove additional whitespace like linebreaks and returns from HTML code.
    page = ' '.join(page.split())

    #find first 10 matches
    matches = news.findall(page)
    matches = matches[:10]

    #unpack tuple of matches and add to rss feed
    data = []
    for (date_string, link, title) in matches:
        # combine the base_url with the tail_url
        link = urlparse.urljoin(base_url,link)
        # Leave the description field null for the time being
        description = ''
        # Pull out the date and reformat it for RSS
        # See: http://feedvalidator.org/docs/error/InvalidRFC2822Date.html
        date_date = time.strptime(date_string, '%B %d, %Y')
        pubDate = time.strftime('%a, %d %b %Y 00:00:00 GMT', date_date)
        record = (title, link, description, pubDate)
        # Append to our data list
        data.append(record)
    # Transform our data list to RSS 2.0
    make_rss_20('Latest FEC News', 'Press releases and announcements.',
                data, 'latest_news.xml')

def latest_filings():
    """
    Returns a list of electronic filings for today's date
    and print them to RSS.
    
    Dependency: BeautifulSoup for HTML parsing
    (http://www.crummy.com/software/BeautifulSoup/)
    
    Usage from within Python shell: 
    from fec import latest_news
    latest_news()
    """
    try:
        from BeautifulSoup import BeautifulSoup
    except ImportError:
        print """
              IMPORT ERROR: Required Beautiful Soup module not found.
               
              Installation instructions:
               
              If you have easy_install, enter
              "sudo easy_install Beautiful Soup"
              via your shell.
               
              Otherwise, the source can be downloaded from
              http://www.crummy.com/software/BeautifulSoup/
              """
        sys.exit()
    # Set the date for the URL string
    d = datetime.date.today()
    dm = str(d.month).zfill(2)
    dd = str(d.day).zfill(2)
    stringdate=dm+'/'+dd+'/'+str(d.year)
    params = {'date':stringdate}
    base_url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/'
    # Open the URL, pass the HTML to Beautiful Soup
    txt=urllib.urlopen(base_url, urllib.urlencode(params)).read()
    soup = BeautifulSoup(txt)
    # Snatch all the <dt> tags
    filings = soup.findAll('dt')
    data = []
    # Iterate through each filing in the HTML and snatch the data we want
    for filing in filings:
        # Pull the committee name and cut off c_id
        committee = filing('h4')[0]('a')[0].contents[0]
        title = re.split(' - ', committee)[0]
        # Pull the hyperlink
        link = filing.contents[2]['href'] 
        # Grab the field with form and date information
        form = filing.contents[5].replace('&nbsp;', '').replace('\n', '')
        # Pull out the description 
        description = re.split(' - ', form)[0].strip()
        # Pull out the date and reformat it for RSS
        # See: http://feedvalidator.org/docs/error/InvalidRFC2822Date.html
        date_string = re.split(' - ', form)[1].split('filed ')[1]
        date_date = time.strptime(string.strip(date_string), '%m/%d/%Y')
        pubDate = time.strftime('%a, %d %b %Y 00:00:00 GMT', date_date)
        # Collect in a tuple
        record = (title, urlparse.urljoin(base_url,link), description, pubDate)
        # Append to our data list
        data.append(record)
    # Transform our data list to RSS 2.0
    make_rss_20('Latest FEC Filings', 'Committee finance reports.',
                data, 'latest_filings.xml')
            

def make_rss_20(title, description, data, file_name):
    """
    Prints out data from both scrapes according RSS 2.0 standards
    http://en.wikipedia.org/wiki/RSS_(file_format)#RSS_2.0
    """
    
    rss="""<?xml version="1.0" encoding="ISO-8859-1"?>
    <rss version="2.0">
        <channel>
            <title>""" + title + """</title>
            <link>http://www.fec.gov/</link>
            <description>""" +  description + """"</description>
            <language>en-us</language>
    """
    
    #find first 10 matches
    latest = data[:10]

    #unpack tuple of matches and add to rss feed
    for (title, link, description, pubDate) in latest:
        rss+="""
        <item>
            <title>%s</title>
            <link>%s</link>
            <description>%s</description>
            <pubDate>%s</pubDate>
        </item>\n""" % (title, link, description, pubDate)

    #close rss feed                
    rss+="""
        </channel>
    </rss>
    """
    
    fh=open(file_name,'w')
    fh.write(rss) 
    fh.close()
    
    
