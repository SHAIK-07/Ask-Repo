from src.helper import repo_ingestion, load_repo, text_splitter, load_embedding
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
import os

documents = load_repo("repo/")
text_chunks = text_splitter(documents)
embeddings = load_embedding()

#storing vector in chromadb
vectordb = Chroma.from_documents(text_chunks, embedding=embeddings, persist_directory='./db')
# Remove the persist() call as it's no longer needed
