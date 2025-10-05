import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
print("--- Starting API Test ---")

load_dotenv()
api_key = os.getenv("GOOGLE_AI_API_KEY")

if not api_key:
    print("\n[ERROR] GOOGLE_AI_API_KEY not found in .env file.")
else:
    try:
        print(f"Configuring API key ending with: ...{api_key[-4:]}")
        genai.configure(api_key=api_key)

        model_name = 'models/gemini-2.5-flash'
        print(f"Initializing model: '{model_name}'...")
        model = genai.GenerativeModel(model_name)

        print("Sending a test prompt to the API...")
        response = model.generate_content("Tell me a fun fact about the Roman Empire.")

        print("\n✅ --- API TEST SUCCESS! --- ✅")
        print("Response from Gemini:", response.text)

    except Exception as e:
        print(f"\n❌ --- API TEST FAILED --- ❌")
        print(f"An error occurred: {e}")

print("\n--- Test Finished ---")

