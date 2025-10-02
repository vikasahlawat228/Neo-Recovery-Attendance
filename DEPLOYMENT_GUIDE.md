# Neo Recovery Attendance System - Deployment Guide

**Complete step-by-step instructions for deploying the attendance management system**

---

## 📋 Prerequisites

Before starting deployment, ensure you have:
- ✅ A Google account with access to Google Sheets and Apps Script
- ✅ Basic understanding of Google Sheets
- ✅ A web browser (Chrome recommended)
- ✅ 30-45 minutes for complete setup

---

## 🎯 Overview

This system consists of:
1. **Google Sheets** - Database (Employees & Attendance data)
2. **Google Apps Script** - Backend API (REST endpoints)
3. **Frontend Pages** - Kiosk interface & Admin dashboard

**Deployment Flow:**
```
Google Sheets → Apps Script → Web App → Frontend Configuration → Testing
```

---

## Phase 1: Google Sheets Setup (10 minutes)

### Step 1.1: Create the Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Click **"+ Blank"** to create a new spreadsheet
3. Rename it to **"Neo Recovery Attendance"**
4. Set the timezone:
   - Go to **File → Settings**
   - Set **Time zone** to **"Asia/Kolkata"**
   - Click **Save**

### Step 1.2: Create Employee Sheet

1. The default sheet is already named "Sheet1" - rename it to **"Employees"**
2. In row 1, add these headers:
   ```
   A1: id
   B1: name  
   C1: active
   ```
3. Format the header row:
   - Select row 1 (A1:C1)
   - Click **Format → Text → Bold**
   - Set background color to light blue

### Step 1.3: Create Attendance Sheet

1. Click the **"+"** button at the bottom to add a new sheet
2. Rename it to **"Attendance"**
3. In row 1, add these headers:
   ```
   A1: date
   B1: employee_id
   C1: employee_name
   D1: arrival_time
   E1: kiosk_id
   ```
4. Format the header row (bold + light blue background)

### Step 1.4: Test Data (Optional)

Add a test employee to verify setup:
1. Go to **Employees** sheet
2. In row 2, add:
   ```
   A2: 1
   B2: Test Employee
   C2: TRUE
   ```

**✅ Phase 1 Complete:** You now have a properly structured Google Sheet.

---

## Phase 2: Google Apps Script Backend (15 minutes)

### Step 2.1: Create Apps Script Project

1. In your Google Sheet, go to **Extensions → Apps Script**
2. A new Apps Script project opens
3. Delete the default `myFunction()` code
4. Copy the entire content from `apps-script-code.gs` and paste it into the editor

### Step 2.2: Initial Setup Function

1. In the Apps Script editor, find the `setupHeaders()` function
2. Click **Run** (▶️) next to `setupHeaders`
3. Grant permissions when prompted:
   - Click **Review permissions**
   - Choose your Google account
   - Click **Advanced → Go to [Project Name] (unsafe)**
   - Click **Allow**
4. Check the execution log for "Setup completed successfully!"

### Step 2.3: Test the API

1. In Apps Script editor, find the `testAPI()` function
2. Click **Run** next to `testAPI`
3. Check the execution log for successful API test results
4. Verify in your Google Sheet that:
   - A test employee was added to **Employees** sheet
   - An attendance record was added to **Attendance** sheet

### Step 2.4: Deploy as Web App

1. In Apps Script editor, click **Deploy → New deployment**
2. Click the gear icon ⚙️ next to **Type** and select **Web app**
3. Configure deployment settings:
   - **Execute as:** Me (your-email@gmail.com)
   - **Who has access:** Anyone with the link
4. Click **Deploy**
5. **IMPORTANT:** Copy the **Web app URL** - you'll need this for the frontend

**✅ Phase 2 Complete:** Your backend API is now live and accessible.

---

## Phase 3: Frontend Configuration (10 minutes)

### Step 3.1: Configure API Connection

1. Open `api.js` in a text editor
2. Find this line:
   ```javascript
   const API_BASE = 'https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec';
   ```
3. Replace `YOUR_SCRIPT_ID` with your actual Web app URL from Step 2.4
4. Save the file

**Example:**
```javascript
const API_BASE = 'https://script.google.com/macros/s/AKfycbx1234567890abcdef/exec';
```

### Step 3.2: Test API Connection

1. Open `index.html` in your web browser
2. Check browser console (F12 → Console tab) for any errors
3. The page should load and show "Loading employees..." or your test employee
4. If you see connection errors, verify the API_BASE URL is correct

### Step 3.3: Host Frontend Files

Choose one of these hosting options:

#### Option A: Local Testing

**Important:** Due to CORS (Cross-Origin Resource Sharing) restrictions, you cannot simply open HTML files directly in your browser for testing. Use one of these methods:

**Method 1: Use the Local Server (Recommended)**
1. **On macOS/Linux:**
   ```bash
   ./start-server.sh
   ```
   
2. **On Windows:**
   ```cmd
   start-server.bat
   ```
   
3. **Manual Python server:**
   ```bash
   python3 server.py
   ```

4. Open your browser to: `http://localhost:8000`

**Method 2: Update Google Apps Script (Alternative)**
If you prefer to open files directly, update your Google Apps Script with the CORS headers provided in the updated `apps-script-code.gs` file. This allows direct file access but requires redeploying your Google Apps Script.

