import os
import google.generativeai as genai
import logging
import json
import time
import re

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    prompt = f"""
    You are an expert recruitment analyst. Analyze the job posting text below and extract the key requirements into a structured JSON object.
    
    The JSON should have keys like "required_skills" (list of strings), "nice_to_have_skills" (list of strings), and "required_experience_years" (integer).
    
    --- JOB POSTING TEXT ---
    {job_text}
    ---
    
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
    {resume_text}
    ---
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

