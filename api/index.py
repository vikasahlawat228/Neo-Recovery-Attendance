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

        # 2. Validate location if provided
        if latitude is not None and longitude is not None:
            location_validation = validate_location(latitude, longitude)
            if not location_validation["ok"]:
                return {"ok": False, "error": location_validation["error"]}

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

def mark_logout(service, spreadsheet_id, employee_id, latitude=None, longitude=None, device_id=None, testing_mode=False):
    """Marks logout for an employee by updating the departure_time in the 'Attendance' sheet."""
    try:
        # 1. Validate employee
        employee = get_employee_by_id(service, spreadsheet_id, int(employee_id))
        if not employee:
            return {"ok": False, "error": "Employee not found or inactive. Please contact HR to verify your employee status."}

        # 2. Validate location if provided
        if latitude is not None and longitude is not None:
            location_validation = validate_location(latitude, longitude)
            if not location_validation["ok"]:
                return {"ok": False, "error": location_validation["error"]}

        # 3. Get current date and time in IST
        tz = ZoneInfo("Asia/Kolkata")
        now = datetime.now(tz)
        date_iso = now.strftime('%Y-%m-%d')
        time_hhmm = now.strftime('%H:%M')

        # 4. Check if employee has marked attendance today
        result = service.values().get(
            spreadsheetId=spreadsheet_id,
            range='Attendance!A:F'
        ).execute()
        rows = result.get('values', [])
        
        # Find the attendance record for today
        attendance_row_index = None
        for i, row in enumerate(rows[1:], start=2):  # Skip header, start from row 2
            if len(row) >= 2 and row[0] == date_iso and row[1] == str(employee_id):
                attendance_row_index = i
                break
        
        if not attendance_row_index:
            return {"ok": False, "error": "You haven't logged in today. Please mark your attendance first before logging out."}
        
        # 5. Check if already logged out
        attendance_row = rows[attendance_row_index - 1]  # Convert to 0-based index
        if len(attendance_row) >= 6 and attendance_row[5]:  # logout_time column exists and has value
            return {"ok": False, "error": "You have already logged out today. No action needed."}

        # 6. Check device session if device_id provided - ensure same user who logged in is logging out
        if device_id:
            app.logger.info(f"Checking device session for device {device_id}, employee {employee_id}, date {date_iso}")
            session_check = check_device_session_for_employee(service, spreadsheet_id, device_id, date_iso, employee_id)
            app.logger.info(f"Device session check result: {session_check}")
            if not session_check["ok"]:
                # If session check fails, log it but don't block logout - the main check is if employee logged in today
                app.logger.warning(f"Device session check failed for device {device_id}, employee {employee_id}: {session_check.get('error', 'Unknown error')}")
            elif session_check["exists"] and session_check["employee_id"] != int(employee_id):
                # Get the name of the employee who is actually logged in
                logged_in_employee = get_employee_by_id(service, spreadsheet_id, session_check["employee_id"])
                logged_in_name = logged_in_employee["name"] if logged_in_employee else f"employee #{session_check['employee_id']}"
                
                # Get the name of the employee trying to logout
                current_employee = get_employee_by_id(service, spreadsheet_id, int(employee_id))
                current_name = current_employee["name"] if current_employee else f"employee #{employee_id}"
                
                error_msg = f"You are logged in as {logged_in_name} today and can only logout for {logged_in_name} today!"
                app.logger.info(f"Blocking logout: {error_msg}")
                return {"ok": False, "error": error_msg}

        # 7. Update the logout_time in the attendance record
        # First, ensure the row has enough columns
        while len(attendance_row) < 6:
            attendance_row.append('')
        
        attendance_row[5] = time_hhmm  # Set logout_time
        
        # Update the specific row
        service.values().update(
            spreadsheetId=spreadsheet_id,
            range=f'Attendance!A{attendance_row_index}:F{attendance_row_index}',
            valueInputOption='USER_ENTERED',
            body={'values': [attendance_row]}
        ).execute()

        return {"ok": True, "logged_out_at": time_hhmm, "date": date_iso}

    except Exception as e:
        app.logger.error(f"Error in mark_logout: {e}")
        return {"ok": False, "error": "System error occurred while marking logout. Please try again in a few moments. If the problem persists, contact IT support.", "details": str(e)}

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
    """Gets the monthly attendance data with login and logout times."""
    try:
        employees = get_employees(service, spreadsheet_id)
        if isinstance(employees, dict) and "error" in employees:
            return employees # Propagate error
        emp_map = {emp['id']: emp['name'] for emp in employees}
        
        # Read all columns including logout_time (column F)
        result = service.values().get(spreadsheetId=spreadsheet_id, range='Attendance!A:F').execute()
        rows = result.get('values', [])
        
        attendance_data = {}
        for row in rows[1:]:
            if len(row) >= 4 and row[0] and row[0].startswith(month):
                date_str = row[0]
                emp_id = row[1]
                arrival_time = row[3]  # arrival_time is in column D (index 3)
                logout_time = row[5] if len(row) > 5 else ''  # logout_time is in column F (index 5)
                day = int(date_str.split('-')[2])
                
                # Format: "HH:MM - HH:MM" or just "HH:MM" if no logout
                if logout_time and logout_time.strip():
                    time_display = f"{arrival_time} - {logout_time}"
                else:
                    time_display = arrival_time
                
                attendance_data[f"{emp_id}|{day}"] = time_display

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

