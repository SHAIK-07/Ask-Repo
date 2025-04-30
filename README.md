# Source Code Analysis with Generative AI 🚀

A powerful tool that leverages Google's Gemini AI to analyze GitHub repositories and provide intelligent insights about the codebase.

## 🌟 Features

- **Repository Analysis**: Analyze any public GitHub repository
- **Interactive Chat Interface**: Ask questions about the codebase
- **Code Understanding**: Get detailed explanations of code structure and functionality
- **Smart Context**: AI remembers conversation context for better responses
- **Rate Limiting**: Built-in protection against API abuse
- **Responsive UI**: Modern, user-friendly interface
- **Real-time Processing**: Quick analysis and response generation

## 🛠️ Tech Stack

- **Backend**:
  - Python 3.10
  - Flask (Web Framework)
  - LangChain (LLM Framework)
  - Google Gemini Pro (LLM Model)
  - ChromaDB (Vector Database)
  - GitPython (Repository Management)

- **Frontend**:
  - HTML5
  - CSS3
  - JavaScript/jQuery
  - Bootstrap 5

## 📋 Prerequisites

- Python 3.10 or higher
- Conda (recommended for environment management)
- Google API Key (Gemini Pro access)
- Git installed on your system

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/SHAIK-07/End-to-end-Source-Code-Analysis-Generative-AI-main
cd End-to-end-Source-Code-Analysis-Generative-AI-main
```

2. **Create and activate Conda environment**
```bash
conda create -n llmapp python=3.10 -y
conda activate llmapp
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
Create a `.env` file in the root directory:
```ini
GOOGLE_API_KEY = "your_google_api_key_here"
```

## 🎯 Usage

1. **Start the application**
```bash
python app.py
```

2. **Access the web interface**
- Open your browser and navigate to `http://localhost:5000`
- Enter a GitHub repository URL
- Click "Analyze Repository"
- Start asking questions about the codebase

## 💡 Example Questions

- "What is the main functionality of this repository?"
- "Explain the architecture of this project"
- "What are the key dependencies used?"
- "How does the error handling work?"
- "Show me the main API endpoints"

## 🔒 Rate Limits

- Repository Analysis: 10 requests per minute
- Chat Queries: 30 requests per minute
- Daily Limit: 200 requests per day

## 🛠️ Project Structure

```
├── app.py                 # Main Flask application
├── src/
│   ├── __init__.py
│   └── helper.py         # Helper functions
├── static/
│   ├── script.js         # Frontend JavaScript
│   └── style.css         # CSS styles
├── templates/
│   └── index.html        # Main HTML template
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## ⚠️ Important Notes

- Ensure your Google API key has access to Gemini Pro
- Large repositories may take longer to analyze
- The tool works best with public repositories
- Keep your API keys secure and never commit them to version control

## 🐳 Docker Deployment

You can run this application using Docker:

1. **Build and start the containers**
```bash
docker-compose up --build -d
```

2. **Access the application**
- Open your browser and navigate to `http://localhost:8080`

3. **View logs**
```bash
docker-compose logs -f
```

4. **Stop the application**
```bash
docker-compose down
```

### Environment Variables
When using Docker, create a `.env` file with:
```ini
GOOGLE_API_KEY=your_google_api_key_here
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

- **Shaik Hidayathulla**
  - GitHub: [@SHAIK-07](https://github.com/SHAIK-07)

## 🙏 Acknowledgments

- Google Gemini Pro for AI capabilities
- LangChain community for the excellent framework
- All contributors and users of this project

---




