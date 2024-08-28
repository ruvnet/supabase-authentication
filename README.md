# Streamlit and FastAPI Authentication with Supabase

This project showcases a comprehensive authentication system using Supabase as the backend, implemented with both Streamlit and FastAPI frontends. It demonstrates how to build secure, user-friendly authentication flows in two popular Python web frameworks.

### Streamlit App
The Streamlit application provides a user-friendly, interactive interface for user registration, login, profile management, and settings customization. It leverages Streamlit's simplicity to create a responsive web app with minimal code.

### FastAPI Backend
The FastAPI backend offers a robust API for handling authentication and user data management. It implements OAuth2 password flow for secure token-based authentication, as shown in the image. The API includes endpoints for user registration, login, profile retrieval, and settings updates.

This dual-frontend approach allows developers to explore different implementation styles while sharing a common Supabase backend. Whether you prefer the rapid prototyping capabilities of Streamlit or the high-performance, type-safe API development with FastAPI, this project provides a solid foundation for building authenticated web applications.

# Streamlit Supabase Authentication App

This Streamlit application demonstrates user authentication and profile management using Supabase as the backend.

## Prerequisites

- Python 3.7+
- Streamlit
- Supabase account and project

## Setup

1. Clone the repository to your local machine.

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Supabase project:
   - Create a new project in Supabase
   - Enable Email Auth in Authentication > Providers
   - Create a `profiles` table in your Supabase database with the following SQL:

     ```sql
     CREATE TABLE profiles (
         id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
         user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
         full_name text,
         email text,
         bio text,
         age integer,
         theme text DEFAULT 'light',
         notifications boolean DEFAULT true,
         language text DEFAULT 'en',
         created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
         updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
     );

     CREATE OR REPLACE FUNCTION update_modified_column()
     RETURNS TRIGGER AS $$
     BEGIN
         NEW.updated_at = now();
         RETURN NEW;
     END;
     $$ language 'plpgsql';

     CREATE TRIGGER update_profiles_modtime
     BEFORE UPDATE ON profiles
     FOR EACH ROW
     EXECUTE FUNCTION update_modified_column();

     CREATE INDEX idx_profiles_user_id ON profiles(user_id);

     ALTER TABLE profiles ADD CONSTRAINT unique_user_profile UNIQUE (user_id);
     ```

4. Create a `.env` file in the root directory with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

## Running the App

To run the Streamlit app, use the following command in your terminal:

```
streamlit run main.py
```

The app should now be running on `http://localhost:8501`.

## Features

- User Registration
- User Login
- Password Reset
- Profile Management
- User Settings (theme, notifications, language)

## File Structure

- `main.py`: The main Streamlit app
- `utils/supabase_client.py`: Supabase client initialization
- `src/auth/`: Authentication-related functions
- `src/pages/`: Different pages of the app (home, profile, settings)

## Customization

You can customize the app by modifying the following:

- `src/pages/`: Add or modify pages
- `src/auth/`: Adjust authentication logic
- `utils/supabase_client.py`: Add more Supabase-related functions

## Troubleshooting

If you encounter any issues:

1. Ensure your Supabase credentials are correct in the `.env` file
2. Check that you've created the `profiles` table in your Supabase database
3. Verify that you've installed all required dependencies

For more help, refer to the Streamlit and Supabase documentation.

## Security Note

This app is for demonstration purposes. In a production environment, ensure you follow best practices for security, including proper error handling and input validation.
 
# FastAPI Supabase Authentication App

This project demonstrates user authentication and profile management using Supabase as the backend, with both Streamlit and FastAPI frontends.

## Prerequisites

- Python 3.7+
- Streamlit
- FastAPI
- Uvicorn
- Supabase account and project

## Setup

1. Clone the repository to your local machine.

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Supabase project as described in the previous instructions.

4. Create a `.env` file in the root directory with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

## Running the FastAPI App

To run the FastAPI app, use the following command:

```
uvicorn fastapi.api:app --reload
```

The FastAPI app should now be running on `http://localhost:8000`.

## FastAPI Details

The FastAPI application is defined in `./fastapi/api.py`. It provides the following endpoints:

- `/login` (POST): Authenticate a user and return an access token
- `/register` (POST): Register a new user
- `/profile` (GET): Get the current user's profile
- `/settings` (PUT): Update user settings
- `/reset-password` (POST): Request a password reset email
- `/confirm` (GET): Confirm email address after registration

### Authentication

The FastAPI app uses OAuth2 password flow for authentication. To log in:

1. Send a POST request to `/login` with the following form data:
   - `grant_type`: "password"
   - `username`: Your email address
   - `password`: Your password
   - `scope`: (Optional)
   - `client_id`: (Optional)
   - `client_secret`: (Optional)

2. Use the returned access token in the `Authorization` header for authenticated requests.

## API Documentation

FastAPI provides automatic API documentation. Once the FastAPI app is running, you can access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## File Structure

- `main.py`: The main Streamlit app
- `fastapi/api.py`: The FastAPI application
- `utils/supabase_client.py`: Supabase client initialization
- `src/auth/`: Authentication-related functions
- `src/pages/`: Different pages of the Streamlit app

## Customization

You can customize both the Streamlit and FastAPI apps by modifying their respective files and adding new endpoints or pages as needed.

## Security Note

This project is for demonstration purposes. In a production environment, ensure you follow best practices for security, including proper error handling, input validation, and secure token management.
 
