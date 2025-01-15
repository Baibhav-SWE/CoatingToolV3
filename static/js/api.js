class Api {
  constructor() { }

  async request(endpoint, method = 'GET', data = null, headers = {}) {
    const url = endpoint;

    // Default headers, including CSRF token from the session if needed
    const defaultHeaders = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };

    // Merge user-provided headers
    headers = { ...defaultHeaders, ...headers };

    const options = {
      method,
      headers,
      credentials: 'include', // Include cookies for session-based tokens
    };

    // Add body for methods that send data
    if (['POST', 'PUT', 'PATCH'].includes(method.toUpperCase()) && data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      // Handle response statuses
      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Request Failed:', errorData);
        return errorData;
      }

      // Parse and return JSON if possible
      const contentType = response.headers.get('Content-Type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return await response.text();
    } catch (error) {
      console.error('API Request Failed:', error);
    }
  }

  get(endpoint, headers = {}) {
    return this.request(endpoint, 'GET', null, headers);
  }

  post(endpoint, data, headers = {}) {
    return this.request(endpoint, 'POST', data, headers);
  }

  put(endpoint, data, headers = {}) {
    return this.request(endpoint, 'PUT', data, headers);
  }

  patch(endpoint, data, headers = {}) {
    return this.request(endpoint, 'PATCH', data, headers);
  }

  delete(endpoint, data = null, headers = {}) {
    return this.request(endpoint, 'DELETE', data, headers);
  }
}
const api = new Api();