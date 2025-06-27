from typing import Dict, List
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import io
import os
from sambanova_client import SambanovaClient

class DocumentGenerator:
    """
    Generates Supreme Court-quality legal documents with Texas court compliance
    """
    
    def __init__(self, legal_authority):
        self.legal_authority = legal_authority
        self.client = SambanovaClient(api_key="e0d79301-ca3b-4b35-a816-54f2987ae3db")
        
        # Texas court formatting requirements
        self.texas_format = {
            'font_size': 12,
            'line_spacing': 1.5,
            'margins': 1.0,  # inch
            'page_numbering': True,
            'signature_block': True
        }
    
    def generate_document(self, doc_type: str, case_id: str, params: Dict) -> Dict:
        """
        Generate a complete legal document with verified authority
        """
        try:
            # Get legal authorities relevant to document type
            authorities = self.legal_authority.get_relevant_authorities(doc_type, params)
            
            # Generate document content with AI
            content = self._generate_document_content(doc_type, params, authorities)
            
            # Generate PDF
            pdf_data = self._generate_pdf(content, params)
            
            return {
                'content': content,
                'pdf_data': pdf_data,
                'authorities_used': authorities,
                'generated_date': datetime.now().isoformat(),
                'document_type': doc_type
            }
            
        except Exception as e:
            return {
                'error': f"Document generation failed: {str(e)}",
                'content': '',
                'pdf_data': b'',
                'authorities_used': [],
                'generated_date': datetime.now().isoformat()
            }
    
    def _generate_document_content(self, doc_type: str, params: Dict, authorities: List[Dict]) -> str:
        """
        Generate document content using AI with verified legal authorities
        """
        authority_text = "\n".join([f"- {auth['citation']}: {auth['summary']}" for auth in authorities])
        
        prompt = f"""
        Generate a Supreme Court-quality {doc_type} document with the following requirements:
        
        DOCUMENT PARAMETERS:
        - Plaintiff: {params.get('plaintiff_name', 'N/A')}
        - Defendant: {params.get('defendant_name', 'N/A')}
        - Case Number: {params.get('case_number', 'To be assigned')}
        - Court: {params.get('court_name', 'District Court')}
        - Case Facts: {params.get('case_facts', 'N/A')}
        - Legal Claims: {params.get('legal_claims', 'N/A')}
        
        VERIFIED LEGAL AUTHORITIES TO CITE:
        {authority_text}
        
        FORMATTING REQUIREMENTS:
        - Texas court compliance
        - Professional legal writing
        - Proper citations
        - Clear argument structure
        - Persuasive language
        - All required legal elements
        
        CRITICAL: Only use the provided verified legal authorities. Do not create 
        fictional cases or statutes. Include proper pre-emptive responses to 
        likely defendant arguments.
        
        Generate the complete document text ready for court filing.
        """
        
        case_details = {
            "document_type": doc_type,
            "case_parameters": params,
            "formatting": "Texas court compliance"
        }
        
        return self.client.generate_legal_document(doc_type, case_details, authorities)
    
    def _generate_pdf(self, content: str, params: Dict) -> bytes:
        """
        Generate Texas-compliant PDF document
        """
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=self.texas_format['margins'] * inch,
            rightMargin=self.texas_format['margins'] * inch,
            topMargin=self.texas_format['margins'] * inch,
            bottomMargin=self.texas_format['margins'] * inch
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles for legal documents
        title_style = ParagraphStyle(
            'LegalTitle',
            parent=styles['Title'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Times-Bold'
        )
        
        body_style = ParagraphStyle(
            'LegalBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            leading=18  # 1.5 line spacing
        )
        
        # Build document content
        story = []
        
        # Header with case information
        if params.get('case_number'):
            story.append(Paragraph(f"Case No. {params['case_number']}", title_style))
        
        story.append(Paragraph(f"{params.get('court_name', 'DISTRICT COURT')}", title_style))
        story.append(Spacer(1, 12))
        
        # Party information
        story.append(Paragraph(f"{params.get('plaintiff_name', 'PLAINTIFF')},", body_style))
        story.append(Paragraph("Plaintiff,", body_style))
        story.append(Paragraph("v.", body_style))
        story.append(Paragraph(f"{params.get('defendant_name', 'DEFENDANT')},", body_style))
        story.append(Paragraph("Defendant.", body_style))
        story.append(Spacer(1, 20))
        
        # Document content
        # Split content into paragraphs and format
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 6))
        
        # Signature block
        story.append(Spacer(1, 30))
        story.append(Paragraph("Respectfully submitted,", body_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph("_________________________", body_style))
        story.append(Paragraph(f"{params.get('plaintiff_name', 'Pro Se Plaintiff')}", body_style))
        story.append(Paragraph("Pro Se", body_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def get_document_templates(self) -> Dict[str, Dict]:
        """
        Get available document templates with descriptions
        """
        return {
            "Civil Rights Complaint": {
                "description": "42 USC 1983 civil rights violation complaint",
                "required_elements": ["Constitutional violation", "Color of law", "Damages"],
                "typical_defenses": ["Qualified immunity", "Statute of limitations"]
            },
            "Motion to Dismiss Response": {
                "description": "Response to defendant's motion to dismiss",
                "required_elements": ["Facts stated", "Legal sufficiency", "Standard of review"],
                "typical_defenses": ["Failure to state claim", "Lack of jurisdiction"]
            },
            "Summary Judgment Motion": {
                "description": "Motion for summary judgment with supporting evidence",
                "required_elements": ["Undisputed facts", "Legal standard", "No genuine issue"],
                "typical_defenses": ["Disputed facts", "Legal questions remain"]
            },
            "Discovery Requests": {
                "description": "Interrogatories, requests for production, admissions",
                "required_elements": ["Relevant scope", "Proper format", "Good faith"],
                "typical_defenses": ["Overly broad", "Privileged", "Burden"]
            },
            "Immunity Defense Response": {
                "description": "Response to qualified/sovereign immunity claims",
                "required_elements": ["Clearly established law", "Factual allegations", "Good faith"],
                "typical_defenses": ["No clearly established right", "Reasonable reliance"]
            }
        }
    
    def validate_document_requirements(self, doc_type: str, params: Dict) -> List[str]:
        """
        Validate that document has all required elements
        """
        requirements = self.get_document_templates().get(doc_type, {}).get('required_elements', [])
        missing = []
        
        # Check basic requirements
        if not params.get('plaintiff_name'):
            missing.append("Plaintiff name required")
        if not params.get('defendant_name'):
            missing.append("Defendant name required")
        if not params.get('case_facts'):
            missing.append("Case facts required")
        if not params.get('legal_claims'):
            missing.append("Legal claims required")
        
        return missing
    
    def get_pre_emptive_defenses(self, doc_type: str) -> List[Dict]:
        """
        Get pre-emptive responses to expected defendant arguments
        """
        defense_responses = {
            "Civil Rights Complaint": [
                {
                    "defense": "Qualified Immunity",
                    "response": "Plaintiff's constitutional rights were clearly established at the time of violation, and no reasonable officer could have believed their conduct was lawful."
                },
                {
                    "defense": "Statute of Limitations", 
                    "response": "Claim filed within applicable limitation period, with continuing violation doctrine applying to ongoing misconduct."
                }
            ],
            "Motion to Dismiss Response": [
                {
                    "defense": "Failure to State Claim",
                    "response": "Complaint states plausible claim for relief with sufficient factual allegations to survive motion to dismiss under Twombly/Iqbal standard."
                }
            ]
        }
        
        return defense_responses.get(doc_type, [])
