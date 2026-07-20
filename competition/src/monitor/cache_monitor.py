class CacheMonitor:
    def __init__(self):
        self.cpu_requests = []
        self.cpu_responses = []
        self.mem_requests = []

    def record_cpu_request(self, request, cycle):
        self.cpu_requests.append({"cycle": cycle, "request": request})

    def record_cpu_response(self, response):
        self.cpu_responses.append(response)

    def record_mem_request(self, request):
        self.mem_requests.append(request)

    def clear(self):
        self.cpu_requests.clear()
        self.cpu_responses.clear()
        self.mem_requests.clear()
