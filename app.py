from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime

app = Flask("datawatchdog")
CORS(app)

field_db = [
    [1, "lifesaverPC_status", "idle"],
    [2, "lifesaverPC_timestamp", "idle"],
    [3, "AsusPC_status", "idle"],
    [4, "AsusPC_timestamp", "idle"],
    [5, "AtomPC_status", "idle"],
    [6, "AtomPC_timestamp", "idle"],
    [7, "lifesaverPC_state", "idle"],
    [7, "lifesaverPC_last", "idle"],
    [8, "AsusPC_state", "idle"],
    [8, "AsusPC_last", "idle"],
    [9, "AtomPC_state", "idle"],
    [9, "AtomPC_last", "idle"],
    [10, "lifesaverPC_url", "idle"],
    [11, "AsusPC_url", "idle"],
    [12, "AtomPC_url", "idle"]
]

def get_next_field_id():
    return len(field_db) + 1

@app.route('/field', methods=['GET'])
def get_field():
    return jsonify(field_db)

@app.route('/field', methods=['POST'])
def add_user():
    data = {
        'name': request.json.get('name', ''),
        'value': request.json.get('value', '')
    }
    
    if not data['name'] or not data['value']:
        return jsonify({"error": "Name and value are required"}), 400
    
    for user in field_db:
        if user[1].lower() == data['name'].lower():
            return jsonify({"error": "Name already exists"}), 400
    
    user_id = get_next_field_id()
    new_field = [user_id, data['name'], data['value']]
    field_db.append(new_field)
    
    return jsonify({"message": "User added successfully", "field": new_field}), 201

@app.route('/field/<name>', methods=['GET'])
def get_field_by_name(name):
    for user in field_db:
        if user[1].lower() == name.lower():
            return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/field/value/<name>', methods=['GET'])
def get_fieldvalue_by_name(name):
    for user in field_db:
        if user[1].lower() == name.lower():
            return user[2]
    return jsonify({"error": "User not found"}), 404

@app.route('/field/<name>', methods=['PUT'])
def update_field_by_name(name):
    data = request.json
    if 'value' not in data:
        return jsonify({"error": "value field is required"}), 400
    
    for user in field_db:
        if user[1].lower() == name.lower():
            user[2] = data['value']
            if name.endswith('_status'):
                # Update corresponding timestamp field
                timestamp_name = f"{name.split('_status')[0]}_timestamp"
                current_time = datetime.now().strftime("%Y/%m/%d-%H/%M/%S")
                for item in field_db:
                    if item[1] == timestamp_name:
                        item[2] = current_time
                        break
            if name.endswith('_state'):
                # Update corresponding timestamp field
                timestamp_name = f"{name.split('_state')[0]}_last"
                current_time = datetime.now().strftime("%Y/%m/%d-%H/%M/%S")
                for item in field_db:
                    if item[1] == timestamp_name:
                        item[2] = current_time
                        break
            return jsonify({"message": "value updated successfully", "field": user})
    
    return jsonify({"error": "User not found"}), 404

@app.route('/field/<name>', methods=['DELETE'])
def delete_field_by_name(name):
    for user in field_db:
        if user[1].lower() == name.lower():
            field_db.remove(user)
            return jsonify({"message": "User deleted successfully"})
    
    return jsonify({"error": "User not found"}), 404

@app.route('/field/download', methods=['GET'])
def download_field():
    text_content = "\n".join([f"{user[0]}, {user[1]}, {user[2]}" for user in field_db])
    response = Response(text_content, mimetype='text/plain')
    response.headers["Content-Disposition"] = "attachment; filename=field.txt"
    
    return response

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the dataWatchdog API"})

if __name__ == '__main__':
    app.run(debug=True)
