"""
LangChain Processing Chains for Job Tracker
Combines prompts + LLM + output parsing into reusable chains
"""

from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import PromptTemplate
from typing import Dict, List, Optional
import json
import re

from prompts import (
    job_extraction_prompt,
    email_analysis_prompt,
    format_rag_context,
    get_rag_hint,
    FEW_SHOT_EXAMPLES,
    build_few_shot_prompt
)
from config import USE_RAG, OLLAMA_MODEL, OLLAMA_BASE_URL

# ==================== LLM INITIALIZATION ====================

def get_ollama_llm(model_name: str = None, temperature: float = 0.1):
    """
    Create an Ollama LLM instance with retry logic

    Args:
        model_name: Ollama model name (uses config default if None)
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)

    Returns:
        Configured OllamaLLM instance
    """
    if model_name is None:
        model_name = OLLAMA_MODEL

    return OllamaLLM(
        model=model_name,
        temperature=temperature,
        num_predict=200,  # Max tokens to generate
        base_url=OLLAMA_BASE_URL  # Ollama API endpoint
    )

# Singleton LLM instances (shared across application)
_llm_cache = {}

def get_cached_llm(model_name: str = None) -> OllamaLLM:
    """Get or create cached LLM instance"""
    if model_name is None:
        model_name = OLLAMA_MODEL

    if model_name not in _llm_cache:
        _llm_cache[model_name] = get_ollama_llm(model_name)
    return _llm_cache[model_name]


# ==================== OUTPUT PARSERS ====================

class RobustJsonParser:
    """Custom JSON parser with fallback strategies"""

    def parse(self, text: str) -> Dict:
        """Parse JSON with multiple fallback strategies"""
        # Strategy 1: Direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Remove markdown code blocks
        try:
            cleaned = re.sub(r'```json\n?|\n?```', '', text)
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            pass

        # Strategy 3: Extract JSON object with regex
        try:
            json_match = re.search(
                r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
                text,
                re.DOTALL
            )
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Strategy 4: Return error dict
        return {
            "error": "Failed to parse JSON",
            "raw_response": text[:200],
            "is_job_related": False
        }

robust_json_parser = RobustJsonParser()


# ==================== RAG INTEGRATION ====================

def get_rag_context(email_data: Dict, rag_engine=None) -> Dict:
    """
    Fetch RAG context for an email

    Args:
        email_data: Email dictionary with subject, from, body
        rag_engine: RAG engine instance (optional)

    Returns:
        Dictionary with RAG context and metadata
    """
    if not USE_RAG or rag_engine is None:
        return {
            "rag_context": "",
            "rag_hint": "",
            "rag_similarity_hint": "",
            "similarity_context": "This appears to be a new type of application.",
            "similar_apps": []
        }

    try:
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')[:500]
        search_query = f"{subject}\n\n{body}"

        similar_apps = rag_engine.search_similar_applications(
            query_text=search_query,
            top_k=3
        )

        if similar_apps:
            return {
                "rag_context": format_rag_context(similar_apps),
                "rag_hint": get_rag_hint(True),
                "rag_similarity_hint": " and similar past applications",
                "similarity_context": f"This email is similar to {len(similar_apps)} past application(s). Consider patterns from those experiences.",
                "similar_apps": similar_apps
            }
        else:
            return {
                "rag_context": "",
                "rag_hint": "",
                "rag_similarity_hint": "",
                "similarity_context": "This appears to be a new type of application.",
                "similar_apps": []
            }

    except Exception as e:
        print(f"RAG error: {e}")
        return {
            "rag_context": "",
            "rag_hint": "",
            "rag_similarity_hint": "",
            "similarity_context": "This appears to be a new type of application.",
            "similar_apps": []
        }


# ==================== MAIN EXTRACTION CHAIN ====================

def create_job_extraction_chain(rag_engine=None):
    """
    Create a LangChain pipeline for job extraction

    Pipeline:
        1. Get RAG context (if enabled)
        2. Format prompt with email data + RAG context
        3. Call LLM
        4. Parse JSON output

    Returns:
        Runnable chain
    """

    def prepare_input(email_data: Dict) -> Dict:
        """Prepare all inputs for the prompt"""
        rag_data = get_rag_context(email_data, rag_engine)

        return {
            "email_subject": email_data.get('subject', ''),
            "email_from": email_data.get('from', ''),
            "email_body": email_data.get('body', '')[:2000],
            **rag_data
        }

    # Build the chain
    chain = (
        RunnableLambda(prepare_input)  # Step 1: Prepare inputs
        | job_extraction_prompt          # Step 2: Format prompt
        | get_cached_llm()              # Step 3: Call LLM
        | RunnableLambda(robust_json_parser.parse)  # Step 4: Parse output
    )

    return chain


# ==================== EMAIL ANALYSIS CHAIN ====================

