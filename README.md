simple-benchmark
================

A simple benchmark implement

sample

from benchmark import Benchmark


bm = Benchmark('./requests.log', host='127.0.0.1', n=1000, c=10, request_timeout=60, verbose=False)

bm.post_all_requests()
print bm.get_benchmark_result()
