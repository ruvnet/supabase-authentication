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
