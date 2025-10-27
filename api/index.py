#!/usr/bin/env python3
"""
Neo Recovery Backend Server (Vercel Serverless Function)
Connects securely to Google Sheets API using a Service Account.
"""
import json
import os
import calendar
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify
from flask_cors import CORS

from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# --- Google Sheets API Service ---
def get_sheets_service():
    """Authenticates and returns a Google Sheets API service object."""
    # Try environment variable first, then fall back to credentials file
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')

    if not spreadsheet_id:
        raise ValueError("Missing SPREADSHEET_ID environment variable")

    try:
        if creds_json_str:
            # Use environment variable
            creds_info = json.loads(creds_json_str)
            creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        else:
            # Use credentials file
            creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
            creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets(), spreadsheet_id
    except json.JSONDecodeError:
        raise ValueError("Failed to decode GOOGLE_CREDENTIALS_JSON")
    except Exception as e:
        # Re-raise other exceptions for better error visibility in Vercel logs
        raise e

# --- Error Handling ---
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle generic exceptions."""
    # Pass through HTTP exceptions
    if hasattr(e, 'code'):
        return jsonify(error=str(e)), e.code
    
    # Log the full error for debugging in Vercel
    app.logger.error(f"Internal Server Error: {e}")

    # For other exceptions, return a 500
    return jsonify(error="An internal server error occurred.", details=str(e)), 500

# --- API Logic (functions like get_employees, mark_attendance, etc. remain the same) ---
def get_employees(service, spreadsheet_id):
    """Fetches active employees from the 'Employees' sheet."""
    try:
        result = service.values().get(
            spreadsheetId=spreadsheet_id,
            range='Employees!A:C'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return []

        header = values[0]
        data_rows = values[1:]

        id_idx = header.index('id')
        name_idx = header.index('name')
        active_idx = header.index('active')

        employees = []
        for row in data_rows:
            if len(row) > active_idx and str(row[active_idx]).upper() == 'TRUE':
                if len(row) > id_idx and len(row) > name_idx:
                    employees.append({
                        "id": int(row[id_idx]),
                        "name": row[name_idx]
                    })
        return employees
    except Exception as e:
        app.logger.error(f"Error in get_employees: {e}")
        return {"error": "Failed to retrieve employee data from sheet.", "details": str(e)}

def get_employee_by_id(service, spreadsheet_id, employee_id):
    """Fetches a single active employee by ID."""
    employees = get_employees(service, spreadsheet_id)
    if isinstance(employees, dict) and "error" in employees:
        return None
    for emp in employees:
        if emp['id'] == employee_id:
            return emp
    return None

def mark_attendance(service, spreadsheet_id, employee_id, latitude=None, longitude=None, device_id=None, testing_mode=False):
    """Marks attendance for an employee by appending a row to the 'Attendance' sheet."""
    try:
        # 1. Validate employee
        employee = get_employee_by_id(service, spreadsheet_id, int(employee_id))
        if not employee:
            return {"ok": False, "error": "Employee not found or inactive"}

        # 2. Validate location if provided and not in testing mode
        if latitude is not None and longitude is not None and not testing_mode:
            location_validation = validate_location(latitude, longitude)
            if not location_validation["ok"]:
                return {"ok": False, "error": location_validation["error"]}
        elif testing_mode:
            app.logger.info(f"🧪 TESTING MODE: Location validation bypassed for employee {employee_id}")

        # 3. Check device session if device_id provided
        if device_id:
            tz = ZoneInfo("Asia/Kolkata")
            now = datetime.now(tz)
            date_iso = now.strftime('%Y-%m-%d')
            
            session_check = check_device_session(service, spreadsheet_id, device_id, date_iso)
            if not session_check["ok"]:
                return {"ok": False, "error": "Failed to check device session"}
            if session_check["exists"]:
                return {"ok": False, "error": "This device has already marked attendance today"}

        # 4. Get current date and time in IST
        tz = ZoneInfo("Asia/Kolkata")
        now = datetime.now(tz)
        date_iso = now.strftime('%Y-%m-%d')
        time_hhmm = now.strftime('%H:%M')

        # 5. Check for duplicates (employee-based)
        result = service.values().get(
            spreadsheetId=spreadsheet_id,
            range='Attendance!A:B'
        ).execute()
        rows = result.get('values', [])
        
        is_already_marked = False
        for row in rows[1:]:
            if len(row) >= 2 and row[0] == date_iso and row[1] == str(employee_id):
                is_already_marked = True
                break
        
        if is_already_marked:
            return {"ok": True, "message": "already marked"}

        # 6. Append new attendance record
        new_row = [date_iso, employee_id, employee['name'], time_hhmm, 'reception']
        service.values().append(
            spreadsheetId=spreadsheet_id,
            range='Attendance!A1',
            valueInputOption='USER_ENTERED',
            body={'values': [new_row]}
        ).execute()

        # 7. Save device session if device_id provided
        if device_id:
            save_device_session(service, spreadsheet_id, device_id, date_iso, employee_id)

        return {"ok": True, "marked_at": time_hhmm, "date": date_iso}

    except Exception as e:
        app.logger.error(f"Error in mark_attendance: {e}")
        return {"ok": False, "error": "Failed to mark attendance.", "details": str(e)}

def add_employee(service, spreadsheet_id, name):
    """Adds a new employee to the 'Employees' sheet."""
    try:
        if not name or not name.strip():
            return {"ok": False, "error": "Employee name cannot be empty"}

        result = service.values().get(spreadsheetId=spreadsheet_id, range='Employees!A:A').execute()
        values = result.get('values', [])
        ids = [int(row[0]) for row in values[1:] if row and row[0].isdigit()]
        next_id = max(ids) + 1 if ids else 1

        new_row = [next_id, name.strip(), True]
        service.values().append(
            spreadsheetId=spreadsheet_id,
            range='Employees!A1',
            valueInputOption='USER_ENTERED',
            body={'values': [new_row]}
        ).execute()
        
        return {"ok": True, "employee": {"id": next_id, "name": name.strip()}}
    except Exception as e:
        app.logger.error(f"Error in add_employee: {e}")
        return {"ok": False, "error": "Failed to add employee.", "details": str(e)}

def update_employee(service, spreadsheet_id, employee_id, data):
    """Updates an employee's name or active status."""
    try:
        result = service.values().get(spreadsheetId=spreadsheet_id, range='Employees!A:A').execute()
        rows = result.get('values', [])
        
        for i, row in enumerate(rows):
            if row and row[0] == str(employee_id):
                row_index = i + 1
                if 'name' in data:
                    service.values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'Employees!B{row_index}',
                        valueInputOption='USER_ENTERED',
                        body={'values': [[data['name']]]}
                    ).execute()
                if 'active' in data:
                     service.values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'Employees!C{row_index}',
                        valueInputOption='USER_ENTERED',
                        body={'values': [[data['active']]]}
                    ).execute()
                return {"ok": True}
                
        return {"ok": False, "error": "Employee not found"}
    except Exception as e:
        app.logger.error(f"Error in update_employee: {e}")
        return {"ok": False, "error": "Failed to update employee.", "details": str(e)}