def get_attendance_week(service, spreadsheet_id, week_start_date):
    """Gets the weekly attendance data with login and logout times."""
    try:
        employees = get_employees(service, spreadsheet_id)
        if isinstance(employees, dict) and "error" in employees:
            return employees # Propagate error
        emp_map = {emp['id']: emp['name'] for emp in employees}
        
        # Calculate week end date (6 days after start)
        from datetime import datetime, timedelta
        start_date = datetime.strptime(week_start_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=6)
        
        # Read all columns including logout_time (column F)
        result = service.values().get(spreadsheetId=spreadsheet_id, range='Attendance!A:F').execute()
        rows = result.get('values', [])
        
        attendance_data = {}
        week_dates = []
        current_date = start_date
        for i in range(7):  # 7 days in a week
            week_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        for row in rows[1:]:
            if len(row) >= 4 and row[0] in week_dates:
                date_str = row[0]
                emp_id = row[1]
                arrival_time = row[3]  # arrival_time is in column D (index 3)
                logout_time = row[5] if len(row) > 5 else ''  # logout_time is in column F (index 5)
                
                # Find which day of the week this is (0-6)
                day_index = week_dates.index(date_str)
                
                # Format: "HH:MM - HH:MM" or just "HH:MM" if no logout
                if logout_time and logout_time.strip():
                    time_display = f"{arrival_time} - {logout_time}"
                else:
                    time_display = arrival_time
                
                attendance_data[f"{emp_id}|{day_index}"] = time_display

        matrix_rows = []
        for emp_id, name in emp_map.items():
            row_data = {"id": emp_id, "name": name}
            for day_index in range(7):
                row_data[str(day_index)] = attendance_data.get(f"{emp_id}|{day_index}", "")
            matrix_rows.append(row_data)
            
        return {"ok": True, "weekDates": week_dates, "rows": matrix_rows}
    except Exception as e:
        app.logger.error(f"Error in get_attendance_week: {e}")
        return {"ok": False, "error": "Failed to get weekly attendance data.", "details": str(e)}

def get_attendance_day(service, spreadsheet_id, date):
    """Gets the daily attendance data with login and logout times - using same logic as week view."""
    try:
        employees = get_employees(service, spreadsheet_id)
        if isinstance(employees, dict) and "error" in employees:
            return employees # Propagate error
        emp_map = {emp['id']: emp['name'] for emp in employees}
        
        # Read all columns including logout_time (column F) - same as week view
        result = service.values().get(spreadsheetId=spreadsheet_id, range='Attendance!A:F').execute()
        rows = result.get('values', [])
        
        attendance_data = {}
        
        # Process attendance data - same logic as week view
        for row in rows[1:]:
            if len(row) >= 4 and row[0] == date:  # Only match the specific date
                emp_id = row[1]
                arrival_time = row[3]  # arrival_time is in column D (index 3)
                logout_time = row[5] if len(row) > 5 else ''  # logout_time is in column F (index 5)
                
                # Format: "HH:MM - HH:MM" or just "HH:MM" if no logout - same as week view
                if logout_time and logout_time.strip():
                    time_display = f"{arrival_time} - {logout_time}"
                else:
                    time_display = arrival_time
                
                # Normalize key to string to match week/month matrix behavior
                attendance_data[str(emp_id)] = time_display

        # Create matrix rows - same structure as week view but only one day (index 0)
        matrix_rows = []
        for emp_id, name in emp_map.items():
            # Access with string key for consistency
            row_data = {"id": emp_id, "name": name, "0": attendance_data.get(str(emp_id), "")}
            matrix_rows.append(row_data)
            
        return {"ok": True, "date": date, "rows": matrix_rows}
    except Exception as e:
        app.logger.error(f"Error in get_attendance_day: {e}")
        return {"ok": False, "error": "Failed to get daily attendance data.", "details": str(e)}

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

