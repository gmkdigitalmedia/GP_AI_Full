"""
Setup script for Calendar AI Agent
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="calendar-ai-agent",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@example.com",
    description="AI-powered calendar management agent using Google Calendar and Vertex AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/calendar-ai-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "web": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "jinja2>=3.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "calendar-ai-agent=main:main",
        ],
    },
    keywords="calendar ai agent google-calendar vertex-ai natural-language scheduling",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/calendar-ai-agent/issues",
        "Source": "https://github.com/yourusername/calendar-ai-agent",
        "Documentation": "https://github.com/yourusername/calendar-ai-agent/wiki",
    },
)