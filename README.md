# SJMD — Clue-Less

Skeletal increment: validates the client/server architecture and messaging (SRS §2).
No game rules yet — handlers send canned responses.

## Architecture

```
 Browser client (client/)  <── JSON over WebSocket (/ws) ──>  Python server (server/)
   index.html, client.js                                        main.py      connections, send/broadcast, logging
                                                                handlers.py  one stub handler per client->server message
                                                                protocol.py  message names + envelope
```

Envelope for every message: `{"type": "<messageName>", "payload": {...}}`.
Message names and payloads are listed in `server/protocol.py` (from SRS §2.4).

## Setup (one time)

You need **Python 3.10 or newer** and **git**. Check with:

```sh
python3 --version      # Windows: python --version
git --version
```

**1. Get the code**

```sh
# For http
git clone https://github.com/Glqzer/SJMD.git

# Or for ssh
git clone git@github.com:Glqzer/SJMD.git

cd SJMD
```

All commands below are run from inside the `SJMD` folder.

**2. Create a virtual environment.** This is a private folder (`.venv/`) holding the project's
Python packages so nothing is installed system-wide. It is git-ignored; each person makes their own.

| macOS / Linux / WSL | Windows (PowerShell or cmd) |
|---|---|
| `python3 -m venv .venv` | `python -m venv .venv` |

> Ubuntu/Debian/WSL: if this fails with "ensurepip is not available", run
> `sudo apt install python3-venv` and try again.

**3. Install the dependencies**

| macOS / Linux / WSL | Windows |
|---|---|
| `.venv/bin/pip install -r requirements.txt` | `.venv\Scripts\pip install -r requirements.txt` |

## Running

**1. Start the server**

| macOS / Linux / WSL | Windows |
|---|---|
| `.venv/bin/python server/main.py` | `.venv\Scripts\python server\main.py` |

You should see:

```
20:39:57.338  Clue-Less server listening on http://localhost:8765
```

Leave this terminal open — it is the server's log. Stop the server with **Ctrl+C**.

**2. Open the client.** Go to **http://localhost:8765** in a browser. Open it in 2–4 separate
windows or tabs to act as different players. The status line under the title should say
"connected".

**3. Check that it works**

1. In each window, type a player name and click **Join game**. Every window shows a blue
   `playerJoined` line.
2. Type a chat message and click **Send**. Every window shows the blue `chatBroadcast`.
3. The server terminal shows each message: `RECV` (from a client), `SEND` (to one client),
   `BCAST` (to all clients).

After pulling new code, restart the server (Ctrl+C, then start it again) and refresh the browser
windows. If `requirements.txt` changed, repeat setup step 3.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'websockets'` | You ran plain `python` instead of the one in `.venv`. Use the exact commands above, or redo setup step 3. |
| `address already in use` / `Errno 98` / `Errno 10048` | A server is already running (maybe in another terminal). Stop it with Ctrl+C, or change `PORT` in `server/main.py`. |
| Browser status says "disconnected" | The server isn't running or was restarted. Start it and refresh the page. |
| `TypeError: unsupported operand type(s) for \|` | Your Python is older than 3.10. Install a newer one. |
| Teammates on other computers can't connect | Expected on most networks. For the demo, run all windows on one machine. |

## What works now

- Server accepts multiple clients, decodes the envelope, dispatches to handlers, logs everything.
- `joinGame` → `playerJoined` broadcast.
- `chatMessage` → `chatBroadcast` to all clients.
- Unknown or not-yet-implemented messages → `invalidAction` to the sender only.
- Client log colours messages: grey = sent, blue = broadcast, brown = private, red = error.

## Open tasks

Search the code for `TODO(` to find each one in place.

**Server** (`server/handlers.py`, `server/main.py`)
- [x] `selectCharacter`, including rejecting a character that's already taken
- [ ] `startGame` → `gameStarted`, different `dealtHand` per player, `yourTurn`, `turnChanged`
- [ ] `moveRequest` → `characterMoved`
- [ ] `makeSuggestion` → `suggestionMade`, `characterMoved`, `requestDisprove` to the next player
- [ ] `disproveResponse` → `cardShown` (suggester only), `suggestionDisproved` (all); also the `cannotDisprove` path
- [ ] `makeAccusation` → `accusationMade`, `accusationResult`, `playerEliminated`/`gameWon`
- [ ] `endTurn` → `turnChanged`, `yourTurn`
- [ ] Broadcast `playerLeft` on disconnect (after it's added to the SRS)

**Client** (`client/index.html`, `client/client.js`)
- [ ] Controls for each client→server message (dropdowns and buttons are fine)
- [ ] Handle `requestDisprove`: show matching cards, send `disproveResponse`
- [ ] Optional: a 3×3 text board redrawn on `characterMoved`

**Docs / SRS**
- [ ] Add transport + envelope (JSON over WebSocket) to SRS §2.4
- [ ] Add missing messages: `characterSelected`, `playerLeft`, `gameState` (reconnect sync), `stayInRoom`
- [ ] Fix glossary leftovers ("Your list leaves out the Conservatory", "Billiard Room and Library are separate squares", secret passages)

**Video** (narrated, ≤15 min, no code walkthrough)
- [ ] Architecture slide → live demo of each flow with server log visible → project plan status / risks → Credits
