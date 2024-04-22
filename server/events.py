from extensions import socketio
from flask_socketio import join_room, leave_room, emit
from models.models import WaitingRoom
from util.decorators import session_required
from flask import session
from sqlalchemy.exc import SQLAlchemyError
import logging
from util.json_errors import ErrorResponse
from flask import request


# All of the events inside the socket
# Generic socket connection
@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


# Handles all logic related to the waiting room
@socketio.on("waiting_room")
def handle_join_waiting_room(data):
    room = data.get("room")
    players = data.get("players")
    join_room(room)
    emit("user joined new room", players, room=room)


@socketio.on("change_game_settings")
def change_settings(data):
    room = data.get("room")
    settings = data.get("settings")
    emit("game_settings", settings, room=room)


@socketio.on("create_multiplayer_game")
def create_game(data):
    game_id, round_id, room = (
        data.get("game_id"),
        data.get("round_id"),
        data.get("room"),
    )
    emit("join_multiplayer_game", {"game_id": game_id, "round_id": round_id}, room=room)


# Handles all logic related to the multiplayer feature
@socketio.on("join_multiplayer_round")
def handle_join_new_multiplayer_round(data):
    room = data.get("room")
    join_room(room)
    emit("new_round", room=room)


@socketio.on("add_secret_code")
def add_secret_code(data):
    status, room = data.get("status"), data.get("room")
    print(status)
    emit("start_round", {"status": status}, room=room)


@socketio.on("make_move")
def make_move(data):
    round_info, room = data.get("round_info"), data.get("room")
    emit("new_move_info", {"round_info": round_info}, room=room)


@socketio.on("create_new_round")
def create_new_round(data):
    game_id, round_id, room = (
        data.get("game_id"),
        data.get("round_id"),
        data.get("room"),
    )
    emit("new_round_info", {"game_id": game_id, "round_id": round_id}, room=room)
    leave_room(room)
