// Neo Recovery Attendance API Client - Backend Version
// Connects to the Vercel serverless backend.

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
    throw error;
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
async function handleResponse(response) {
  if (!response.ok) {
    const errorBody = await response.text();
    console.error("API Error Response:", errorBody);
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}
