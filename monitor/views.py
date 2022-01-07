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

def detail(request, instance_id):
    instance = Instance.objects.get(id=instance_id)
    miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
    headers = {'Authorization':'Bearer ' + token }
    resp = requests.get(miner_url, headers=headers)
    return HttpResponse("<h2>Details for Album id" + str(instance_id) + "</h2><pre>" + resp.text + "</pre>")

def old(request):
    all_instances = Instance.objects.all()
    html = ''
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