def delete_employee(service, spreadsheet_id, employee_id):
    """Soft deletes an employee by setting their status to FALSE."""
    return update_employee(service, spreadsheet_id, employee_id, {"active": False})

def get_attendance_matrix(service, spreadsheet_id, month):
    """Gets the monthly attendance data."""
    try:
        employees = get_employees(service, spreadsheet_id)
        if isinstance(employees, dict) and "error" in employees:
            return employees # Propagate error
        emp_map = {emp['id']: emp['name'] for emp in employees}
        
        result = service.values().get(spreadsheetId=spreadsheet_id, range='Attendance!A:D').execute()
        rows = result.get('values', [])
        
        attendance_data = {}
        for row in rows[1:]:
            if len(row) >= 4 and row[0] and row[0].startswith(month):
                date_str, emp_id, _, time = row
                day = int(date_str.split('-')[2])
                attendance_data[f"{emp_id}|{day}"] = time

        year, month_num = map(int, month.split('-'))
        days_in_month = calendar.monthrange(year, month_num)[1]
        
        matrix_rows = []
        for emp_id, name in emp_map.items():
            row_data = {"id": emp_id, "name": name}
            for d in range(1, days_in_month + 1):
                row_data[str(d)] = attendance_data.get(f"{emp_id}|{d}", "")
            matrix_rows.append(row_data)
            
        return {"ok": True, "daysInMonth": days_in_month, "rows": matrix_rows}
    except Exception as e:
        app.logger.error(f"Error in get_attendance_matrix: {e}")
        return {"ok": False, "error": "Failed to get attendance matrix.", "details": str(e)}

