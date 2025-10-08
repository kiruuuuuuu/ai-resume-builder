import os
import google.generativeai as genai
import fitz
import docx
import logging
import re
import json
from typing import List, Dict, Any
import time

# --- ADDED: Model imports for helper function ---
from .models import Experience, Education, Skill, Project, Certification, Achievement, Language, Hobby
# --- END ADDITION ---

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Gemini API Functions ---

def _get_gemini_model(model_name: str = 'models/gemini-2.5-flash'):
    """
    Initializes and returns a Gemini model instance.
    """
    try:
        from django.conf import settings
        api_key = settings.GOOGLE_AI_API_KEY
        if not api_key:
            logger.error("GOOGLE_AI_API_KEY not found for scoring.")
            return None
        
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(model_name)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model for scoring: {e}")
        return None

def _call_gemini_with_retry(model, prompt, max_retries=3, base_delay=1):
    """Calls the Gemini API with exponential backoff for retries."""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            logger.warning(f"Gemini API call failed on attempt {attempt + 1}/{max_retries}. Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt)) # Exponential backoff
            else:
                logger.error("Max retries reached. Gemini API call failed.")
                return None

def parse_text_with_gemini(text: str) -> Dict[str, Any]:
    """
    Sends resume text to the Gemini API and asks it to parse the content
    into a structured JSON format. Includes a few-shot example for better accuracy.
    """
    model = _get_gemini_model()
    if not model or not text:
        return None

    prompt = f"""
    You are an expert resume parsing system. Analyze the following resume text and extract the information into a structured JSON object.

    The JSON object must have the following top-level keys: "personal_details", "professional_summary", "experience", "education", "skills", "projects", "certifications", "achievements", "languages", "hobbies".

    - "personal_details" should be an object with keys: "full_name", "email", "phone_number", "address", "portfolio_url", "linkedin_url".
    - "experience", "education", "projects", "certifications", "achievements", and "languages" should be lists of objects with appropriate fields (e.g., "job_title", "company" for experience).
    - "skills" should be a list of objects, each with "name" and "category" keys. Infer the category from the skill name from this list only: ['Frontend', 'Backend', 'Database', 'DevOps', 'Tools', 'Other'].
    - "hobbies" should be a simple list of strings.
    - If a section is not present in the text, its value should be an empty list or null.
    - Ensure all date fields are formatted as YYYY-MM-DD where possible.

    --- EXAMPLE ---
    INPUT TEXT:
    "Jane Doe - Software Engineer. Contact: jane.d@email.com, 555-1234. Experience: Lead Developer at TechCorp (2020-2023). Education: B.S. in Computer Science from State University (2016-2020). Skills: Python (Backend), React (Frontend)."

    EXPECTED JSON OUTPUT:
    {{
      "personal_details": {{
        "full_name": "Jane Doe",
        "email": "jane.d@email.com",
        "phone_number": "555-1234",
        "address": null,
        "portfolio_url": null,
        "linkedin_url": null
      }},
      "professional_summary": "Software Engineer",
      "experience": [
        {{
          "job_title": "Lead Developer",
          "company": "TechCorp",
          "start_date": "2020-01-01",
          "end_date": "2023-01-01",
          "description": null
        }}
      ],
      "education": [
        {{
          "institution": "State University",
          "degree": "B.S. in Computer Science",
          "start_date": "2016-09-01",
          "end_date": "2020-05-01",
          "field_of_study": "Computer Science"
        }}
      ],
      "skills": [
        {{ "name": "Python", "category": "Backend" }},
        {{ "name": "React", "category": "Frontend" }}
      ],
      "projects": [],
      "certifications": [],
      "achievements": [],
      "languages": [],
      "hobbies": []
    }}
    ---

    --- ACTUAL RESUME TEXT TO PARSE ---
    {text}
    ---

    Return ONLY the raw JSON object, without any surrounding text or markdown.
    """

    try:
        response = _call_gemini_with_retry(model, prompt)
        if not response:
            return None

        text_response = response.text
        start_index = text_response.find('{')
        end_index = text_response.rfind('}') + 1
        
        if start_index != -1 and end_index != 0:
            json_string = text_response[start_index:end_index]
            return json.loads(json_string)
        else:
            logger.error("Could not find a valid JSON object in the Gemini response.")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding Gemini JSON response: {e}")
        logger.error(f"Raw response was: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error parsing with Gemini: {e}")
        return None

def enhance_text_with_gemini(text_to_enhance: str, context: str) -> str:
    """
    Uses Gemini to rewrite and improve a piece of text from a resume, with more specific contextual instructions.
    """
    model = _get_gemini_model()
    if not model or not text_to_enhance:
        return text_to_enhance
        
    context_instructions = ""
    # --- THE FIX IS HERE: Updated character limits ---
    if context == 'experience_description':
        context_instructions = "Focus on using strong action verbs and quantifying achievements. The entire response must be under 500 characters."
    elif context == 'professional_summary':
        context_instructions = "Keep it a concise and powerful introduction (2-3 sentences). The entire response must be under 600 characters."
    elif context == 'project_description':
        context_instructions = "Clearly explain the project's purpose and your role. The entire response must be under 400 characters."


    prompt = f"""
    You are an expert career coach and resume writer. Your task is to rewrite and enhance the following text for a resume's '{context}' section to be more professional, impactful, and tailored to its purpose.
    
    {context_instructions}

    Return ONLY the enhanced plain text, without any markdown formatting (like asterisks or bullet points) or introductory phrases like "Here's the enhanced text:".

    --- ORIGINAL TEXT ---
    {text_to_enhance}
    ---
    
    ENHANCED TEXT:
    """
    try:
        response = _call_gemini_with_retry(model, prompt)
        if not response:
            return text_to_enhance
        
        enhanced_text = response.text.strip()
        # Clean up any residual markdown that might slip through
        cleaned_text = enhanced_text.replace('**', '').replace('*', '').strip()
        return cleaned_text
    except Exception as e:
        logger.error(f"Error enhancing text with Gemini: {e}")
        return text_to_enhance

# --- START: New AI Resume Scoring and Feedback Function ---
def score_and_critique_resume(full_resume_text: str) -> Dict[str, Any]:
    """
    Uses Gemini to provide a holistic score and feedback for a resume.
    """
    model = _get_gemini_model()
    if not model or not full_resume_text:
        return {'score': 0, 'feedback': ['Could not analyze resume. Add some content first.']}

    prompt = f"""
    You are an expert and encouraging career coach reviewing a resume. Analyze the complete resume text provided below.

    Your task is to provide a holistic quality score from 0 to 100 and 2-3 brief, actionable, and encouraging feedback points.

    **Scoring Guidelines:**
    - **Fresher/Entry-Level Resume:** If the resume has no 'Work Experience' section, evaluate it as a fresher's resume. In this case, give higher weight to 'Projects', 'Skills', and 'Education' sections. A well-detailed project section can compensate for a lack of formal work experience.
    - **Impact & Action Verbs (40%):** Does the resume use strong action verbs? Is the language impactful? For freshers, look for this in their project descriptions.
    - **Clarity & Readability (30%):** Is the resume easy to read, concise, and free of errors?
    - **Completeness & Detail (30%):** Are key sections like Education, Skills, and Projects well-described?

    **Feedback Guidelines:**
    - Provide 2 to 3 bullet points of constructive, encouraging feedback.
    - If it's a fresher resume, your feedback should be tailored to them. For example: "This is a strong start for an entry-level resume. To make it even better, consider contributing to an open-source project to further demonstrate your skills."
    - Each point should be a single, concise sentence.

    --- RESUME TEXT ---
    {full_resume_text}
    ---

    Return a single, raw JSON object with two keys: "score" (an integer) and "feedback" (a list of strings).
    Example for a fresher: {{"score": 85, "feedback": ["Your project descriptions are detailed and use strong action verbs.", "Consider adding a link to your GitHub or portfolio to showcase your work directly."]}}
    """

    try:
        response = _call_gemini_with_retry(model, prompt)
        if not response:
            return None

        text_response = response.text
        start_index = text_response.find('{')
        end_index = text_response.rfind('}') + 1
        
        if start_index != -1 and end_index != 0:
            json_string = text_response[start_index:end_index]
            data = json.loads(json_string)
            if isinstance(data.get('score'), int) and isinstance(data.get('feedback'), list):
                return data
            else:
                logger.warning(f"Gemini returned improperly structured JSON for critique: {data}")
                return None
        else:
            logger.error(f"Could not find a valid JSON object in the Gemini critique response: {text_response}")
            return None
    except Exception as e:
        logger.error(f"Error critiquing resume with Gemini: {e}")
        return None
# --- END: New AI Function ---


# --- File Extraction Functions ---

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        with fitz.open(file_path) as doc:
            text = "\n".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        logger.error('Error reading PDF file: %s', e)
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        logger.error('Error reading DOCX file: %s', e)
        return ""

# --- START: Moved Helper Function ---
def get_full_resume_text(resume):
    """Helper function to compile all resume information into a single string."""
    profile = resume.profile
    full_text = f"Name: {profile.full_name}\n"
    full_text += f"Summary: {profile.professional_summary or ''}\n\n"
    
    experiences = Experience.objects.filter(resume=resume)
    if experiences:
        full_text += "Experience:\n" + "\n".join([f"- {e.job_title} at {e.company}: {e.description}" for e in experiences]) + "\n\n"
    
    educations = Education.objects.filter(resume=resume)
    if educations:
        full_text += "Education:\n" + "\n".join([f"- {e.degree} from {e.institution}" for e in educations]) + "\n\n"
    
    projects = Project.objects.filter(resume=resume)
    if projects:
        full_text += "Projects:\n" + "\n".join([f"- {p.title}: {p.description or ''}" for p in projects]) + "\n\n"
    
    skills = Skill.objects.filter(resume=resume)
    if skills:
        full_text += "Skills: " + ", ".join([s.name for s in skills]) + "\n\n"
    
    certifications = Certification.objects.filter(resume=resume)
    if certifications:
        full_text += "Certifications:\n" + "\n".join([f"- {c.name} from {c.issuing_organization}" for c in certifications]) + "\n\n"
    
    achievements = Achievement.objects.filter(resume=resume)
    if achievements:
        full_text += "Achievements:\n" + "\n".join([f"- {a.description}" for a in achievements]) + "\n\n"

    languages = Language.objects.filter(resume=resume)
    if languages:
        full_text += "Languages: " + ", ".join([f"{l.name} ({l.get_proficiency_display()})" for l in languages]) + "\n"
    
    return full_text
# --- END: Moved Helper Function ---

