from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process
import mimetypes
import json
import urllib.parse
import pathlib
import socket
import logging

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb://mongodb:27017"

HTTPServer_Port = 3000
UDP_IP = '127.0.0.1'
UDP_PORT = 5000



class HttpGetHandler(BaseHTTPRequestHandler):
    #TODO Реалізувати логіку веб сервера для обробки статичних ресурсів, відправки вірних статус кодів та маршрутизації
    # Документація наслідуваних методів з BaseHTTPRequestHandler: https://docs.python.org/3/library/http.server.html 
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') 
    for el in data_parse.split('&')]}
        print(data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/contact':
            self.send_html_file('contact.html')
        else:
            self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
    mt = mimetypes.guess_type(self.path)
    if mt:
        self.send_header("Content-type", mt[0])
    else:
        self.send_header("Content-type", 'text/plain')
    self.end_headers()
    with open(f'.{self.path}', 'rb') as file:
        self.wfile.write(file.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpGetHandler):
    server_address = ('0.0.0.0', HTTPServer_Port)
    http = server_class(server_address, handler_class)
    #TODO Додати логування та обробку винятків та завершенням серверу у разі помилки
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
    http.serve_forever()


def send_data_to_socket(data):
    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #server = UDP_IP, UDP_PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = UDP_IP, 5000
    sock.sendto(data, server)
    sock.close()
    #TODO Дописати відправку даних

def save_data(data):
    client = MongoClient(uri, server_api=ServerApi("1"))
    #db = client.DB_NAME
    db = client.final_hw
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        data_parse = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        data_parse['date'] = str(datetime.now())
        db.messages.insert_one(data_parse)

    except ValueError as err:
        logging.error(f'Failed to parse data: {err}')
    except Exception as err:
        logging.error(f'Failed to write or read data: {err}')
    finally:
        client.close()
    # Дописати логіку збереження даних в БД з відповідними вимогами до структурою документу
    """
    { 
	    "date": "2024-04-28 20:21:11.812177",
        "username": "Who",    
	    "message": "What"  
    }
    """
    # Ключ "date" кожного повідомлення — це час отримання повідомлення: datetime.now()
    #data_parse = urllib.parse.unquote_plus(data.decode())
    

def run_socket_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    #TODO Дописати логіку прийняття даних та їх збереження в БД
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f'Received data: {data.decode()} from: {address}')
            sock.sendto(data, address)
            print(f'Send data: {data.decode()} to: {address}')

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(threadName)s %(message)s')

    #TODO Зробити два процеса для кожного з серверів
    http_server_process = Process()
    http_server_process.start()

    socket_server_process = Process()
    socket_server_process.start()

