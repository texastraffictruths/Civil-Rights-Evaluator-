import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from sambanova_client import SambanovaClient

class ProSeEducation:
    """
    Pro Se Legal Education Center with step-by-step guidance
    """
    
    def __init__(self):
        self.client = SambanovaClient(api_key="e0d79301-ca3b-4b35-a816-54f2987ae3db")
        
        # Education content categories
        self.education_topics = {
            "Civil Procedure": {
                "description": "Rules governing civil litigation process",
                "subtopics": ["Filing Complaints", "Service of Process", "Discovery", "Motions", "Trial Procedure"]
            },
            "Evidence Law": {
                "description": "Rules for presenting evidence in court",
                "subtopics": ["Admissibility", "Hearsay", "Authentication", "Expert Testimony", "Objections"]
            },
            "Constitutional Rights": {
                "description": "Understanding your constitutional protections",
                "subtopics": ["Due Process", "Equal Protection", "First Amendment", "Fourth Amendment", "Civil Rights"]
            },
            "Texas State Law": {
                "description": "Texas-specific legal requirements and procedures",
                "subtopics": ["Texas Civil Practice", "State Court Rules", "Texas Statutes", "Local Rules", "Jurisdiction"]
            },
            "Federal Law": {
                "description": "Federal court procedures and requirements",
                "subtopics": ["Federal Rules", "Jurisdiction", "Section 1983", "Federal Question", "Diversity"]
            }
        }
        
        # Common legal procedures with step-by-step guidance
        self.procedures = {
            "Filing a Complaint": {
                "description": "How to properly file a civil complaint",
                "steps": [
                    "Research applicable law and jurisdiction",
                    "Draft complaint with required elements",
                    "Calculate and pay filing fees",
                    "File with appropriate court clerk",
                    "Arrange for service of process",
                    "File proof of service with court"
                ],
                "requirements": ["Standing", "Jurisdiction", "Proper venue", "Statute of limitations", "Legal claims"]
            },
            "Discovery Process": {
                "description": "How to conduct legal discovery",
                "steps": [
                    "Plan discovery strategy",
                    "Serve initial disclosures",
                    "Draft and serve discovery requests",
                    "Respond to opposing discovery",
                    "Take and defend depositions",
                    "Compile evidence for trial"
                ],
                "requirements": ["Meet and confer", "Good faith efforts", "Proportionality", "Privilege protection"]
            },
            "Motion Practice": {
                "description": "How to file and argue motions",
                "steps": [
                    "Research applicable law",
                    "Draft motion with supporting brief",
                    "File motion with court",
                    "Serve opposing party",
                    "Prepare for hearing if required",
                    "Follow up on court's ruling"
                ],
                "requirements": ["Legal basis", "Factual support", "Proper formatting", "Meet and confer if required"]
            }
        }
    
    def get_education_content(self, topic: str) -> str:
        """
        Get comprehensive education content for a specific topic
        """
        try:
            if topic not in self.education_topics:
                return f"Topic '{topic}' not found. Available topics: {', '.join(self.education_topics.keys())}"
            
            topic_info = self.education_topics[topic]
            
            prompt = f"""
            Provide comprehensive educational content about {topic} for pro se litigants.
            
            Topic Description: {topic_info['description']}
            Subtopics to Cover: {', '.join(topic_info['subtopics'])}
            
            Please provide:
            1. Clear explanation of key concepts
            2. Practical guidance for pro se litigants
            3. Common pitfalls to avoid
            4. Texas-specific considerations where applicable
            5. Step-by-step guidance when possible
            6. Resources for further learning
            
            Focus on practical, actionable information that helps pro se litigants understand and apply the law effectively.
            """
            
            return self.client.provide_legal_advice(prompt, {"topic": topic, "education_type": "comprehensive"})
            
        except Exception as e:
            return f"Education content generation failed: {str(e)}"
    
    def get_procedure_guide(self, procedure: str) -> str:
        """
        Get detailed procedure guide with Texas-specific requirements
        """
        try:
            if procedure not in self.procedures:
                return f"Procedure '{procedure}' not found. Available procedures: {', '.join(self.procedures.keys())}"
            
            procedure_info = self.procedures[procedure]
            
            prompt = f"""
            Provide detailed step-by-step guidance for: {procedure}
            
            Description: {procedure_info['description']}
            Steps: {', '.join(procedure_info['steps'])}
            Requirements: {', '.join(procedure_info['requirements'])}
            
            Please provide:
            1. Detailed explanation of each step
            2. Texas court specific requirements
            3. Required forms and documents
            4. Common mistakes to avoid
            5. Timeline considerations
            6. Cost estimates where applicable
            7. Pro se litigant tips
            
            Make this practical and actionable for someone representing themselves.
            """
            
            return self.client.provide_legal_advice(prompt, {"procedure": procedure, "guide_type": "step_by_step"})
            
        except Exception as e:
            return f"Procedure guide generation failed: {str(e)}"
    
    def get_legal_forms_guide(self, form_type: str) -> Dict:
        """
        Get guidance on completing legal forms
        """
        try:
            form_guides = {
                "Complaint": "How to draft and file a civil complaint",
                "Answer": "How to respond to a lawsuit",
                "Motion": "How to file various types of motions",
                "Discovery": "How to complete discovery forms",
                "Subpoena": "How to issue and serve subpoenas"
            }
            
            if form_type not in form_guides:
                return {
                    'error': f"Form type '{form_type}' not available",
                    'available_forms': list(form_guides.keys())
                }
            
            prompt = f"""
            Provide comprehensive guidance for completing {form_type} forms for pro se litigants.
            
            Include:
            1. Required information and documents
            2. Step-by-step completion instructions
            3. Common errors to avoid
            4. Texas court formatting requirements
            5. Filing procedures and fees
            6. Sample language and templates
            7. What happens after filing
            
            Focus on practical, error-preventing guidance.
            """
            
            guidance = self.client.analyze_legal_text(prompt, "form_guidance")
            
            return {
                'form_type': form_type,
                'description': form_guides[form_type],
                'guidance': guidance,
                'generated_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Form guidance generation failed: {str(e)}",
                'form_type': form_type
            }
    
    def get_courtroom_etiquette_guide(self) -> str:
        """
        Get comprehensive courtroom etiquette and behavior guidance
        """
        return """
        COURTROOM ETIQUETTE FOR PRO SE LITIGANTS
        
        BEFORE ENTERING THE COURTROOM:
        • Arrive 15-30 minutes early
        • Dress professionally (business attire)
        • Bring organized case materials
        • Turn off or silence electronic devices
        • Review your notes and key points
        
        ADDRESSING THE COURT:
        • Always stand when speaking to the judge
        • Address the judge as "Your Honor"
        • Wait to be recognized before speaking
        • Speak clearly and at appropriate volume
        • Never interrupt the judge or opposing counsel
        
        COURTROOM BEHAVIOR:
        • Maintain respectful demeanor at all times
        • Do not argue with opposing counsel directly
        • Address all remarks to the judge
        • Avoid emotional outbursts or personal attacks
        • Take notes quietly during proceedings
        
        PRESENTING YOUR CASE:
        • Organize your arguments logically
        • Cite relevant law and evidence
        • Stick to the facts and legal issues
        • Be prepared to answer the judge's questions
        • Respect time limits set by the court
        
        COMMON MISTAKES TO AVOID:
        • Speaking out of turn
        • Arguing when the judge has made a ruling
        • Bringing up irrelevant personal details
        • Failing to follow court rules and procedures
        • Being unprepared or disorganized
        
        TEXAS-SPECIFIC CONSIDERATIONS:
        • Review local court rules for your specific court
        • Some courts require pre-trial conferences
        • Mediation may be required in certain cases
        • Electronic filing may be mandatory
        • Check court website for specific requirements
        """
    
    def get_confidence_building_tips(self) -> List[str]:
        """
        Get confidence-building tips for pro se litigants
        """
        return [
            "Remember: You have the right to represent yourself in court",
            "Preparation is your greatest advantage - know your facts and law",
            "Practice presenting your case out loud before the hearing",
            "Organize all documents and evidence in advance",
            "Focus on the legal issues, not personal emotions",
            "Ask the court clerk questions about procedures if needed",
            "Observe other court proceedings to learn courtroom dynamics",
            "Speak slowly and clearly - the court reporter must record everything",
            "Bring backup copies of all important documents",
            "Stay calm and professional, even under pressure",
            "Know that judges are generally patient with pro se litigants",
            "Focus on presenting facts and evidence, not arguments",
            "Be honest about what you don't know - it's better than guessing",
            "Dress professionally to show respect for the court",
            "Arrive early to familiarize yourself with the courtroom"
        ]
    
    def get_case_evaluation_checklist(self) -> Dict:
        """
        Get checklist for evaluating whether to proceed pro se
        """
        return {
            'case_complexity': {
                'simple_cases': [
                    "Small claims disputes",
                    "Uncontested divorces", 
                    "Simple contract disputes",
                    "Basic landlord-tenant issues"
                ],
                'complex_cases': [
                    "Federal civil rights cases",
                    "Multi-party litigation",
                    "Cases requiring expert testimony",
                    "Complex commercial disputes"
                ]
            },
            'evaluation_questions': [
                "Do I understand the legal issues in my case?",
                "Can I clearly explain the facts to a judge?",
                "Do I have time to research and prepare properly?",
                "Am I comfortable speaking in court?",
                "Can I afford attorney fees if I lose?",
                "Are there complex procedural requirements?",
                "Will I need expert witnesses?",
                "Is the opposing party represented by counsel?"
            ],
            'proceed_pro_se_if': [
                "Case is relatively straightforward",
                "You have time to prepare thoroughly",
                "Court procedures are manageable",
                "Potential recovery justifies the effort",
                "You're comfortable with public speaking"
            ],
            'consider_attorney_if': [
                "Case involves complex legal issues",
                "Significant money or rights at stake",
                "Multiple parties involved",
                "Expert testimony required",
                "Opposing counsel is experienced"
            ],
            'resources_available': [
                "Court self-help centers",
                "Legal aid organizations",
                "Law library resources",
                "Online legal research tools",
                "Paralegal assistance services"
            ]
        }
    
    def get_resource_directory(self) -> Dict:
        """
        Get directory of helpful resources for pro se litigants
        """
        return {
            'texas_courts': {
                'supreme_court': "https://www.txcourts.gov/supreme-court/",
                'court_of_appeals': "https://www.txcourts.gov/courts-of-appeals/",
                'district_courts': "https://www.txcourts.gov/trial-courts/",
                'self_help': "https://www.txcourts.gov/programs-services/self-help/"
            },
            'legal_research': {
                'texas_statutes': "https://statutes.capitol.texas.gov/",
                'case_law': "https://casetext.com/",
                'court_rules': "https://www.txcourts.gov/rules-forms/",
                'legal_forms': "https://www.txcourts.gov/rules-forms/forms/"
            },
            'assistance_programs': {
                'legal_aid': "https://www.texaslawhelp.org/",
                'pro_bono': "https://www.texasbar.com/AM/Template.cfm?Section=Lawyer_Referral_Service",
                'law_libraries': "Contact your local county law library",
                'self_help_centers': "Available at most Texas courthouses"
            },
            'educational_resources': {
                'texas_bar': "https://www.texasbar.com/AM/Template.cfm?Section=Free_Legal_Information",
                'nolo_legal': "https://www.nolo.com/",
                'justia': "https://www.justia.com/",
                'cornell_law': "https://www.law.cornell.edu/"
            },
            'filing_information': {
                'court_fees': "Varies by court and case type",
                'fee_waivers': "Available for indigent litigants",
                'electronic_filing': "Check with specific court",
                'service_requirements': "Personal service usually required"
            }
        }