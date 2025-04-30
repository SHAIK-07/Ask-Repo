from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from src.helper import load_embedding, repo_ingestion
from dotenv import load_dotenv
import os
import logging
import shutil
import stat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the application properly closes resources on shutdown
def cleanup_on_shutdown():
    try:
        if os.path.exists("db"):
            import chromadb
            # Close any open ChromaDB instances
            client = chromadb.Client()
            client.reset()
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {str(e)}")

# Register the cleanup function
import atexit
atexit.register(cleanup_on_shutdown)

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        logger.error(f"Error removing readonly file {path}: {str(e)}")

def cleanup_directories():
    """Clean up directories with better error handling for Git repositories"""
    def force_remove_readonly(func, path, _):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            logger.warning(f"Could not remove {path}: {str(e)}")

    try:
        # Force close any open database connections
        import sqlite3
        try:
            sqlite3.connect('db/chroma.sqlite3').close()
        except:
            pass

        # Force garbage collection to release file handles
        import gc
        gc.collect()

        if os.path.exists("repo"):
            logger.info("Removing existing repo directory")
            shutil.rmtree("repo", onerror=force_remove_readonly)

        if os.path.exists("db"):
            logger.info("Removing existing db directory")
            # Wait a moment for any file handles to be released
            import time
            time.sleep(1)
            shutil.rmtree("db", onerror=force_remove_readonly)

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        # Continue execution even if cleanup fails
        pass

# Run cleanup at startup
cleanup_directories()

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Initialize Flask app and limiter
app = Flask(__name__)
CORS(app)

# Simple in-memory limiter configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_options={"STORAGE_BACKEND": "memory"}
)

def validate_github_url(url):
    """Validate if the provided URL is a GitHub repository URL."""
    if not isinstance(url, str):
        return False
    url = url.lower()
    return url.startswith(('http://github.com/', 'https://github.com/')) and len(url.split('/')) >= 5

def initialize_chat_model():
    """Initialize the chat model and vector store."""
    try:
        embeddings = load_embedding()
        vectordb = Chroma(
            persist_directory="db",
            embedding_function=embeddings
        )
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.6,
            google_api_key=GOOGLE_API_KEY,
            max_output_tokens=2048  # Add token limit
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"  # Specify output key
        )
        
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectordb.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 4, "fetch_k": 20}  # Adjust retrieval parameters
            ),
            memory=memory,
            return_source_documents=True,  # Include source documents
            verbose=True
        )
        return qa_chain
    except Exception as e:
        logger.error(f"Error initializing chat model: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=["POST"])
@limiter.limit("10 per minute")
def process_repository():
    try:
        repo_url = request.form.get('question')
        
        if not repo_url:
            return jsonify({"error": "Repository URL is required"}), 400
        
        if not validate_github_url(repo_url):
            return jsonify({"error": "Invalid GitHub repository URL"}), 400

        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        # Clear existing repo and db if they exist
        cleanup_directories()

        # Clone and process the repository
        repo_ingestion(repo_url)
        
        # Initialize the vector store
        try:
            os.system("python store_index.py")
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            return jsonify({"error": "Failed to create search index"}), 500

        return jsonify({
            "success": True, 
            "message": "Repository processed successfully",
            "repo_name": repo_name
        })

    except Exception as e:
        logger.error(f"Error processing repository: {str(e)}")
        cleanup_directories()  # Cleanup on error
        return jsonify({"error": "Failed to process repository. Please try again."}), 500

@app.route("/get", methods=["POST"])
@limiter.limit("30 per minute")
def chat():
    try:
        message = request.form.get('msg')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400

        if not os.path.exists("db"):
            return jsonify({"error": "Please analyze a repository first"}), 400

        qa_chain = initialize_chat_model()
        result = qa_chain.invoke({
            "question": message
        })
        
        # Extract the answer from the result
        answer = result.get('answer', '')
        if not answer:
            return jsonify({"error": "No response generated"}), 500

        # Clean and format the response
        answer = answer.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route("/get_current_repo", methods=["GET"])
def get_current_repo():
    try:
        if os.path.exists("repo"):
            # Get the repository name from the cloned URL
            with open("repo/.git/config", "r") as f:
                config = f.read()
                # Extract repo name from the URL
                for line in config.split('\n'):
                    if 'url = ' in line:
                        url = line.strip().split('url = ')[1]
                        repo_name = url.split('/')[-1]
                        if repo_name.endswith('.git'):
                            repo_name = repo_name[:-4]
                        return jsonify({"repo_name": repo_name})
        return jsonify({"repo_name": None})
    except Exception as e:
        logger.error(f"Error getting repo name: {str(e)}")
        return jsonify({"error": "Failed to get repo name"}), 500

@app.route("/clear_cache", methods=["POST"])
def clear_cache():
    try:
        def force_remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            if os.path.exists(path):
                func(path)

        # Close any open file handles in the db directory
        if os.path.exists("db"):
            try:
                import gc
                gc.collect()  # Force garbage collection
                shutil.rmtree("db", onerror=force_remove_readonly)
            except Exception as e:
                logger.warning(f"Error removing db directory: {str(e)}")

        # Handle Git repository cleanup
        if os.path.exists("repo"):
            try:
                # Force close Git repository
                import git
                try:
                    repo = git.Repo("repo")
                    repo.git.gc()
                    repo.close()
                except:
                    pass

                # Wait for handles to be released
                import time
                time.sleep(1)

                # Remove read-only attributes recursively
                for root, dirs, files in os.walk("repo", topdown=False):
                    for name in files:
                        try:
                            file_path = os.path.join(root, name)
                            os.chmod(file_path, stat.S_IWRITE)
                        except:
                            pass
                    for name in dirs:
                        try:
                            dir_path = os.path.join(root, name)
                            os.chmod(dir_path, stat.S_IWRITE)
                        except:
                            pass

                shutil.rmtree("repo", onerror=force_remove_readonly)
            except Exception as e:
                logger.warning(f"Error removing repo directory: {str(e)}")

        return jsonify({"message": "Cache cleared successfully"}), 200
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({"error": "Failed to clear cache"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

























