from client_server.service import ServerService


print("=== FIRST SERVICE INSTANCE ===")
service1 = ServerService()

print("\nLoaded users:")
print(service1.users)

print("\nLoaded messages:")
print(service1.messages)

print("\nLoaded comments:")
print(service1.comments)

print("\nAdding Diana...")
success, message = service1.register_user("Diana", "127.0.0.1", 5004, 6004)
print(success, message)

success, message = service1.update_subjects("Diana", ["news"])
print(success, message)

success, message = service1.publish_message(
    "Diana",
    "news",
    "Breaking News",
    "A major event happened today."
)
print(success, message)

print("\n=== SECOND SERVICE INSTANCE (SIMULATED RESTART) ===")
service2 = ServerService()

print("\nLoaded users after restart:")
print(service2.users)

print("\nLoaded messages after restart:")
print(service2.messages)

print("\nLoaded comments after restart:")
print(service2.comments)