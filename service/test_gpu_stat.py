from gpustat import GPUStatCollection
from pprint import pprint

stat = GPUStatCollection.new_query().jsonify()

pprint(stat)
