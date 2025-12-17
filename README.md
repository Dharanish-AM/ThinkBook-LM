# ThinkBook LM 🧠

A private, offline-first AI research assistant designed for secure document analysis. ThinkBook LM runs entirely on your local machine, using local LLMs and vector databases to index and chat with your documents without any data leaving your device.

![ThinkBook LM UI](https://placehold.co/1200x600/1e1e1e/FFF?text=ThinkBook+LM+Dashboard)

## ✨ Key Features

-   **🔒 100% Private**: Runs locally. No cloud APIs, no data leakage.
-   **📚 Multi-Modal Support**:
    -   **Documents**: PDF, DOCX, TXT
    -   **Multimedia**: Audio (WAV/MP3) and Video (MP4) transcription via Whisper.
    -   **Images**: OCR and visual analysis.
-   **🤖 Intelligent RAG**:
    -   **Vector Search**: Powered by **Qdrant** and **SentenceTransformers** (all-MiniLM-L6-v2).
    -   **Expert Answers**: Grounded responses using **Ollama (Llama 3.1 8B)**.
-   **🎨 Premium UI**:
    -   Modern **Glassmorphism** design with Dark Mode.
    -   Smooth **Animations** and interactive Drag & Drop.
    -   **Rich Text Chat**: Supports tables, code blocks, and blockquotes using Markdown.

## 🛠️ Tech Stack

### Backend (Server)
-   **Framework**: FastAPI (Python 3.10+)
-   **Vector DB**: Qdrant (Local)
-   **LLM Engine**: Ollama (Llama 3.1)
-   **Embeddings**: SentenceTransformers
-   **Processing**: PyPDF2, Whisper, MoviePy

### Frontend (Client)
-   **Framework**: React 18 + Vite
-   **Styling**: TailwindCSS 4, Shadcn/UI
-   **Icons**: Lucide React
-   **State**: Hooks + REST API

## 🚀 Getting Started

### Prerequisites
-   **Python 3.10+**
-   **Node.js 18+**
-   **Ollama**: Installed and running (`ollama serve`). Pull the model:
    ```bash
    ollama pull llama3.1:8b
    ```

### 1. Backend Setup

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```
*Server runs on `http://localhost:8000`*

### 2. Frontend Setup

```bash
cd client

# Install dependencies
npm install

# Start the dev server
npm run dev
```
*Client runs on `http://localhost:5173`*

## 🧪 Testing

Run the end-to-end test suite to verify file uploads and retrieval:

```bash
cd server/tests
python e2e_test.py
```

## 📜 License

MIT License. Built for local privacy.
