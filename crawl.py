import requests
from requests_html import HTML
from datetime import datetime
# date = "2014-02-24 2018-04-10" # example
date = "2020-02-24 2020-02-25"

class BoardCrawler(object):
    def __init__(self, board):
        self.board = board
        self.articles = []
            
    def fetch(self):
        url = 'https://www.ptt.cc' + self.board
        # response = requests.get(url)
        response = requests.get(url, cookies={'over18': '1'})
        return response
    
    def parse_article(self, text):
        """get a list of articles"""
        html = HTML(html = text)
        article_entries = html.find('div.r-ent')

        return article_entries

    def parse_article_data(self, entry):
        """get information by each article"""
        info = {}
        info['title'] = entry.find('div.title', first = True).text
        info['category'] = self.board.split('/')[2]
        info['date'] = entry.find('div.date', first = True).text

        try:
            info['author'] = entry.find('div.author', first = True).text
            info['link'] = entry.find('div.title > a', first=True).attrs['href']
            # into the article by the link
            details = self.get_article_detail(info['link'])
            parse = {**info, **details}  # merge 2 dict
        except AttributeError:
            parse = {}  # the article has been deleted    
        
        return parse

    def get_article_detail(self, link):
        """enter an article to get the detail(content, push...)"""
        detail = {}
        url = 'https://www.ptt.cc' + link
        response = requests.get(url, cookies={'over18': '1'})
        html = HTML(html = response.text)

        metadata = html.find('span.article-meta-value')

        # name = html.find('span.article-meta-value', first=True).text
        name = metadata[0].text.split(' ')
        authorId = name[0]
        authorName = name[1][1:-1]
        publishedTime = metadata[3].text
        
        pushes = html.find('div.push')
        content = html.xpath('/html/body/div[3]/div[1]/text()')
        
        detail['authorId'] = authorId
        detail['authorName'] = authorName
        detail['publishedTime'] = publishedTime
        detail['content'] = content
        detail['pushes'] = pushes
        return detail
    
    def get_previous_page(self, text):
        html = HTML(html = text)
        control = html.find('.action-bar a.btn.wide')[1]
        print(control)
        try:
            link = control.attrs['href']
            return link
        except KeyError:
            return None

    def date_compare(self, date1, date2, data):
        """return the action, whether the date in the segment"""
        k = data['publishedTime']
        format = k.split(' ')
        m, y, d = format[1], format[-1],format[2]
        x = datetime.strptime(y+'-'+m+'-'+d, "%Y-%b-%d")
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")

        if d1 <= x <= d2:
            return 1
        elif x > d2:
            return 0
        elif x < d1:
            return -1
        
def get_key(dict):
    value = hash((dict['authorId'], dict['publishedTime'], dict['title']))
    return(value, dict)

# c = BoardCrawler("/bbs/Gossiping/index.html")
c = BoardCrawler("/bbs/WomenTalk/index.html")

response = c.fetch()


article = 0
pages = 0
enough_article = 0

go_to_previous_page = True

while go_to_previous_page:
    articles = c.parse_article(response.text) 
    # print(articles)
    prevous = c.get_previous_page(response.text)
    
    start, end = 0, len(articles)
    while start < end:
        article = articles[start]
        
        data = c.parse_article_data(article)
        # the article has been deleted
        if data == {}:
            start += 1
            continue
        date1, date2 = date.split(' ')[0], date.split(' ')[1]
        action = c.date_compare(date1, date2, data)
        if action == 1:
            # crawl this article
            print(data['title'])
            print(data['publishedTime'])

            key, entry = get_key(data)      # store in database
            print(key, entry['title'])

        elif action == 0:
            if prevous != None:
                c.board = prevous
                response = c.fetch()
                articles = c.parse_article(response.text)
                break
                # list = [0, 0, 0, 0, 5]
                # start, end = 0, len(list)
            else:
                go_to_previous_page = False
                break

        elif action == -1:
            go_to_previous_page = False

        start += 1
    
    if prevous != None and go_to_previous_page:
        c.board = prevous
        response = c.fetch()
        articles = c.parse_article(response.text)