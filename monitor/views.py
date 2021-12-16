from django.http import HttpResponse
from .models import Instance
import requests, json
import threading

# responses = []
miner_api_port = 9000
miner_api_summary = '/2/summary'
token = 'newtoken'
headers = {'Authorization': 'Bearer ' + token}
threadLock = threading.Lock()  # TODO


class myThread(threading.Thread):
    def __init__(self, threadID, instance_name, url, miner_url, html):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.url = url
        self.miner_url = miner_url
        self.instance_name = instance_name
        self.html = html

    def run(self):
        print("Starting " + self.url)
        try:
            resp = requests.get(self.miner_url, headers=headers)
            obj = json.loads(resp.content)
            threadLock.acquire()
            self.html += '<a href="' + self.url + '">' + self.instance_name + '</a> - <a href="' + \
                         self.miner_url + '">' + self.miner_url + '</a>' + str(headers) + ';' + self.miner_url + \
                         ' status = ' + str(obj['hashrate']) + '<br>'
            threadLock.release()
        except Exception as err:
            threadLock.acquire()
            self.html += '<a href="' + self.url + '">' + self.instance_name + '</a> - <a href="' + \
                         self.miner_url + '">' + self.miner_url + '</a>' + str(headers) + ';' + self.miner_url + \
                         ' status = ' + str(err) + '<br>'
            threadLock.release()

        # Get lock to synchronize threads
        # threadLock.acquire()
        # print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        # threadLock.release()

def index(request):
    all_instances = Instance.objects.all()
    html = ''
    threads = []

    for instance in all_instances:
        miner_url = 'http://' + str(instance.local_ip) + ':' + str(miner_api_port) + str(miner_api_summary)
        url = '/monitor/' + str(instance.id) + '/'
        print('Creating ' + str(instance.id))
        thread = myThread(instance.id, instance.name, url, miner_url, html)
        print('Starting ' + str(instance.id))
        thread.start()
        print('Appending ' + str(instance.id))
        threads.append(thread)

    for t in threads:
        print('Joining ' + str(t.threadID))
        t.join()
    print("Exiting index")

    print('html ' + str(html))
    return HttpResponse(html)


def detail(request, instance_id):
    return HttpResponse("<h2>Details for Album id" + str(instance_id) + "</h2>")
