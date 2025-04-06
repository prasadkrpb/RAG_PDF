import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Cassandra
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
import cassio

# Load environment variables
load_dotenv()
# Connect to Astra DB
cassio.init(
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    database_id=os.getenv("ASTRA_DB_ID"),
    keyspace=os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")
)

st.set_page_config(page_title="📄 PDF Query GenAI", layout="wide")
st.title("📄 Upload and Query Your PDFs (RAG (Astra DB) + ChatGroq (gemma2-9b-it))")

# Set up embedding and vectorstore
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Cassandra(
    embedding=embeddings,
    table_name="pdf_chunks",
    session=None
)

# 🧹 Add a delete button
if st.button("🗑️ Clear All Stored Chunks from Astra DB"):
    vectorstore.delete_collection()
    st.warning("🚨 All chunks deleted from the 'pdf_chunks' table!")

# Upload multiple PDFs
uploaded_files = st.file_uploader("📤 Upload PDF files (up to 10)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded.")
    
    if st.button("📚 Process and Upload PDFs to Astra DB"):
        all_chunks = []
        
        for uploaded_file in uploaded_files[:10]:  # limit to 10 files
            reader = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_text(text)
            all_chunks.extend(chunks)

            st.info(f"✅ Processed {uploaded_file.name} with {len(chunks)} chunks.")
        
        vectorstore.add_texts(all_chunks)
        st.success(f"✅ Uploaded total {len(all_chunks)} chunks from {len(uploaded_files)} PDFs to Astra DB!")

# Ask questions
st.markdown("---")
query = st.text_input("🔍 Ask a question based on the uploaded PDFs:")
if query:
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatGroq(temperature=0, model_name="gemma2-9b-it")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    with st.spinner("🔎 Thinking..."):
        result = qa_chain({"query": query})

    st.markdown("### 📌 Answer")
    st.write(result["result"])

    st.markdown("### 📚 Source Documents")
    for i, doc in enumerate(result["source_documents"]):
        st.markdown(f"**Source {i+1}:**")
        st.write(doc.page_content[:500] + "...")
