"""
LLM Provider Wrapper for HealthLabelCheck
Supports Groq and Google Gemini APIs
"""

import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, model: str, temperature: float = 0.3, max_tokens: int = 500):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response from messages"""
        raise NotImplementedError


class GroqProvider(LLMProvider):
    """Groq API provider"""
    
    def __init__(self, model: str = None, temperature: float = 0.3, max_tokens: int = 500):
        super().__init__(
            model=model or os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile'),
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.api_key = os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Groq API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=float(os.getenv('LLM_TOP_P', 0.9))
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")


class GeminiProvider(LLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, model: str = None, temperature: float = 0.3, max_tokens: int = 500):
        super().__init__(
            model=model or os.getenv('GEMINI_MODEL', 'gemini-pro'),
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Gemini API"""
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            response = self.client.generate_content(
                prompt,
                generation_config={
                    'temperature': self.temperature,
                    'max_output_tokens': self.max_tokens,
                    'top_p': float(os.getenv('LLM_TOP_P', 0.9))
                }
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to single prompt"""
        prompt_parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt_parts.append(f"System: {content}\n")
            elif role == 'user':
                prompt_parts.append(f"User: {content}\n")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}\n")
        return "\n".join(prompt_parts)


class HealthLabelCheckLLM:
    """Main LLM interface for HealthLabelCheck"""
    
    def __init__(self, provider: str = None):
        """
        Initialize LLM with specified provider
        
        Args:
            provider: "groq" or "gemini" (defaults to LLM_PROVIDER env var)
        """
        self.provider_name = provider or os.getenv('LLM_PROVIDER', 'groq')
        self.temperature = float(os.getenv('LLM_TEMPERATURE', 0.3))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', 500))
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
        # Initialize provider
        if self.provider_name.lower() == 'groq':
            self.provider = GroqProvider(
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        elif self.provider_name.lower() == 'gemini':
            self.provider = GeminiProvider(
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider_name}. Use 'groq' or 'gemini'")
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file"""
        prompt_path = 'prompts/system_prompt.md'
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback system prompt
            return """You are HealthLabelCheck AI, an expert in FSSAI food labelling regulations.
Help small food business owners understand what must be printed on their food packets.
Always cite regulation numbers and provide practical guidance."""
    
    def _load_task_prompt(self, task: str) -> Optional[str]:
        """Load task-specific prompt"""
        prompt_path = f'prompts/task_{task}.md'
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
    
    def chat(self, user_message: str, task: str = "answer_question", context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a chat response
        
        Args:
            user_message: User's question or input
            task: Task type ("answer_question", "checklist_generator")
            context: Optional context (retrieved regulations, etc.)
        
        Returns:
            Dict with answer, confidence, follow_up
        """
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add task-specific prompt if available
        task_prompt = self._load_task_prompt(task)
        if task_prompt:
            messages.append({"role": "system", "content": task_prompt})
        
        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Relevant regulations:\n{context}"
            })
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        response_text = self.provider.generate(messages)
        
        # Try to parse JSON response
        try:
            response_data = json.loads(response_text)
            return response_data
        except json.JSONDecodeError:
            # If not JSON, wrap in default structure
            return {
                "answer": response_text,
                "confidence": 0.8,
                "follow_up": None
            }
    
    def answer_question(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Answer a user question about FSSAI regulations"""
        return self.chat(question, task="answer_question", context=context)
    
    def generate_checklist(self, product_info: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Generate a compliance checklist"""
        return self.chat(product_info, task="checklist_generator", context=context)


# Singleton instance
_llm_instance: Optional[HealthLabelCheckLLM] = None


def get_llm() -> HealthLabelCheckLLM:
    """Get or create LLM singleton instance"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = HealthLabelCheckLLM()
    return _llm_instance


if __name__ == "__main__":
    # Test the LLM wrapper
    print("=== Testing HealthLabelCheck LLM ===\n")
    
    try:
        llm = get_llm()
        print(f"Provider: {llm.provider_name}")
        print(f"Model: {llm.provider.model}")
        print(f"Temperature: {llm.temperature}\n")
        
        # Test question
        test_question = "What is the rule for the vegetarian symbol?"
        print(f"Question: {test_question}\n")
        
        response = llm.answer_question(test_question)
        print(f"Answer: {response['answer'][:200]}...")
        print(f"\nConfidence: {response.get('confidence', 'N/A')}")
        print(f"Follow-up: {response.get('follow_up', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key to .env")
        print("3. Install required package: pip install groq  (or google-generativeai)")