def get_todays_attendance(service, spreadsheet_id):
    """Counts the number of attendance entries for the current day."""
    try:
        # Get current date in IST
        tz = ZoneInfo("Asia/Kolkata")
        now = datetime.now(tz)
        date_iso = now.strftime('%Y-%m-%d')
        
        result = service.values().get(
            spreadsheetId=spreadsheet_id,
            range='Attendance!A:A'
        ).execute()
        rows = result.get('values', [])
        
        count = 0
        if rows and len(rows) > 1:
            for row in rows[1:]:
                if row and row[0] == date_iso:
                    count += 1
        
        return {"ok": True, "count": count}
    except Exception as e:
        app.logger.error(f"Error in get_todays_attendance: {e}")
        return {"ok": False, "error": "Failed to get today's attendance count.", "details": str(e)}

def check_device_session(service, spreadsheet_id, device_id, date):
    """Check if device has already submitted attendance for the given date."""
    try:
        # Try to get the AttendanceSessions sheet
        try:
            result = service.values().get(
                spreadsheetId=spreadsheet_id,
                range='AttendanceSessions!A:C'
            ).execute()
            rows = result.get('values', [])
        except:
            # If sheet doesn't exist, create it
            create_sessions_sheet(service, spreadsheet_id)
            return {"ok": True, "exists": False}
        
        if not rows or len(rows) < 2:
            return {"ok": True, "exists": False}
        
        # Check if device_id + date combination exists
        for row in rows[1:]:
            if len(row) >= 2 and row[0] == device_id and row[1] == date:
                return {"ok": True, "exists": True}
        
        return {"ok": True, "exists": False}
    except Exception as e:
        app.logger.error(f"Error in check_device_session: {e}")
        return {"ok": False, "error": "Failed to check device session.", "details": str(e)}

def save_device_session(service, spreadsheet_id, device_id, date, employee_id):
    """Save device session to prevent duplicate submissions."""
    try:
        # Try to get the AttendanceSessions sheet
        try:
            service.values().get(
                spreadsheetId=spreadsheet_id,
                range='AttendanceSessions!A1'
            ).execute()
        except:
            # If sheet doesn't exist, create it
            create_sessions_sheet(service, spreadsheet_id)
        
        # Append new session record
        tz = ZoneInfo("Asia/Kolkata")
        now = datetime.now(tz)
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        new_row = [device_id, date, employee_id, timestamp]
        service.values().append(
            spreadsheetId=spreadsheet_id,
            range='AttendanceSessions!A1',
            valueInputOption='USER_ENTERED',
            body={'values': [new_row]}
        ).execute()
        
        return {"ok": True}
    except Exception as e:
        app.logger.error(f"Error in save_device_session: {e}")
        return {"ok": False, "error": "Failed to save device session.", "details": str(e)}

def create_sessions_sheet(service, spreadsheet_id):
    """Create the AttendanceSessions sheet with proper headers."""
    try:
        # Create the sheet
        sheet_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': 'AttendanceSessions'
                    }
                }
            }]
        }
        service.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=sheet_body
        ).execute()
        
        # Add headers
        headers = [['device_id', 'date', 'employee_id', 'timestamp']]
        service.values().update(
            spreadsheetId=spreadsheet_id,
            range='AttendanceSessions!A1',
            valueInputOption='USER_ENTERED',
            body={'values': headers}
        ).execute()
        
        return True
    except Exception as e:
        app.logger.error(f"Error creating sessions sheet: {e}")
        return False

