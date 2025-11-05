import os
import google.generativeai as genai
import logging
import json
import time
import re

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Prompt Injection Protection ---
def sanitize_prompt_input(text: str) -> str:
    """
    Sanitizes user input to prevent prompt injection attacks.
    Strips common injection phrases and escapes special characters.
    """
    if not text:
        return ""
    
    # Common prompt injection phrases to remove or neutralize
    injection_phrases = [
        r'ignore\s+all\s+previous\s+instructions',
        r'ignore\s+previous\s+instructions',
        r'new\s+prompt\s*:',
        r'return\s+only',
        r'you\s+are\s+now',
        r'forget\s+everything',
        r'disregard\s+the\s+above',
        r'system\s*:',
        r'user\s*:',
        r'assistant\s*:',
    ]
    
    sanitized = text
    for phrase in injection_phrases:
        sanitized = re.sub(phrase, '', sanitized, flags=re.IGNORECASE)
    
    # Limit length to prevent extremely long inputs
    max_length = 50000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... [truncated]"
    
    return sanitized.strip()

# --- Gemini API Functions ---

def _get_gemini_model(model_name: str = 'models/gemini-2.5-flash'):
    """Initializes and returns a Gemini model instance."""
    try:
        from django.conf import settings
        api_key = settings.GOOGLE_AI_API_KEY
        if not api_key:
            logger.error("GOOGLE_AI_API_KEY not found for scoring.")
            return None
        
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(model_name)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
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
                # *** FIX: Corrected typo from 'i' to 'attempt' ***
                time.sleep(base_delay * (2 ** attempt))
            else:
                logger.error("Max retries reached. Gemini API call failed.")
                return None

def _extract_job_details(job_text: str) -> dict:
    """Uses Gemini to parse a job description into a structured format."""
    model = _get_gemini_model()
    if not model:
        return None

    # Sanitize user input to prevent prompt injection
    sanitized_text = sanitize_prompt_input(job_text)

    prompt = f"""
    You are an expert recruitment analyst. Analyze the job posting text below and extract the key requirements into a structured JSON object.
    
    The JSON should have keys like "required_skills" (list of strings), "nice_to_have_skills" (list of strings), and "required_experience_years" (integer).
    
    --- JOB POSTING TEXT ---
    {sanitized_text}
    ---
    
    CRITICAL: You MUST return ONLY the raw JSON object. Do not include any other text, markdown formatting, or explanatory comments.
    
    Return ONLY the raw JSON object.
    """
    try:
        response = _call_gemini_with_retry(model, prompt)
        if not response or not response.text:
            return None
        
        json_string = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(json_string)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to extract job details with Gemini: {e}")
        return None

def score_resume_with_gemini(resume_text: str, job_details: dict) -> int:
    """Calculates the match score using the Gemini API with structured data."""
    model = _get_gemini_model()
    if not model:
        return 0

    # Sanitize user input to prevent prompt injection
    sanitized_resume_text = sanitize_prompt_input(resume_text)

    prompt = f"""
    You are a very strict technical recruiter. Analyze the RESUME against the structured JOB REQUIREMENTS below and produce a realistic match score from 0-100. Be very critical: a score of 95+ should be extremely rare.

    **Scoring Guidelines:**
      - **Experience (50%):** Compare the years of experience and job titles in the resume against the job requirements.
      - **Required Skills (35%):** This is critical. Heavily penalize the score for each missing "required_skill".
      - **Nice-to-Have Skills (15%):** Award bonus points for matching "nice_to_have_skills".

    Return ONLY a single raw JSON object with one key: "score". Example: {{"score": 78}}

    --- JOB REQUIREMENTS ---
    {json.dumps(job_details, indent=2)}
    ---
    --- RESUME TEXT ---
    {sanitized_resume_text}
    ---
    
    CRITICAL: You MUST return ONLY a single raw JSON object with one key: "score". Do not include any other text, markdown formatting, or explanatory comments.
    """
    try:
        response = _call_gemini_with_retry(model, prompt)
        if not response or not response.text:
            return 0
        
        text_response = response.text
        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if match:
            json_string = match.group(0)
            data = json.loads(json_string)
            score = data.get("score")
            
            if isinstance(score, int):
                return max(0, min(99, score))
        
        logger.warning(f"Gemini returned an unexpected format for score: {text_response}")
        return 0
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error scoring with Gemini: {e}")
        return 0

