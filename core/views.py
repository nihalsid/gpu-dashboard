from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from pymongo import MongoClient
from datetime import datetime, timedelta, date, time
from collections import defaultdict
import functools


def get_most_recent_per_gpu_logs(collection):
    time_three_hours_ago = datetime.now() - timedelta(hours=3)

    # get all gpus active in the 3 hours
    gpu_logs = collection.find({'query_time': {"$gt": time_three_hours_ago}})
    gpus = defaultdict(set)

    for log in gpu_logs:
        gpus[log['hostname']].add(log['index'])

    last_gpu_entry = defaultdict(dict)

    # get last entry for all these gpus, get utilization, user, specifics of the gpu that will be shown in the card, etc
    for hostname in gpus:
        for index in list(gpus[hostname]):
            last_gpu_entry[hostname][index] = list(collection.find({'hostname': hostname, 'index': index}).sort("query_time", -1).limit(1))[0]

    return last_gpu_entry


def get_user_distribution(request):
    client = MongoClient('mongodb://pegasus.vc.in.tum.de:27017/')
    db = client['gpu_logs']
    collection = db['logs']
    last_gpu_entry = get_most_recent_per_gpu_logs(collection)

    user_gpus = defaultdict(int)
    for hostname in last_gpu_entry:
        for index in last_gpu_entry[hostname]:
            if last_gpu_entry[hostname][index]['utilization_memory'] > 100 and  len(last_gpu_entry[hostname][index]['process_list']) != 0:
                for process in last_gpu_entry[hostname][index]['process_list']:
                    if process['username'] != 'root':
                        user_gpus[process['username']] += 1

    client.close()
    ret_val = {'user': [], 'usage': []}
    for user in user_gpus:
        ret_val['user'].append(user)
        ret_val['usage'].append(user_gpus[user])

    return JsonResponse(ret_val)


def get_usage_history(request):
    client = MongoClient('mongodb://pegasus.vc.in.tum.de:27017/')
    db = client['gpu_logs']
    collection = db['logs']
    TIME_RESOLUTION = 1  # logs in server were made every 1 minutes

    # gpu hours timeline
    timeline = []
    usage = []
    time_end = datetime.now()
    for days_back in range(7):
        time_start = datetime.combine(date.today(), time()) - timedelta(days=days_back)
        day_stats = collection.find({'query_time': {"$gt": time_start, "$lt": time_end}})
        num_occupied = 0
        for log in day_stats:
            if log['utilization_memory'] > 100 and len(log['process_list']) != 0:
                num_occupied += 1
        timeline.append(time_start.strftime("%d/%b"))
        usage.append(num_occupied * TIME_RESOLUTION / 60.0)
        time_end = time_start
    client.close()

    return JsonResponse({'time': timeline[::-1], 'usage': usage[::-1]})


def index(request):

    client = MongoClient('mongodb://pegasus.vc.in.tum.de:27017/')
    db = client['gpu_logs']
    collection = db['logs']
    TIME_RESOLUTION = 5  # logs in server were made every 5 minutes

    last_gpu_entry = get_most_recent_per_gpu_logs(collection)

    # number of GPUs
    num_gpus = functools.reduce(lambda x, y: x + y, [len(last_gpu_entry[hostname].keys()) for hostname in last_gpu_entry])

    # number of servers
    num_servers = len(last_gpu_entry.keys())

    # total usage, per server usage, user_gpus, current_state
    utilization_gpu = 0
    utilization_per_server = defaultdict(int)
    gpu_current_state = defaultdict(dict)
    for hostname in last_gpu_entry:
        for index in last_gpu_entry[hostname]:

            print(hostname, index, last_gpu_entry[hostname][index]['utilization_memory'], len(last_gpu_entry[hostname][index]['process_list']))
            gpu_current_state[hostname][index] = {
                'occupied': last_gpu_entry[hostname][index]['utilization_memory'] > 100 and len(last_gpu_entry[hostname][index]['process_list']) != 0,
                'temperature': last_gpu_entry[hostname][index]['temperature'],
                'utilization_memory': round(last_gpu_entry[hostname][index]['utilization_memory'] / 1024.0),
                'utilization_gpu': last_gpu_entry[hostname][index]['utilization_gpu'],
                'total_memory': round(last_gpu_entry[hostname][index]['total_memory'] / 1024.0),
                'name': last_gpu_entry[hostname][index]['name']
            }
            if last_gpu_entry[hostname][index]['utilization_memory'] > 100 and len(last_gpu_entry[hostname][index]['process_list']) != 0:
                utilization_gpu += 1
                utilization_per_server[hostname] += 1

        utilization_per_server[hostname] = round(utilization_per_server[hostname] * 100.0 / len(last_gpu_entry[hostname].keys()))
    from pprint import pprint
    pprint(gpu_current_state)
    utilization_gpu = round(utilization_gpu * 100.0 / num_gpus)
    client.close()
    return render(request, 'index.html', {"num_gpus": num_gpus, "num_servers": num_servers, "utilization_gpu": utilization_gpu, "utilization_per_server": dict(utilization_per_server), "gpu_current_state": dict(gpu_current_state)})
