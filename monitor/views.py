from django.http import HttpResponse
from .models import Instance
import requests,json
import threading

responses = []



def index(request):
    all_instances = Instance.objects.all()
    html = ''
    miner_url = 'http://'
    miner_api_port = 9000
    miner_api_summary = '/2/summary'
    token='newtoken'
    for instance in all_instances:
        url = '/monitor/' + str(instance.id) + '/'
        miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
        headers = {'Authorization':'Bearer ' + token }
        try:
            resp = requests.get(miner_url, headers=headers)
            obj = json.loads(resp.content)
            html +=  '<a href="' + url + '">' + instance.name + '</a> - <a href="' + miner_url + '">' + miner_url + '</a>' + str(headers) +';' + miner_url + ' status = ' + str(obj['hashrate']) +   '<br>'
        except Exception as err:
           html +=  '<a href="' + url + '">' + instance.name + '</a> - <a href="' + miner_url + '">' + miner_url + '</a>' + str(headers) +';' + miner_url + ' status = ' + str(err) + '<br>'
    return HttpResponse(html)


def detail(request, instance_id):

    return HttpResponse("<h2>Details for Album id" + str(instance_id) + "</h2>")
