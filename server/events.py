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
    emit("user_joined", players, room=room)


@socketio.on("init_game_settings")
def init_game_settings(data):
    room = data.get("room")
    settings = data.get("settings")
    emit("game_settings", settings, room=room)


@socketio.on("change_game_settings")
def change_settings(data):
    room = data.get("room")
    settings = data.get("settings")
    emit("game_settings", settings, room=room)
