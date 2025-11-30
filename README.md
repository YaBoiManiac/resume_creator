# Resume Creator - Proof of Concept

A Python-based TUI (Text User Interface) application that collects personal information and generates AI-powered, job-specific resumes.

## Project Overview

This project consists of two main scripts:

1. **Data Collection Script** (`collect_info.py`) - Gathers and stores user information
2. **Resume Generator Script** (`generate_resume.py`) - Creates tailored resumes using AI

## Features

### Data Collection (`collect_info.py`)
- Collects basic personal information (name, phone number, email, etc.)
- Stores job experience with detailed information:
  - Job title
  - Company name
  - Position/role
  - Start and end dates
  - Job duties and responsibilities
- Saves all data to a JSON file for easy access

### Resume Generator (`generate_resume.py`)
- Reads stored personal information from JSON
- Accepts job description input (paste from job posting)
- Uses AI (ChatGPT API) to:
  - Generate a tailored "About Me" section
  - Select relevant job experiences
  - Highlight applicable duties and skills
- Outputs a formatted resume

## Project Structure

```
resume_creator/
├── README.md
├── requirements.txt
├── .env (for API keys)
├── .gitignore
├── data/
│   └── user_data.json
├── collect_info.py
├── generate_resume.py
├── utils/
│   ├── __init__.py
│   ├── data_handler.py
│   ├── ai_client.py
│   └── resume_builder.py
└── resumes/
    └── (generated resumes)
```

## Todo List

### Phase 1: Setup & Planning
- [x] Create README and project structure
- [x] Set up virtual environment
- [x] Create requirements.txt with dependencies
- [x] Set up .gitignore file
- [x] Create data directory and JSON schema

### Phase 2: Data Collection Script
- [x] Design JSON schema for user data
  - [x] Personal information fields
  - [x] Job experience sub-table structure
- [x] Implement `collect_info.py`:
  - [x] TUI for personal information input
  - [x] TUI for job experience entry (multiple jobs)
  - [x] Input validation
  - [x] Save to JSON functionality
  - [ ] Edit existing data functionality (skipped - manual editing)
  - [ ] View stored data functionality (skipped - manual viewing)

### Phase 3: Utility Functions
- [x] Create `data_handler.py`:
  - [x] Load JSON data
  - [x] Save JSON data
  - [x] Validate JSON structure
- [x] Create `ai_client.py`:
  - [x] OpenAI API integration
  - [x] Prompt engineering functions
  - [x] Error handling for API calls

### Phase 3.5: Resume Constructor
- [x] Create `resume_builder.py`:
  - [x] Initialize Word document
  - [x] Format header with personal information
  - [x] Add "About Me" section
  - [x] Format job experience entries
  - [x] Add education section
  - [x] Add skills section
  - [x] Apply professional styling
  - [x] Save to DOCX file

### Phase 4: Resume Generator Script
- [x] Implement `generate_resume.py`:
  - [x] Load user data from JSON
  - [x] TUI for job description input
  - [x] Parse and analyze job description
  - [x] Build AI prompts with context
  - [x] Generate "About Me" section
  - [x] Select relevant job experiences
  - [x] Highlight relevant duties
  - [x] Generate tailored skills list
  - [x] Format dates (year only)
  - [x] Format and display resume preview
  - [x] Save resume to DOCX file

### Phase 5: Testing & Refinement
- [ ] Test data collection flow
- [ ] Test resume generation with various job descriptions
- [ ] Refine AI prompts for better output
- [ ] Add error handling
- [ ] Add user feedback messages
- [ ] Documentation and code comments

### Phase 6: Future Enhancements (Optional)
- [ ] Multiple resume templates
- [ ] Export to PDF
- [ ] Skills extraction from job descriptions
- [ ] Resume formatting options
- [ ] Multiple user profiles
- [ ] Resume version history

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file and add your OpenAI API key
```

## Usage

### Collect Information
```bash
python collect_info.py
```

### Generate Resume
```bash
python generate_resume.py
```

## Dependencies (Planned)

- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `rich` - Enhanced TUI experience
- `pydantic` - Data validation
- `python-docx` - Word document generation

## Configuration

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

## JSON Data Schema (Draft)

```json
{
  "personal_info": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "string (optional)",
    "portfolio": "string (optional)"
  },
  "job_experience": [
    {
      "id": "integer",
      "title": "string",
      "company": "string",
      "position": "string",
      "start_date": "string (YYYY-MM)",
      "end_date": "string (YYYY-MM or 'Present')",
      "duties": ["array of strings"],
      "achievements": ["array of strings (optional)"]
    }
  ],
  "education": [],
  "skills": [],
  "certifications": []
}
```

## Notes

- This is a proof of concept - focus on core functionality
- TUI only (no GUI for now)
- Manual input for most data
- AI assists with tailoring and formatting

## License

Personal Project
