import time, queue, random, re
import requests
import os


from multiprocessing.managers import BaseManager

# setup the queue
BaseManager.register('get_master_queue')
BaseManager.register('get_worker_queue')
BaseManager.register('get_date_queue')
BaseManager.register('get_info_queue')

server_addr = '127.0.0.1'
manager = BaseManager(address=(server_addr, 5000), authkey=b'abc')

manager.connect()


master = manager.get_master_queue()
worker = manager.get_worker_queue()
date_info = manager.get_date_queue()
information = manager.get_info_queue()


# get task from master, process then put it into worker
pid = os.getpid()
while not master.empty():
    url = master.get(timeout=100)
    date = date_info.get(timeout=100)
    date_info.put(date)
    print(url)
    print(date)
    
    time.sleep(1)  # because processing...
    ''' here call the function in crawl.py, argument is url (board)'''
    # sumulation there are ? articles in the date segment = r
    r = random.randint(1,10)
    for _ in range(r):
        information.put([str(pid), "random: need to crawl articles: "+str(r)+", is processing: ", url])


print("master is empty")
        
 
