"""Stub handlers, one per client -> server message (SRS §2.4).

For the skeletal increment each handler only needs to log the message and send
back the SRS-defined responses with canned data -- no game rules yet. Real
logic (board, case file, turn order, rule checks) comes in the minimal increment.

Each handler gets:
    hub      -- the Hub from main.py: hub.send(conn, ...) / hub.broadcast(...)
    conn     -- the sender's connection; hub.players[conn] is their Player record
    payload  -- the decoded payload dict

Working examples: handle_join_game, handle_chat_message.
Everything marked TODO(server) is open for a team member to pick up.
"""

from protocol import *
import random


async def handle_join_game(hub, conn, payload):
    name = payload.get("playerName", "").strip()
    if not name:
        await hub.send(conn, INVALID_ACTION, reason="playerName is required")
        return
    hub.players[conn].name = name
    await hub.broadcast(PLAYER_JOINED, playerName=name, character=None)


async def handle_select_character(hub, conn, payload):
    # The 6 characters
    valid_characters = {
            "scarlet",
            "mustard",
            "white",
            "green",
            "peacock",
            "plum",
    }

    # Get requested character
    character = payload.get("character")

    # Validate selection exists
    if character not in valid_characters:
        await hub.send(conn, INVALID_ACTION, reason="Invalid character")
        return

    # Validate selection available
    for other_conn, player in hub.players.items():
        if other_conn != conn and player.character == character:
            await hub.send(conn, INVALID_ACTION, reason=f"{character} is already taken")
            return

    # Save character selection to hub.players[conn].character
    hub.players[conn].character = character

    # Broadcast message
    # PLAYER_JOINED (or characterSelected once that message is added to the SRS).
    await hub.broadcast(CHARACTER_SELECTED, playerName=hub.players[conn].name, character=character)


async def handle_start_game(hub, conn, payload):
    # TODO - Should block new players from joining the game at this point. Will also have to add code to unblock this if for some reason we don't start the game (like there aren't 6 players)
    # block_new_joins()

    # Get all connected players
    players = list(hub.players.values())

    # Ensure there's enough players. Maybe change if we add bots?
    player_count = len(players)
    if player_count != 6:
        await hub.send(conn, INVALID_ACTION, reason=f"There are {player_count} player(s), need exactly 6")
        return

    # Create random turn order
    random.shuffle(players)

    # Assign turn orders
    turnOrder = [] # This is the payload for broadcast message GAME_STARTED
    for turn_order, player in enumerate(players, start=1):
        player.turn_order = turn_order
        turnOrder.append(
            {
                "name": player.name,
                "character": player.character,
                "turn_order": turn_order
            }
        )

    # Send the turn order to all clients
    await hub.broadcast(conn, GAME_STARTED, turnOrder=turnOrder)


async def handle_move_request(hub, conn, payload):
    # TODO(server): broadcast CHARACTER_MOVED {character, location: destination}.
    await hub.send(conn, INVALID_ACTION, reason="moveRequest not implemented yet")


async def handle_make_suggestion(hub, conn, payload):
    # TODO(server): this is the most important demo flow:
    #   1. broadcast SUGGESTION_MADE {player, suspect, weapon, room}
    #   2. broadcast CHARACTER_MOVED for the suspect (moved into the room)
    #   3. send REQUEST_DISPROVE to the *next* player only {suggestion, matchingCards}
    #   Store the pending suggestion on the hub so handle_disprove_response can find
    #   the suggester. Also demo the CANNOT_DISPROVE path (e.g. if no other players).
    await hub.send(conn, INVALID_ACTION, reason="makeSuggestion not implemented yet")


async def handle_disprove_response(hub, conn, payload):
    # TODO(server): send CARD_SHOWN {card, shownBy} to the suggester ONLY, and
    #   broadcast SUGGESTION_DISPROVED {disprovingPlayer} (no card) to everyone.
    await hub.send(conn, INVALID_ACTION, reason="disproveResponse not implemented yet")


async def handle_make_accusation(hub, conn, payload):
    # TODO(server): broadcast ACCUSATION_MADE, send ACCUSATION_RESULT to the accuser,
    #   then broadcast PLAYER_ELIMINATED or GAME_WON (use a canned case file).
    await hub.send(conn, INVALID_ACTION, reason="makeAccusation not implemented yet")


async def handle_end_turn(hub, conn, payload):
    # TODO(server): broadcast TURN_CHANGED {player: next}, send YOUR_TURN to that player.
    await hub.send(conn, INVALID_ACTION, reason="endTurn not implemented yet")


async def handle_chat_message(hub, conn, payload):
    sender = hub.players[conn].name or "anonymous"
    await hub.broadcast(CHAT_BROADCAST, sender=sender, text=payload.get("text", ""))


HANDLERS = {
    JOIN_GAME: handle_join_game,
    SELECT_CHARACTER: handle_select_character,
    START_GAME: handle_start_game,
    MOVE_REQUEST: handle_move_request,
    MAKE_SUGGESTION: handle_make_suggestion,
    DISPROVE_RESPONSE: handle_disprove_response,
    MAKE_ACCUSATION: handle_make_accusation,
    END_TURN: handle_end_turn,
    CHAT_MESSAGE: handle_chat_message,
}
