# Business Intelligence Agent

An AI-powered competitive analysis tool built with React (Next.js) frontend and FastAPI backend. This application allows users to input their business description and receive comprehensive competitor analysis powered by OpenAI.

## 🚀 Features

- **AI-Powered Analysis**: Uses OpenAI to analyze competitors and market positioning
- **Web Scraping**: Automatically discovers and analyzes competitor websites
- **Real-time Processing**: Live updates during analysis with loading states
- **Modern UI**: Built with React, Next.js, and Tailwind CSS
- **RESTful API**: FastAPI backend with automatic API documentation

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### For Mac Users:
- **Node.js** (v18 or higher): [Download from nodejs.org](https://nodejs.org/)
- **Python** (v3.8 or higher): [Download from python.org](https://www.python.org/)
- **Git**: Usually pre-installed, or install via Xcode Command Line Tools

### For Windows Users:
- **Node.js** (v18 or higher): [Download from nodejs.org](https://nodejs.org/)
- **Python** (v3.8 or higher): [Download from python.org](https://www.python.org/)
- **Git**: [Download from git-scm.com](https://git-scm.com/)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd reactFastApiAgent
```

### 2. Environment Variables Setup

Create a `.env` file in the `backend` directory:

```bash
# Navigate to backend directory
cd backend

# Create .env file
touch .env  # Mac/Linux
# OR
echo. > .env  # Windows Command Prompt
```

Add the following to your `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**To get your OpenAI API key:**
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy and paste it into your `.env` file

### 3. Backend Setup (FastAPI)

#### Mac Users:
```bash
# Navigate to backend directory (if not already there)
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload --port 8001
```

#### Windows Users:
```cmd
# Navigate to backend directory (if not already there)
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload --port 8001
```

The backend will be running at `http://localhost:8001`

### 4. Frontend Setup (React/Next.js)

Open a new terminal window/tab and:

#### Mac Users:
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

#### Windows Users:
```cmd
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be running at `http://localhost:3000`

## 🖥️ Usage

1. **Start both servers** (backend on port 8001, frontend on port 3000)
2. **Open your browser** and go to `http://localhost:3000`
3. **Enter your business description** in the text area
4. **Click "Analyze Competitors"** to start the AI analysis
5. **Wait for results** - the analysis typically takes 30-60 seconds

### Example Business Descriptions:
- "AI-powered customer service platform for e-commerce companies"
- "Project management tool for remote software development teams"
- "Online marketplace for handmade crafts and artisan goods"

## 📁 Project Structure

```
reactFastApiAgent/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (create this)
└── frontend/
    ├── pages/
    │   ├── _app.tsx         # Next.js app wrapper
    │   └── index.tsx        # Main application page
    ├── styles/
    │   └── globals.css      # Global styles
    ├── package.json         # Node.js dependencies
    └── tailwind.config.js   # Tailwind CSS configuration
```

## 🔧 API Endpoints

The backend provides the following endpoints:

- `POST /analyze-competitors` - Analyze competitors for a given business
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

Visit `http://localhost:8001/docs` to explore the API interactively.

## 🚨 Troubleshooting

### Common Issues:

#### Backend Issues:
1. **"ModuleNotFoundError"**: Make sure your virtual environment is activated and dependencies are installed
2. **"OPENAI_API_KEY not set"**: Check your `.env` file in the backend directory
3. **Port 8001 already in use**: Change the port with `uvicorn main:app --reload --port 8002`

#### Frontend Issues:
1. **"Cannot connect to backend"**: Ensure backend is running on port 8001
2. **CORS errors**: Backend is configured for `localhost:3000` - make sure frontend is running on this port
3. **"npm install fails"**: Try clearing npm cache: `npm cache clean --force`

#### Mac-Specific:
- If Python3 command not found: `brew install python3`
- If npm not found: Reinstall Node.js from the official website

#### Windows-Specific:
- If Python command not found: Add Python to your PATH during installation
- If npm not found: Reinstall Node.js and ensure "Add to PATH" is checked
- Use PowerShell or Command Prompt as Administrator if you encounter permission issues

### Virtual Environment Issues:

#### If virtual environment activation fails:

**Mac/Linux:**
```bash
# Alternative activation methods
source ./venv/bin/activate
# OR
. venv/bin/activate
```

**Windows:**
```cmd
# Alternative activation methods
venv\Scripts\activate.bat
# OR for PowerShell
venv\Scripts\Activate.ps1
```

## 🚀 Production Deployment

### Backend Deployment:
1. Set environment variables on your hosting platform
2. Use `uvicorn main:app --host 0.0.0.0 --port $PORT` for production
3. Consider using Gunicorn for production: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker`

### Frontend Deployment:
1. Build the application: `npm run build`
2. Start production server: `npm run start`
3. Update API endpoint in the frontend to point to your production backend

## 📝 License

This project is for educational purposes. Please ensure you comply with OpenAI's usage policies and terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📧 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are installed correctly
3. Verify your OpenAI API key is valid and has sufficient credits
4. Check that both servers are running on the correct ports

---

**Happy analyzing! 🎉**