def check_device_session_for_employee(service, spreadsheet_id, device_id, date, employee_id):
    """Check if device has submitted attendance for the given date and return the employee_id."""
    try:
        # Try to get the AttendanceSessions sheet
        try:
            result = service.values().get(
                spreadsheetId=spreadsheet_id,
                range='AttendanceSessions!A:D'
            ).execute()
            rows = result.get('values', [])
        except:
            # If sheet doesn't exist, create it
            create_sessions_sheet(service, spreadsheet_id)
            return {"ok": True, "exists": False}
        
        if not rows or len(rows) < 2:
            return {"ok": True, "exists": False}
        
        # Check if device_id + date combination exists and get the employee_id
        for row in rows[1:]:
            if len(row) >= 3 and row[0] == device_id and row[1] == date:
                return {"ok": True, "exists": True, "employee_id": int(row[2])}
        
        return {"ok": True, "exists": False}
    except Exception as e:
        app.logger.error(f"Error in check_device_session_for_employee: {e}")
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

def get_office_hours(service, spreadsheet_id):
    """Gets the office hours configuration from the 'OfficeHours' sheet."""
    try:
        # Try to get the OfficeHours sheet
        try:
            result = service.values().get(
                spreadsheetId=spreadsheet_id,
                range='OfficeHours!A:B'
            ).execute()
            rows = result.get('values', [])
        except:
            # If sheet doesn't exist, create it with default values
            create_office_hours_sheet(service, spreadsheet_id)
            return {"ok": True, "hours": {"loginTime": "10:00", "logoutTime": "18:00"}}
        
        if not rows or len(rows) < 2:
            # If no data, return defaults
            return {"ok": True, "hours": {"loginTime": "10:00", "logoutTime": "18:00"}}
        
        # Parse the data
        hours = {}
        for row in rows[1:]:  # Skip header
            if len(row) >= 2:
                key = row[0].lower().replace(' ', '')
                value = row[1]
                if key == 'logintime':
                    hours['loginTime'] = value
                elif key == 'logouttime':
                    hours['logoutTime'] = value
        
        # Ensure we have both values
        if 'loginTime' not in hours:
            hours['loginTime'] = "10:00"
        if 'logoutTime' not in hours:
            hours['logoutTime'] = "18:00"
        
        return {"ok": True, "hours": hours}
    except Exception as e:
        app.logger.error(f"Error in get_office_hours: {e}")
        return {"ok": False, "error": "Failed to get office hours.", "details": str(e)}

