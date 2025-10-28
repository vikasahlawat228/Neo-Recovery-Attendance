"""
Test configuration and fixtures for attendance system tests.
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from zoneinfo import ZoneInfo


@pytest.fixture
def mock_sheets_service():
    """Mock Google Sheets service for testing."""
    service = Mock()
    
    # Mock employees data
    employees_data = {
        'values': [
            ['id', 'name', 'active'],
            ['1', 'John Doe', 'TRUE'],
            ['2', 'Jane Smith', 'TRUE'],
            ['3', 'Bob Wilson', 'FALSE'],  # Inactive employee
            ['4', 'Alice Brown', 'TRUE'],
            ['11', 'Test Employee', 'TRUE']
        ]
    }
    
    # Mock attendance data (date, employee_id, name, arrival_time, location, logout_time)
    attendance_data = {
        'values': [
            ['date', 'employee_id', 'name', 'arrival_time', 'location', 'logout_time'],
            ['2024-01-15', '1', 'John Doe', '09:00', 'reception', ''],
            ['2024-01-15', '2', 'Jane Smith', '09:30', 'reception', '17:30'],
            ['2024-01-16', '1', 'John Doe', '08:45', 'reception', '18:00']
            # No data for employee 11 - clean slate for testing
        ]
    }
    
    # Mock device sessions data (device_id, date, employee_id, timestamp)
    sessions_data = {
        'values': [
            ['device_id', 'date', 'employee_id', 'timestamp'],
            ['device_123', '2024-01-15', '1', '2024-01-15 09:00:00'],
            ['device_456', '2024-01-15', '2', '2024-01-15 09:30:00']
            # No session data for employee 11 - clean slate for testing
        ]
    }
    
    # Mock office hours data
    office_hours_data = {
        'values': [
            ['day', 'start_time', 'end_time'],
            ['Monday', '09:00', '18:00'],
            ['Tuesday', '09:00', '18:00'],
            ['Wednesday', '09:00', '18:00'],
            ['Thursday', '09:00', '18:00'],
            ['Friday', '09:00', '18:00']
        ]
    }
    
    def mock_get(spreadsheetId, range):
        """Mock the values().get() method."""
        mock_result = Mock()
        if 'Employees' in range:
            mock_result.execute.return_value = employees_data
        elif 'Attendance' in range and 'AttendanceSessions' not in range:
            mock_result.execute.return_value = attendance_data
        elif 'AttendanceSessions' in range:
            mock_result.execute.return_value = sessions_data
        elif 'OfficeHours' in range:
            mock_result.execute.return_value = office_hours_data
        else:
            mock_result.execute.return_value = {'values': []}
        return mock_result
    
    def mock_append(spreadsheetId, range, **kwargs):
        """Mock the values().append() method."""
        mock_result = Mock()
        mock_result.execute.return_value = {}
        return mock_result
    
    def mock_update(spreadsheetId, range, **kwargs):
        """Mock the values().update() method."""
        mock_result = Mock()
        mock_result.execute.return_value = {}
        return mock_result
    
    service.values.return_value.get = mock_get
    service.values.return_value.append = mock_append
    service.values.return_value.update = mock_update
    
    # Mock the create_sessions_sheet function
    def mock_create_sessions_sheet(service, spreadsheet_id):
        return True
    
    # Add the mock function to the service
    service.create_sessions_sheet = mock_create_sessions_sheet
    
    return service


@pytest.fixture
def sample_employees():
    """Sample employee data for testing."""
    return [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Smith"},
        {"id": 4, "name": "Alice Brown"},
        {"id": 11, "name": "Test Employee"}
    ]


@pytest.fixture
def sample_date():
    """Sample date for testing."""
    tz = ZoneInfo("Asia/Kolkata")
    return datetime.now(tz).strftime('%Y-%m-%d')


@pytest.fixture
def sample_time():
    """Sample time for testing."""
    tz = ZoneInfo("Asia/Kolkata")
    return datetime.now(tz).strftime('%H:%M')


@pytest.fixture
def sample_device_id():
    """Sample device ID for testing."""
    return "test_device_123"


@pytest.fixture
def office_location():
    """Office location coordinates for testing."""
    return {
        "lat": 28.6139,  # Delhi coordinates
        "lon": 77.2090,
        "radius": 100  # 100 meters radius
    }


@pytest.fixture
def mock_location_validation():
    """Mock location validation results."""
    def create_validation(allowed=True, distance=50, location="office"):
        return {
            "ok": allowed,
            "error": None if allowed else f"Location is outside allowed office area",
            "distance": distance,
            "location": location
        }
    return create_validation
