import time, queue, random
import requests
import os

from multiprocessing.managers import BaseManager
from requests_html import HTML


task_num = 3

# BaseManager.register('get_master_queue')
# BaseManager.register('get_worker_queue')
# BaseManager.register('get_date_queue')
# BaseManager.register('get_info_queue')

# server_addr = '127.0.0.1'
# manager = BaseManager(address=(server_addr, 5000), authkey=b'abc')

# manager.connect()


# master = manager.get_master_queue()
# worker = manager.get_worker_queue()
# date_info = manager.get_date_queue()
# information = manager.get_info_queue()

class BoardCrawler(object):
    def __init__(self, board):
        self.board = board
        # self.last_page = self.get_last_page()
        self.articles = []
            
    def fetch(self):
        url = 'https://www.ptt.cc' + self.board
        # response = requests.get(url)
        response = requests.get(url, cookies={'over18': '1'})
        return response
    
    def parse_article(self, text):
        html = HTML(html = text)
        article_entries = html.find('div.r-ent')

        # previous_page = self.get_previous_page(html)
        # print("previous page")
        # print(previous_page)
        
        return article_entries

    def parse_article_data(self, entry):
        info = {}
        info['title'] = entry.find('div.title', first = True).text
        info['category'] = self.board.split('/')[2]
        info['author'] = entry.find('div.author', first = True).text
        info['link'] = entry.find('div.title > a', first=True).attrs['href']
        # into the article by the link
        details = self.get_article_detail(info['link'])

        # print(details)
        print(info)
        return info

    def get_article_detail(self, link):
        detail = {}
        url = 'https://www.ptt.cc' + link
        response = requests.get(url, cookies={'over18': '1'})
        html = HTML(html = response.text)

        name = html.find('span.article-meta-value', first=True).text
        pushes = html.find('div.push')
        
        print(link)
        print(name)

        # for push in pushes:
        #     print(push.text)

        return detail
    
    def get_previous_page(self, text):
        html = HTML(html = text)
        control = html.find('.action-bar a.btn.wide')[1]
        print(control)
        try:
            link = control.attrs['href']
            previous_url = 'https://www.ptt.cc/'+link
            print(previous_url)
            return previous_url
        except KeyError:
            return None


def process(n):
    return n+1



c = BoardCrawler("/bbs/Gossiping/index.html")
response = c.fetch()


articles = c.parse_article(response.text) 
prevous = c.get_previous_page(response.text)
print(prevous)
for a in articles:
    data = c.parse_article_data(a)
        

    # print(data)

# content = c.get_article_detail('/bbs/Gossiping/M.1582734767.A.CFC.html')




# get task from master, process then put it into worker

# for _ in range(task_num):
#     try:
#         n = master.get()
#         print(n)
#         # process n
#         result = process(n)
#         worker.put(result)
#     except queue.Empty:
#         print("task is empty")

# pid = os.getpid()
# while not master.empty():
#     url = master.get(timeout=100)
#     date = date_info.get(timeout=100)
#     date_info.put(date)
#     print(url)
#     print(date)
    
#     time.sleep(1)  # because processing...
#     r = random.randint(1,10)
#     for _ in range(r):
#         print("put")
#         information.put([str(pid), "random:"+str(r)])

# print("master is empty")
        
 
