from client_server.service import ServerService
from client_server.storage import save_state, load_state


service = ServerService()

service.register_user("Alice", "127.0.0.1", 5001, 6001)
service.update_subjects("Alice", ["sports", "technology"])
service.publish_message(
    "Alice",
    "sports",
    "Big Match Tonight",
    "The finals will be played at 8 PM.",
)

save_state(service.users, service.messages, service.comments)

users, messages, comments = load_state()

print("USERS:")
print(users)

print("\nMESSAGES:")
print(messages)

print("\nCOMMENTS:")
print(comments)