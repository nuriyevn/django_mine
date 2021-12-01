import requests,json
from django.http import HttpResponse
import threading
from .models import Instance
import math

responses = []

miner_url = 'http://'
miner_api_port = 9000
miner_api_summary = '/2/summary'
token='newtoken'

def index(request):
    all_instances = Instance.objects.all()
    html = ''
    total_all = {'10s': 0, '60s': 0, '15m': 0 }
    for instance in all_instances:
        url = '/monitor/' + str(instance.id) + '/'
        miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
        headers = {'Authorization':'Bearer ' + token }
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
    for i in total_all:
        total_all[i] = str(math.floor(float(total_all[i])))
    html += '<br>' + str(total_all)
    return HttpResponse(html)


def detail(request, instance_id):
    instance = Instance.objects.get(id=instance_id)
    miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
    headers = {'Authorization':'Bearer ' + token }
    resp = requests.get(miner_url, headers=headers)
    return HttpResponse("<h2>Details for Album id" + str(instance_id) + "</h2><pre>" + resp.text + "</pre>")

