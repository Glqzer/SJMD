"""Clue-Less message protocol (SRS §2.4).

Transport: JSON over a WebSocket at ws://<host>:<port>/ws
Every message, in both directions, uses the same envelope:

    {"type": "<messageName>", "payload": {...}}

The constants below are the single source of truth for message names.
The client mirrors them in client/client.js -- keep the two in sync.

TODO(docs): Add the transport + envelope description above to the SRS §2.4.
TODO(docs/server/client): The SRS is missing a few messages we will need:
    - characterSelected (all clients): a character was taken, so others' pickers update
    - playerLeft (all clients): a player disconnected
    - gameState (specific client): full public state sync, for reconnects (Availability NFR)
    - stayInRoom (client -> server): player moved by a suggestion chooses to stay and suggest
  Agree on names/payloads as a team, add them to the SRS, then add them here and in client.js.
"""

import json

# --- Client -> Server -------------------------------------------------------
JOIN_GAME = "joinGame"                    # {playerName}
SELECT_CHARACTER = "selectCharacter"      # {character}
START_GAME = "startGame"                  # {}
MOVE_REQUEST = "moveRequest"              # {destination}
MAKE_SUGGESTION = "makeSuggestion"        # {suspect, weapon}
DISPROVE_RESPONSE = "disproveResponse"    # {card}
MAKE_ACCUSATION = "makeAccusation"        # {suspect, weapon, room}
END_TURN = "endTurn"                      # {}
CHAT_MESSAGE = "chatMessage"              # {text}

# --- Server -> Specific Client ---------------------------------------------
DEALT_HAND = "dealtHand"                  # {cards}
YOUR_TURN = "yourTurn"                    # {validMoves}
REQUEST_DISPROVE = "requestDisprove"      # {suggestion, matchingCards}
CARD_SHOWN = "cardShown"                  # {card, shownBy}
ACCUSATION_RESULT = "accusationResult"    # {correct, caseFile}
INVALID_ACTION = "invalidAction"          # {reason}

# --- Server -> All Clients --------------------------------------------------
PLAYER_JOINED = "playerJoined"            # {playerName, character}
CHARACTER_SELECTED = "characterSelected"  # {playerName, character}
GAME_STARTED = "gameStarted"              # {turnOrder}
CHARACTER_MOVED = "characterMoved"        # {character, location}
SUGGESTION_MADE = "suggestionMade"        # {player, suspect, weapon, room}
SUGGESTION_DISPROVED = "suggestionDisproved"  # {disprovingPlayer}
CANNOT_DISPROVE = "cannotDisprove"        # {player}
ACCUSATION_MADE = "accusationMade"        # {player, suspect, weapon, room}
PLAYER_ELIMINATED = "playerEliminated"    # {player}
GAME_WON = "gameWon"                      # {player, caseFile}
TURN_CHANGED = "turnChanged"              # {player}
CHAT_BROADCAST = "chatBroadcast"          # {sender, text}


def encode(msg_type, **payload):
    return json.dumps({"type": msg_type, "payload": payload})


def decode(raw):
    """Return (type, payload). Raises ValueError on a malformed message."""
    msg = json.loads(raw)
    if not isinstance(msg, dict) or "type" not in msg:
        raise ValueError("message must be an object with a 'type' field")
    return msg["type"], msg.get("payload") or {}
