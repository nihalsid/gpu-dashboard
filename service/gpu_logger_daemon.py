from pymongo import MongoClient
from gpustat import GPUStatCollection
import logging
import datetime
import time
import os
import sys

script_path = os.path.dirname(sys.argv[0])

if not os.path.exists(os.path.join(script_path, 'logs')):
	os.makedirs(os.path.join(script_path, 'logs'))

logging.basicConfig(filename=os.path.join(script_path, 'logs', datetime.datetime.now().strftime("%d%m%y_%H%M%S")+".log"),filemode='w', format="[%(levelname)s][%(name)s]: %(message)s")


def create_gpu_state_dict(hostname, query_time, index, total_memory, utilization_memory, name, power, temperature, utilization_gpu, process_list, active_user_list):
	return {
		'hostname': hostname,
		'query_time': query_time,
		'index': index,
		'total_memory': total_memory,
		'utilization_memory': utilization_memory,
		'utilization_gpu': utilization_gpu,
		'name': name,
		'power': power,
		'temperature': temperature,
		'process_list': process_list,
		'active_user_list': active_user_list
	}

def log_gpu_state(collection):
	stat = GPUStatCollection.new_query().jsonify()
	if not len(stat['gpus']) > 0:
		logging.error('No gpus found')
	for gpu in stat['gpus']:
		hostname = stat['hostname']
		query_time = stat['query_time']
		index = gpu['index']
		total_memory = gpu['memory.total']
		utilization_memory = gpu['memory.used']
		name = gpu['name']
		power = gpu['power.draw']
		temperature = gpu['temperature.gpu']
		utilization_gpu = gpu['utilization.gpu']
		process_list = gpu['processes']
		active_user_list = []
		for process in process_list:
			active_user_list.append(process['username'])
		collection.insert_one((create_gpu_state_dict(hostname, query_time, index, total_memory, utilization_memory, name, power, temperature, utilization_gpu, process_list, active_user_list)))


if __name__ == '__main__':
	try:
		client = MongoClient("mongodb://pegasus.vc.in.tum.de:27017/")
		db = client['gpu_logs']
		collection = db['logs']
		logging.info('Connection successful')
		while True:
			log_gpu_state(collection)
			time.sleep(1 * 60)

	except Exception as e:
		logging.error('Error : %s' % e, exc_info=True)
