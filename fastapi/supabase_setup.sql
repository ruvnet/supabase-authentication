-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the profiles table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    full_name TEXT,
    bio TEXT,
    age INT,
    theme TEXT DEFAULT 'light',
    notifications BOOLEAN DEFAULT true,
    language TEXT DEFAULT 'en'
);

-- Create a function to handle new user signups
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id)
    VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a trigger to call the function on new user signups
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create a table for storing user-specific vector indexes
CREATE TABLE IF NOT EXISTS user_indexes (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    index_name TEXT NOT NULL,
    embedding VECTOR(1536)
);

-- Create an index on the embedding column for faster similarity searches
CREATE INDEX ON user_indexes USING ivfflat (embedding vector_cosine_ops);
