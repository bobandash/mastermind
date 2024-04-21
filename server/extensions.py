from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")


# Generic socket connection
@socketio.on("connect")
def handle_connect():
    print("Client connected")
