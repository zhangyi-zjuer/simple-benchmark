# coding:utf-8

import hashlib
from benchmark import Benchmark

def md5(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

bm = Benchmark('./request.log', host='127.0.0.1', n=1000, c=10, request_timeout=60, verbose=False, response_func=md5)

bm.post_all_requests()
print bm.get_benchmark_result()
