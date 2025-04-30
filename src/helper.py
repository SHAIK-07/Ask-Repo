import os
import logging
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.language.language_parser import LanguageParser
from langchain.text_splitter import Language
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY



#clone any github repositories 
def repo_ingestion(repo_url):
    try:
        os.makedirs("repo", exist_ok=True)
        repo_path = "repo/"
        Repo.clone_from(repo_url, to_path=repo_path)
    except Exception as e:
        logging.error(f"Failed to clone repository: {str(e)}")
        raise




#Loading repositories as documents
def load_repo(repo_path):
    try:
        loader = GenericLoader.from_filesystem(repo_path,
                                        glob = "**/*",
                                       suffixes=[".py"],
                                       parser = LanguageParser(language=Language.PYTHON, parser_threshold=500)
                                        )
    except Exception as e:
        logging.error(f"Failed to clone repository: {str(e)}")
        raise
    
    documents = loader.load()

    return documents




#Creating text chunks 
def text_splitter(documents):
    try:
        documents_splitter = RecursiveCharacterTextSplitter.from_language(language = Language.PYTHON,
                                                             chunk_size = 2000,
                                                             chunk_overlap = 200)
    except Exception as e:
        logging.error(f"Failed to clone repository: {str(e)}")
        raise
    
    text_chunks = documents_splitter.split_documents(documents)

    return text_chunks



#loading embeddings model
def load_embedding():
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY,
            task_type="retrieval_query"
        )
    except Exception as e:
        logging.error(f"Failed to load embeddings: {str(e)}")
        raise
    
    return embeddings



