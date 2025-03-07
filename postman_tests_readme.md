# API Python - Postman Test Collection

This repository contains a Postman collection for testing all API endpoints in the API Python codebase.

## Getting Started

### Prerequisites

1. [Postman](https://www.postman.com/downloads/) application installed
2. API Python server running (locally or on a remote server)

### Importing the Collection

1. Open Postman
2. Click on "Import" button in the top left corner
3. Select the `postman_tests.json` file
4. Click "Import"

### Configuring the Environment

1. Create a new environment in Postman (Environments > Add)
2. Add a variable named `baseUrl` with the base URL of your API server:
   - For local development: `http://localhost:8000`
   - For testing environment: `https://[your-test-server-url]`
   - For production: `https://[your-production-server-url]`

### Running Tests

The collection is organized into folders by module:

- Authentication
- Authorization
- Subscription
- Partner
- Party
- API Keys
- Metering
- Cookies
- IP Ranges

You can:

1. Run the entire collection (click the "Run" button on the collection)
2. Run a specific folder (right-click on a folder and select "Run")
3. Run individual requests as needed

## Test Data

The test requests include sample data that should be modified to match your specific environment:

- Party IDs
- Partner IDs
- User credentials
- API keys

## Authentication

Many endpoints require authentication. Make sure to:

1. Run the "Login" request first to get an authentication token
2. Save the token from the response (can be automated with a test script)
3. Use the token in subsequent requests that require authentication

## Additional Notes

- The collection includes basic GET, POST, PUT, and DELETE operations for all API endpoints
- The request bodies contain sample JSON data which should be modified as needed
- For endpoints that require pagination, modify the URL parameters as needed

## Extending the Collection

Feel free to extend this collection by:

1. Adding more test cases
2. Adding test scripts to validate responses
3. Creating environment variables for commonly used values
4. Setting up pre-request scripts for authentication

## Troubleshooting

If you encounter issues:

1. Verify the API server is running
2. Check that your `baseUrl` is correctly configured
3. Ensure you have the necessary permissions to access the endpoints
4. Check authentication token expiration
