import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from sambanova_client import SambanovaClient

class AICompanion:
    """
    Omnipresent AI Legal Companion with sharp, witty personality
    and top 1% trial preparation skills
    """
    
    def __init__(self):
        self.client = SambanovaClient(api_key="e0d79301-ca3b-4b35-a816-54f2987ae3db")
        
        self.personality = """
        You are a sharp, witty AI legal companion with world-class trial skills and top 1% 
        legal expertise. You specialize in Texas law and pro se litigation support.
        
        Your personality traits:
        - Direct and confident
        - Sharp wit with legal humor
        - Zero tolerance for legal nonsense
        - Focused on winning cases
        - Protective of pro se litigants
        
        Your expertise includes:
        - Texas civil procedure
        - Federal court procedures
        - Evidence law and strategy
        - Document drafting excellence
        - Pre-emptive defense neutralization
        - Strategic case positioning
        """
    
    def get_response(self, user_query: str, case_id: Optional[str] = None) -> str:
        """
        Get response from AI companion with personality and expertise
        """
        try:
            system_prompt = f"""
            {self.personality}
            
            Current context: The user is asking about their legal matter. 
            Case ID: {case_id if case_id else 'No active case'}
            
            CRITICAL: Only provide legal information backed by verified authorities. 
            Never give theoretical legal advice. Always remind users to verify 
            legal information independently.
            
            Respond with confidence and wit, but ensure all legal claims are accurate.
            """
            
            return self.client.provide_legal_advice(user_query, {"case_id": case_id})
            
        except Exception as e:
            return f"I'm having trouble connecting right now. Error: {str(e)}. But don't worry - I'll be back with sharp legal insights soon!"
    
    def analyze_case_facts(self, case_id: str) -> str:
        """
        Analyze case facts and identify legal theories
        """
        try:
            prompt = """
            Analyze the case facts and identify potential legal theories and claims.
            Focus on:
            1. Strongest legal claims
            2. Required elements for each claim
            3. Evidence needed
            4. Potential defenses to expect
            5. Strategic recommendations
            
            Be specific about Texas law requirements and cite relevant statutes.
            """
            
            return self.client.analyze_legal_text(prompt, "case_analysis")
            
        except Exception as e:
            return f"Case analysis temporarily unavailable: {str(e)}"
    
    def assess_case_strength(self, case_id: str) -> str:
        """
        Assess overall case strength and likelihood of success
        """
        try:
            prompt = """
            Provide a realistic assessment of case strength based on:
            1. Legal merits
            2. Evidence quality
            3. Procedural positioning
            4. Opponent's likely defenses
            5. Settlement vs. trial considerations
            
            Give a frank assessment with specific recommendations for improvement.
            Include potential monetary recovery estimates if applicable.
            """
            
            return self.client.provide_legal_advice(prompt, {"analysis_type": "case_strength"})
            
        except Exception as e:
            return f"Case strength assessment unavailable: {str(e)}"
    
    def generate_strategy(self, case_id: str) -> str:
        """
        Generate comprehensive litigation strategy
        """
        try:
            prompt = """
            Generate a comprehensive litigation strategy including:
            1. Phase-by-phase approach
            2. Key deadlines and milestones
            3. Discovery strategy
            4. Motion practice recommendations
            5. Settlement positioning
            6. Trial preparation priorities
            
            Focus on Texas-specific procedures and winning tactics.
            """
            
            return self.client.provide_legal_advice(prompt, {"strategy_type": "comprehensive"})
            
        except Exception as e:
            return f"Strategy generation unavailable: {str(e)}"
    
    def get_document_suggestions(self, document_type: str, case_context: Dict) -> List[str]:
        """
        Get smart suggestions for document improvement
        """
        try:
            prompt = f"""
            Provide specific suggestions for improving a {document_type} document.
            Consider Texas court requirements and best practices.
            Case context: {json.dumps(case_context, indent=2)}
            
            Provide actionable suggestions as a numbered list.
            """
            
            response = self.client.provide_legal_advice(prompt, case_context)
            
            # Extract suggestions from response
            suggestions = []
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    suggestions.append(line)
            
            return suggestions[:10]  # Limit to 10 suggestions
            
        except Exception as e:
            return [f"Document suggestions unavailable: {str(e)}"]
    
    def check_for_missing_elements(self, case_id: str) -> List[str]:
        """
        Identify missing case elements that need attention
        """
        try:
            prompt = """
            Identify missing elements in this case that need immediate attention:
            1. Required legal documents
            2. Missing evidence
            3. Procedural deadlines
            4. Strategic weaknesses
            5. Compliance issues
            
            Prioritize by urgency and importance.
            """
            
            response = self.client.analyze_legal_text(prompt, "missing_elements")
            
            # Extract missing elements from response
            missing_elements = []
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    missing_elements.append(line)
            
            return missing_elements[:15]  # Limit to 15 elements
            
        except Exception as e:
            return [f"Missing elements check unavailable: {str(e)}"]