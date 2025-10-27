// Neo Recovery Attendance API Client - Backend Version
// Connects to the Vercel serverless backend.
// Updated: Fixed error handling to return error objects instead of throwing exceptions

const API_BASE = window.API_BASE || '/api'; // Use window.API_BASE for local dev, relative path for Vercel

async function apiGet(path, params = {}) {
  try {
    const queryParams = new URLSearchParams(params).toString();
    const url = queryParams ? `${API_BASE}/${path}?${queryParams}` : `${API_BASE}/${path}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return await handleResponse(response);
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

async function apiPost(path, body = {}) {
  try {
    const response = await fetch(`${API_BASE}/${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    return await handleResponse(response);
  } catch (error) {
    console.error('API POST Error:', error);
    // Return error object instead of throwing
    return { ok: false, error: error.message };
  }
}

// PUT request helper
async function apiPut(path, id, body = {}) {
  try {
    const response = await fetch(`${API_BASE}/${path}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    return await handleResponse(response);
  } catch (error) {
    console.error('API PUT Error:', error);
    throw error;
  }
}

// DELETE request helper
async function apiDelete(path, id) {
  try {
    const response = await fetch(`${API_BASE}/${path}/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return await handleResponse(response);
  } catch (error) {
    console.error('API DELETE Error:', error);
    throw error;
  }
}

// Helper function to handle API responses
// Updated: Fixed error handling to return error objects instead of throwing exceptions
async function handleResponse(response) {
  if (!response.ok) {
    const errorBody = await response.text();
    console.error("API Error Response:", errorBody);
    
    // Try to parse error body as JSON for better error messages
    let errorMessage = `HTTP error! status: ${response.status}`;
    let errorData = null;
    try {
      errorData = JSON.parse(errorBody);
      if (errorData.error) {
        errorMessage = errorData.error;
      }
    } catch (e) {
      // If parsing fails, use the original error message
    }
    
    // Provide user-friendly messages based on status codes
    if (response.status === 400) {
      errorMessage = errorMessage || "Invalid request. Please check your input and try again.";
    } else if (response.status === 404) {
      errorMessage = errorMessage || "Requested resource not found. Please try again.";
    } else if (response.status === 500) {
      errorMessage = errorMessage || "Server error occurred. Please try again in a few moments.";
    } else if (response.status === 0) {
      errorMessage = "Network error. Please check your internet connection and try again.";
    }
    
    // Return error response instead of throwing exception
    // This allows the frontend to handle specific error messages properly
    console.log("Returning error object instead of throwing:", errorData || { ok: false, error: errorMessage });
    if (errorData) {
      return errorData; // Return the full error object with ok: false, error: "..."
    } else {
      return { ok: false, error: errorMessage };
    }
  }
  return response.json();
}
