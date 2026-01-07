# ThinkBook LM 🧠

<div align="center">

![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.2.0-009688.svg)
![Electron](https://img.shields.io/badge/electron-39-47848f.svg)

**A Privacy-First AI Research Assistant for Secure Document Analysis**

*Chat with your documents using local LLMs - no cloud, no tracking, no compromises*

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#️-architecture) • [API Docs](#-api-documentation) • [Testing](#-testing)

</div>

---

## 🌟 Overview

ThinkBook LM is a **100% local, privacy-focused** AI assistant that lets you chat with your documents using state-of-the-art language models. Everything runs on your machine - your data never leaves your device.

Built with a modern tech stack (FastAPI + React + Electron), it provides enterprise-grade document intelligence through a clean desktop interface, making AI-powered research accessible while keeping your information completely private.

### Why ThinkBook LM?

- 🔒 **Complete Privacy**: Zero telemetry, zero cloud APIs, zero data leaks
- ⚡ **Production-Ready**: File validation, streaming responses, comprehensive tests
- 🎯 **Developer-Friendly**: OpenAPI docs, typed APIs, modular architecture
- 📦 **Desktop-First**: Native Electron app with cross-platform installers
- 🧠 **State-of-the-Art**: RAG pipeline with Qdrant + Llama 3.1 8B

---

## ✨ Features

### 🔐 Privacy & Security
- **Offline-First Architecture** - No internet required after initial setup
- **File Validation** - MIME type verification, 50MB size limits, extension whitelisting
- **Path Protection** - Automatic filename sanitization prevents directory traversal
- **Content Verification** - Real file type detection using `python-magic` (with graceful fallback)
- **Duplicate Prevention** - Automatic detection of already-indexed files

### 📚 Document Processing
| Format | Technology | Capabilities |
|--------|-----------|--------------|
| **PDF** | PyPDF2 | Multi-page extraction, metadata preservation |
| **DOCX** | python-docx | Full document parsing with formatting |
| **TXT** | Built-in | Direct text ingestion |
| **Images** | Tesseract OCR | PNG/JPG text extraction |
| **Audio** | OpenAI Whisper | WAV/MP3 transcription |
| **Video** | MoviePy + Whisper | MP4 audio extraction & transcription |

### 🤖 AI Capabilities
- **RAG Pipeline** - Retrieval-Augmented Generation for accurate, grounded responses
- **Vector Search** - Qdrant with 384-dimensional embeddings (all-MiniLM-L6-v2)
- **Local LLM** - Llama 3.1 8B via Ollama (no API keys, no rate limits)
- **Streaming** - Real-time token generation via Server-Sent Events
- **Intelligent Chunking** - 800-token chunks with 150-token overlap for context coherence

### 🎨 User Experience
- **Modern UI** - React 18 with shadcn/ui components and TailwindCSS 4
- **Dark Mode** - System-aware theme switching with next-themes
- **Responsive** - Optimized for desktop and tablet layouts
- **Live Progress** - Real-time upload indicators and streaming chat responses
- **Markdown Support** - Rich rendering with tables, code blocks, and GFM syntax

### 🛠️ Developer Experience
- **OpenAPI/Swagger** - Interactive API docs at `/docs` with examples
- **Full Test Coverage** - 30+ unit tests across security, embeddings, chunking, parsers
- **Environment Config** - Centralized settings via `.env` files
- **Typed APIs** - Pydantic models for compile-time safety
- **Electron Builds** - Configured for macOS/Windows/Linux distribution

---

## 🆕 What's New in v0.2.0

| Feature | Description | Impact |
|---------|-------------|--------|
| **Streaming Responses** | SSE-based real-time LLM output | ⚡ Better UX |
| **Enhanced Security** | MIME validation + size limits + sanitization | 🛡️ Production-ready |
| **Unit Tests** | 30+ tests for parsers, security, RAG | ✅ Quality assurance |
| **API Documentation** | Full OpenAPI spec with examples | 📖 Better DX |
| **Desktop Builds** | Electron builder configs for all platforms | 📦 Easy distribution |
| **Environment Config** | `.env` support for client/server | 🔧 Flexible deployment |
| **Database Sync** | Auto-validation of file registry vs Qdrant | 🔄 Data consistency |

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Python** | 3.10+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | Frontend build | [nodejs.org](https://nodejs.org/) |
| **Ollama** | Latest | Local LLM | [ollama.ai](https://ollama.ai/) |

### 1️⃣ Clone & Setup Ollama

```bash
# Clone repository
git clone https://github.com/Dharanish-AM/ThinkBook-LM.git
cd ThinkBook-LM

# Start Ollama (in separate terminal)
ollama serve

# Pull Llama 3.1 model
ollama pull llama3.1:8b
```

### 2️⃣ Backend Setup

```bash
cd server

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install libmagic for enhanced MIME validation
# macOS:
brew install libmagic
# Ubuntu/Debian:
sudo apt-get install libmagic1
# Note: Server works fine without libmagic (graceful fallback)

# Start development server
uvicorn app.main:app --reload
```

✅ **Backend running**  
- API: http://localhost:8000  
- Swagger Docs: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc

### 3️⃣ Frontend Setup

```bash
# In new terminal
cd client

# Install dependencies
npm install

# Optional: Configure API endpoint
cp .env.example .env
# Edit .env if needed: VITE_API_URL=http://localhost:8000

# Start development server
npm run dev
```

✅ **Frontend running** at http://localhost:5173

### 4️⃣ Using the Application

1. **Upload Documents**: Drag & drop or click to upload (PDF, DOCX, TXT, images, audio, video)
2. **Wait for Indexing**: Progress bar shows chunking and embedding status
3. **Ask Questions**: Type queries and get AI-generated answers with source citations
4. **View Sources**: Check which document chunks were used for each answer

### 5️⃣ Desktop App Build (Optional)

```bash
cd client

# Development with hot reload
npm run electron:dev

# Production builds
npm run electron:build        # Current platform
npm run electron:build:mac    # macOS (DMG + ZIP)
npm run electron:build:win    # Windows (NSIS + Portable)
npm run electron:build:linux  # Linux (AppImage + DEB + RPM)
```

Build artifacts saved to `client/dist/`

---

## 🏗️ Architecture

### System Overview

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│                  │         │                  │         │                  │
│   React Client   │ ◄─────► │  FastAPI Server  │ ◄─────► │   Qdrant DB      │
│   (Port 5173)    │  HTTP   │   (Port 8000)    │ Vector  │   (SQLite)       │
│                  │   REST  │                  │  Store  │                  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
                                      │                            
                                      ▼                            
                              ┌──────────────────┐                
                              │                  │                
                              │  Ollama LLM      │                
                              │  (Port 11434)    │                
                              │  Llama 3.1 8B    │                
                              │                  │                
                              └──────────────────┘                
```

### Tech Stack

#### Backend Stack
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | Latest | Async REST API with auto-docs |
| **Vector DB** | Qdrant Client | Latest | Semantic search (local SQLite mode) |
| **Embeddings** | SentenceTransformers | Latest | all-MiniLM-L6-v2 (384-dim vectors) |
| **LLM** | Ollama | Latest | Local Llama 3.1 8B inference |
| **PDF Parser** | PyPDF2 | Latest | Multi-page PDF text extraction |
| **DOCX Parser** | python-docx | Latest | Word document processing |
| **OCR** | Tesseract (pytesseract) | Latest | Image text extraction |
| **Audio** | OpenAI Whisper | Latest | Speech-to-text transcription |
| **Video** | MoviePy | Latest | Audio extraction from video |
| **Security** | python-magic | Latest | MIME type verification (optional) |
| **Validation** | Pydantic | Latest | Request/response schemas |
| **Testing** | pytest | Latest | Unit and integration tests |

#### Frontend Stack
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 18.3.1 | Component-based UI |
| **Build Tool** | Vite | Latest | Fast dev server & bundling |
| **UI Library** | shadcn/ui + Radix | Latest | Accessible component primitives |
| **Styling** | TailwindCSS | 4.x | Utility-first CSS |
| **State** | TanStack Query | 5.x | Server state & caching |
| **Routing** | React Router | 6.x | Client-side navigation |
| **Markdown** | react-markdown | Latest | Rich text rendering |
| **GFM Support** | remark-gfm | Latest | GitHub Flavored Markdown |
| **Desktop** | Electron | 39.x | Cross-platform packaging |
| **Theme** | next-themes | Latest | Dark/light mode toggle |
| **Icons** | lucide-react | Latest | Beautiful icon set |
| **Forms** | react-hook-form | Latest | Form state management |

### Data Flow

#### 📤 Upload & Indexing Flow
```
1. User uploads file via React UI
   ↓
2. FastAPI validates file:
   - Size check (max 50MB)
   - MIME type verification (python-magic)
   - Extension whitelist check
   - Duplicate detection
   ↓
3. Parser registry routes file:
   - PDF → PyPDF2
   - DOCX → python-docx
   - TXT → direct read
   - Images → Tesseract OCR
   - Audio → Whisper transcription
   - Video → MoviePy + Whisper
   ↓
4. Text chunking:
   - Split into 800-token chunks
   - 150-token overlap for context
   - tiktoken for accurate counting
   ↓
5. Embedding generation:
   - SentenceTransformers encode
   - 384-dimensional vectors
   - Batched processing
   ↓
6. Qdrant storage:
   - Vectors + metadata
   - File registry update
   - Local SQLite persistence
```

#### 💬 Query & Response Flow
```
1. User submits question
   ↓
2. Query embedding:
   - Same model as indexing
   - 384-dim vector representation
   ↓
3. Vector similarity search:
   - Qdrant COSINE distance
   - Retrieve top-k chunks (default 4)
   - Include source metadata
   ↓
4. Context assembly:
   - Combine retrieved chunks
   - Format with sources
   - Build LLM prompt
   ↓
5. LLM generation:
   - Ollama streams response
   - Server-Sent Events (SSE)
   - Token-by-token delivery
   ↓
6. UI rendering:
   - React processes SSE stream
   - Markdown formatting
   - Live updates to chat
```

### File Structure

```
ThinkBook-LM/
├── server/                  # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # FastAPI app + CORS + metadata
│   │   ├── api/
│   │   │   ├── routes.py   # REST endpoints (upload, query, list, delete)
│   │   │   └── models.py   # Pydantic request/response models
│   │   ├── core/
│   │   │   ├── config.py   # Environment variables
│   │   │   ├── security.py # File validation + sanitization
│   │   │   ├── logging_config.py
│   │   │   └── utils.py
│   │   ├── parsers/
│   │   │   ├── registry.py # Parser factory pattern
│   │   │   ├── pdf_parser.py
│   │   │   ├── docx_parser.py
│   │   │   ├── text_parser.py
│   │   │   ├── image_parser.py
│   │   │   ├── audio_parser.py
│   │   │   └── video_parser.py
│   │   ├── rag/
│   │   │   ├── embeddings.py      # SentenceTransformers
│   │   │   ├── chunking.py        # Token-based splitting
│   │   │   └── qdrant_store.py    # Vector DB operations
│   │   └── services/
│   │       ├── llm_service.py     # Ollama integration
│   │       └── rag_service.py     # RAG pipeline orchestration
│   ├── tests/              # Unit tests (30+ tests)
│   │   ├── conftest.py
│   │   ├── test_security.py
│   │   ├── test_embeddings.py
│   │   ├── test_chunking.py
│   │   └── test_parsers.py
│   ├── data/
│   │   ├── uploads/        # Uploaded files
│   │   └── qdrant/         # Vector database (SQLite)
│   └── requirements.txt
│
├── client/                 # React + Electron Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   └── Index.tsx   # Main application page
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx    # Chat interface
│   │   │   ├── UploadPanel.tsx  # File upload UI
│   │   │   ├── ThemeToggle.tsx  # Dark mode switcher
│   │   │   └── ui/              # shadcn components (40+)
│   │   ├── config/
│   │   │   └── api.ts      # API endpoint configuration
│   │   └── hooks/
│   │       └── use-toast.ts
│   ├── electron/
│   │   ├── main.js         # Electron main process
│   │   └── preload.js      # Secure IPC bridge
│   ├── build/
│   │   └── entitlements.mac.plist
│   ├── package.json        # electron-builder config
│   └── .env.example
│
├── README.md
└── openapi.json           # Exported API specification
```

---

## 📚 API Documentation

### Interactive Docs

Once the server is running at `http://localhost:8000`, access:

- **Swagger UI**: http://localhost:8000/docs (interactive API explorer)
- **ReDoc**: http://localhost:8000/redoc (beautiful documentation)
- **OpenAPI Spec**: [openapi.json](openapi.json) (machine-readable schema)

### Key Endpoints

#### `POST /api/upload_file`
Upload and index a document for later querying.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/upload_file" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "status": "ok",
  "file": "document.pdf",
  "chunks": 25
}
```

**Validation:**
- Max size: 50MB
- Allowed types: PDF, DOCX, TXT, PNG, JPG, WAV, MP3, MP4
- Duplicate detection via filename

---

#### `POST /api/query`
Query indexed documents (non-streaming).

**Request:**
```bash
curl -X POST "http://localhost:8000/api/query" \
  -d "q=What are the main findings?" \
  -d "k=4"
```

**Response:**
```json
{
  "answer": "Based on the documents, the main findings are...",
  "sources": [
    {"source": "document.pdf", "chunk_index": 0},
    {"source": "document.pdf", "chunk_index": 3}
  ],
  "raw_retrieval": ["First relevant chunk...", "Second chunk..."],
  "duration": 2.45
}
```

**Parameters:**
- `q` (required): Query text
- `k` (optional, default=4): Number of chunks to retrieve

---

#### `POST /api/query_stream`
Query with real-time streaming response (Server-Sent Events).

**Request:**
```bash
curl -X POST "http://localhost:8000/api/query_stream" \
  -d "q=Explain the methodology" \
  -d "k=4"
```

**Response (SSE stream):**
```
data: {"type":"answer","content":"Based"}
data: {"type":"answer","content":" on"}
data: {"type":"answer","content":" the"}
...
```

---

#### `GET /api/list_files`
List all indexed files with chunk counts.

**Request:**
```bash
curl "http://localhost:8000/api/list_files"
```

**Response:**
```json
[
  {"name": "document.pdf", "chunks": 25},
  {"name": "notes.txt", "chunks": 8}
]
```

---

#### `DELETE /api/delete_file?name={filename}`
Remove a file from index and filesystem.

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/delete_file?name=document.pdf"
```

**Response:**
```json
{
  "status": "ok",
  "deleted_file": "document.pdf",
  "deleted_chunks": 25
}
```

⚠️ **Warning:** This operation is irreversible.

---

## 🧪 Testing

### Running Tests

```bash
cd server

# Activate virtual environment
source .venv/bin/activate

# Run all tests with verbose output
pytest tests/ -v

# Run specific test modules
pytest tests/test_security.py -v        # File validation tests
pytest tests/test_embeddings.py -v      # Embedding quality tests
pytest tests/test_chunking.py -v        # Text chunking tests
pytest tests/test_parsers.py -v         # Parser registry tests

# Generate coverage report
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Coverage

| Module | Tests | What's Tested |
|--------|-------|---------------|
| **Security** | 12 tests | File size, MIME types, extensions, path sanitization, duplicates |
| **Embeddings** | 6 tests | Vector quality, similarity scoring, determinism, caching |
| **Chunking** | 5 tests | Token counting, overlap, edge cases, large documents |
| **Parsers** | 7 tests | Registry pattern, format detection, extraction quality |

**Total: 30+ tests** covering critical paths and edge cases.

### Manual End-to-End Testing

```bash
cd server/tests

# Run full workflow test
python e2e_test.py

# Expected output:
# ✓ Upload sample_notes.txt
# ✓ Query: "What are the main topics?"
# ✓ Verify response quality
# ✓ Delete file
# ✓ Verify cleanup
```

---

## 🔧 Configuration

### Server Configuration

Create `server/.env.app` (optional - defaults work out of the box):

```bash
# Server Settings
THINKBOOK_HOST=0.0.0.0
THINKBOOK_PORT=8000
THINKBOOK_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Ollama Configuration
THINKBOOK_OLLAMA_URL=http://localhost:11434/api/generate
THINKBOOK_OLLAMA_MODEL=llama3.1:8b

# File Storage
THINKBOOK_UPLOAD_DIR=./data/uploads
THINKBOOK_QDRANT_DIR=./data/qdrant

# Security
THINKBOOK_MAX_FILE_SIZE_MB=50  # Max upload size

# RAG Pipeline
THINKBOOK_CHUNK_SIZE_TOKENS=800       # Chunk size for text splitting
THINKBOOK_CHUNK_OVERLAP_TOKENS=150    # Overlap between chunks
THINKBOOK_EMBEDDING_MODEL=all-MiniLM-L6-v2  # SentenceTransformers model

# LLM Generation
THINKBOOK_MAX_TOKENS=512      # Max response length
THINKBOOK_TEMPERATURE=0.0     # 0 = deterministic, 1 = creative
```

### Client Configuration

Create `client/.env` (optional - defaults to http://localhost:8000):

```bash
VITE_API_URL=http://localhost:8000
```

### Electron Build Configuration

The `client/package.json` already includes electron-builder configuration:

```json
{
  "build": {
    "appId": "com.thinkbook.lm",
    "productName": "ThinkBook LM",
    "directories": {
      "output": "dist"
    },
    "mac": {
      "target": ["dmg", "zip"],
      "category": "public.app-category.productivity"
    },
    "win": {
      "target": ["nsis", "portable"]
    },
    "linux": {
      "target": ["AppImage", "deb", "rpm"],
      "category": "Office"
    }
  }
}
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Development Workflow

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/ThinkBook-LM.git
cd ThinkBook-LM

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make your changes
# - Add tests for new features
# - Update documentation
# - Follow code style guidelines

# 4. Run tests
cd server
pytest tests/ -v

# 5. Commit with conventional commits
git commit -m "feat: add amazing feature"

# 6. Push and create pull request
git push origin feature/amazing-feature
```

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/updates
- `refactor:` Code refactoring (no behavior change)
- `perf:` Performance improvements
- `chore:` Build/tooling changes

### Code Style

**Python:**
- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting: `black app/`
- Use `isort` for imports: `isort app/`
- Type hints encouraged

**TypeScript/React:**
- Use Prettier (configured in project)
- Follow React best practices
- Functional components with hooks

### Adding New Parsers

To add support for a new file format:

1. Create `server/app/parsers/your_parser.py`:

```python
from .base import BaseParser

class YourParser(BaseParser):
    @staticmethod
    def extract_text(file_path: str) -> str:
        # Your extraction logic
        return extracted_text
```

2. Register in `server/app/parsers/registry.py`:

```python
from .your_parser import YourParser

PARSER_REGISTRY = {
    # ...existing parsers...
    ".your_ext": YourParser,
}
```

3. Add tests in `server/tests/test_parsers.py`

---

## 🗺️ Roadmap

### v0.3.0 (Planned)
- [ ] **Docker Support**: One-command deployment with docker-compose
- [ ] **Multi-User**: Authentication and workspace isolation
- [ ] **Advanced RAG**: Hybrid search (vector + keyword) and re-ranking
- [ ] **More LLMs**: GPT4All, llama.cpp, Mistral support
- [ ] **Export**: Save conversations to Markdown/PDF
- [ ] **Browser Extension**: Index web pages directly

### v0.4.0 (Future)
- [ ] **Internationalization**: Multi-language UI (i18n)
- [ ] **Plugin System**: Custom parsers without code changes
- [ ] **Knowledge Graph**: Visualize document relationships
- [ ] **Collaboration**: Share workspaces with teams
- [ ] **Mobile Apps**: iOS/Android companion apps
- [ ] **Cloud Sync**: Optional encrypted backup

### Community Ideas
Have a feature request? [Open a discussion](https://github.com/Dharanish-AM/ThinkBook-LM/discussions)!

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**TL;DR:** You can use, modify, and distribute this software freely. Just include the original copyright notice.

---

## 🙏 Acknowledgments

ThinkBook LM wouldn't be possible without these amazing open-source projects:

- **[Ollama](https://ollama.ai/)** - Making local LLMs accessible to everyone
- **[Qdrant](https://qdrant.tech/)** - High-performance vector search engine
- **[SentenceTransformers](https://www.sbert.net/)** - State-of-the-art sentence embeddings
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[shadcn/ui](https://ui.shadcn.com/)** - Beautiful, accessible React components
- **[Radix UI](https://www.radix-ui.com/)** - Unstyled, accessible component primitives
- **[TailwindCSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Electron](https://www.electronjs.org/)** - Cross-platform desktop apps

---

## 📞 Support & Community

### Get Help
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Dharanish-AM/ThinkBook-LM/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/Dharanish-AM/ThinkBook-LM/discussions)
- 📖 **Documentation**: Check [/docs](http://localhost:8000/docs) when server is running
- ❓ **Questions**: [Start a discussion](https://github.com/Dharanish-AM/ThinkBook-LM/discussions/new)

### Stay Updated
- ⭐ **Star this repo** to get notified of new releases
- 👀 **Watch** for all activity updates
- 🍴 **Fork** to create your own version

---

## 🔒 Security & Privacy

ThinkBook LM is designed with privacy as a core principle:

- ✅ **No Analytics**: Zero telemetry or usage tracking
- ✅ **No Cloud**: All processing happens locally
- ✅ **No Network**: Works completely offline after setup
- ✅ **Open Source**: Inspect every line of code
- ✅ **Local Storage**: Your data stays on your machine

For security concerns, please email: [security@thinkbook.dev](mailto:security@thinkbook.dev)

---

<div align="center">

### Built with ❤️ for Privacy-Conscious Researchers

**⭐ Star this repo if you find it useful!**

[![GitHub](https://img.shields.io/badge/GitHub-Dharanish--AM-181717?logo=github)](https://github.com/Dharanish-AM)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>
