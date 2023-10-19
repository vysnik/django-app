from django.http import HttpRequest
from django.shortcuts import render
import time

def set_useragent_middleware(get_response):
    # print("initial call")
    def middleware(request: HttpRequest):
        # print("before get response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        # print("after get response")
        return response

    return middleware

class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exceptions_count = 0
        self.requests_time = {}

    def __call__(self, request: HttpRequest):
        time_delay = 5

        if request.META.get("REMOTE_ADDR") not in self.requests_time:
            print("This is the first request after starting the server")
        else:
            if round(time.time()) - self.requests_time[request.META.get("REMOTE_ADDR")] < time_delay:
                print("It took less than 5 seconds to re-request the IP address:", request.META.get("REMOTE_ADDR"))
                return render(request, "requestdataapp/error-request.html")

        self.requests_time[request.META.get("REMOTE_ADDR")] = round(time.time())

        response = self.get_response(request)
        return response

    def process_exceptions(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        # print("got", self.exceptions_count, "exceptions so far")
