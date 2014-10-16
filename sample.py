# coding:utf-8

from benchmark import Benchmark

bm = Benchmark('./request.log', host='127.0.0.1', n=1000, c=10, request_timeout=60, verbose=False)

bm.post_all_requests()
print bm.get_benchmark_result()