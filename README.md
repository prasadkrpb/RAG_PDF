📦 Astra DB Integration Guide for PDF RAG App

🔐 1. Connect to Astra DB
Connect to Astra DB using the following credentials:

Database ID
Application Token
Keyspace Name
These are required to authenticate and interact with the vector store.

🧹 2. Clean Up Old Chunks (If Needed)
Before uploading new documents, clear existing chunks if you're concerned about hitting limits.

Astra DB Free Tier Limits:

80,000 rows per table
1 GB total storage
5 GB/month data transfer
Example:
If you have 258 chunks:
Remaining capacity = 80,000 - 258 = 79,742 chunks

🔍 3. Check Chunk Count via CQL
You can use Cassandra Query Language (CQL) to check current chunk count:

USE your_keyspace_name;
SELECT COUNT(*) FROM your_table_name;



📤 4. Upload & Embed Multiple PDFs
Upload and process multiple PDF files:

Split content into chunks
Generate embeddings (e.g., using all-MiniLM-L6-v2)
Store vectors in Astra DB
This creates the knowledge base for your GenAI app.

💬 5. Ask Questions Using RAG
Once PDFs are uploaded:

Ask any question related to the content
The app retrieves relevant chunks
An LLM (like gemma2-9b-it) generates a context-aware answer
🚀 Just shoot your questions — and get answers based only on the content of your uploaded PDFs.
