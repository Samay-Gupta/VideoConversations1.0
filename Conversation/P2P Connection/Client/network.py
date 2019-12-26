import socket as client
import json

class Connection:
    def __init__(self, host="127.0.0.1", port=8080):
        self.__connections = {}
        self.__server_data = {}
        self.__server_data["host"] = host
        self.__server_data["port"] = port
        self.__connections["general"] = client.socket()
        
    def establish_connection(self):
        self.__connections["general"].connect((self.__server_data["host"], self.__server_data["port"]))
        connection_ports_raw = self.__connections["general"].recv(2048).decode()
        connection_ports = json.loads(connection_ports_raw)
        channels = ["message", "audio", "video"]
        for channel in channels:
            self.__connections[channel] = client.socket(family=client.AF_INET, type=client.SOCK_STREAM)
            self.__connections[channel].connect((self.__server_data["host"], connection_ports[channel]))

    def get_audio_connection(self):
        return self.__connections["audio"]

    def get_video_connection(self):
        return self.__connections["video"]

    def get_message_connection(self):
        return self.__connections["message"]
