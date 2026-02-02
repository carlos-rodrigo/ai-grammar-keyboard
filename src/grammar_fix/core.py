"""Core grammar fixing logic - platform agnostic."""

import requests
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:1b"

PROMPT_TEMPLATE = """Fix grammar/spelling. Output ONLY the corrected sentence, nothing else.

Input: {text}
Output:"""


def extract_corrected_text(response: str, original: str) -> str:
    """Extract the corrected text from LLM response."""
    text = response.strip()
    if not text:
        return original
    
    lines = text.split('\n')
    result = lines[0].strip()
    
    # Remove common prefixes
    for prefix in ['Output:', 'Corrected:', 'Corrected text:', 'Result:']:
        if result.lower().startswith(prefix.lower()):
            result = result[len(prefix):].strip()
    
    # Remove quotes
    result = result.strip('"\'')
    
    # Sanity check
    if len(result) < 2 or len(result) > len(original) * 3:
        return original
    
    return result


def fix_grammar(text: str, model: str = DEFAULT_MODEL) -> str:
    """
    Fix grammar using Ollama.
    
    Args:
        text: The text to fix
        model: Ollama model to use
        
    Returns:
        Corrected text, or original if error/no changes
    """
    if not text or not text.strip():
        return text
    
    prompt = PROMPT_TEMPLATE.format(text=text)
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        raw = response.json().get("response", "")
        return extract_corrected_text(raw, text)
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Ollama is not running. Start it with: ollama serve")
    except requests.exceptions.Timeout:
        raise TimeoutError("Ollama took too long to respond")
    except Exception as e:
        raise RuntimeError(f"Error calling Ollama: {e}")


def check_ollama() -> tuple[bool, str]:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if any(DEFAULT_MODEL in name for name in model_names):
                return True, f"Ollama running with {DEFAULT_MODEL}"
            else:
                return False, f"Model {DEFAULT_MODEL} not found. Run: ollama pull {DEFAULT_MODEL}"
        return False, "Ollama responded but with error"
    except requests.exceptions.ConnectionError:
        return False, "Ollama not running. Start with: ollama serve"
    except Exception as e:
        return False, f"Error checking Ollama: {e}"
