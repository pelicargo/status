import http.server
import json
import subprocess
import pprint
import time
import os

cacheTime = time.time()
cache = ""
directory = os.getenv("INSTALL_DIR") or os.getenv("HOME")

def query():
    cacheTime = time.time()
    query = subprocess.run(["docker", "ps", "--format", "{{json .}}", "--no-trunc"], capture_output=True).stdout.decode("utf8").strip()
    responses = query.split("\n")

    containers = {}
    for response in responses:
        ps = json.loads(response)
        containers[ps["Names"]] = {
            "name": ps["Names"],
            "state": ps["State"],
            "uptime": ps["RunningFor"],
        }
    branch = subprocess.run(["git", "-C", os.path.join(directory, "pelicargo"), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True).stdout.decode("utf8").strip()
    tainted = len(subprocess.run(["git", "-C", os.path.join(directory, "pelicargo"), "diff"], capture_output=True).stdout.decode("utf8").strip())
    return {"containers": containers, "branch": branch, "tainted": tainted > 0}

def queryCache():
    global cache
    global cacheTime
    if cacheTime < time.time():
        cache = json.dumps(query()).encode("utf8")
        cacheTime = time.time() + 60
    return cache

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        # Do something
        self.send_response(200)
        info = query()
        self.wfile.write(queryCache())

server_address = ('', 8086)
httpd = http.server.HTTPServer(server_address, HTTPRequestHandler)
httpd.serve_forever()
