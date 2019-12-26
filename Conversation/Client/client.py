from network import Connection
from threading import Thread
from media import MediaHandler

HOST = "192.168.0.145"
PORT = 8080
if __name__ == "__main__":
    conn = Connection(HOST, PORT)
    conn.establish_connection()
    handler = MediaHandler(audio_conn=conn.get_audio_connection(), video_conn=conn.get_video_connection())
    handler.initialise_audio_stream()
    handler.initialise_video_stream()
