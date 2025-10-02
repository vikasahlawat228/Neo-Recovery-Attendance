# Vercel Hosting Guide for Neo Recovery App

This guide outlines the steps to deploy your Neo Recovery application to Vercel.

## Overview

We will deploy the application with the following structure:
- **Frontend**: The HTML, CSS, and client-side JavaScript files will be served as a static site.
- **Backend**: The Python API in `backend.py` will be deployed as a Vercel Serverless Function.

## Step 1: Restructure Your Project

Vercel can automatically detect and deploy your application if you follow a specific directory structure.

1.  Create a new directory named `api` in the root of your project.
2.  Move your `backend.py` file into this new `api` directory.
3.  Rename `api/backend.py` to `api/index.py`. Vercel uses `index.py` as the default entry point for a Python serverless function in a directory.
4.  Your frontend files (`index-backend.html`, `admin-backend.html`, `api-backend.js`, and any other assets) should remain in the root directory.

Your project structure should look like this:

```
/
├── admin-backend.html
├── index-backend.html
├── api-backend.js
├── requirements.txt
├── vercel.json
└── api/
    └── index.py
```

## Step 2: Adapt the Python Backend for Vercel

We need to modify the Python backend to work as a serverless function. We'll use the Flask web framework for this, as it's lightweight and well-supported on Vercel.

1.  **Update `requirements.txt`**: Add `Flask` to your `requirements.txt` file.

    ```
    google-api-python-client
    google-auth-httplib2
    google-auth-oauthlib
    Flask
    ```

2.  **Modify `api/index.py`**: Update the Python script to be a Flask application. The server part of the code will be replaced by a Flask request handler.

    The new `api/index.py` will look something like this (this is a conceptual guide, you'll need to adapt your existing logic):

    ```python
    from flask import Flask, request, jsonify
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    import os

    # All your existing functions (get_employees, mark_attendance, etc.) go here.
    # ...

    app = Flask(__name__)

    # --- Configuration ---
    # Load credentials from environment variables for security
    # You will set these in the Vercel dashboard
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

    if not creds_json or not SPREADSHEET_ID:
        raise ValueError("Missing GOOGLE_CREDENTIALS_JSON or SPREADSHEET_ID environment variables")

    creds_info = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds).spreadsheets()


    # Example of a route
    @app.route('/api/employees', methods=['GET'])
    def employees_route():
        employees = get_employees(service)
        return jsonify(employees)

    # You will need to create routes for all your API endpoints
    # e.g., @app.route('/api/attendance', methods=['POST'])
    # ...

    # This part is needed for local testing, but Vercel handles the server.
    if __name__ == "__main__":
        app.run(debug=True)

    ```
    You will need to create a Flask route for each of your existing API endpoints.

## Step 3: Configure Vercel (`vercel.json`)

Create a `vercel.json` file in the root of your project to tell Vercel how to handle routing and builds.

```json
{
  "version": 2,
  "builds": [
    {
      "src": "/api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

This configuration does two things:
- It tells Vercel that `api/index.py` is a Python serverless function.
- It routes all requests starting with `/api/` to your Python function, and all other requests to your static frontend files.

## Step 4: Handle Secrets Securely

Your `credentials.json` file contains sensitive information and should not be committed to your Git repository.

1.  **Add `credentials.json` to `.gitignore`**:
    ```
    credentials.json
    ```

2.  **Use Environment Variables in Vercel**:
    - Go to your project settings in the Vercel dashboard.
    - Navigate to "Environment Variables".
    - Create a new environment variable named `GOOGLE_CREDENTIALS_JSON`.
    - Copy the entire content of your `credentials.json` file and paste it as the value for this variable.
    - Create another variable `SPREADSHEET_ID` and add your spreadsheet ID.
    - Your Python code will then read these variables instead of the file.

## Step 5: Update Frontend API calls

Your `api-backend.js` file currently points to `http://localhost:8081`. You need to change this to use relative paths so it calls your Vercel API.

Change:
`const API_BASE = 'http://localhost:8081';`

To:
`const API_BASE = '/api';`

And update your API calls to match the new routes, for example:
`apiGet('employees')` would now fetch `/api/employees`.

## Step 6: Deploy

1.  Push your code to a Git repository (e.g., GitHub, GitLab).
2.  Import your repository into Vercel.
3.  Configure the environment variables as described in Step 4.
4.  Deploy!

Vercel will automatically build and deploy your static frontend and your Python serverless backend.
