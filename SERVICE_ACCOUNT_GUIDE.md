# Guide to Creating a Google Service Account for Neo Recovery App

This guide will walk you through creating a service account, which will allow our Python proxy server to securely access your Google Sheet data without requiring a public web app deployment.

### Step 1: Create or Select a Google Cloud Project

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  If you don't have a project, click the project dropdown at the top of the page and click **"New Project"**. Give it a name like "Neo Recovery App" and create it.
3.  If you have an existing project, make sure it's selected.

### Step 2: Enable Necessary APIs

We need to give your project permission to use the Google Drive and Google Sheets APIs.

1.  In the Cloud Console, use the search bar at the top to search for and select **"Google Drive API"**. Click the **"Enable"** button.
2.  Go back to the search bar and search for **"Google Sheets API"**. Click the **"Enable"** button.

### Step 3: Create the Service Account

This creates a special robot user that our server will use.

1.  In the search bar, search for and go to **"Service Accounts"**.
2.  Click **"+ CREATE SERVICE ACCOUNT"** at the top.
3.  **Service account name:** Enter something descriptive, like `neo-recovery-sheets-editor`.
4.  Click **"CREATE AND CONTINUE"**.
5.  **Grant access (Optional):** You can skip adding a role for now. Click **"CONTINUE"**.
6.  **Grant users access (Optional):** You can also skip this step. Click **"DONE"**.

### Step 4: Create and Download a JSON Key

This is the password file for your service account.

1.  You should now be back on the "Service Accounts" page. Find the account you just created and click on the email address in the `Email` column.
2.  Click on the **"KEYS"** tab.
3.  Click **"ADD KEY"** and select **"Create new key"**.
4.  Choose **"JSON"** as the key type and click **"CREATE"**.
5.  A JSON file will be downloaded to your computer. This file is very important and sensitive.

### Step 5: Use the Key File

1.  Find the downloaded file and rename it to `credentials.json`.
2.  Move this `credentials.json` file into the root of your project directory (`/Users/vikasahlawat/Documents/Neo Recovery/`).
3.  **IMPORTANT:** This file contains private keys. **Do not commit it to version control (like Git) or share it publicly.**

### Step 6: Share Your Google Sheet with the Service Account

The final step is to give your new robot user permission to edit your spreadsheet.

1.  Open the `credentials.json` file you just moved.
2.  Find the value for `"client_email"`. It will look like `neo-recovery-sheets-editor@your-project-id.iam.gserviceaccount.com`. Copy this email address.
3.  Open your "Neo Recovery" Google Sheet.
4.  Click the **"Share"** button in the top right.
5.  Paste the `client_email` you copied into the "Add people and groups" field.
6.  Make sure it has the **"Editor"** role.
7.  Click **"Share"**.

---

Once you have completed all these steps, please let me know. I will then modify the Python proxy server to use these new credentials.
