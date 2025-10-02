# Neo Recovery Attendance System

A simple, elegant attendance management system built with Google Sheets as the backend and vanilla HTML/JS for the frontend.

## 🚀 Quick Start

### 1. Set up Google Sheets Backend

1. Create a new Google Sheet named "Neo Recovery Attendance"
2. Create two tabs:
   - **Employees**: Columns `id`, `name`, `active`
   - **Attendance**: Columns `date`, `employee_id`, `employee_name`, `arrival_time`, `kiosk_id`
3. Set the spreadsheet timezone to **Asia/Kolkata**

### 2. Deploy Google Apps Script

1. Go to **Extensions → Apps Script** in your Google Sheet
2. Replace the default code with the content from `apps-script-code.gs`
3. Run the `setupHeaders()` function once to create headers
4. Deploy as **Web App**:
   - Execute as: **Me**
   - Who has access: **Anyone with the link**
5. Copy the web app URL

### 3. Configure Frontend

1. Open `api.js` and replace `YOUR_SCRIPT_ID` with your actual Apps Script web app URL
2. Open `index.html` in a browser for the kiosk interface
3. Open `admin.html` in a browser for the admin dashboard

## 📁 Project Structure

```
Neo Recovery/
├── index.html          # Kiosk interface for marking attendance
├── admin.html          # Admin dashboard for managing employees and viewing reports
├── api.js              # API client for communicating with Google Apps Script
├── apps-script-code.gs # Google Apps Script backend code
└── README.md           # This file
```

## 🎯 Features

### Kiosk Interface (`index.html`)
- ✅ Employee search and selection
- ✅ One-click attendance marking
- ✅ Duplicate prevention (already marked today)
- ✅ Beautiful, responsive design
- ✅ Real-time feedback

### Admin Dashboard (`admin.html`)
- 👥 Employee management (add, edit, remove)
- 📊 Monthly attendance reports
- 📈 Statistics dashboard
- 📄 CSV export functionality
- 🔍 Search and filter capabilities

## 🔧 API Endpoints

The Google Apps Script provides these REST endpoints:

- `GET /employees` - List all active employees
- `POST /employees` - Add new employee
- `PUT /employees/:id` - Update employee
- `DELETE /employees/:id` - Soft delete employee
- `POST /attendance` - Mark attendance
- `GET /attendance?month=YYYY-MM` - Get monthly attendance matrix

## 🎨 Customization

### Styling
- Modify CSS in the `<style>` sections of HTML files
- Colors, fonts, and layouts can be easily customized
- Responsive design works on tablets and mobile devices

### Functionality
- Add new features by extending the Apps Script code
- Modify the frontend JavaScript for additional interactions
- Add authentication if needed (not included in basic version)

## 🚀 Deployment Options

### Local Development
- Simply open the HTML files in a web browser
- Perfect for testing and development

### Web Hosting
- Upload files to any static hosting service (Netlify, Vercel, GitHub Pages)
- No server-side requirements
- Works with any web server

### Kiosk Mode
- Use browser fullscreen mode (F11)
- Set browser to open only the kiosk page
- Disable browser navigation for a true kiosk experience

## 🔒 Security Notes

- The basic version has no authentication
- For production use, consider adding:
  - Admin password protection
  - IP address restrictions
  - HTTPS enforcement
  - Rate limiting

## 📱 Mobile Support

- Responsive design works on mobile devices
- Touch-friendly interface
- Optimized for tablet kiosks

## 🐛 Troubleshooting

### Common Issues

1. **"Failed to load employees"**
   - Check that the API_BASE URL in `api.js` is correct
   - Verify the Google Apps Script is deployed and accessible

2. **"Attendance not marking"**
   - Ensure the Google Sheet has proper headers
   - Check that the Apps Script has permission to access the sheet

3. **"CORS errors"**
   - Google Apps Script handles CORS automatically
   - If issues persist, check browser console for specific errors

### Debug Mode
- Open browser developer tools (F12)
- Check the Console tab for error messages
- Network tab shows API request/response details

## 📈 Future Enhancements

- [ ] Employee photo support
- [ ] Advanced reporting (charts, graphs)
- [ ] Email notifications
- [ ] Multi-location support
- [ ] Mobile app version
- [ ] Integration with HR systems

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Google Apps Script logs
3. Test API endpoints directly in the browser

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for Neo Recovery**
