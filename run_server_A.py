from src.server.server_app import ServerApp
from src.shared import SERVER_A

if __name__ == '__main__':
    print('Running Server A')
    server = ServerApp(server_config=SERVER_A)
    server.run()