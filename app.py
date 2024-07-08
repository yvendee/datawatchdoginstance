from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime

app = Flask("datawatchdog")

# MySQL connection setup
try:
    db_connection = mysql.connector.connect(
        host="ow7.h.filess.io",
        user="datawatch_yardspider",
        password="b6a53437c6f7b9e93dfa46f61db473213f4d8e3a",
        database="datawatch_yardspider",
        port=3307
    )
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL: {e}")
    db_connection = None

def get_cursor():
    if db_connection:
        return db_connection.cursor()
    else:
        return None

def is_mysql_available():
    return db_connection is not None

# Route to handle MySQL errors
def handle_mysql_error(e):
    print(f"MySQL Error: {e}")
    return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

@app.route('/createdb', methods=['GET'])
def create_datawatch_table():
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            # Check if table 'datawatch' exists
            cursor.execute("SHOW TABLES LIKE 'datawatch'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.close()
                return jsonify({"message": "Table 'datawatch' already exists"}), 200
            else:
                # Define SQL query to create table if it doesn't exist
                sql_create_table = """
                CREATE TABLE datawatch (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    field TEXT,
                    value TEXT
                )
                """
                cursor.execute(sql_create_table)
                db_connection.commit()
                cursor.close()
                return jsonify({"message": "Table 'datawatch' created successfully"}), 200
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

# Initial list of fields
field_db = [
    ["lifesaverPC_status", "idle"],
    ["lifesaverPC_timestamp", "idle"],
    ["AsusPC_status", "idle"],
    ["AsusPC_timestamp", "idle"],
    ["AtomPC_status", "idle"],
    ["AtomPC_timestamp", "idle"],
    ["lifesaverPC_state", "idle"],
    ["lifesaverPC_last", "idle"],
    ["AsusPC_state", "idle"],
    ["AsusPC_last", "idle"],
    ["AtomPC_state", "idle"],
    ["AtomPC_last", "idle"],
    ["lifesaverPC_url", "idle"],
    ["AsusPC_url", "idle"],
    ["AtomPC_url", "idle"]
]

@app.route('/insertdata', methods=['GET'])
def insert_data():
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            for field in field_db:
                name = field[0]
                value = field[1]
                
                # Check if the field already exists
                sql_select = "SELECT * FROM datawatch WHERE field = %s"
                cursor.execute(sql_select, (name,))
                existing_field = cursor.fetchone()
                
                if not existing_field:
                    # Insert new field if it doesn't exist
                    sql_insert = "INSERT INTO datawatch (field, value) VALUES (%s, %s)"
                    cursor.execute(sql_insert, (name, value))
            
            db_connection.commit()
            cursor.close()
            return jsonify({"message": "Data inserted successfully"}), 200
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/field', methods=['GET'])
def get_fields():
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            cursor.execute("SELECT * FROM datawatch")
            fields = cursor.fetchall()
            cursor.close()
            return jsonify(fields)
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/field', methods=['POST'])
def add_field():
    data = request.json
    if not data or 'field' not in data or 'value' not in data:
        return jsonify({"error": "Field and value are required"}), 400

    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            sql_insert = "INSERT INTO datawatch (field, value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE value = %s"
            cursor.execute(sql_insert, (data['field'], data['value'], data['value']))
            db_connection.commit()
            cursor.close()
            return jsonify({"message": "Field added or updated successfully"}), 201
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/field/<name>', methods=['GET'])
def get_field_by_name(name):
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            sql_select = "SELECT * FROM datawatch WHERE field = %s"
            cursor.execute(sql_select, (name,))
            field = cursor.fetchone()
            cursor.close()
            if field:
                return jsonify(field)
            else:
                return jsonify({"error": "Field not found"}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/field/<name>', methods=['PUT'])
def update_field_by_name(name):
    data = request.json
    if not data or 'value' not in data:
        return jsonify({"error": "Value field is required"}), 400

    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            sql_update = "UPDATE datawatch SET value = %s WHERE field = %s"
            cursor.execute(sql_update, (data['value'], name))
            db_connection.commit()
            cursor.close()
            
            return jsonify({"message": "Field updated successfully"}), 200
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/field/<name>', methods=['DELETE'])
def delete_field_by_name(name):
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            sql_delete = "DELETE FROM datawatch WHERE field = %s"
            cursor.execute(sql_delete, (name,))
            db_connection.commit()
            cursor.close()
            return jsonify({"message": "Field deleted successfully"}), 200
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/field/value/<name>', methods=['GET'])
def get_fieldvalue_by_name(name):
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            sql_select = "SELECT value FROM datawatch WHERE field = %s"
            cursor.execute(sql_select, (name,))
            field_value = cursor.fetchone()
            
            if field_value:
                return jsonify({"value": field_value[0]})
            else:
                return jsonify({"error": "Field not found"}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/', methods=['GET'])
def index():
    if is_mysql_available():
        return jsonify({"message": "Welcome to the dataWatchdog API"})
    else:
        return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

if __name__ == '__main__':
    app.run(debug=True)