# --- Main Scorer Function ---

def calculate_match_score(resume_text, job_description_text):
    """
    Primary function to calculate match score using a structured, two-step AI process.
    """
    if not resume_text or not job_description_text:
        return 0
        
    # Step 1: Have the AI pre-analyze the job description.
    job_details = _extract_job_details(job_description_text)
    if not job_details:
        logger.warning("Could not extract structured details from job description. Scoring may be less accurate.")
        # Fallback to a simpler prompt if extraction fails
        job_details = {"requirements": job_description_text}

    # Step 2: Perform the final scoring with structured data.
    gemini_score = score_resume_with_gemini(resume_text, job_details)
    
    if gemini_score is not None:
        logger.info(f"Final Gemini Score: {gemini_score}")
        return gemini_score
    
    logger.error("Both primary and fallback Gemini scoring failed.")
    return 0

# --- AI Job Description Generator ---

def generate_job_description(job_title: str, keywords: str = "") -> dict:
    """
    Uses Gemini to generate a professional job description and requirements
    based on job title and optional keywords.
    Returns a dict with 'description' and 'requirements' keys.
    """
    model = _get_gemini_model()
    if not model or not job_title:
        return {'description': '', 'requirements': ''}

    # Sanitize inputs
    sanitized_title = sanitize_prompt_input(job_title)
    sanitized_keywords = sanitize_prompt_input(keywords) if keywords else ""

    prompt = f"""
    You are an expert HR professional and job description writer. Generate a professional, comprehensive job posting.

    **Job Title:** {sanitized_title}
    **Keywords/Skills:** {sanitized_keywords if sanitized_keywords else "General skills relevant to the role"}

    Create:
    1. **Job Description** (3-5 paragraphs): A compelling overview of the role, company expectations, day-to-day responsibilities, and what makes this position exciting. Be specific and engaging. Aim for 200-400 words.

    2. **Requirements** (bullet points or numbered list): List essential qualifications, technical skills, experience level, and any nice-to-have attributes. Be realistic and specific. Include 5-8 key requirements.

    CRITICAL: You MUST return ONLY a single raw JSON object with two keys: "description" (string) and "requirements" (string). Do not include any other text, markdown formatting, or explanatory comments.

    Return format:
    {{
        "description": "Full job description text here...",
        "requirements": "Requirements list here..."
    }}
    """

    try:
        response = _call_gemini_with_retry(model, prompt)
        if not response or not response.text:
            return {'description': '', 'requirements': ''}

        text_response = response.text
        start_index = text_response.find('{')
        end_index = text_response.rfind('}') + 1

        if start_index != -1 and end_index != 0:
            json_string = text_response[start_index:end_index]
            data = json.loads(json_string)
            
            if isinstance(data.get('description'), str) and isinstance(data.get('requirements'), str):
                return {
                    'description': data['description'].strip(),
                    'requirements': data['requirements'].strip()
                }
        
        logger.warning(f"Gemini returned improperly structured JSON for job generation: {text_response}")
        return {'description': '', 'requirements': ''}
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error generating job description with Gemini: {e}")
        return {'description': '', 'requirements': ''}

