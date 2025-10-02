# Neo Recovery Attendance - Project Workplan

This document outlines the development plan for the Neo Recovery Attendance system. The project uses a Python backend to securely interact with a Google Sheet, which acts as the database.

---

## Current Architecture

*   **Backend:** Python 3 (`backend.py`)
    *   Acts as a secure proxy to the Google Sheets API.
    *   Requires a Google Service Account (`credentials.json`) for authentication.
    *   Handles all business logic (CRUD operations, attendance marking).
*   **Database:** Google Sheets
    *   One sheet with two tabs: `Employees` and `Attendance`.
*   **Frontend:** Vanilla HTML/JS/CSS
    *   `index-backend.html`: Kiosk for employees to mark attendance.
    *   `admin-backend.html`: Dashboard for managing employees and viewing reports.

---

## Phase 0: Foundation (Completed)

*   [x] **Google Sheet Design:**
    *   Created a Google Sheet named "Neo Recovery Attendance".
    *   Set up two tabs:
        1.  `Employees` (columns: `id`, `name`, `active`)
        2.  `Attendance` (columns: `date`, `employee_id`, `employee_name`, `arrival_time`, `kiosk_id`)
    *   Set the spreadsheet timezone to `Asia/Kolkata`.

---

## Phase 1: Python Backend (Completed)

*   [x] **Setup Secure Google Sheets Access:**
    *   Created a Google Service Account.
    *   Generated and configured `credentials.json`.
    *   Shared the Google Sheet with the service account email.
    *   *(See `SERVICE_ACCOUNT_GUIDE.md` for details)*
*   [x] **Implemented API Endpoints:**
    *   `GET /employees`: List all active employees.
    *   `POST /employees`: Add a new employee.
    *   `PUT /employees/:id`: Update an employee's details.
    *   `DELETE /employees/:id`: Deactivate an employee.
    *   `POST /attendance`: Mark an employee's attendance for the day.
    *   `GET /attendance?month=YYYY-MM`: Fetch a monthly attendance report.

---

## Phase 2: Frontend Development (Completed)

*   [x] **Kiosk Interface (`index-backend.html`):**
    *   Searchable dropdown to find and select employees.
    *   "Mark Present" functionality.
    *   Real-time feedback messages (success, error, already marked).
    *   Clean, responsive user interface.
*   [x] **Admin Dashboard (`admin-backend.html`):**
    *   **Employee Management (CRUD):**
        *   View all active employees.
        *   Add a new employee.
        *   Edit an existing employee's name.
        *   Remove (deactivate) an employee.
    *   **Attendance Report:**
        *   Month selector to choose a reporting period.
        *   Displays a grid of the monthly attendance data.
        *   "Export to CSV" functionality.

---

## Phase 3: Next Steps & Future Enhancements (To Be Implemented)

This section outlines the planned improvements and new features.

### Immediate Tasks:
*   [ ] **Implement "Today's Attendance" Stat:**
    *   **Backend:** Create a new endpoint in `backend.py` to count the number of attendance entries for the current day.
    *   **Frontend:** Update `admin-backend.html` to call this new endpoint and display the count in the statistics section.
*   [ ] **UI Polish for Admin Dashboard:**
    *   Improve the layout of the employee list for better readability.
    *   Ensure all buttons and inputs are consistently styled.

### Future Features:
*   [ ] **Advanced Reporting:**
    *   Add charts and graphs to visualize attendance trends.
    *   Calculate and display individual attendance percentages.
*   [ ] **Employee Photos:**
    *   Allow uploading and displaying employee photos on the kiosk and admin pages.
*   [ ] **Enhanced Security:**
    *   Add simple password protection for the admin dashboard (`admin-backend.html`).
*   [ ] **System Reliability:**
    *   Implement an "offline mode" for the kiosk that queues attendance marks in `localStorage` if the backend server is unreachable and syncs them later.
*   [ ] **Email Notifications:**
    *   Send daily or weekly attendance summary reports to an admin email address.
