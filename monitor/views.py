import requests,json
from django.http import HttpResponse, JsonResponse
from .models import Instance
import math
from queue import Queue
from threading import Thread
import time
from asgiref.sync import sync_to_async
import asyncio
import httpx
from django_q.tasks import async_task, result
from monitor.services import Res
from time import sleep
responses = []

miner_url = 'http://'
miner_api_port = 9000
miner_api_summary = '/2/summary'
token='newtoken'


session = requests.session()
results = {}

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

@sync_to_async
def crunching_stuff():
    sleep(3)    
    print("Woke up after 3 seconds!")

async def simple(request):
    json_payload = {
        "message":"Hello world"
    }
    loop = asyncio.get_event_loop()
    loop.create_task(crunching_stuff())
    return JsonResponse(json_payload)


def refresh(request):
    print('refresh: is called')
    html = ''
    total_all = {'10s':0, '60s':0, '15m':0}
    print('refresh: str(Res.res)' + str(Res.res))
    for i in Res.res:
        
        print('refresh: i = ' + str(i))
        obj = json.loads(Res.res[i]['json'])
        print('refresh: obj = ' + str(obj))
        data = Res.res[i]['data']
        html +=  '<a href="' + data['url'] + '">' + data['instance_name'] + '</a> - <a href="' + data['miner_url'] + '">' + data['miner_url'] + '</a>' + "headers" +';' + data['miner_url'] + ' status = ' + str(obj['hashrate']) +   '<br>'
        if obj['hashrate']['total'][0] is not None:
            total_all['10s'] += obj['hashrate']['total'][0]
        if obj['hashrate']['total'][1] is not None:
            total_all['60s'] += obj['hashrate']['total'][1]
        if obj['hashrate']['total'][2] is not None:
            total_all['15m'] += obj['hashrate']['total'][2]

    print('refresh:final html = ' + html)
    return HttpResponse(html)

def process(request):
    all_instances = Instance.objects.all()
    html = ''
    total_all = {'10s': 0, '60s': 0, '15m': 0}
    urls = []
    
    Res.last_piece = False
    Res.request = request
    print('process: request = ' + str(request))
    Res.res = {}   
    Res.res.clear() 
    Res.i = 0
    r = Res()
    for instance in all_instances:
        if instance.enabled == False:
            continue
        url = '/monitor/' + str(instance.id) + '/'
        miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
        #headers = {'Authorization':'Bearer ' + token }
        data = {'url' :url, 'miner_url':miner_url, 'instance_id':instance.id, 'instance_name':instance.name, 'request' : 'request'}
        print("process: async_task started")
        async_task("monitor.services.get_data", data, hook="monitor.services.get_data_hook")
        urls.append(url)
    return HttpResponse("started...")



def test_index(request):
    json_payload = { 
      "message": "Hello World"
    }
    async_task("monitor.services.get_data", "http://192.168.1.119:9000" + miner_api_summary, hook="monitor.services.get_data_hook")
    return JsonResponse(json_payload)



#def get_url(url):
#    async

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
            hashrate_total = obj['hashrate']['total']
            html +=  '<a href="' + url + '">' + instance.name + '</a> - <a href="' + miner_url + '">' + miner_url + '</a>' + ' status = ' + str(obj['hashrate']) +   '<br>'
            if hashrate_total[0] is not None:
                total['10s'] += hashrate_total[0]
            if hashrate_total[1] is not None:
                total['1m'] += hashrate_total[1]
            if hashrate_total[2] is not None:
                total['15m'] += hashrate_total[2]
        except Exception as err:
           html +=  '<a href="' + url + '">' + instance.name + '</a> - <a href="' + miner_url + '">' + miner_url + '</a>' + ' status = ' + str(err) + '<br>'
    total = dict([a, int(x)] for a, x in total.items())  
    html = html + "<pre>"+ str(total) + "</pre>"
    return HttpResponse(html)


def test(request):
    return HttpReponse("<h1>test</h1>")



# helpers
async def http_call_async():
    for num in range(1, 6):
        await asyncio.sleep(1)
        print(num)
    async with httpx.AsyncClient() as client:
        r = await client.get("https://httpbin.org/")
        print(r)
def http_call_sync():
    for num in range(1, 6):
        sleep(1)
        print(num)
    r = httpx.get("https://httpbin.org/")
    print(r)
# views
async def newindex(request):
    async_task("monitor.services.sleep_and_print", 5, hook="monitor.services.hook_after_sleeping")
    return HttpResponse("Hello, async Django!")

async def async_view(request):
    loop = asyncio.get_event_loop()
    loop.create_task(http_call_async())
    return HttpResponse("Non-blocking HTTP request")
def sync_view(request):
    http_call_sync()
    return HttpResponse("Blocking HTTP request")




from typing import List


async def smoke(smokables: List[str] = None, flavor: str = "Sweet Baby Ray's") -> None:
    """ Smokes some meats and applies the Sweet Baby Ray's """
    if smokables is None:
        smokables = [
            "ribs",
            "brisket",
            "lemon chicken",
            "salmon",
            "bison sirloin",
            "sausage",
        ]
    if (loved_smokable := smokables[0]) == "ribs":
        loved_smokable = "meats"
    for smokable in smokables:
        print(f"Smoking some {smokable}....")
        await asyncio.sleep(1)
        print(f"Applying the {flavor}....")
        await asyncio.sleep(1)
        print(f"{smokable.capitalize()} smoked.")
    print(f"Who doesn't love smoked {loved_smokable}?")





async def smoke_some_meats(request) -> HttpResponse:
    loop = asyncio.get_event_loop()
    smoke_args = []
    if to_smoke := request.GET.get("to_smoke"):
        # Grab smokables
        to_smoke = to_smoke.split(",")
        smoke_args += [[smokable.lower().strip() for smokable in to_smoke]]
        # Do some string prettification
        if (smoke_list_len := len(to_smoke)) == 2:
            to_smoke = " and ".join(to_smoke)
        elif smoke_list_len > 2:
            to_smoke[-1] = f"and {to_smoke[-1]}"
            to_smoke = ", ".join(to_smoke)
    else:
        to_smoke = "meats"
    if flavor := request.GET.get("flavor"):
        smoke_args.append(flavor)
    loop.create_task(smoke(*smoke_args))
    return HttpResponse(f"Smoking some {to_smoke}....")