def validate_location(latitude, longitude):
    """Validate if the provided coordinates are within allowed office locations."""
    try:
        # Office locations (same as frontend)
        allowed_locations = [
            {"lat": 12.9716, "lon": 77.5946, "radius": 50},
            {"lat": 12.9784, "lon": 77.6008, "radius": 50},
            {"lat": 28.66925, "lon": 77.1107778, "radius": 50}
        ]
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate distance between two points in meters."""
            R = 6371000  # Earth's radius in meters
            d_lat = (lat2 - lat1) * 3.14159265359 / 180
            d_lon = (lon2 - lon1) * 3.14159265359 / 180
            a = (0.5 - 0.5 * (d_lat / 2)) + 0.5 * (lat1 * 3.14159265359 / 180) * 0.5 * (lat2 * 3.14159265359 / 180) * (1 - 0.5 * (d_lon / 2))
            c = 2 * 0.78539816339 * (a ** 0.5)
            return R * c
        
        for location in allowed_locations:
            distance = haversine_distance(latitude, longitude, location["lat"], location["lon"])
            if distance <= location["radius"]:
                return {"ok": True, "distance": round(distance)}
        
        return {"ok": False, "error": "Location is outside allowed office area"}
    except Exception as e:
        app.logger.error(f"Error in validate_location: {e}")
        return {"ok": False, "error": "Location validation failed", "details": str(e)}

# --- Flask Routes ---
@app.route("/api/employees", methods=['GET', 'POST'])
def handle_employees():
    service, spreadsheet_id = get_sheets_service()
    if request.method == 'GET':
        data = get_employees(service, spreadsheet_id)
        return jsonify(data)
    elif request.method == 'POST':
        body = request.get_json()
        data = add_employee(service, spreadsheet_id, body.get('name'))
        status = 400 if 'error' in data else 201
        return jsonify(data), status

@app.route("/api/employees/<int:employee_id>", methods=['PUT', 'DELETE'])
def handle_employee(employee_id):
    service, spreadsheet_id = get_sheets_service()
    if request.method == 'PUT':
        body = request.get_json()
        data = update_employee(service, spreadsheet_id, employee_id, body)
        status = 404 if 'error' in data else 200
        return jsonify(data), status
    elif request.method == 'DELETE':
        data = delete_employee(service, spreadsheet_id, employee_id)
        status = 404 if 'error' in data else 200
        return jsonify(data), status

@app.route("/api/attendance", methods=['POST'])
def handle_attendance_post():
    service, spreadsheet_id = get_sheets_service()
    body = request.get_json()
    emp_id = body.get('employee_id')
    latitude = body.get('latitude')
    longitude = body.get('longitude')
    device_id = body.get('device_id')
    testing_mode = body.get('testing_mode', False)
    
    if not emp_id:
        return jsonify({"ok": False, "error": "employee_id is required"}), 400
    
    data = mark_attendance(service, spreadsheet_id, emp_id, latitude, longitude, device_id, testing_mode)
    status = 404 if 'error' in data and data.get("error") != "already marked" else 200
    return jsonify(data), status

@app.route("/api/attendance", methods=['GET'])
def handle_attendance_get():
    service, spreadsheet_id = get_sheets_service()
    month = request.args.get('month')
    if not month:
        return jsonify({"ok": False, "error": "month parameter is required"}), 400
    data = get_attendance_matrix(service, spreadsheet_id, month)
    status = 500 if 'error' in data else 200
    return jsonify(data), status

@app.route("/api/attendance/today", methods=['GET'])
def handle_attendance_today():
    service, spreadsheet_id = get_sheets_service()
    data = get_todays_attendance(service, spreadsheet_id)
    status = 500 if 'error' in data else 200
    return jsonify(data), status

@app.route("/api/attendance/session", methods=['GET', 'POST'])
def handle_attendance_session():
    service, spreadsheet_id = get_sheets_service()
    
    if request.method == 'GET':
        device_id = request.args.get('device_id')
        date = request.args.get('date')
        
        if not device_id or not date:
            return jsonify({"ok": False, "error": "device_id and date are required"}), 400
        
        data = check_device_session(service, spreadsheet_id, device_id, date)
        status = 500 if 'error' in data else 200
        return jsonify(data), status
    
    elif request.method == 'POST':
        body = request.get_json()
        device_id = body.get('device_id')
        date = body.get('date')
        employee_id = body.get('employee_id')
        
        if not device_id or not date or not employee_id:
            return jsonify({"ok": False, "error": "device_id, date, and employee_id are required"}), 400
        
        data = save_device_session(service, spreadsheet_id, device_id, date, employee_id)
        status = 500 if 'error' in data else 200
        return jsonify(data), status

if __name__ == '__main__':
    app.run(debug=True)
