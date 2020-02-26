# coding=utf-8
import time, queue
import requests  
import pickle


from pathlib import Path
from lxml import etree, html
from multiprocessing.managers import BaseManager


masterQueue = queue.Queue()  # put task
workerQueue = queue.Queue()  # get result
##  still need a queue to get the information of how many workers, their progress 
dateQueue = queue.Queue()
infoQueue = queue.Queue()

BaseManager.register('get_master_queue', callable=lambda: masterQueue)
BaseManager.register('get_worker_queue', callable=lambda: workerQueue)

BaseManager.register('get_date_queue', callable=lambda: dateQueue)
BaseManager.register('get_info_queue', callable=lambda: infoQueue)

manager = BaseManager(address=('', 5000), authkey=b'abc')

manager.start()

# using registered queue
master = manager.get_master_queue()
worker = manager.get_worker_queue()

date_info = manager.get_date_queue()
information = manager.get_info_queue()

class Node(object):
    def __init__(self, url, name):
        self.url = url
        self.name = name
    def __repr__(self):
        return str(self.url)

    def __hash__(self):
        return hash((self.url, self.name))

    def __eq__(self, other):
        return (self.url, self.name) == (other.url, other.name)

    def __ne__(self, other):
        return not(self == other)


# get all categories from ptt
def gen_all_board(start, end):
    url = 'https://www.ptt.cc/cls/1'  # category  
    r = requests.get(url)  
    r.encoding = 'utf-8'
    raw_html = r.text
    parsed_html = html.fromstring(raw_html)

    groups = parsed_html.xpath('//a[@class="board"]')

    for g in groups[start:end]:
        print(g)
        node = Node(g.attrib['href'], g.text_content())
        print(node)
        get_child(node)

    while len(need_to_check) > 0:
        check = need_to_check[0]
        # run the function
        get_child(check)
        need_to_check.remove(check)
        has_check.append(check)
        print("---")
        # print(need_to_check)
        # print(index)
        print('---')
        print(len(need_to_check), len(index))


def get_child(node):
    url = 'https://www.ptt.cc' + str(node.url)
    r = requests.get(url)  
    r.encoding = 'utf-8'
    raw_html = r.text
    parsed_html = html.fromstring(raw_html)
    groups = parsed_html.xpath('//a[@class="board"]')
    for i in groups:
        n = Node(i.attrib['href'], i.text_content())
        print(n)
        if n not in has_check:
            if "index" in n.url:
                index.append(n.url)
            elif "cls" in n.url :
                need_to_check.append(n)


def crawler(index):
    workers = []
    # put url to queue
    date = "2020-02-02"
    index = list(index)
    for i in index[:100]:
        master.put(i)
    date_info.put(date)

    while not master.empty():
        print("get something from result")
        
        time.sleep(5)
        
        print("surveillance")
        message = []
        while not information.empty():
            
            info = information.get()
            message.append(info)
            
        # process surveillance message
        error = surveillance(message, workers)
        if error:
            print("workers are missing")
            print(error)
            
def surveillance(message, workers):
    # show surveillance message
    print("show message")
    for m in message:
        pid = m[0]
        info = m[1]
        print(pid, info)
    # reverse the list, find how many different workers, if find a new worker, append to workers
    filter = []
    catch_worker = []
    message.reverse()
    for i in message:
        if i[0] not in catch_worker:
            filter.append(i)
            catch_worker.append(i[0])
    
    print(filter)       # message of surveillance!
    print(catch_worker)
    for w in catch_worker:
        if w not in workers:
            workers.append(w)
    # if worker decrease, is an error, else return None
    missing = []
    for w in workers:
        if w not in catch_worker:
            missing.append(w)
    return missing

if __name__ == '__main__':
    # main()

    my_file = Path("boards.pkl")
    if my_file.is_file():
        with open("boards.pkl", 'rb') as f:
            index = pickle.load(f)
        
    else:
        index = []
        has_check = []
        need_to_check = []
        # group A~L
        start = 0
        end = 12
        gen_all_board(start, end)
        index = set(index)
        with open('boards.pkl', 'wb') as fp:
            pickle.dump(index, fp)

    print("start to crawl")
    crawler(index)

# # put task into the master queue
# for i in range(10):
#     master.put(i)


# #...
# # every 5 second, collect data, and show crawler's status:
# # ex: cid1, has done x articles, cid2, has done x2 articles...


# for i in range(10):
#     r = worker.get()
#     print(r)

# afer the task queue is empty, delay a few second then shutdown
time.sleep(5)
manager.shutdown()