def set_office_hours(service, spreadsheet_id, login_time, logout_time):
    """Sets the office hours configuration in the 'OfficeHours' sheet."""
    try:
        # Try to get the OfficeHours sheet
        try:
            service.values().get(
                spreadsheetId=spreadsheet_id,
                range='OfficeHours!A1'
            ).execute()
        except:
            # If sheet doesn't exist, create it
            create_office_hours_sheet(service, spreadsheet_id)
        
        # Update the office hours
        values = [
            ['Setting', 'Value'],
            ['LoginTime', login_time],
            ['LogoutTime', logout_time]
        ]
        
        service.values().update(
            spreadsheetId=spreadsheet_id,
            range='OfficeHours!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
        
        return {"ok": True, "hours": {"loginTime": login_time, "logoutTime": logout_time}}
    except Exception as e:
        app.logger.error(f"Error in set_office_hours: {e}")
        return {"ok": False, "error": "Failed to set office hours.", "details": str(e)}

def create_office_hours_sheet(service, spreadsheet_id):
    """Create the OfficeHours sheet with default values."""
    try:
        # Create the sheet
        sheet_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': 'OfficeHours'
                    }
                }
            }]
        }
        service.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=sheet_body
        ).execute()
        
        # Add default values
        values = [
            ['Setting', 'Value'],
            ['LoginTime', '10:00'],
            ['LogoutTime', '18:00']
        ]
        service.values().update(
            spreadsheetId=spreadsheet_id,
            range='OfficeHours!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
        
        return True
    except Exception as e:
        app.logger.error(f"Error creating office hours sheet: {e}")
        return False

def validate_location(latitude, longitude):
    """Validate if the provided coordinates are within allowed office locations."""
    try:
        # Office locations (same as frontend)
        allowed_locations = [
            {"lat": 28.678139, "lon": 77.106889, "radius": 50}
        ]
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate distance between two points in meters."""
            import math
            R = 6371000  # Earth's radius in meters
            d_lat = (lat2 - lat1) * math.pi / 180
            d_lon = (lon2 - lon1) * math.pi / 180
            a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(d_lon/2) * math.sin(d_lon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c
        
        # Check if within any office radius
        for location in allowed_locations:
            distance = haversine_distance(latitude, longitude, location["lat"], location["lon"])
            if distance <= location["radius"]:
                return {"ok": True, "distance": round(distance)}
        
        # If not within specific radius, check if within reasonable distance (200m) of any office
        min_distance = float('inf')
        for location in allowed_locations:
            distance = haversine_distance(latitude, longitude, location["lat"], location["lon"])
            if distance < min_distance:
                min_distance = distance
        
        # Allow if within 200m of any office location
        if min_distance <= 200:
            return {"ok": True, "distance": round(min_distance)}
        
        return {"ok": False, "error": f"Location is outside allowed office area. You are {round(min_distance)}m away from the nearest office location. Please ensure you are at the office building and try again."}
    except Exception as e:
        app.logger.error(f"Error in validate_location: {e}")
        return {"ok": False, "error": "Unable to verify your location. Please check your GPS settings and try again.", "details": str(e)}

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

@app.route("/api/logout", methods=['POST'])
def handle_logout_post():
    service, spreadsheet_id = get_sheets_service()
    body = request.get_json()
    emp_id = body.get('employee_id')
    latitude = body.get('latitude')
    longitude = body.get('longitude')
    device_id = body.get('device_id')
    testing_mode = body.get('testing_mode', False)
    
    if not emp_id:
        return jsonify({"ok": False, "error": "Employee ID is required to mark logout. Please select your employee profile and try again."}), 400
    
    data = mark_logout(service, spreadsheet_id, emp_id, latitude, longitude, device_id, testing_mode)
    status = 404 if 'error' in data and data.get("error") != "already logged out" else 200
    return jsonify(data), status

@app.route("/api/attendance", methods=['GET'])
def handle_attendance_get():
    service, spreadsheet_id = get_sheets_service()
    view_type = request.args.get('view', 'month')
    
    if view_type == 'month':
        month = request.args.get('month')
        if not month:
            return jsonify({"ok": False, "error": "month parameter is required"}), 400
        data = get_attendance_matrix(service, spreadsheet_id, month)
    elif view_type == 'week':
        week_start = request.args.get('week_start')
        if not week_start:
            return jsonify({"ok": False, "error": "week_start parameter is required"}), 400
        data = get_attendance_week(service, spreadsheet_id, week_start)
    elif view_type == 'day':
        date = request.args.get('date')
        if not date:
            return jsonify({"ok": False, "error": "date parameter is required"}), 400
        data = get_attendance_day(service, spreadsheet_id, date)
    else:
        return jsonify({"ok": False, "error": "Invalid view type. Use 'month', 'week', or 'day'"}), 400
    
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

@app.route("/api/office-hours", methods=['GET', 'POST'])
def handle_office_hours():
    service, spreadsheet_id = get_sheets_service()
    
    if request.method == 'GET':
        data = get_office_hours(service, spreadsheet_id)
        status = 500 if 'error' in data else 200
        return jsonify(data), status
    
    elif request.method == 'POST':
        body = request.get_json()
        login_time = body.get('loginTime')
        logout_time = body.get('logoutTime')
        
        if not login_time or not logout_time:
            return jsonify({"ok": False, "error": "loginTime and logoutTime are required"}), 400
        
        data = set_office_hours(service, spreadsheet_id, login_time, logout_time)
        status = 500 if 'error' in data else 200
        return jsonify(data), status

@app.route("/api/test-location", methods=['POST'])
def test_location():
    """Test endpoint to verify location validation without Google Sheets."""
    body = request.get_json()
    latitude = body.get('latitude')
    longitude = body.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({"ok": False, "error": "latitude and longitude are required"}), 400
    
    # Test location validation
    location_validation = validate_location(latitude, longitude)
    return jsonify(location_validation)

if __name__ == '__main__':
    app.run(debug=True, port=8081)
