# Distributed Publish-Subscribe Client-Server System

## Project Overview

This project implements a distributed publish-subscribe news delivery system using TCP and UDP sockets in Python.

The system supports:

- client registration and deregistration
- client profile updates
- subject subscription updates
- publishing news messages
- publishing comments on existing news
- local message delivery to interested users
- server-to-server forwarding between two regional servers
- persistence across restart
- logging of important server events

The project is organized in five phases, and the final implementation completes all five.

---

## System Architecture

### Core Components

- `client_server/models.py`  
  Defines:
  - User
  - NewsMessage
  - Comment

- `client_server/service.py`  
  Handles all business logic:
  - register / deregister users
  - update user information
  - update subject subscriptions
  - publish messages
  - publish comments
  - trigger persistence
  - trigger logging

- `client_server/protocol.py`  
  Builds and parses protocol messages between clients and servers.

- `client_server/tcp_handler.py`  
  Handles TCP control requests:
  - REGISTER
  - DE-REGISTER
  - UPDATE
  - SUBJECTS

- `client_server/udp_handler.py`  
  Handles UDP real-time messaging:
  - PUBLISH
  - PUBLISH-COMMENT
  - FORWARD
  - FORWARD-COMMENT

- `client_server/storage.py`  
  Handles persistence:
  - save state to JSON files
  - load state from JSON files

- `client_server/logger.py`  
  Handles timestamped logging to terminal and log files.

- `run_servers.py` / `run_servers_b.py`  
  Used to start Server A and Server B.

---

## Protocol Design

### Message Format

All messages follow this format:

```
COMMAND|field1|field2|...
```

### Examples

```
REGISTER|1|user|127.0.0.1|5001|6001
SUBJECTS|2|user|sports,technology
PUBLISH|100|user|sports|Title|Text
```

---

### TCP Commands

- `REGISTER` → `REGISTERED` / `REGISTER-DENIED`
- `DE-REGISTER` → `DE-REGISTERED` (or ignored if user not found)
- `UPDATE` → `UPDATE-CONFIRMED` / `UPDATE-DENIED` / `REFER`
- `SUBJECTS` → `SUBJECTS-UPDATED` / `SUBJECTS-REJECTED`

---

### UDP Commands

- `PUBLISH` → MESSAGE delivery to subscribers
- `PUBLISH-COMMENT` → COMMENT delivery
- `FORWARD` → server-to-server message forwarding
- `FORWARD-COMMENT` → server-to-server comment forwarding

---

## Persistence

Server state is stored in:

- `data/servera_state.json`
- `data/serverb_state.json`

These files store:

- users
- messages
- comments

On restart, the server automatically reloads its previous state.

---

## Assumptions and Error Handling

### Assumptions

- Subjects are predefined in `config.py`
- Users must register before performing any action
- Two servers represent two different regions
- Request IDs are per request (not per user)

### Error Handling

- Invalid message format → rejected
- Invalid IP address or port → rejected
- Invalid subjects → rejected
- Unregistered users → rejected
- Unknown DE-REGISTER → ignored
- Comment requires an existing message

---

## How to Run

### 1. Start Server A

```bash
python3 run_servers.py
```

### 2. Start Server B

```bash
python3 run_servers_b.py
```

### 3. Run TCP Client

```bash
python3 test_tcp_client.py
```

### 4. Run UDP Client

```bash
python3 test_udp_client.py
```

### 5. Run UDP Listener

```bash
python3 udp_listener.py <username> <udp_port>
```

---

## Demo Flow

1. Start both servers
2. Register users
3. Update subject subscriptions
4. Publish a message
5. Verify local message delivery
6. Verify cross-server forwarding
7. Publish a comment
8. Verify comment delivery
9. Restart servers
10. Verify persistence

---

## Final Status

The system successfully implements:

- TCP control plane
- UDP publish-subscribe messaging
- inter-server forwarding
- comment system
- persistent storage
- logging

All required phases (Phase 1 to Phase 5) are fully completed and functional.
