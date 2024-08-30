-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a table to store documents
CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  title TEXT,
  body TEXT,
  embedding VECTOR(384)
);

-- Create an index on the embedding column for faster similarity searches
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);

-- Create a function to match documents
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding VECTOR(384),
  match_threshold FLOAT,
  match_count INT
)
RETURNS TABLE (
  id BIGINT,
  title TEXT,
  body TEXT,
  similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    documents.id,
    documents.title,
    documents.body,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
$$
;

-- Create a table to store user-specific indexes
CREATE TABLE IF NOT EXISTS user_indexes (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  index_name TEXT NOT NULL,
  embedding VECTOR(384)
);

-- Create an index on the embedding column for user-specific indexes
CREATE INDEX ON user_indexes USING ivfflat (embedding vector_cosine_ops);

-- Create a function to handle new user signups
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_indexes (id, index_name)
  VALUES (NEW.id, 'default_index');
  RETURN NEW;
END;
$$
 LANGUAGE plpgsql SECURITY DEFINER;

-- Create a trigger to call the function on new user signups
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Enable Row Level Security (RLS) on the documents table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows users to see only their own documents
CREATE POLICY "Users can only access their own documents" ON documents
  FOR ALL USING (auth.uid() = user_id);

-- Add a user_id column to the documents table to associate documents with users
ALTER TABLE documents ADD COLUMN user_id UUID REFERENCES auth.users(id);