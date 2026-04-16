# Vapi Vaidya - Medical Voice Assistant for Non-English Speakers

## 🏥 Overview

Vapi Vaidya is a multilingual medical voice assistant designed for patients who don't understand English and need to manage their medical data like a personal gallery on their phone. This hackathon project integrates **Vapi** and **Qdrant** to provide voice-based medical consultations in patients' native languages, helping them remember important medical information after hospital visits.

## 🎯 Problem Statement

Patients often forget crucial medical details after returning from the hospital. This solution allows them to:
- Store medical records (PDFs, prescriptions) as a personal gallery
- Ask questions in their native language (currently Kannada)
- Get voice responses in their preferred language
- Maintain a comprehensive medical history accessible via voice

## 🏗️ Architecture

### Core Components

#### 1. **FastAPI Backend** (`main.py`)
- RESTful API server with streaming responses
- Vapi-compatible `/chat/completions` endpoint
- Integrates with RAG system for intelligent responses

#### 2. **Medical RAG System** (`medical_rag.py`)
- **Vector Database**: Qdrant for semantic search
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: Groq (Llama 3.3 70B) for medical Q&A
- **Multi-modal ingestion**: PDF transcripts + prescription images

#### 3. **Query Engine** (`query_rag.py`)
- Patient-specific medical record retrieval
- Context-aware question answering
- CLI interface for testing

#### 4. **Vapi Assistant Setup** (`create_assistant.py`)
- Voice: Azure Kannada (kn-IN-GaganNeural)
- Transcriber: Azure Kannada recognition
- Custom LLM integration

### Data Flow

```
Patient Voice → Vapi → FastAPI → RAG System → Qdrant + Groq → Voice Response
```

## 📊 Data Storage

### Medical Records (`data/`)
- **April_16_2026_Consultation.pdf**
- **March_15_2026_Consultation.pdf**

### Prescriptions (`images/`)
- **april_15_2026.jpeg**
- **march_15_2026.jpeg**

### Data Processing
- PDFs → Text extraction → AI summarization → Vector embeddings
- Images → OCR (Prescripto API) → Medication extraction → Vector embeddings

## 🔧 Technology Stack

- **Backend**: FastAPI, Python
- **Voice AI**: Vapi, Azure Speech Services
- **Vector DB**: Qdrant Cloud
- **LLM**: Groq (Llama 3.3 70B)
- **Embeddings**: Sentence Transformers
- **OCR**: Prescripto API
- **PDF Processing**: PyPDF

## 🚀 React Native Integration (Next Phase)

This backend is designed to integrate with a **React Native mobile app** that will provide:

### Mobile App Features
- **Voice Interface**: Native voice input/output in multiple languages
- **Medical Gallery**: Visual gallery of all medical documents
- **Upload Functionality**: Camera integration for prescription photos
- **Patient Profiles**: Multi-patient support with secure authentication
- **Offline Access**: Cached medical records for offline viewing
- **Push Notifications**: Medication reminders and appointment alerts

### API Endpoints for Mobile
```javascript
// Voice Chat
POST /chat/completions
{
  "messages": [{"role": "user", "content": "ನನ್ನ ಔಷಧಿಗಳು ಯಾವುವು?"}]
}

// Future endpoints for mobile app
POST /upload/prescription
POST /upload/medical-record
GET /patient/{id}/gallery
GET /patient/{id}/medications
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Qdrant Cloud account
- Groq API key
- Vapi API key
- Prescripto API key

### Installation
```bash
# Clone repository
git clone <repository-url>
cd Vapi_Vaidya_

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
```env
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
GROQ_API_KEY=your_groq_key
VAPI_API_KEY=your_vapi_key
PRESCRIPTO_API_KEY=your_prescripto_key
```

### Running the Application

1. **Set up the database and ingest data**:
```bash
python medical_rag.py
```

2. **Start the FastAPI server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Create Vapi assistant**:
```bash
python create_assistant.py
```

4. **Test the RAG system**:
```bash
python query_rag.py
```

## 🌍 Multilingual Support

Currently configured for **Kannada (kn-IN)** with:
- Voice synthesis: `kn-IN-GaganNeural`
- Speech recognition: Kannada language model

Easily extensible to other Indian languages by updating the voice and transcriber configuration in `create_assistant.py`.

## 🏆 Hackathon Highlights

- **Vapi Integration**: Voice-first medical assistant
- **Qdrant Vector Search**: Semantic medical record retrieval
- **Multi-modal AI**: Text + image processing
- **Patient-Centric**: Personal medical gallery concept
- **Non-English Focus**: Breaking language barriers in healthcare
- **React Native Ready**: Backend prepared for mobile deployment

## 🔮 Future Roadmap

1. **React Native App Development**
2. **Multi-language support** (Hindi, Tamil, Telugu, etc.)
3. **Medication reminders and scheduling**
4. **Doctor appointment booking**
5. **Emergency medical information sharing**
6. **Integration with hospital systems**
7. **AI-powered health insights and recommendations**

## 📱 Mobile App Architecture (Planned)

```
React Native App
├── Voice Interface (Vapi SDK)
├── Camera Integration (Document Upload)
├── Medical Gallery (Image/Document Viewer)
├── Patient Profiles (Secure Auth)
├── Offline Storage (AsyncStorage)
└── Push Notifications (Medication Reminders)
```

## 🤝 Contributing

This project is built for healthcare accessibility. Contributions welcome for:
- Additional language support
- Enhanced medical data extraction
- Mobile app development
- UI/UX improvements

## 📄 License

MIT License - Built for healthcare accessibility during hackathon.