**Method 3: Browser with Disabled Security (Not Recommended)**
```bash
# Chrome (macOS/Linux)
google-chrome --disable-web-security --user-data-dir=/tmp/chrome_dev

# Chrome (Windows)
chrome.exe --disable-web-security --user-data-dir=c:\temp\chrome_dev
```
⚠️ **Warning:** Only use this for testing, never for regular browsing.

#### Option B: Static Hosting (Recommended for Production)
1. **Netlify:**
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop your project folder
   - Get a free custom URL

2. **Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your project from GitHub or upload files

3. **GitHub Pages:**
   - Upload files to a GitHub repository
   - Enable Pages in repository settings

**✅ Phase 3 Complete:** Frontend is configured and accessible.

---

## Phase 4: Testing & Verification (10 minutes)

### Step 4.1: Test Kiosk Interface (`index.html`)

1. Open the kiosk page
2. Verify employee dropdown loads
3. Select an employee and click "Mark Present"
4. Check for success message with timestamp
5. Verify attendance record appears in Google Sheet

### Step 4.2: Test Admin Dashboard (`admin.html`)

1. Open the admin page
2. Test employee management:
   - Add a new employee
   - Edit an existing employee name
   - Remove an employee
3. Test attendance dashboard:
   - Select current month
   - Click "Load Data"
   - Verify attendance matrix displays correctly
4. Test CSV export functionality

### Step 4.3: Test Edge Cases

1. **Duplicate Prevention:**
   - Try marking the same employee twice in one day
   - Should show "Already marked for today" message

2. **Error Handling:**
   - Test with invalid employee ID
   - Test with empty employee name
   - Verify appropriate error messages

3. **Data Integrity:**
   - Check Google Sheet data matches frontend display
   - Verify timestamps are in correct timezone (Asia/Kolkata)

**✅ Phase 4 Complete:** System is fully functional and tested.

---

## Phase 5: Production Deployment (5 minutes)

### Step 5.1: Security Considerations

1. **Access Control:**
   - Consider adding password protection to admin page
   - Restrict Google Sheet access to authorized users only
   - Use HTTPS for production hosting

2. **Data Backup:**
   - Enable Google Sheets version history
   - Set up regular exports of attendance data
   - Consider monthly sheet backups

### Step 5.2: Kiosk Setup

1. **Hardware Setup:**
   - Use a tablet or touchscreen computer
   - Set browser to fullscreen mode (F11)
   - Disable browser navigation (optional)

2. **Browser Configuration:**
   - Set kiosk page as homepage
   - Disable pop-ups and notifications
   - Enable auto-refresh if needed

### Step 5.3: Monitoring

1. **Regular Checks:**
   - Monitor Google Apps Script execution logs
   - Check for failed API calls
   - Verify data consistency

2. **Maintenance:**
   - Update employee list as needed
   - Archive old attendance data periodically
   - Monitor system performance

**✅ Phase 5 Complete:** System is production-ready.

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### "Failed to load employees"
- **Cause:** Incorrect API_BASE URL
- **Solution:** Verify Web app URL in `api.js`

#### "Attendance not marking"
- **Cause:** Apps Script permissions or sheet structure
- **Solution:** Re-run `setupHeaders()` function

#### "CORS errors" (Access to fetch blocked)
- **Cause:** Browser security restrictions when opening HTML files directly
- **Symptoms:** 
  - `Access to fetch at 'https://script.google.com/...' from origin 'null' has been blocked by CORS policy`
  - `Failed to load resource: net::ERR_FAILED`
- **Solutions:**
  1. **Use the local server:** Run `./start-server.sh` (macOS/Linux) or `start-server.bat` (Windows)
  2. **Update Google Apps Script:** Deploy the updated `apps-script-code.gs` with CORS headers
  3. **Check URL format:** Ensure API_BASE URL in `api.js` is correct

#### "Employee not found"
- **Cause:** Employee marked as inactive
- **Solution:** Check `active` column in Employees sheet

### Debug Steps

1. **Check Browser Console:**
   - Press F12 → Console tab
   - Look for JavaScript errors
   - Check network requests

2. **Check Apps Script Logs:**
   - Go to Apps Script editor
   - Click **Executions** to see run history
   - Check for error messages

3. **Verify Sheet Structure:**
   - Ensure headers match exactly
   - Check for extra spaces in column names
   - Verify data types (numbers vs text)

---

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Google Apps    │    │   Google Sheets │
│   (HTML/JS)     │◄──►│   Script API     │◄──►│   (Database)    │
│                 │    │                  │    │                 │
│ • index.html    │    │ • REST Endpoints │    │ • Employees     │
│ • admin.html    │    │ • Authentication │    │ • Attendance    │
│ • api.js        │    │ • Data Processing │    │ • Version Ctrl  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 🔧 Maintenance Tasks

### Daily
- Monitor attendance marking
- Check for system errors

### Weekly  
- Review attendance data
- Update employee list if needed

### Monthly
- Export attendance reports
- Backup Google Sheet
- Review system performance

### Quarterly
- Update Apps Script if needed
- Review security settings
- Plan system improvements

---

## 📞 Support

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review Google Apps Script logs** for backend errors
3. **Check browser console** for frontend errors
4. **Verify Google Sheet structure** matches requirements

**System Status:** ✅ Production Ready
**Last Updated:** December 2024
**Version:** 1.0

---

**🎉 Congratulations! Your Neo Recovery Attendance System is now deployed and ready for use.**
