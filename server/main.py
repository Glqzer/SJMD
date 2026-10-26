"""Clue-Less server subsystem.

Serves the browser client over HTTP and accepts WebSocket connections at /ws,
all on one port. Every message in and out is written to the system log -- that
log is what we show in the skeletal demo video.

Run:  .venv/bin/python server/main.py   then open http://localhost:8765
"""

import asyncio
import logging
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path

from websockets.asyncio.server import serve
from websockets.datastructures import Headers
from websockets.http11 import Response

import protocol
from handlers import HANDLERS

HOST = "0.0.0.0"
PORT = 8765
CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/client.js": ("client.js", "text/javascript; charset=utf-8"),
}

log = logging.getLogger("clueless")


@dataclass
class Player:
    name: str = ""
    character: str | None = None
    # TODO(server): add status (active/eliminated) and moved_by_suggestion (SRS §2.3)
    #   when the minimal increment needs them.


class Hub:
    """Tracks connected players and implements the two delivery paths in the SRS:
    server -> specific client (send) and server -> all clients (broadcast)."""

    def __init__(self):
        self.players = {}  # connection -> Player
        # TODO(server): game-level state (turn order, pending suggestion, ...) goes here
        #   for now; move it into a separate game/ module in the minimal increment.

    def label(self, conn):
        return self.players[conn].name or f"conn-{id(conn) % 10000}"

    async def send(self, conn, msg_type, **payload):
        log.info("SEND  -> %-12s %s %s", self.label(conn), msg_type, payload)
        await conn.send(protocol.encode(msg_type, **payload))

    async def broadcast(self, msg_type, **payload):
        log.info("BCAST -> ALL(%d)      %s %s", len(self.players), msg_type, payload)
        raw = protocol.encode(msg_type, **payload)
        await asyncio.gather(*(c.send(raw) for c in self.players), return_exceptions=True)

    async def handle(self, conn):
        self.players[conn] = Player()
        log.info("CONNECT %s", self.label(conn))
        try:
            async for raw in conn:
                try:
                    msg_type, payload = protocol.decode(raw)
                except ValueError as e:
                    await self.send(conn, protocol.INVALID_ACTION, reason=f"bad message: {e}")
                    continue
                log.info("RECV  <- %-12s %s %s", self.label(conn), msg_type, payload)
                handler = HANDLERS.get(msg_type)
                if handler is None:
                    await self.send(conn, protocol.INVALID_ACTION, reason=f"unknown type {msg_type}")
                else:
                    await handler(self, conn, payload)
        finally:
            log.info("DISCONNECT %s", self.label(conn))
            del self.players[conn]
            # TODO(server): broadcast playerLeft once it is added to the SRS/protocol.


def serve_static(connection, request):
    """Serve the client files over plain HTTP; let /ws continue to the WebSocket handshake."""
    if request.path == "/ws":
        return None
    entry = STATIC_FILES.get(request.path)
    if entry is None:
        return connection.respond(HTTPStatus.NOT_FOUND, "Not found\n")
    filename, content_type = entry
    body = (CLIENT_DIR / filename).read_bytes()
    headers = Headers([("Content-Type", content_type), ("Content-Length", str(len(body)))])
    return Response(HTTPStatus.OK.value, "OK", headers, body)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d  %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("websockets").setLevel(logging.WARNING)  # keep the demo log to our messages
    hub = Hub()
    async with serve(hub.handle, HOST, PORT, process_request=serve_static) as server:
        log.info("Clue-Less server listening on http://localhost:%d", PORT)
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
