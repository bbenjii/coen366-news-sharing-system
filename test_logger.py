from client_server.service import ServerService


service = ServerService()

service.register_user("Charlie", "127.0.0.1", 5003, 6003)
service.update_subjects("Charlie", ["finance"])
service.publish_message("Charlie", "finance", "Market Update", "Stocks moved today.")