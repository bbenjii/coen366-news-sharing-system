# News Sharing System

This repository contains an implementation of the COEN 366 Winter 2026 project: a News Sharing System (NSS).

- Developers working on the codebase alongside the team
- The course staff reviewing the project structure and current implementation

At the moment, the codebase mainly implements the TCP control-plane portion of the project:

- user registration
- deregistration
- login of previously registered users
- user endpoint updates
- subject updates
- JSON-based persistence of registered users

## Installation

The project currently uses only the Python standard library.

### Prerequisites

- Python 3.10 or newer

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## How To Run

Open separate terminals from the project root.

### Terminal 1: Start Server A

```bash
python3 run_server_A.py
```

Expected behavior:

- prints that Server A is running
- starts listening for TCP connections on `localhost:10000`

### Terminal 2: Start Server B

```bash
python3 run_server_B.py
```

Expected behavior:

- prints that Server B is running
- starts listening for TCP connections on `localhost:10001`

### Terminal 3: Start a Client

```bash
python3 run_client.py
```

The client will prompt for:

- which server to connect to (`A` or `B`)
- whether to `/login` or `/register`
- local TCP/UDP ports during registration or update



## Repository Structure

```text
news-sharing-system/
├── COEN366_PROJECT.pdf        # Official project brief
├── README.md                  # Project overview, setup, and demo guide
├── TODO.md                    # Implementation status against the PDF
├── requirements.txt           # Currently no third-party dependencies
├── run_client.py              # CLI entry point for the client
├── run_server_A.py            # CLI entry point for region server A
├── run_server_B.py            # CLI entry point for region server B
├── demo/                      # Extra demo launchers / historical demo assets
├── data/                      # Runtime persistence folder created by the server
└── src/
    ├── client/
    │   ├── client_app.py      # Interactive client CLI and command loop
    │   ├── state.py           # In-memory client session state
    │   └── tcp_client.py      # TCP client operations for control messages
    ├── server/
    │   ├── server_app.py      # Server application wrapper
    │   ├── tcp_server.py      # TCP server, request handling, persistence hooks
    │   ├── persistence.py     # JSON load/save for registered users
    │   └── data/              # Historical sample JSON files, not the main runtime path
    └── shared/
        ├── config.py          # Server configs and allowed subjects
        ├── models.py          # Dataclasses for request/response payloads
        └── protocol.py        # Text protocol serialization/parsing helpers
```

## Architecture Overview

### 1. `src/shared`

This package is the protocol contract shared by client and server.

- `config.py` defines:
  - `SERVER_A`
  - `SERVER_B`
  - `ALLOWED_SUBJECTS`
- `models.py` contains dataclasses for TCP request/response payloads
- `protocol.py` serializes and parses the current text-based protocol messages and validates IP addresses and ports

This is the correct place to extend when adding:

- UDP message definitions
- inter-server forwarding messages
- `REFER`, `PUBLISH`, `FORWARD`, `MESSAGE`, `PUBLISH-COMMENT`, and `COMMENT`

### 2. `src/server`

This package contains the current server implementation.

- `server_app.py` is a thin wrapper that starts the TCP server
- `tcp_server.py` handles:
  - accepting TCP connections
  - spawning one thread per TCP client
  - parsing incoming requests
  - register / login / update / subject update / deregister behavior
  - saving and loading persistent user state
- `persistence.py` stores registrations in JSON files under `data/`

Current behavior:

- The server listens on TCP only
- Each request is handled independently
- User records are keyed by unique name
- Registered user data persists across restarts through JSON files

Current limitation:

- There is no UDP socket, no publish/comment pipeline, and no server-to-server communication yet

### 3. `src/client`

This package contains the interactive command-line client.

- `client_app.py` manages:
  - initial server selection
  - login or registration
  - interactive command loop
  - local session state display
- `state.py` stores the current user/session information
- `tcp_client.py` opens TCP connections and sends the current control messages

Current client commands:

- `/register`
- `/update`
- `/subjects`
- `/deregister`
- `/logout`
- `/server`

Important limitation:

- The client does not open a UDP socket to receive `MESSAGE` or `COMMENT` traffic yet

## Current Protocol Coverage

Implemented in code:

- `REGISTER`
- `REGISTERED`
- `REGISTER-DENIED`
- `DE-REGISTER`
- `UPDATE`
- `UPDATE-CONFIRMED`
- `UPDATE-DENIED`
- `SUBJECTS`
- `SUBJECTS-UPDATED`
- `SUBJECTS-REJECTED`
- `LOGIN`
- `LOGIN-CONFIRMED`
- `LOGIN-DENIED`

Required by the PDF but not implemented yet:

- `REFER`
- `PUBLISH`
- `PUBLISH-DENIED`
- `FORWARD`
- `MESSAGE`
- `PUBLISH COMMENT` / `PUBLISH-COMMENT`
- `COMMENT`

Note: `LOGIN` is a project convenience added by this implementation. It is not explicitly defined in the PDF, but it is useful for reloading persisted users without forcing re-registration.

## Persistence

Server state is currently stored as JSON on disk through `src/server/persistence.py`.

Runtime behavior:

- each server writes a file named after the server, such as `data/server_a_registrations.json`
- the file is loaded on startup
- the file is rewritten whenever a user record changes

Why this matters:

- this partially addresses the PDF persistence requirement
- it allows a professor or developer to stop and restart a server and observe that registered users remain stored


## Developer Notes

### Design Direction

The current code is already separated into three useful layers:

- protocol/shared types in `src/shared`
- client behavior in `src/client`
- server behavior in `src/server`

That structure is a reasonable foundation for the remaining work. The next implementation phase should preserve that split:

- add UDP protocol/message types in `src/shared`
- add a UDP listener/sender on the client side
- add both TCP and UDP services on the server side
- add server-to-server forwarding logic without mixing it into the CLI layer

### Important Deviations From the PDF

These should be understood by anyone continuing development:

- the code currently uses `LOGIN`, which is not part of the PDF protocol text
- request IDs are currently hardcoded as `"1"` in the client rather than generated per request
- no regional referral logic exists yet
- no inter-server communication exists yet
- message naming in code does not always match the PDF wording exactly

These are not just documentation issues; they are implementation gaps that should be resolved before final submission.

## Recommended Next Steps

- Implement UDP publish and comment flows
- Add server-to-server forwarding
- Implement `REFER` handling for wrong-region registration/update
- Add a real request ID generator and request tracking
- Add tests for protocol parsing and core server behaviors
- Standardize persistence/data file locations

For the status breakdown, see `TODO.md`.
