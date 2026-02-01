import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.tools.retriever import create_retriever_tool
from langchain_text_splitters import RecursiveCharacterTextSplitter

file_path = os.path.join(os.path.dirname(__file__), "..", "Data", "company_policy.pdf")
loader = PyPDFLoader(file_path)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_docs = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
client_settings = Settings(anonymized_telemetry=False)
vectorstore = Chroma.from_documents(split_docs, embeddings, client_settings=client_settings)

retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

companypolicy_tool = create_retriever_tool(
    retriever,
    name="companypolicy_tool",
    description="Search and retrieve company policy from PDF"
)