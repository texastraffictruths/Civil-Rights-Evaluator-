import json
import os
import requests
from typing import Dict, List, Optional

class SambanovaClient:
    """
    SambaNova AI client for legal analysis and document generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "e0d79301-ca3b-4b35-a816-54f2987ae3db"
        self.base_url = "https://api.sambanova.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def chat_completion(self, messages: List[Dict], model: str = "Meta-Llama-3.1-8B-Instruct", 
                       max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """
        Generate chat completion using SambaNova API
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def analyze_legal_text(self, text: str, analysis_type: str = "general") -> str:
        """
        Analyze legal text using SambaNova AI
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert legal analyst specializing in Texas law. Provide thorough, accurate legal analysis with specific citations to Texas statutes and case law when applicable."
            },
            {
                "role": "user", 
                "content": f"Analyze this legal text for {analysis_type} analysis:\n\n{text}"
            }
        ]
        
        return self.chat_completion(messages)
    
    def generate_legal_document(self, document_type: str, case_details: Dict, 
                              legal_authorities: Optional[List[Dict]] = None) -> str:
        """
        Generate legal document content using SambaNova AI
        """
        authorities_text = ""
        if legal_authorities:
            authorities_text = "\n\nRelevant Legal Authorities:\n"
            for auth in legal_authorities:
                authorities_text += f"- {auth.get('citation', '')}: {auth.get('summary', '')}\n"
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert legal document writer specializing in Texas court documents. Generate Supreme Court-quality legal documents that comply with Texas court formatting requirements. Use proper legal citations and ensure all arguments are supported by verified legal authority."
            },
            {
                "role": "user",
                "content": f"Generate a {document_type} document with the following case details:\n\n{json.dumps(case_details, indent=2)}{authorities_text}\n\nEnsure the document is court-ready with proper formatting, legal citations, and persuasive arguments."
            }
        ]
        
        return self.chat_completion(messages, max_tokens=4000)
    
    def provide_legal_advice(self, query: str, case_context: Optional[Dict] = None) -> str:
        """
        Provide legal advice with sharp, witty personality
        """
        context_text = ""
        if case_context:
            context_text = f"\n\nCase Context:\n{json.dumps(case_context, indent=2)}"
        
        messages = [
            {
                "role": "system", 
                "content": "You are a sharp, witty AI legal companion with world-class trial preparation skills. You specialize in Texas law and provide top 1% quality legal advice for pro se litigants. Your personality is confident, direct, and focused on winning cases. Provide practical, actionable advice while maintaining professional standards."
            },
            {
                "role": "user",
                "content": f"{query}{context_text}"
            }
        ]
        
        return self.chat_completion(messages)
    
    def analyze_evidence(self, evidence_description: str, case_type: str) -> Dict:
        """
        Analyze evidence for legal relevance and strategy
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert evidence analyst for legal cases. Analyze evidence for relevance, admissibility, and strategic value. Provide JSON response with analysis."
            },
            {
                "role": "user",
                "content": f"Analyze this evidence for a {case_type} case:\n\n{evidence_description}\n\nProvide analysis in JSON format with keys: relevance_score, admissibility_issues, strategic_value, recommendations."
            }
        ]
        
        response = self.chat_completion(messages)
        try:
            return json.loads(response)
        except:
            return {
                "relevance_score": "Unknown",
                "admissibility_issues": "Analysis failed",
                "strategic_value": "Unknown", 
                "recommendations": response
            }
    
    def generate_defense_counter(self, defense_type: str, case_facts: str) -> str:
        """
        Generate counter-response to common legal defenses
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert litigation strategist specializing in defeating common legal defenses. Generate comprehensive counter-arguments with supporting legal authority and tactical approaches specific to Texas law."
            },
            {
                "role": "user",
                "content": f"Generate a comprehensive counter-response to {defense_type} defense based on these case facts:\n\n{case_facts}\n\nInclude legal citations, tactical approaches, and pre-emptive arguments."
            }
        ]
        
        return self.chat_completion(messages, max_tokens=3000)
    
    def test_connection(self) -> bool:
        """
        Test API connection and functionality
        """
        try:
            messages = [{"role": "user", "content": "Test connection"}]
            response = self.chat_completion(messages)
            return "error" not in response.lower()
        except:
            return False