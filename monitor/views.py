import requests,json
from django.http import HttpResponse
from .models import Instance
import math
from queue import Queue
from threading import Thread
import time


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


def get(url):
    i = url.split('/')[-1]
    r = session.get(url, headers={'Authorization': 'Bearer newtoken'})
    results[i] = r.json()
    print(url + " " + str(results[i]['hashrate']))


responses = []

miner_url = 'http://'
miner_api_port = 9000
miner_api_summary = '/2/summary'
token='newtoken'


session = requests.session()
results = {}


async def index(request):
    all_instances = Instance.objects.all()
    html = ''
    total_all = {'10s': 0, '60s': 0, '15m': 0 }
    
    urls = []
    for instance in all_instances:
        url = '/monitor/' + str(instance.id) + '/'
        miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
        #headers = {'Authorization':'Bearer ' + token }
        
        urls.append(url)
        
        '''
        try:
            resp = requests.get(miner_url, headers=headers)
            obj = json.loads(resp.content)
            html +=  '<a href="' + url + '">' + instance.name + '</a> - <a href="' + miner_url + '">' + miner_url + '</a>' + str(headers) +';' + miner_url + ' status = ' + str(obj['hashrate']) +   '<br>'
            if obj['hashrate']['total'][0] is not None:
                total_all['10s'] += obj['hashrate']['total'][0]
            if obj['hashrate']['total'][1] is not None:
                total_all['60s'] += obj['hashrate']['total'][1]
            if obj['hashrate']['total'][2] is not None:
                total_all['15m'] += obj['hashrate']['total'][2]
        except Exception as err:
           html +=  '<a href="' + url + '">' + instance.name + '</a> - <a href="' + miner_url + '">' + miner_url + '</a>' + str(headers) +';' + miner_url + ' status = ' + str(err) + '<br>'
        '''

    #urls = [f"http://192.168.1.{i}:9000/2/summary" for i in range(100, 126)]

    pool = ThreadPool(25)
    #results = {}
    #session = requests.session()


    now = time.time()
    pool.map(get, urls)
    pool.wait_completion()
    time_taken = time.time() - now

    print(time_taken)

    '''
    for i in total_all:
        total_all[i] = str(math.floor(float(total_all[i])))
    html += '<br>' + str(total_all)
    '''
    return HttpResponse(html)


def detail(request, instance_id):
    instance = Instance.objects.get(id=instance_id)
    miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
    headers = {'Authorization':'Bearer ' + token }
    resp = requests.get(miner_url, headers=headers)
    return HttpResponse("<h2>Details for Album id" + str(instance_id) + "</h2><pre>" + resp.text + "</pre>")



def old(request):
    all_instances = Instance.objects.all()
    html = ''
    miner_url = 'http://'
    miner_api_port = 9000
    miner_api_summary = '/2/summary'
    token='newtoken'
    total = {'10s':0, '1m':0, '15m':0}
    for instance in all_instances:
        url = '/monitor/' + str(instance.id) + '/'
        miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
        headers = {'Authorization':'Bearer ' + token }
        try:
            resp = requests.get(miner_url, headers=headers)
            obj = json.loads(resp.content)
            html +=  '<a href="' + url + '">' + instance.name + '</a> - <a href="' + miner_url + '">' + miner_url + '</a>' + ' status = ' + str(obj['hashrate']) +   '<br>'
            total['10s'] += obj['hashrate']['total'][0]
            total['1m'] += obj['hashrate']['total'][1]
            total['15m'] += obj['hashrate']['total'][2]

        except Exception as err:
           html +=  '<a href="' + url + '">' + instance.name + '</a> - <a href="' + miner_url + '">' + miner_url + '</a>' + ' status = ' + str(err) + '<br>'
    total = dict([a, int(x)] for a, x in total.items())  
    html = html + "<pre>"+ str(total) + "</pre>"
    return HttpResponse(html)


def test(request):
    return HttpReponse("<h1>test</h1>")
