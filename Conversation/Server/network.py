import socket as server
import threading
import datetime
import platform
import subprocess
import json

class RouteServer:
    def __init__(self, host=None):
        self.__connections = {}
        self.__connections["clients"] = {}
        self.__connections["client_list"] = []
        self.__connections["client_limit"] = 4
        self.__server_data = {}
        if host is None:
            self.__server_data["host"] = self.__get_server_address()
        else:
            self.__server_data["host"] = host
        self.__server_data["port"] = 8080
        self.__server_data["server_data"] = (self.__server_data["host"], self.__server_data["port"])
        self.__server_data["server_conn"] = {}
        self.__server_data["server_conn"]["general"] = server.socket()
        self.__server_data["server_conn"]["general"].bind(self.__server_data["server_data"])
        self.__server_data["server_conn"]["clients"] = {}
        print("ROUTE SERVER ACTIVE")
        print("HOST: {}".format(self.__server_data["host"]))
        print("PORT: {} \n".format(self.__server_data["port"]))

    def allow_connections(self, limit=4):
        LIMIT = limit if ((limit + len(self.__connections["clients"])) < self.__connections["client_limit"]) else (self.__connections["client_limit"] - len(self.__connections["clients"]))
        print("ACCEPTING {} CONNECTIONS".format(LIMIT))
        for CONN_NO in range(1, LIMIT+1):
            try:
                ID_NO = len(self.__connections["clients"]) + 1
                CLIENT_ID = "C#{}".format(ID_NO)
                print("NEW CONNECTION {}".format(CONN_NO))
                print("CLIENT ID: {} \n".format(CLIENT_ID))
                self.__server_data["server_conn"]["general"].listen(1)
                CLIENT_CONN, (CLIENT_ADDRESS, CLIENT_PORT) = self.__server_data["server_conn"]["general"].accept()
                print("GENERAL CONNECTION ESTABLISHED")
                MESSAGE_PORT = 20000 + (10000//self.__connections["client_limit"]) * (ID_NO)
                AUDIO_PORT = 30000 + (10000//self.__connections["client_limit"]) * (ID_NO)
                VIDEO_PORT = 40000 + (10000//self.__connections["client_limit"]) * (ID_NO)
                CLIENT_DATA = {}
                CLIENT_DATA["addr"] = CLIENT_ADDRESS
                CLIENT_DATA["conn"] = {}
                CLIENT_DATA["conn"]["general"] = CLIENT_CONN
                CLIENT_DATA["ports"] = {}
                CLIENT_DATA["ports"]["general"] = CLIENT_PORT
                CLIENT_DICT = {}
                CLIENT_DICT["ID"] = CLIENT_ID
                CLIENT_DICT["message"] = MESSAGE_PORT
                CLIENT_DICT["audio"] = AUDIO_PORT
                CLIENT_DICT["video"] = VIDEO_PORT
                CLIENT_DICT_AS_STR = json.dumps(CLIENT_DICT)
                CLIENT_DICT_AS_UTF = CLIENT_DICT_AS_STR.encode("UTF-8")
                CLIENT_DATA["conn"]["general"].send(CLIENT_DICT_AS_UTF)
                self.__server_data["server_conn"]["clients"][CLIENT_ID] = {}
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["message"] = server.socket()
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["message"].bind((self.__server_data["host"], MESSAGE_PORT))
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["message"].listen(1)
                CLIENT_MESSAGE_CONN, (CLIENT_ADDRESS, CLIENT_MESSAGE_PORT) = self.__server_data["server_conn"]["clients"][CLIENT_ID]["message"].accept()
                print("MESSAGE CONNECTION ESTABLISHED \n")
                CLIENT_DATA["conn"]["message"] = CLIENT_MESSAGE_CONN
                CLIENT_DATA["ports"]["message"] = CLIENT_MESSAGE_PORT
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["audio"] = server.socket()
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["audio"].bind((self.__server_data["host"], AUDIO_PORT))
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["audio"].listen(1)
                CLIENT_AUDIO_CONN, (CLIENT_ADDRESS, CLIENT_AUDIO_PORT) = self.__server_data["server_conn"]["clients"][CLIENT_ID]["audio"].accept()
                print("AUDIO CONNECTION ESTABLISHED \n")
                CLIENT_DATA["conn"]["audio"] = CLIENT_AUDIO_CONN
                CLIENT_DATA["ports"]["audio"] = CLIENT_AUDIO_PORT
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["video"] = server.socket()
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["video"].bind((self.__server_data["host"], VIDEO_PORT))
                self.__server_data["server_conn"]["clients"][CLIENT_ID]["video"].listen(1)
                CLIENT_VIDEO_CONN, (CLIENT_ADDRESS, CLIENT_VIDEO_PORT),  = self.__server_data["server_conn"]["clients"][CLIENT_ID]["video"].accept()
                print("VIDEO CONNECTION ESTABLISHED \n")
                CLIENT_DATA["conn"]["video"] = CLIENT_VIDEO_CONN
                CLIENT_DATA["ports"]["video"] = CLIENT_VIDEO_PORT
                self.__connections["clients"][CLIENT_ID] = CLIENT_DATA
                self.__connections["client_list"].append(CLIENT_ID)
                print("CONNECTION TO CLIENT NO {} ESTABLISHED ON {}".format(CLIENT_ID, CLIENT_ADDRESS))
            except Exception as ConnectionException:
                print("CONNECTION UNSUCCESSFULL")
                print("EXCEPTION RAISED: {}".format(ConnectionException))

    def send_from_to(self, c1, c2, sz):
        while True:
            c1.send(c2.recv(sz))

    def start_all(self):
        v1 = self.__connections["clients"]["C#1"]["conn"]["video"]
        v2 = self.__connections["clients"]["C#2"]["conn"]["video"]
        a1 = self.__connections["clients"]["C#1"]["conn"]["audio"]
        a2 = self.__connections["clients"]["C#2"]["conn"]["audio"]
        for (x,y,z) in [(v1, v2, 5000), (v2, v1, 5000), (a1, a2, 4096), (a2, a1, 4096)]:
            a = threading.Thread(target=self.send_from_to, args=(x,y,z))
            a.start()
        while a.is_alive():
            pass

    def __get_server_address(self):
        cmd = 'ipconfig' if platform.system() == 'Windows' else 'ifconfig'
        terminal_result = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].decode()
        base_ip_list = ["192.168", "169.254"]
        for base_ip in base_ip_list:
            if base_ip in terminal_result:
                start = terminal_result.index(base_ip)
                end = start + terminal_result[start:].index(' ')
                ip_address = terminal_result[start:end].strip()
                return ip_address
        else:
            return server.gethostname()

    def relay_audio(self):
        pass
