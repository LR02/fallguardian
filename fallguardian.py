from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json

import time
import math

from pymetawear.discover import select_device
from pymetawear.client import MetaWearClient


json_data = None
client = None

class WebServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json_data)

    def do_HEAD(self):
        self._set_headers()
        
def acc_callback(data):
    global json_data
    global client

    distance = math.sqrt(pow(data[1][0], 2) + pow(data[1][1], 2) + pow(data[1][2], 2))
    fall = False

    data_p = {'t': data[0], 'x': data[1][0], 'y': data[1][1], 'z': data[1][2], 'd': distance, 'f': fall}
    json_data = json.dumps(data_p)
    if distance >= 5.0:
        fall = True
        pattern = client.led.load_preset_pattern('solid', repeat_count=3)
        client.led.write_pattern(pattern, 'r')
        client.led.play()
	print("Fall detected: " + json_data)
        
    #print(json_data)
    
def run(server_class=HTTPServer, handler_class=WebServer, port=80):
    global client
    client = MetaWearClient("F5:7F:3B:92:1C:01", 'pybluez', debug=False)
    print("New client created: {0}".format(client))
    
    
    print("Get possible accelerometer settings...")
    settings = client.accelerometer.get_possible_settings()
    print(settings)

    time.sleep(1.0)

    print("Write accelerometer settings...")
    client.accelerometer.set_settings(data_rate=12.5, data_range=16.0)

    time.sleep(1.0)
    

    print("Subscribing to accelerometer signal notifications...")
    client.accelerometer.high_frequency_stream = False
    client.accelerometer.notifications(acc_callback)
    
    pattern = client.led.load_preset_pattern('solid', repeat_count=3)
    client.led.write_pattern(pattern, 'g')
    client.led.play()
    
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

