import socket as server
import json

class Connection:
    def __init__(self, host="127.0.0.1", port=8080):
        self.__connections = {}
        self.__server_data = {}
        self.__server_data["host"] = host
        self.__server_data["port"] = port
        self.__connections["server"] = server.socket()
        self.__connections["server"].bind((self.__server_data["host"], self.__server_data["port"]))
        
    def establish_connection(self):
        self.__connections["server"].listen(1)
        self.__connections["general"], (IP_ADDR, PORT) = self.__connections["server"].accept()
        CLIENT_DICT = {}
        CLIENT_DICT["ID"] = "C#1"
        CLIENT_DICT["message"] = 20000
        CLIENT_DICT["audio"] = 30000
        CLIENT_DICT["video"] = 40000
        CLIENT_DICT_AS_STR = json.dumps(CLIENT_DICT)
        CLIENT_DICT_AS_UTF = CLIENT_DICT_AS_STR.encode("UTF-8")
        self.__connections["general"].send(CLIENT_DICT_AS_UTF)
        channels = ["message", "audio", "video"]
        for channel in channels:
            self.__connections["server"] = server.socket(family=server.AF_INET, type=server.SOCK_STREAM)
            self.__connections["server"].bind((self.__server_data["host"], CLIENT_DICT[channel]))
            self.__connections["server"].listen(1)
            self.__connections[channel], (IP_ADDR, PORT) = self.__connections["server"].accept()
        
    def get_audio_connection(self):
        return self.__connections["audio"]

    def get_video_connection(self):
        return self.__connections["video"]

    def get_message_connection(self):
        return self.__connections["message"]