def create_email_analysis_chain(rag_engine=None):
    """
    Create a chain for detailed email analysis

    Returns:
        Runnable chain for email analysis
    """

    def prepare_analysis_input(email_data: Dict) -> Dict:
        """Prepare inputs for analysis prompt"""
        rag_data = get_rag_context(email_data, rag_engine)

        return {
            "email_subject": email_data.get('subject', ''),
            "email_body": email_data.get('body', '')[:2000],
            **rag_data
        }

    chain = (
        RunnableLambda(prepare_analysis_input)
        | email_analysis_prompt
        | get_cached_llm()
        | RunnableLambda(robust_json_parser.parse)
    )

    return chain


# ==================== FEW-SHOT EXTRACTION CHAIN (Phase 4) ====================

def create_few_shot_extraction_chain(examples: List[Dict] = FEW_SHOT_EXAMPLES):
    """
    Create a few-shot learning chain with examples

    Args:
        examples: List of example email extractions

    Returns:
        Runnable chain with few-shot prompting
    """

    def prepare_few_shot_prompt(email_data: Dict) -> str:
        """Build few-shot prompt with examples"""
        return build_few_shot_prompt(examples, email_data)

    chain = (
        RunnableLambda(prepare_few_shot_prompt)
        | get_cached_llm()
        | RunnableLambda(robust_json_parser.parse)
    )

    return chain


# ==================== CHAIN-OF-THOUGHT EXTRACTION (Phase 4) ====================

def create_cot_extraction_chain():
    """
    Create a chain-of-thought reasoning chain

    Returns:
        Chain that shows step-by-step reasoning
    """
    from prompts import cot_extraction_prompt

    def prepare_cot_input(email_data: Dict) -> Dict:
        return {
            "email_subject": email_data.get('subject', ''),
            "email_from": email_data.get('from', ''),
            "email_body": email_data.get('body', '')[:2000]
        }

    chain = (
        RunnableLambda(prepare_cot_input)
        | cot_extraction_prompt
        | get_cached_llm(temperature=0.3)  # Slightly higher for reasoning
        | RunnableLambda(robust_json_parser.parse)
    )

    return chain


# ==================== RETRY CHAIN WITH ERROR HANDLING ====================

def create_retry_chain(base_chain, max_retries: int = 3):
    """
    Wrap a chain with retry logic

    Args:
        base_chain: The chain to wrap
        max_retries: Maximum number of retry attempts

    Returns:
        Chain with retry capability
    """

    def run_with_retry(input_data: Dict) -> Dict:
        """Execute chain with retries"""
        last_error = None

        for attempt in range(max_retries):
            try:
                result = base_chain.invoke(input_data)

                # Validate result
                if isinstance(result, dict) and "error" not in result:
                    return result

                # If result has error, retry
                print(f"Attempt {attempt + 1} failed, retrying...")

            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} error: {e}")

        # All retries failed
        return {
            "error": f"All {max_retries} attempts failed",
            "last_error": str(last_error),
            "is_job_related": False
        }

    return RunnableLambda(run_with_retry)


# ==================== CHAIN FACTORY ====================

class ChainFactory:
    """Factory for creating and caching chains"""

    def __init__(self, rag_engine=None):
        self.rag_engine = rag_engine
        self._chain_cache = {}

    def get_extraction_chain(self, mode: str = "standard"):
        """
        Get job extraction chain

        Args:
            mode: "standard", "few_shot", or "cot"

        Returns:
            Configured extraction chain
        """
        cache_key = f"extraction_{mode}"

        if cache_key not in self._chain_cache:
            if mode == "standard":
                self._chain_cache[cache_key] = create_job_extraction_chain(self.rag_engine)
            elif mode == "few_shot":
                self._chain_cache[cache_key] = create_few_shot_extraction_chain()
            elif mode == "cot":
                self._chain_cache[cache_key] = create_cot_extraction_chain()
            else:
                raise ValueError(f"Unknown mode: {mode}")

        return self._chain_cache[cache_key]

    def get_analysis_chain(self):
        """Get email analysis chain"""
        if "analysis" not in self._chain_cache:
            self._chain_cache["analysis"] = create_email_analysis_chain(self.rag_engine)
        return self._chain_cache["analysis"]


# ==================== CONVENIENCE FUNCTIONS ====================

def extract_job_info_with_chain(email_data: Dict, rag_engine=None) -> Dict:
    """
    Extract job info using LangChain (drop-in replacement for old function)

    Args:
        email_data: Email dictionary
        rag_engine: Optional RAG engine

    Returns:
        Extracted job information
    """
    chain = create_job_extraction_chain(rag_engine)
    result = chain.invoke(email_data)

    # Add email metadata
    if isinstance(result, dict) and "error" not in result:
        result['email_subject'] = email_data.get('subject', '')
        result['email_from'] = email_data.get('from', '')
        result['email_date'] = email_data.get('date', '')
        result['email_body'] = email_data.get('body', '')[:2000]

    return result


def analyze_email_with_chain(email_data: Dict, rag_engine=None) -> Dict:
    """
    Analyze email using LangChain

    Args:
        email_data: Email dictionary
        rag_engine: Optional RAG engine

    Returns:
        Analysis results
    """
    chain = create_email_analysis_chain(rag_engine)
    return chain.invoke(email_data)
