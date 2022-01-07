from time import sleep
from . import views 
import requests,httpx,json
from django.http import HttpResponseRedirect

class Res:
    res = {}
    last_piece = False
    i = 0
    request = None

def get_data(data):
    all_data = {'data': data, 'json' : json.loads("{}")}
    try:
        print('getdata:actual session get:')
        print('getdata:' + data['miner_url'])
        r = requests.get(data['miner_url'], headers={'Authorization': 'Bearer newtoken'})
        print('getdata: r = '+ str(r) + '; r.json() = ' + str(r.json())[0:20])
        all_data = {'data': data, 'json': str(r.json()) }
        print('getdata: alldata =' + str(all_data)[0:20])
    except Exception as err:
        print(str(err))
    else:
        pass
    return all_data

def get_data_hook(task):
    #print("get_data_hook: Res=" + str(Res.res[Res.i]))
    #Res.res[Res.i] = task.result
    #Res.i = Res.i + 1
    #i = url.split('/')[-1]
    print("get_data_hook: task_result" + str(task.result)[0:220])
    print("get_data_hook: data request" + str(task.result['data']['request']))
    HttpResponseRedirect('/monitor/refresh/')
    #views.refresh()