def generate_applicant_summary(resume_text: str, job_description: str) -> str:
    """
    Uses Gemini to generate a 3-bullet summary of an applicant highlighting their fit for a job.
    Returns a string with bullet points.
    """
    model = _get_gemini_model()
    if not model or not resume_text or not job_description:
        return ""

    # Sanitize inputs
    sanitized_resume = sanitize_prompt_input(resume_text)
    sanitized_job = sanitize_prompt_input(job_description)

    prompt = f"""
    You are an expert recruiter. Analyze the candidate's resume and the job description, then create a concise 3-bullet summary highlighting the candidate's fit for this specific role.

    Focus on:
    - Relevant experience and skills that match the job requirements
    - Key strengths that make them a strong candidate
    - Notable achievements or qualifications

    Keep each bullet point to one concise sentence (maximum 100 words total).

    --- JOB DESCRIPTION ---
    {sanitized_job}
    ---
    
    --- CANDIDATE RESUME ---
    {sanitized_resume}
    ---

    CRITICAL: You MUST return ONLY a single raw JSON object with one key: "summary" (string containing exactly 3 bullet points, each on a new line starting with "- "). Do not include any other text, markdown formatting, or explanatory comments.

    Return format:
    {{
        "summary": "- First bullet point\\n- Second bullet point\\n- Third bullet point"
    }}
    """

    try:
        response = _call_gemini_with_retry(model, prompt)
        if not response or not response.text:
            return ""

        text_response = response.text
        start_index = text_response.find('{')
        end_index = text_response.rfind('}') + 1

        if start_index != -1 and end_index != 0:
            json_string = text_response[start_index:end_index]
            data = json.loads(json_string)
            
            if isinstance(data.get('summary'), str):
                return data['summary'].strip()
        
        logger.warning(f"Gemini returned improperly structured JSON for applicant summary: {text_response}")
        return ""
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error generating applicant summary with Gemini: {e}")
        return ""

def generate_interview_prep(resume_text: str, job_description: str) -> dict:
    """
    Uses Gemini to generate interview preparation questions and STAR-method answers
    based on the candidate's resume and job description.
    Returns a dict with 'questions' (list of dicts with 'question' and 'answer' keys).
    """
    model = _get_gemini_model()
    if not model or not resume_text or not job_description:
        return {'questions': []}

    # Sanitize inputs
    sanitized_resume = sanitize_prompt_input(resume_text)
    sanitized_job = sanitize_prompt_input(job_description)

    prompt = f"""
    You are an AI career coach helping a candidate prepare for an interview. Based on the candidate's resume and the job description, generate 5 likely interview questions. For each question, provide a sample answer using the STAR method (Situation, Task, Action, Result), tailored to the candidate's experience.

    **Instructions:**
    - Generate 5 questions that are relevant to the job requirements and the candidate's background
    - Each answer should use the STAR method:
      * Situation: Set the context
      * Task: Describe what you needed to accomplish
      * Action: Explain what you did
      * Result: Share the outcome and impact
    - Answers should reference specific experiences, skills, or projects from the resume
    - Keep each answer concise but complete (150-200 words per answer)

    --- JOB DESCRIPTION ---
    {sanitized_job}
    ---
    
    --- CANDIDATE RESUME ---
    {sanitized_resume}
    ---

    CRITICAL: You MUST return ONLY a single raw JSON object with one key: "questions" (array of 5 objects, each with "question" (string) and "answer" (string) keys). Do not include any other text, markdown formatting, or explanatory comments.

    Return format:
    {{
        "questions": [
            {{"question": "Question 1", "answer": "STAR method answer 1"}},
            {{"question": "Question 2", "answer": "STAR method answer 2"}},
            {{"question": "Question 3", "answer": "STAR method answer 3"}},
            {{"question": "Question 4", "answer": "STAR method answer 4"}},
            {{"question": "Question 5", "answer": "STAR method answer 5"}}
        ]
    }}
    """

    try:
        response = _call_gemini_with_retry(model, prompt)
        if not response or not response.text:
            return {'questions': []}

        text_response = response.text
        start_index = text_response.find('{')
        end_index = text_response.rfind('}') + 1

        if start_index != -1 and end_index != 0:
            json_string = text_response[start_index:end_index]
            data = json.loads(json_string)
            
            if isinstance(data.get('questions'), list) and len(data['questions']) > 0:
                return {'questions': data['questions']}
        
        logger.warning(f"Gemini returned improperly structured JSON for interview prep: {text_response}")
        return {'questions': []}
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error generating interview prep with Gemini: {e}")
        return {'questions': []}

