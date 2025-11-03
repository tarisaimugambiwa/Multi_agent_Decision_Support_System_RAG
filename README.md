# 🏥 Medical AI Diagnostic System

A comprehensive Django-based medical diagnostic system that combines AI-powered diagnosis suggestions with RAG (Retrieval-Augmented Generation) technology to assist healthcare professionals in making informed decisions.

![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)
![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Medical AI Diagnostic System is designed to assist healthcare professionals by providing intelligent diagnostic suggestions based on patient symptoms, vital signs, and a comprehensive medical knowledge base. The system uses advanced natural language processing and vector similarity search to retrieve relevant medical information from WHO guidelines, pediatric protocols, and standard treatment manuals.

### Key Capabilities

- **AI-Powered Diagnosis**: Generates diagnostic suggestions with confidence scores
- **RAG Knowledge Base**: 14,179+ medical knowledge chunks from authoritative sources
- **Role-Based Access**: Separate dashboards for Nurses and Doctors
- **Case Management**: Complete workflow from case creation to doctor review
- **Audit Trail**: Track all decisions and modifications for accountability

## ✨ Features

### For Nurses
- 👤 **Patient Management**: Search, create, and manage patient records
- 📝 **Case Creation**: Enter symptoms, vital signs, and medical history
- 🤖 **AI Diagnosis**: Get instant diagnostic suggestions from AI
- 📊 **Dashboard**: View active cases and pending reviews
- 🔍 **Patient Search**: Quick search with autocomplete

### For Doctors
- 📋 **Case Review**: Review AI-generated diagnoses
- ✅ **Decision Making**: Approve, modify, or reject AI recommendations
- 📝 **Clinical Notes**: Add modifications and rejection reasons
- 📈 **Case Analytics**: View case statistics and trends
- 🕐 **Case Timeline**: Track complete case history

### AI & Knowledge Base
- 🧠 **RAG System**: Semantic search across 14,179+ medical knowledge chunks
- 📚 **Medical Sources**: WHO guidelines, pediatric protocols, treatment manuals
- 🎯 **Context-Aware**: Age-specific and symptom-based recommendations
- 🔬 **Evidence-Based**: All suggestions backed by authoritative sources
- 📊 **Confidence Scoring**: Each diagnosis comes with a confidence level

### System Features
- 🔐 **Authentication**: Secure login with role-based access control
- 🎨 **Responsive UI**: Modern, mobile-friendly interface
- 📱 **Real-Time Updates**: Live case status updates
- 🔔 **Notifications**: Urgent case alerts
- 📈 **Analytics Dashboard**: System-wide statistics and insights

## 🛠 Technology Stack

### Backend
- **Django 5.2.7**: Web framework
- **Python 3.13**: Programming language
- **SQLite**: Database (development)
- **Django REST Framework**: API endpoints

### AI & Machine Learning
- **LangChain**: RAG framework
- **HuggingFace Transformers**: Embeddings (all-MiniLM-L6-v2)
- **FAISS**: Vector similarity search
- **sentence-transformers**: Text embeddings
- **NumPy**: Numerical computations

### Document Processing
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX file processing
- **RecursiveCharacterTextSplitter**: Text chunking

### Frontend
- **Bootstrap 5**: UI framework
- **Font Awesome**: Icons
- **JavaScript**: Interactive features
- **AJAX**: Asynchronous requests

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- pip (Python package installer)
- Virtual environment tool (venv)
- Git (optional)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/medical-ai-system.git
cd medical-ai-system
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install django==5.2.7
pip install djangorestframework
pip install langchain
pip install langchain-community
pip install sentence-transformers
pip install faiss-cpu
pip install PyPDF2
pip install python-docx
pip install numpy
```

Or use requirements.txt (if available):

```bash
pip install -r requirements.txt
```

### Step 4: Database Setup

```bash
python manage.py migrate
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Process Medical Documents (Optional)

If you have medical documents in the `sample_documents/` folder:

```bash
python manage.py shell
```

Then in the Python shell:

```python
from knowledge.rag_utils import process_all_documents
process_all_documents()
```

### Step 7: Run Development Server

```bash

from django.db.models import Q
from django.http import JsonResponse

@login_required
def search_patients(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    patients = Patient.objects.filter(
        Q(patient_id__icontains=query) |
        Q(phone_number__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )[:10]
    
    results = [{
        'id': patient.id,
        'patient_id': patient.patient_id,
        'name': f"{patient.first_name} {patient.last_name}",
        'phone': patient.phone_number,
        'dob': patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else '',
    } for patient in patients]
    
    return JsonResponse({'results': results})
```

Visit http://127.0.0.1:8000/ in your browser.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### User Roles Configuration

After creating users, assign roles via Django shell:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Make user a nurse
user = User.objects.get(username='nurse_username')
user.role = 'NURSE'
user.save()

# Make user a doctor
user = User.objects.get(username='doctor_username')
user.role = 'DOCTOR'
user.save()
```

### Knowledge Base Setup

Place medical documents (PDF, DOCX, TXT) in `sample_documents/` folder and run:

```python
from knowledge.rag_utils import process_all_documents
process_all_documents()
```

## 📖 Usage Guide

### For Nurses

1. **Login**: Use your nurse credentials at `/accounts/login/`
2. **Create Patient**: 
   - Go to Nurse Dashboard
   - Click "New Case"
   - Search for existing patient or create new
3. **Enter Case Details**:
   - Fill in chief complaint
   - Enter symptoms (comma-separated)
   - Record vital signs
   - Add medical history
4. **Get AI Diagnosis**:
   - Click "Submit for AI Analysis"
   - Review AI suggestions
   - Check confidence scores
5. **Submit for Review**: Send case to doctor for final approval

### For Doctors

1. **Login**: Use your doctor credentials at `/accounts/login/`
2. **View Cases**: 
   - See all pending cases in Doctor Dashboard
   - Click "Review" on any case
3. **Review AI Diagnosis**:
   - Read AI suggestions
   - Check supporting evidence from knowledge base
   - Review patient history and vitals
4. **Make Decision**:
   - **Approve**: Accept AI diagnosis as-is
   - **Modify**: Make changes and add notes
   - **Reject**: Provide alternative diagnosis and reason
5. **Track Progress**: Monitor case status and timeline

### Admin Panel

Access the Django admin at `/admin/` to:
- Manage users and roles
- View all patients and cases
- Manage knowledge base documents
- Configure system settings

## 🔌 API Documentation

### Authentication

All API endpoints require authentication via session or token.

### Endpoints

#### Patient Search API

```http
GET /api/patients/search/?q=<search_term>
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "patient_id": "P001",
      "date_of_birth": "1990-01-01",
      "phone": "555-0123"
    }
  ]
}
```

#### Case Creation API

```http
POST /diagnoses/api/create-case/
Content-Type: application/json

