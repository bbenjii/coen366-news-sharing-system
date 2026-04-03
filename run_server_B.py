from src.server.server_app import ServerApp
from src.shared import SERVER_B

if __name__ == '__main__':
    print('Running Server B')
    server = ServerApp(server_config=SERVER_B)
    server.run()