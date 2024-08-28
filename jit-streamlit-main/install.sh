#!/bin/bash

# Create the main files
touch main.py config.py setup.py

# Create pyproject.toml for Poetry
cat << EOF > pyproject.toml
[tool.poetry]
name = "streamlit-supabase-app"
version = "0.1.0"
description = "A Streamlit app with Supabase authentication"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
streamlit = "^1.12.0"
supabase = "^1.0.3"

[tool.poetry.dev-dependencies]
pytest = "^7.1.2"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
EOF

# Create setup.py
cat << EOF > setup.py
from setuptools import setup, find_packages

setup(
    name="streamlit-supabase-app",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.12.0",
        "supabase>=1.0.3",
    ],
)
EOF

# Create utils directory and its files
mkdir -p utils
touch utils/__init__.py utils/supabase_client.py

# Create auth directory and its files
mkdir -p auth
touch auth/__init__.py auth/forms.py auth/handlers.py

# Create pages directory and its files
mkdir -p pages
touch pages/__init__.py pages/home.py pages/profile.py pages/settings.py

# Create tests directory
mkdir -p tests
touch tests/__init__.py tests/test_main.py

echo "Project structure created successfully!"

# Print the directory structure
echo "Directory structure:"
if command -v tree &> /dev/null; then
    tree
else
    find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'
fi

echo "You can now copy the content into each file."
echo "Remember to update the pyproject.toml and setup.py files with your specific project details."