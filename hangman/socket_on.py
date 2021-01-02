from . import socketio

count = 0

@socketio.on('connect')
def handle_connect():
    global count
    count += 1
    print(count, " connected")


@socketio.on('disconnect')
def handle_disconnect():
    global count
    count -= 1
    print(count, " connected")