{
  "patient_id": 1,
  "chief_complaint": "Fever and cough",
  "symptoms": "high fever, persistent cough, fatigue",
  "vital_signs": {
    "temperature": 38.5,
    "blood_pressure": "120/80",
    "pulse": 90,
    "respiratory_rate": 20
  }
}
```

#### AI Diagnosis API

```http
POST /diagnoses/api/get-diagnosis/
Content-Type: application/json

{
  "symptoms": ["fever", "cough", "fatigue"],
  "patient_age": 35,
  "vital_signs": {...}
}
```

**Response:**
```json
{
  "diagnosis": "Upper Respiratory Tract Infection",
  "confidence": 0.85,
  "differential_diagnoses": [...],
  "recommendations": [...],
  "supporting_evidence": [...]
}
```

## 📁 Project Structure

```
DS_System/
├── diagnoses/              # Diagnosis app
│   ├── ai_utils.py        # AI diagnostic engine
│   ├── models.py          # Case models
│   ├── views.py           # Case views
│   └── urls.py            # Diagnosis URLs
├── knowledge/             # Knowledge base app
│   ├── rag_utils.py       # RAG implementation
│   ├── models.py          # Document models
│   ├── faiss_index.faiss  # Vector database
│   └── faiss_index.pkl    # Text chunks
├── patients/              # Patient management
│   ├── models.py          # Patient models
│   ├── views.py           # Patient views
│   └── urls.py            # Patient URLs
├── users/                 # User management
│   ├── models.py          # Custom user model
│   └── admin.py           # User admin
├── medical_ai/            # Project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URLs
│   └── wsgi.py            # WSGI config
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── home.html          # Dashboard
│   ├── nurse_dashboard.html
│   ├── doctor_dashboard.html
│   ├── case_review.html
│   └── registration/      # Auth templates
├── sample_documents/      # Medical documents
│   └── *.pdf              # WHO guidelines, etc.
├── db.sqlite3             # Database
├── manage.py              # Django management
└── README.md              # This file
```

## 📸 Screenshots

### Login Page
![Login](screenshots/login.png)
*Secure login with role-based access*

### Nurse Dashboard
![Nurse Dashboard](screenshots/nurse_dashboard.png)
*Create cases and manage patients*

### AI Diagnosis
![AI Diagnosis](screenshots/ai_diagnosis.png)
*Get AI-powered diagnostic suggestions*

### Doctor Dashboard
![Doctor Dashboard](screenshots/doctor_dashboard.png)
*Review and approve cases*

### Case Review
![Case Review](screenshots/case_review.png)
*Comprehensive case review interface*

### Knowledge Base
![Knowledge Base](screenshots/knowledge_base.png)
*14,179+ medical knowledge chunks*

## 🧪 Testing

Run tests:

```bash
python manage.py test
```

Run specific app tests:

```bash
python manage.py test diagnoses
python manage.py test patients
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up static files serving
- [ ] Configure allowed hosts
- [ ] Set up SSL/HTTPS
- [ ] Configure email backend
- [ ] Set up logging
- [ ] Run security checks: `python manage.py check --deploy`

### Recommended Hosting

- **Backend**: Heroku, AWS, DigitalOcean
- **Database**: PostgreSQL on AWS RDS
- **Static Files**: AWS S3 or CDN
- **SSL**: Let's Encrypt

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- WHO for medical guidelines and protocols
- ESPGHAN for pediatric coeliac disease guidelines
- LangChain community for RAG framework
- HuggingFace for transformer models
- Django community for the excellent framework

## 📞 Support

For support, email support@medicalai.com or open an issue in the repository.

## 🔮 Roadmap

- [ ] Add more medical document sources
- [ ] Implement real-time notifications
- [ ] Add telemedicine integration
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with hospital systems
- [ ] Drug interaction checker
- [ ] Lab results integration

## ⚠️ Disclaimer

This system is designed to assist healthcare professionals and should not be used as a sole basis for medical decisions. Always consult with qualified healthcare providers for diagnosis and treatment.

---

**Built with ❤️ for healthcare professionals**
