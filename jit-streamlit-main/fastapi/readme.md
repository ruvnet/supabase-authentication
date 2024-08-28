# FastAPI Supabase Authentication App

This FastAPI application demonstrates user authentication using Supabase as the backend.

## Prerequisites

- Python 3.7+
- FastAPI
- Supabase account and project

## Setup

1. Clone the repository to your local machine.

2. Install the required dependencies:
   ```
   pip install fastapi uvicorn supabase python-multipart
   ```

3. Set up your Supabase project:
   - Create a new project in Supabase
   - Enable Email Auth in Authentication > Providers

4. Create a `.env` file in the root directory with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

## Running the App

To run the FastAPI app, use the following command in your terminal:

```
uvicorn main:app --reload
```

The app should now be running on `http://localhost:8000`.

## API Documentation

Once the app is running, you can view the automatic API documentation at:

```
http://localhost:8000/docs
```

This will show you all available endpoints and allow you to test them directly from the browser.

## Authentication

The app uses OAuth2 password flow for authentication. To log in:

1. Navigate to the `/login` endpoint in the Swagger UI.
2. Use the following parameters in the request body:
   - `grant_type`: Set to "password"
   - `username`: Your email address
   - `password`: Your password
   - `scope`: Can be left empty
   - `client_id`: Can be left empty
   - `client_secret`: Can be left empty

3. Execute the request to receive an access token.

Use this access token in the "Authorize" button at the top of the Swagger UI to authenticate other endpoints.

## Available Endpoints

- `/login`: Authenticate and receive an access token
- `/register`: Create a new user account
- `/profile`: Get the current user's profile
- `/settings`: Update user settings
- `/reset-password`: Request a password reset email
- `/confirm`: Confirm email address after registration

## Security Note

This app is for demonstration purposes. In a production environment, ensure you follow best practices for security, including proper error handling and input validation.
