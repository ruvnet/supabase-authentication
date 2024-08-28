-- Create the profiles table
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

-- Create a function to automatically update the 'updated_at' column
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$
 language 'plpgsql';

-- Create a trigger to call this function whenever a row is updated
CREATE TRIGGER update_profiles_modtime
BEFORE UPDATE ON profiles
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- Create an index on user_id for faster lookups
CREATE INDEX idx_profiles_user_id ON profiles(user_id);

-- Add a unique constraint on user_id to ensure one profile per user
ALTER TABLE profiles ADD CONSTRAINT unique_user_profile UNIQUE (user_id);