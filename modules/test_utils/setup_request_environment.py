
def setup_request_environment(request):
    request["wsgi"]["environ"] = {
        "wsgi.multiprocess": False,
        "HTTP_REFERER": "http://127.0.0.1:8000/%s/req/req/create" % request.application,
        "wsgi.multithread": True,
        "SERVER_SOFTWARE": "Rocket 1.2.2",
        "SCRIPT_NAME": "",
        "REQUEST_METHOD": "GET",
        "HTTP_HOST": "127.0.0.1:8000",
        "PATH_INFO": "/%s/hrm/create_inline" % request.application,
        "SERVER_PROTOCOL": "HTTP/1.1",
        "QUERY_STRING": "format=inner_form",
        "wsgi.version": 1,
        "HTTP_ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "HTTP_CONNECTION": "keep-alive",
        "REMOTE_ADDR": "127.0.0.1",
        "wsgi.run_once": False,
        "HTTP_ACCEPT_LANGUAGE": "en-gb",
        "wsgi.url_scheme": "http",
        "HTTP_ACCEPT_ENCODING": "gzip, deflate"
    }
