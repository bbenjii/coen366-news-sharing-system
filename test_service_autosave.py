from client_server.service import ServerService
from client_server.storage import load_state


service = ServerService()

service.register_user("Bob", "127.0.0.1", 5002, 6002)
service.update_subjects("Bob", ["health"])
service.publish_message("Bob", "health", "Health Update", "Drink more water.")

users, messages, comments = load_state()

print("USERS:")
print(users)

print("\nMESSAGES:")
print(messages)

print("\nCOMMENTS:")
print(comments)