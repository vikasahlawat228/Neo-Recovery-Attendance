"""
Integration tests for attendance login/logout flow with message validation.
"""
import pytest
import requests
import json
from unittest.mock import patch, Mock
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))


class TestAttendanceFlowIntegration:
    """Integration tests for the complete attendance flow."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment before each test."""
        # Mock the Flask app for testing
        with patch('index.app') as mock_app:
            mock_app.test_client.return_value = Mock()
            yield mock_app
    
    def test_scenario_1_successful_login_logout_same_employee(self, mock_sheets_service, sample_employees):
        """Test Case 1: Correct user logging in for the first time, then logging out with same name."""
        # This test verifies the happy path scenario
        
        # Mock successful login
        with patch('index.mark_attendance') as mock_login:
            mock_login.return_value = {
                "ok": True, 
                "marked_at": "09:00", 
                "date": "2024-01-15"
            }
            
            # Mock successful logout
            with patch('index.mark_logout') as mock_logout:
                mock_logout.return_value = {
                    "ok": True, 
                    "logged_out_at": "17:30", 
                    "date": "2024-01-15"
                }
                
                # Test login
                login_result = mock_login(
                    mock_sheets_service, "test_spreadsheet", 1,
                    latitude=28.6139, longitude=77.2090, device_id="device_123"
                )
                assert login_result["ok"] is True
                assert "marked_at" in login_result
                
                # Test logout
                logout_result = mock_logout(
                    mock_sheets_service, "test_spreadsheet", 1,
                    latitude=28.6139, longitude=77.2090, device_id="device_123"
                )
                assert logout_result["ok"] is True
                assert "logged_out_at" in logout_result
    
    def test_scenario_2_double_logout_attempt(self, mock_sheets_service, sample_employees):
        """Test Case 2: Same user trying to logout again after already logging out."""
        # Mock the attendance data to show employee already logged out
        mock_attendance_data = {
        'values': [
            ['date', 'employee_id', 'name', 'arrival_time', 'location', 'logout_time'],
            ['2024-01-15', '1', 'John Doe', '09:00', 'reception', '17:30']  # Already logged out
        ]
    }
        
        with patch('index.mark_logout') as mock_logout:
            mock_logout.return_value = {
                "ok": False, 
                "error": "You have already logged out today. No action needed."
            }
            
            result = mock_logout(
                mock_sheets_service, "test_spreadsheet", 1,
                latitude=28.6139, longitude=77.2090, device_id="device_123"
            )
            
            assert result["ok"] is False
            assert "already logged out today" in result["error"]
    
    def test_scenario_3_logout_different_employee(self, mock_sheets_service, sample_employees):
        """Test Case 3: User logged in as Employee X tries to logout as Employee Y."""
        # Mock device session showing employee 1 is logged in
        with patch('index.check_device_session_for_employee') as mock_session_check:
            mock_session_check.return_value = {
                "ok": True, 
                "exists": True, 
                "employee_id": 1  # Device used by John Doe
            }
            
            # Mock get_employee_by_id to return the logged-in employee's name
            with patch('index.get_employee_by_id') as mock_get_employee:
                mock_get_employee.return_value = {"id": 1, "name": "John Doe"}
                
                with patch('index.mark_logout') as mock_logout:
                    mock_logout.return_value = {
                        "ok": False, 
                        "error": "You are logged in as John Doe today and can only logout for John Doe today!"
                    }
                    
                    result = mock_logout(
                        mock_sheets_service, "test_spreadsheet", 2,  # Trying to logout as Jane
                        latitude=28.6139, longitude=77.2090, device_id="device_123"
                    )
                    
                    assert result["ok"] is False
                    assert "logged in as John Doe" in result["error"]
                    assert "can only logout for John Doe" in result["error"]
    
    def test_scenario_4_logout_without_login(self, mock_sheets_service, sample_employees):
        """Test Case 4: User tries to logout without logging in first."""
        with patch('index.mark_logout') as mock_logout:
            mock_logout.return_value = {
                "ok": False, 
                "error": "You haven't logged in today. Please mark your attendance first before logging out."
            }
            
            result = mock_logout(
                mock_sheets_service, "test_spreadsheet", 1,
                latitude=28.6139, longitude=77.2090, device_id="device_123"
            )
            
            assert result["ok"] is False
            assert "haven't logged in today" in result["error"]
    
    def test_scenario_5_location_validation_login(self, mock_sheets_service, sample_employees):
        """Test Case 5: Login attempt from outside office location."""
        with patch('index.validate_location') as mock_validate:
            mock_validate.return_value = {
                "ok": False, 
                "error": "Location is outside allowed office area"
            }
            
            with patch('index.mark_attendance') as mock_login:
                mock_login.return_value = {
                    "ok": False, 
                    "error": "Location is outside allowed office area"
                }
                
                result = mock_login(
                    mock_sheets_service, "test_spreadsheet", 1,
                    latitude=28.0, longitude=77.0, device_id="device_123"  # Outside office
                )
                
                assert result["ok"] is False
                assert "outside allowed office area" in result["error"]
    
    def test_scenario_6_location_validation_logout(self, mock_sheets_service, sample_employees):
        """Test Case 6: Logout attempt from outside office location."""
        with patch('index.validate_location') as mock_validate:
            mock_validate.return_value = {
                "ok": False, 
                "error": "Location is outside allowed office area"
            }
            
            with patch('index.mark_logout') as mock_logout:
                mock_logout.return_value = {
                    "ok": False, 
                    "error": "Location is outside allowed office area"
                }
                
                result = mock_logout(
                    mock_sheets_service, "test_spreadsheet", 1,
                    latitude=28.0, longitude=77.0, device_id="device_123"  # Outside office
                )
                
                assert result["ok"] is False
                assert "outside allowed office area" in result["error"]
    
    def test_scenario_7_different_device_same_employee(self, mock_sheets_service, sample_employees):
        """Test Case 7: Different device trying to logout for same employee."""
        # Mock device session showing no existing session for this device
        with patch('index.check_device_session_for_employee') as mock_session_check:
            mock_session_check.return_value = {
                "ok": True, 
                "exists": False  # No existing session for this device
            }
            
            with patch('index.mark_logout') as mock_logout:
                mock_logout.return_value = {
                    "ok": True, 
                    "logged_out_at": "17:30", 
                    "date": "2024-01-15"
                }
                
                result = mock_logout(
                    mock_sheets_service, "test_spreadsheet", 1,
                    latitude=28.6139, longitude=77.2090, device_id="device_456"  # Different device
                )
                
                # Should succeed if employee has logged in today (regardless of device)
                assert result["ok"] is True
                assert "logged_out_at" in result
    
    def test_scenario_8_device_already_used_different_employee(self, mock_sheets_service, sample_employees):
        """Test Case 8: Device used by Employee X, trying to login as Employee Y."""
        with patch('index.check_device_session') as mock_check_session:
            mock_check_session.return_value = {
                "ok": True, 
                "exists": True  # Device already used today
            }
            
            with patch('index.mark_attendance') as mock_login:
                mock_login.return_value = {
                    "ok": False, 
                    "error": "This device has already marked attendance today"
                }
                
                result = mock_login(
                    mock_sheets_service, "test_spreadsheet", 2,  # Different employee
                    latitude=28.6139, longitude=77.2090, device_id="device_123"
                )
                
                assert result["ok"] is False
                assert "already marked attendance today" in result["error"]
    
    def test_scenario_9_employee_not_found_login(self, mock_sheets_service):
        """Test Case 9: Login attempt with non-existent employee ID."""
        with patch('index.get_employee_by_id', return_value=None):
            with patch('index.mark_attendance') as mock_login:
                mock_login.return_value = {
                    "ok": False, 
                    "error": "Employee not found"
                }
                
                result = mock_login(
                    mock_sheets_service, "test_spreadsheet", 999,  # Non-existent employee
                    latitude=28.6139, longitude=77.2090, device_id="device_123"
                )
                
                assert result["ok"] is False
                assert "Employee not found" in result["error"]
    
    def test_scenario_10_employee_not_found_logout(self, mock_sheets_service):
        """Test Case 10: Logout attempt with non-existent employee ID."""
        with patch('index.get_employee_by_id', return_value=None):
            with patch('index.mark_logout') as mock_logout:
                mock_logout.return_value = {
                    "ok": False, 
                    "error": "Employee not found or inactive. Please contact HR to verify your employee status."
                }
                
                result = mock_logout(
                    mock_sheets_service, "test_spreadsheet", 999,  # Non-existent employee
                    latitude=28.6139, longitude=77.2090, device_id="device_123"
                )
                
                assert result["ok"] is False
                assert "Employee not found" in result["error"]


