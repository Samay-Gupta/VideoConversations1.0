from network import RouteServer
from threading import Thread

if __name__ == "__main__":
    router = RouteServer()
    router.allow_connections(2)
    router.start_all()
