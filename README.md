# KnowMate AI 📚

**An AI-powered document question-answering assistant built with Streamlit and Google Gemini.**

KnowMate AI lets users upload documents and ask questions in natural language. It retrieves relevant document content and generates answers grounded in the provided information.

## ✨ Features

- 📄 Upload documents for question answering
- 🔍 Retrieve relevant text from documents
- 💬 Ask questions in natural language
- 🧠 Handle follow-up questions using conversation history
- 🛡️ Reduce hallucinations by acknowledging missing information
- 📌 Include source page information when available
- 🌐 Respond in the language of the user's question

## 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini API
- PyPDF

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd knowmate-ai
```

### 2. Install dependencies

```bash
pip install streamlit pypdf google-genai
```

### 3. Configure your API key

Create `.streamlit/secrets.toml` and add:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Keep your API key private. Never commit `secrets.toml` to GitHub.

### 4. Run the application

```bash
streamlit run app.py
```

## 🧪 Tested Capabilities

- Relevant information retrieval
- Follow-up question understanding
- Handling questions about information missing from the document
- Answering document-based safety questions

## 🎯 Project Goal

The goal of KnowMate AI is to make document-based information retrieval easier through a simple conversational interface, while keeping answers grounded in the uploaded content.

## 👨‍💻 Author

Built as an AI engineering portfolio project.
## 🏗️ How It Works

1. **Document Upload:** The user uploads a document through the Streamlit interface.
2. **Text Extraction:** Text is extracted from the uploaded document.
3. **Relevant Context Retrieval:** The application identifies text chunks relevant to the user's question.
4. **AI Answer Generation:** Google Gemini generates an answer using the retrieved document context and conversation history.
5. **Grounded Responses:** The assistant aims to answer from the provided document and acknowledges when requested information cannot be found.

## 🔮 Future Improvements

- Add support for more document formats.
- Improve retrieval accuracy with embedding-based semantic search.
- Add automated evaluation tests for retrieval and answer quality.
- Improve source citations and document navigation.
