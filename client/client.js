// Clue-Less client subsystem: connection + message log.
// All game logic lives on the server; this file only sends and displays messages.

// Message names -- keep in sync with server/protocol.py
const MSG = {
  // Client -> Server
  JOIN_GAME: "joinGame",
  SELECT_CHARACTER: "selectCharacter",
  START_GAME: "startGame",
  MOVE_REQUEST: "moveRequest",
  MAKE_SUGGESTION: "makeSuggestion",
  DISPROVE_RESPONSE: "disproveResponse",
  MAKE_ACCUSATION: "makeAccusation",
  END_TURN: "endTurn",
  CHAT_MESSAGE: "chatMessage",
};

// Server -> specific client messages, used to colour the log (private vs broadcast).
const PRIVATE_TYPES = new Set([
  "dealtHand", "yourTurn", "requestDisprove", "cardShown", "accusationResult", "invalidAction",
]);

const logEl = document.getElementById("log");
const statusEl = document.getElementById("status");
const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);

function logLine(text, cls) {
  const line = document.createElement("div");
  line.className = cls;
  line.textContent = `${new Date().toLocaleTimeString()}  ${text}`;
  logEl.appendChild(line);
  logEl.scrollTop = logEl.scrollHeight;
}

function send(type, payload = {}) {
  ws.send(JSON.stringify({ type, payload }));
  logLine(`SENT     ${type} ${JSON.stringify(payload)}`, "out");
}

ws.onopen = () => { statusEl.textContent = "connected"; };
ws.onclose = () => { statusEl.textContent = "disconnected"; };

ws.onmessage = (event) => {
  const { type, payload } = JSON.parse(event.data);
  const isPrivate = PRIVATE_TYPES.has(type);
  logLine(`${isPrivate ? "PRIVATE " : "BCAST   "} ${type} ${JSON.stringify(payload)}`,
          type === "invalidAction" ? "error" : isPrivate ? "private" : "broadcast");

  // TODO(client): keep a local copy of the public game state (SRS §2.3) and update
  //   the UI per message type, e.g.
  //   switch (type) { case "characterMoved": ...; case "requestDisprove": ...; }
  //   requestDisprove should show the matching cards and let the player pick one
  //   to send back as disproveResponse.
};

document.getElementById("join").onclick = () =>
  send(MSG.JOIN_GAME, { playerName: document.getElementById("name").value });

document.getElementById("send-chat").onclick = () => {
  const input = document.getElementById("chat");
  send(MSG.CHAT_MESSAGE, { text: input.value });
  input.value = "";
};

document.querySelectorAll("#character-buttons button").forEach((button) => {
  button.onclick = () => {
    const character = button.dataset.character;
    send(MSG.SELECT_CHARACTER, { character });
  };
});
// TODO(client): wire up the remaining buttons added in index.html, e.g.
//   document.getElementById("end-turn").onclick = () => send(MSG.END_TURN);
