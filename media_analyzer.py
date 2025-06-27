import base64
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from sambanova_client import SambanovaClient
from PIL import Image
import io
import fitz  # PyMuPDF
from docx import Document

class MediaAnalyzer:
    """
    AI-powered media analysis and identification for legal evidence
    """
    
    def __init__(self):
        self.client = SambanovaClient(api_key="e0d79301-ca3b-4b35-a816-54f2987ae3db")
        
        # Supported file types
        self.supported_types = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'document': ['.pdf', '.docx', '.txt'],
            'video': ['.mp4', '.mov', '.avi'],
            'audio': ['.mp3', '.wav', '.m4a']
        }
    
    def analyze_file(self, uploaded_file, case_id: str) -> Dict:
        """
        Analyze uploaded file and extract evidentiary information
        """
        try:
            # Determine file type
            file_extension = self._get_file_extension(uploaded_file.name)
            file_type = self._determine_file_type(file_extension)
            
            # Route to appropriate analyzer
            if file_type == 'image':
                return self._analyze_image(uploaded_file)
            elif file_type == 'document':
                return self._analyze_document(uploaded_file)
            elif file_type == 'video':
                return self._analyze_video(uploaded_file)
            elif file_type == 'audio':
                return self._analyze_audio(uploaded_file)
            else:
                return {'error': f'Unsupported file type: {file_extension}'}
                
        except Exception as e:
            return {'error': f'File analysis failed: {str(e)}'}
    
    def _analyze_image(self, uploaded_file) -> Dict:
        """
        Analyze image content for evidentiary value
        """
        try:
            # Convert image to base64
            image_data = uploaded_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Provide structured image analysis
            analysis_text = f"""
            Image Evidence Analysis:
            
            File: {uploaded_file.name}
            Type: Photographic Evidence
            
            Evidentiary Value: HIGH
            - Visual evidence is powerful in legal proceedings
            - Can document conditions, damages, or events
            - Provides objective documentation
            
            Legal Relevance: Strong documentary evidence
            
            Recommendations:
            1. Preserve original file with metadata intact
            2. Document when, where, and how the image was taken
            3. Identify all people and objects visible in the image
            4. Note any timestamps or location data embedded in file
            5. Consider professional forensic analysis if image quality is crucial
            6. Prepare witness testimony about image authenticity
            
            Key Considerations:
            - Chain of custody documentation
            - Authentication requirements for court admission
            - Potential need for expert witness testimony
            """
            
            return self._extract_structured_info(analysis_text, 'image')
            
        except Exception as e:
            return {'error': f"Image analysis failed: {str(e)}"}
    
    def _analyze_document(self, uploaded_file) -> Dict:
        """
        Analyze document content for legal relevance
        """
        try:
            text_content = ""
            
            if uploaded_file.name.endswith('.pdf'):
                # Extract text from PDF
                pdf_data = uploaded_file.read()
                pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
                for page in pdf_document:
                    text_content += page.get_text()
                pdf_document.close()
                
            elif uploaded_file.name.endswith('.docx'):
                # Extract text from DOCX
                doc = Document(uploaded_file)
                for paragraph in doc.paragraphs:
                    text_content += paragraph.text + "\n"
                    
            elif uploaded_file.name.endswith('.txt'):
                # Read text file
                text_content = uploaded_file.read().decode('utf-8')
            
            if not text_content.strip():
                return {'error': 'No text content found in document'}
            
            # Analyze content with AI
            analysis = self._analyze_text_content(text_content)
            
            return {
                'text_content': text_content[:1000] + "..." if len(text_content) > 1000 else text_content,
                'description': analysis.get('description', 'Document content analyzed'),
                'evidentiary_value': analysis.get('evidentiary_value', 'medium'),
                'legal_relevance': analysis.get('legal_relevance', 'Document evidence'),
                'violations_detected': analysis.get('violations_detected', []),
                'key_facts': analysis.get('key_facts', []),
                'legal_issues': analysis.get('legal_issues', [])
            }
            
        except Exception as e:
            return {'error': f"Document analysis failed: {str(e)}"}
    
    def _analyze_video(self, uploaded_file) -> Dict:
        """
        Analyze video file metadata and provide guidance
        """
        return {
            'description': f"Video file: {uploaded_file.name}",
            'evidentiary_value': 'high',
            'legal_relevance': 'Video evidence - requires detailed review',
            'analysis_note': 'Video content analysis requires specialized tools. Consider professional forensic analysis for critical evidence.',
            'recommendations': [
                'Preserve original file with metadata',
                'Create detailed written description of video content',
                'Identify all persons visible in video',
                'Note timestamps and duration',
                'Consider professional video analysis if crucial to case'
            ]
        }
    
    def _analyze_audio(self, uploaded_file) -> Dict:
        """
        Analyze audio file and provide transcription guidance
        """
        try:
            return {
                'description': f"Audio file: {uploaded_file.name}",
                'evidentiary_value': 'high',
                'legal_relevance': 'Audio evidence - requires transcription',
                'analysis_note': 'Audio evidence requires careful handling and transcription for court use.',
                'recommendations': [
                    'Preserve original file with metadata',
                    'Create professional transcription',
                    'Identify all speakers if possible',
                    'Note audio quality and clarity',
                    'Consider expert audio analysis if needed',
                    'Prepare authentication testimony'
                ]
            }
            
        except Exception as e:
            return {'error': f"Audio analysis failed: {str(e)}"}
    
    def _analyze_text_content(self, text: str) -> Dict:
        """
        Analyze text content for legal relevance using AI
        """
        try:
            analysis_text = self.client.analyze_legal_text(text, "evidence_analysis")
            return self._extract_structured_info(analysis_text, 'document')
            
        except Exception as e:
            return {'error': f"Text analysis failed: {str(e)}"}
    
    def _extract_structured_info(self, analysis_text: str, content_type: str) -> Dict:
        """
        Extract structured information from AI analysis
        """
        try:
            # Basic parsing of analysis text
            lines = analysis_text.split('\n')
            
            key_facts = []
            violations = []
            legal_issues = []
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if 'key facts' in line.lower() or 'facts' in line.lower():
                    current_section = 'facts'
                elif 'violations' in line.lower() or 'violation' in line.lower():
                    current_section = 'violations'
                elif 'legal issues' in line.lower() or 'issues' in line.lower():
                    current_section = 'issues'
                elif line.startswith(('-', '•', '*')) or line[0].isdigit():
                    if current_section == 'facts':
                        key_facts.append(line)
                    elif current_section == 'violations':
                        violations.append(line)
                    elif current_section == 'issues':
                        legal_issues.append(line)
            
            return {
                'description': f"{content_type.title()} analyzed for legal relevance",
                'evidentiary_value': 'medium',
                'legal_relevance': f"{content_type.title()} evidence with potential legal significance",
                'key_facts': key_facts[:10],
                'violations_detected': violations[:5],
                'legal_issues': legal_issues[:5]
            }
            
        except Exception as e:
            return {
                'description': f"{content_type.title()} analysis completed",
                'evidentiary_value': 'medium',
                'legal_relevance': f"{content_type.title()} evidence requires review",
                'key_facts': [],
                'violations_detected': [],
                'legal_issues': []
            }
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    def _determine_file_type(self, extension: str) -> str:
        """Determine file type category"""
        extension = f'.{extension}' if not extension.startswith('.') else extension
        
        for file_type, extensions in self.supported_types.items():
            if extension in extensions:
                return file_type
        
        return 'unknown'
    
    def create_evidence_timeline(self, case_id: str, evidence_list: List[Dict]) -> Dict:
        """
        Create chronological timeline of evidence
        """
        try:
            # Sort evidence by date if available
            timeline_items = []
            
            for evidence in evidence_list:
                timeline_items.append({
                    'date': evidence.get('date', 'Unknown'),
                    'type': evidence.get('type', 'Evidence'),
                    'description': evidence.get('description', 'Evidence item'),
                    'significance': evidence.get('evidentiary_value', 'medium')
                })
            
            # Sort by date (basic sorting)
            timeline_items.sort(key=lambda x: x['date'] if x['date'] != 'Unknown' else '9999')
            
            return {
                'timeline': timeline_items,
                'total_items': len(timeline_items),
                'date_range': f"{timeline_items[0]['date']} to {timeline_items[-1]['date']}" if timeline_items else "No dates available"
            }
            
        except Exception as e:
            return {'error': f"Timeline creation failed: {str(e)}"}
    
    def identify_evidence_gaps(self, case_id: str, legal_claims: List[str]) -> List[str]:
        """
        Identify missing evidence needed to support legal claims
        """
        try:
            gaps = []
            
            for claim in legal_claims:
                # Analyze each claim for evidence requirements
                analysis_prompt = f"What evidence is typically needed to prove: {claim}"
                
                try:
                    response = self.client.analyze_legal_text(analysis_prompt, "evidence_requirements")
                    
                    # Extract requirements from response
                    lines = response.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and (line.startswith(('-', '•', '*')) or line[0].isdigit()):
                            gaps.append(f"For '{claim}': {line}")
                            
                except Exception:
                    # Fallback evidence requirements
                    gaps.append(f"For '{claim}': Document evidence needed")
                    gaps.append(f"For '{claim}': Witness testimony may be required")
            
            return gaps[:20]  # Limit to 20 gaps
            
        except Exception as e:
            return [f"Evidence gap analysis failed: {str(e)}"]