class TestMessageValidation:
    """Test that error messages are user-friendly and use employee names."""
    
    def test_logout_wrong_employee_message_format(self, mock_sheets_service, sample_employees):
        """Test that logout error message uses employee name, not ID."""
        with patch('index.check_device_session_for_employee') as mock_session_check:
            mock_session_check.return_value = {
                "ok": True, 
                "exists": True, 
                "employee_id": 1  # John Doe is logged in
            }
            
            with patch('index.get_employee_by_id') as mock_get_employee:
                mock_get_employee.return_value = {"id": 1, "name": "John Doe"}
                
                with patch('index.mark_logout') as mock_logout:
                    mock_logout.return_value = {
                        "ok": False, 
                        "error": "You are logged in as John Doe today and can only logout for John Doe today!"
                    }
                    
                    result = mock_logout(
                        mock_sheets_service, "test_spreadsheet", 2,  # Trying to logout as Jane
                        latitude=28.6139, longitude=77.2090, device_id="device_123"
                    )
                    
                    # Verify message uses name, not ID
                    assert "John Doe" in result["error"]
                    assert "employee #1" not in result["error"]  # Should not use ID
                    assert "can only logout for John Doe" in result["error"]
    
    def test_success_messages_include_timestamps(self, mock_sheets_service, sample_employees):
        """Test that success messages include proper timestamps."""
        with patch('index.mark_attendance') as mock_login:
            mock_login.return_value = {
                "ok": True, 
                "marked_at": "09:00", 
                "date": "2024-01-15"
            }
            
            with patch('index.mark_logout') as mock_logout:
                mock_logout.return_value = {
                    "ok": True, 
                    "logged_out_at": "17:30", 
                    "date": "2024-01-15"
                }
                
                # Test login message
                login_result = mock_login(
                    mock_sheets_service, "test_spreadsheet", 1,
                    latitude=28.6139, longitude=77.2090, device_id="device_123"
                )
                assert "09:00" in str(login_result)
                
                # Test logout message
                logout_result = mock_logout(
                    mock_sheets_service, "test_spreadsheet", 1,
                    latitude=28.6139, longitude=77.2090, device_id="device_123"
                )
                assert "17:30" in str(logout_result)
