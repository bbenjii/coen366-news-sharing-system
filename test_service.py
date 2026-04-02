from client_server.service import ServerService


def print_section(title: str) -> None:
    print(f"\n---- {title} ----")


service = ServerService()

print_section("Register Alice")
success, message = service.register_user("Alice", "127.0.0.1", 5001, 6001)
print(success, message)

print_section("Update Alice")
success, message = service.update_user("Alice", "127.0.0.1", 7001, 8001)
print(success, message)

user = service.get_user("Alice")
print_section("Updated Alice data")
print(user)

print_section("Update missing user")
success, message = service.update_user("Bob", "127.0.0.1", 9001, 9002)
print(success, message)

print_section("Deregister Alice")
success, message = service.deregister_user("Alice")
print(success, message)

print_section("Update deregistered Alice")
success, message = service.update_user("Alice", "127.0.0.1", 9999, 9998)
print(success, message)

print_section("Register Alice again")
success, message = service.register_user("Alice", "127.0.0.1", 5001, 6001)
print(success, message)

print_section("Update valid subjects for Alice")
success, message = service.update_subjects("Alice", ["Sports", "TECHNOLOGY"])
print(success, message)

user = service.get_user("Alice")
print_section("Alice subjects")
print(user.subjects)

print_section("Update invalid subjects for Alice")
success, message = service.update_subjects("Alice", ["Sports", "Cooking"])
print(success, message)

print_section("Publish valid message")
success, message = service.publish_message(
    "Alice",
    "Sports",
    "Big Match Tonight",
    "The finals will be played at 8 PM."
)
print(success, message)

print_section("Stored messages")
print(service.messages)

print_section("Publish invalid subject")
success, message = service.publish_message(
    "Alice",
    "Cooking",
    "Best Recipe",
    "Try this new pasta recipe."
)
print(success, message)

print_section("Publish subject not in interests")
success, message = service.publish_message(
    "Alice",
    "health",
    "Workout Tips",
    "Train consistently."
)
print(success, message)

print_section("Publish valid comment")
success, message = service.publish_comment(
    "Alice",
    "Sports",
    "Big Match Tonight",
    "I think this will be a great game."
)
print(success, message)

print_section("Stored comments")
print(service.comments)

print_section("Publish comment on missing message")
success, message = service.publish_comment(
    "Alice",
    "Sports",
    "Unknown Title",
    "This should fail."
)
print(success, message)

print_section("Publish comment with invalid subject")
success, message = service.publish_comment(
    "Alice",
    "Cooking",
    "Big Match Tonight",
    "This should also fail."
)
print(success, message)

print_section("Register Bob")
success, message = service.register_user("Bob", "127.0.0.1", 5002, 6002)
print(success, message)

print_section("Bob valid subjects")
success, message = service.update_subjects("Bob", ["Health", "Sports"])
print(success, message)

print_section("Registered users")
print(service.get_registered_users())

print_section("Interested users in sports")
print(service.get_interested_users("sports"))

print_section("Interested users in health")
print(service.get_interested_users("health"))

print_section("Interested users in technology")
print(service.get_interested_users("technology"))

print_section("Message exists: sports / Big Match Tonight")
print(service.message_exists("sports", "Big Match Tonight"))

print_section("Message exists: sports / Missing Title")
print(service.message_exists("sports", "Missing Title"))