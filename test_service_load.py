from client_server.service import ServerService


service = ServerService()

print("USERS:")
print(service.users)

print("\nMESSAGES:")
print(service.messages)

print("\nCOMMENTS:")
print(service.comments)