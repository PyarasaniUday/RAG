import os
import requests
from typing import Any
from dotenv import load_dotenv
from src.utils.helpers import logger, load_config

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

# Load environment variables
load_dotenv()

def get_llm_client() -> Any:
    """Initializes and returns the LangChain Google Gemini client.
    Note: For Groq, we make direct API calls to keep dependencies lightweight.
    """
    config = load_config()
    llm_config = config.get("llm", {})
    provider = llm_config.get("provider", "gemini")
    
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set.")
            
        model_name = llm_config.get("model", "gemini-1.5-flash")
        temperature = llm_config.get("temperature", 0.2)
        
        logger.info(f"Initializing Gemini LLM client (model={model_name})")
        if ChatGoogleGenerativeAI is None:
            raise ImportError("langchain-google-genai package is not installed.")
            
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key
        )
    else:
        logger.info("Using Groq provider (direct API completion)")
        return None

def generate_answer_via_groq(prompt: str, model_name: str, temperature: float) -> str:
    """Invokes the Groq completions endpoint directly using requests."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY is missing from environment variables.")
        return "I could not generate an answer because the GROQ_API_KEY is not configured. Please set the key in your .env file."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature
    }
    
    try:
        logger.info(f"Sending prompt to Groq API using model '{model_name}'.")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Groq API returned error status {response.status_code}: {response.text}")
            return f"Error from Groq API (status code {response.status_code}): {response.text}"
            
        res_data = response.json()
        answer = res_data["choices"][0]["message"]["content"]
        
        if hasattr(answer, "strip"):
            answer = answer.strip()
            
        logger.info("Groq response generated successfully.")
        return answer
    except Exception as e:
        logger.error(f"Groq API call failed: {e}", exc_info=True)
        return f"An error occurred while contacting the Groq language model: {str(e)}"

def generate_answer(prompt: str) -> str:
    """Routes prompt to configured LLM (Gemini or Groq) and returns response text."""
    config = load_config()
    llm_config = config.get("llm", {})
    provider = llm_config.get("provider", "gemini")
    model_name = llm_config.get("model", "llama-3.1-8b-instant")
    temperature = llm_config.get("temperature", 0.2)
    
    if provider == "groq":
        return generate_answer_via_groq(prompt, model_name, temperature)
        
    # Default to Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # If Gemini key is missing, check if Groq key exists and fall back to Groq!
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            logger.info("GEMINI_API_KEY missing, falling back to Groq since GROQ_API_KEY is present.")
            return generate_answer_via_groq(prompt, "llama-3.1-8b-instant", temperature)
            
        logger.error("No API keys found in environment variables.")
        return "I could not generate an answer because no API keys (GEMINI_API_KEY or GROQ_API_KEY) are configured. Please set them in your .env file."
        
    try:
        logger.info("Sending prompt to Gemini LLM.")
        llm = get_llm_client()
        response = llm.invoke(prompt)
        answer = response.content
        if hasattr(answer, "strip"):
            answer = answer.strip()
        logger.info("Gemini response generated successfully.")
        return answer
    except Exception as e:
        logger.error(f"Gemini generation failed: {e}", exc_info=True)
        # Final fallback to Groq if Gemini fails but Groq key is present
        if os.getenv("GROQ_API_KEY"):
            logger.info("Gemini execution failed. Attempting fallback to Groq API.")
            return generate_answer_via_groq(prompt, "llama-3.1-8b-instant", temperature)
        return f"An error occurred while contacting the language model: {str(e)}"
