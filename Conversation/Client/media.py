import struct
import zlib
import array
import threading

import cv2
import numpy as np
from imutils.video import WebcamVideoStream

import pyaudio

class MediaHandler:
    def __init__(self, video_conn=None, audio_conn=None):
        self.video_connection = video_conn
        self.audio_connection = audio_conn
        self.status = {
            "SEND_AUDIO": False,
            "RECV_AUDIO": False,
            "SEND_VIDEO": False,
            "RECV_VIDEO": False,
        }
        self.threads = {
            "SEND_AUDIO": None,
            "RECV_AUDIO": None,
            "SEND_VIDEO": None,
            "RECV_VIDEO": None,
        }

    def initialise_audio_stream(self):
        if self.audio_connection is not None:
            self.audio_handler = pyaudio.PyAudio()
            self.audio_stream = self.audio_handler.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, output=True, frames_per_buffer=1024)
            self.status["SEND_AUDIO"] = True
            self.threads["SEND_AUDIO"] = threading.Thread(target=self.__send_audio, args=(1024,))
            self.threads["SEND_AUDIO"].start()
            self.status["RECV_AUDIO"] = True
            self.threads["RECV_AUDIO"] = threading.Thread(target=self.__recv_audio, args=(4096, 1024,))
            self.threads["RECV_AUDIO"].start()

    def __send_audio(self, chunk_size):
        while self.status["SEND_AUDIO"]:
            self.audio_connection.sendall(array.array('h', self.audio_stream.read(chunk_size)))

    def __recv_audio(self, buffer_size, chunk_size):
        while self.status["RECV_AUDIO"]:
            self.audio_stream.write(self.__recvall_audio(buffer_size, chunk_size))

    def __recvall_audio(self, buffer_size, chunk_size):
        data = b''
        while len(data) != buffer_size:
            remaining = buffer_size-len(data)
            if remaining > chunk_size*4:
                data += self.audio_connection.recv(chunk_size*4)
            else:
                data += self.audio_connection.recv(remaining)
        return data

    def initialise_video_stream(self):
        if self.video_connection is not None:
            self.video_stream = WebcamVideoStream(0).start()
            self.status["SEND_VIDEO"] = True
            self.threads["SEND_VIDEO"] = threading.Thread(target=self.__send_video, args=(1024,))
            self.threads["SEND_VIDEO"].start()
            self.status["RECV_VIDEO"] = True
            self.threads["RECV_VIDEO"] = threading.Thread(target=self.__recv_video, args=(1024,))
            self.threads["RECV_VIDEO"].start()

    def __send_video(self, chunk_size):
        while self.status["SEND_VIDEO"]:
            try:
                frame = self.video_stream.read()
                cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.array(cv2.resize(frame, (640, 480)), dtype = np.uint8).reshape(1, 640*480*3)
                data = zlib.compress(bytearray(frame), 9)
                size = struct.pack('!I', len(data))
                img_bytes = b''
                self.video_connection.sendall(size)
                while len(data) > 0:
                    if (chunk_size*5000) <= len(data):
                        img_bytes = data[:(chunk_size*5000)]
                        data = data[(chunk_size*5000):]
                        self.video_connection.sendall(img_bytes)
                    else:
                        img_bytes = data
                        self.video_connection.sendall(img_bytes)
                        data= b''
            except Exception as e:
                print(e)

    def __recv_video(self, chunk_size):
        while self.status["RECV_VIDEO"]:
            try:
                size, = struct.unpack('!I', self.__recvall_video(4, chunk_size))
                data = self.__recvall_video(size, chunk_size)
                img = zlib.decompress(data)
                if len(data) == size:
                    img = np.array(np.array(list(img)), dtype = np.uint8).reshape(480, 640, 3)
                    cv2.imshow("Video Chat", img)
                    if cv2.waitKey(1) == 27:
                        cv2.destroyAllWindows()
            except Exception as e:
                print(e)

    def __recvall_video(self, size, chunk_size):
        data = b''
        while len(data) != size:
            remaining = size - len(data)
            if remaining > chunk_size*5000:
                data += self.video_connection.recv(chunk_size*5000)
            else:
                data += self.video_connection.recv(remaining)
        return data
