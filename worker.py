import time, queue, random
import os
from multiprocessing.managers import BaseManager


task_num = 3

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

def process(n):
    return n+1

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

pid = os.getpid()
while not master.empty():
    url = master.get(timeout=100)
    date = date_info.get(timeout=100)
    date_info.put(date)
    print(url)
    print(date)
    
    time.sleep(1)  # because processing...
    r = random.randint(1,10)
    for _ in range(r):
        print("put")
        information.put([str(pid), "random:"+str(r)])

print("master is empty")
        
 
