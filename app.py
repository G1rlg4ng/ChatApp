from flask import Flask, request, render_template,redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, send
from utils import generate_room_code

app = Flask(__name__)
app.config["SECRET_KEY"] = "mypassword" # For securely signing session cookies
socketio = SocketIO(app) # Allows you to use WebSocket functionality in the Flask application.

# A mock database to persist data
rooms = {}

# Build routes
@app.route('/', methods=["GET", "POST"])
def home():
    session.clear # Clears user session
    
    if request.method == "POST":
        name = request.form.get('name')
        create = request.form.get('create', False)
        code = request.form.get('code')
        join = request.form.get('join', False)
        
        if not name:
            return render_template('index.html', error="Name is required", code=code)
        
        if create != False:
            room_code = generate_room_code(6, list(rooms.keys()))
            new_room = {
                'members' : 0,
                'messages' : []
            }
            rooms[room_code] = new_room
        
        if join != False:
            # no code
            if not code:
                return render_template('index.html', error="Please enter a room code to enter the chat room", name=name)
            #invalid code
            if code not in rooms:
                return render_template('index.html', error="Invalid room code, please check and try again", name=name)
            
            room_code = code
        session['room'] = room_code
        session['name'] = name
        return redirect(url_for('room'))
    else:
        return render_template('index.html')

@app.route('/room')
def room():
    room = session.get('room')
    name = session.get('name')
    
    if name is None or room is None or room not in rooms:
        return redirect(url_for('home'))
    
    messages = rooms[room]['messages']
    return render_template('room.html', room = room, user = name, messages = messages)
            
# Build the SocketIO event handlers
@socketio.on('connect') # Event handler for the connect event   
def handle_connect():
    name = session.get('name')
    room = session.get('room')
    
    if name is None or room is None:
        return
    if room not in rooms:
        leave_room(room)
        
    join_room(room)
    send({
        "sender": "",
        "message":f"{name} has entered the chat"
    }, to=room)
    rooms[room]["members"] += 1
    
@socketio.on('message')
def handle_message(payload):
    room = session.get('room')
    name = session.get('name')
    
    if room not in rooms:
        return
    
    message = {
        "sender": name,
        "message": payload["message"]
    }
    send(message, to=room)
    rooms[room]["messages"].append(message)
    
@socketio.on('disconnect')
def handle_disconect():
    room = session.get('room')
    name = session.get('name')
    
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
            
    send({
        "message": f"{name} has left the room",
        "sender": ""
    }, to=room)
    
if __name__ == "__main__":
    socketio.run(app, debug=True) # Run Flask App with SocketIO support