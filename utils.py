import re
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import json
import os
import mimetypes
from pathlib import Path
import pytz

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount for display
    """
    try:
        if currency == "USD":
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except (ValueError, TypeError):
        return f"${0.00:,.2f}"

def get_texas_time() -> datetime:
    """
    Get current time in Texas (Central Time)
    """
    try:
        texas_tz = pytz.timezone('America/Chicago')
        return datetime.now(texas_tz)
    except Exception:
        # Fallback to UTC if timezone handling fails
        return datetime.now()

def format_texas_date(date_obj: datetime, include_time: bool = False) -> str:
    """
    Format date for Texas court documents
    """
    try:
        if include_time:
            return date_obj.strftime("%B %d, %Y at %I:%M %p CST")
        else:
            return date_obj.strftime("%B %d, %Y")
    except Exception:
        return "Date formatting error"

def generate_case_id() -> str:
    """
    Generate unique case ID
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"case_{timestamp}_{unique_id}"

def generate_document_id(doc_type: str) -> str:
    """
    Generate unique document ID
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_prefix = doc_type.lower().replace(" ", "_")[:10]
    unique_id = str(uuid.uuid4())[:6]
    return f"{doc_prefix}_{timestamp}_{unique_id}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system storage
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:190] + ext
    return sanitized or "unnamed_file"

def calculate_file_hash(file_content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content
    """
    return hashlib.sha256(file_content).hexdigest()

def get_file_type_category(filename: str) -> str:
    """
    Categorize file type based on extension
    """
    file_extension = Path(filename).suffix.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    document_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'}
    
    if file_extension in image_extensions:
        return 'image'
    elif file_extension in document_extensions:
        return 'document'
    elif file_extension in video_extensions:
        return 'video'
    elif file_extension in audio_extensions:
        return 'audio'
    else:
        return 'other'

def validate_email(email: str) -> bool:
    """
    Validate email address format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate US phone number format
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid US phone number (10 or 11 digits)
    return len(digits) in [10, 11] and (len(digits) == 10 or digits[0] == '1')

def format_phone(phone: str) -> str:
    """
    Format phone number for display
    """
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"1-({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't format

def parse_legal_citation(citation: str) -> Dict[str, str]:
    """
    Parse legal citation into components
    """
    # Basic citation parsing - could be enhanced with more sophisticated regex
    result = {
        'case_name': '',
        'volume': '',
        'reporter': '',
        'page': '',
        'year': '',
        'court': '',
        'full_citation': citation.strip()
    }
    
    try:
        # Pattern for basic case citation: Case Name, Volume Reporter Page (Court Year)
        pattern = r'^(.+?),\s*(\d+)\s+([A-Za-z\.]+)\s+(\d+)\s*\(([^)]+)\s+(\d{4})\)'
        match = re.match(pattern, citation.strip())
        
        if match:
            result.update({
                'case_name': match.group(1).strip(),
                'volume': match.group(2),
                'reporter': match.group(3),
                'page': match.group(4),
                'court': match.group(5).strip(),
                'year': match.group(6)
            })
    except Exception:
        pass  # Return basic result if parsing fails
    
    return result

def calculate_deadline(start_date: datetime, days: int, 
                      exclude_weekends: bool = True, 
                      exclude_holidays: bool = True) -> datetime:
    """
    Calculate deadline date considering business days and holidays
    """
    current_date = start_date
    days_added = 0
    
    # Basic US federal holidays (simplified)
    holidays_2024 = [
        datetime(2024, 1, 1),   # New Year's Day
        datetime(2024, 7, 4),   # Independence Day  
        datetime(2024, 12, 25), # Christmas Day
        # Add more holidays as needed
    ]
    
    holidays_2025 = [
        datetime(2025, 1, 1),   # New Year's Day
        datetime(2025, 7, 4),   # Independence Day
        datetime(2025, 12, 25), # Christmas Day
        # Add more holidays as needed
    ]
    
    all_holidays = holidays_2024 + holidays_2025
    
    while days_added < days:
        current_date += timedelta(days=1)
        
        # Check if it's a weekend
        if exclude_weekends and current_date.weekday() >= 5:  # Saturday=5, Sunday=6
            continue
            
        # Check if it's a holiday
        if exclude_holidays and current_date.date() in [h.date() for h in all_holidays]:
            continue
            
        days_added += 1
    
    return current_date

def get_texas_filing_deadlines() -> Dict[str, int]:
    """
    Get standard Texas court filing deadlines (in days)
    """
    return {
        'answer_to_lawsuit': 20,  # Days to file answer after service
        'motion_to_dismiss_response': 21,  # Days to respond to MTD
        'discovery_response': 30,  # Days to respond to discovery
        'summary_judgment_response': 21,  # Days to respond to MSJ
        'appeal_notice': 30,  # Days to file notice of appeal
        'appellate_brief': 40,  # Days to file appellate brief
        'motion_response_general': 21,  # General motion response time
        'deposition_notice': 30,  # Days notice for deposition
    }

def estimate_litigation_costs(case_type: str, complexity: str = 'medium') -> Dict[str, float]:
    """
    Estimate litigation costs for different case types
    """
    base_costs = {
        'Civil Rights Violation': {
            'low': 2500, 'medium': 7500, 'high': 25000
        },
        'Employment Discrimination': {
            'low': 3000, 'medium': 10000, 'high': 30000
        },
        'Personal Injury': {
            'low': 5000, 'medium': 15000, 'high': 50000
        },
        'Contract Dispute': {
            'low': 2000, 'medium': 8000, 'high': 20000
        },
        'Property Dispute': {
            'low': 3000, 'medium': 10000, 'high': 25000
        },
        'Other': {
            'low': 2500, 'medium': 8000, 'high': 20000
        }
    }
    
    case_costs = base_costs.get(case_type, base_costs['Other'])
    estimated_attorney_fees = case_costs.get(complexity, case_costs['medium'])
    
    # Pro se costs (much lower)
    pro_se_costs = {
        'filing_fees': 300,
        'service_costs': 100,
        'document_preparation': 200,
        'expert_witnesses': 1000,
        'court_reporter': 500,
        'miscellaneous': 300
    }
    
    return {
        'estimated_attorney_fees': estimated_attorney_fees,
        'pro_se_total_costs': sum(pro_se_costs.values()),
        'cost_breakdown': pro_se_costs,
        'potential_savings': estimated_attorney_fees - sum(pro_se_costs.values())
    }

def assess_case_strength(factors: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assess overall case strength based on various factors
    """
    strength_score = 0
    max_score = 0
    assessment_details = []
    
    # Legal merit (0-30 points)
    legal_merit = factors.get('legal_merit', 'medium')
    if legal_merit == 'strong':
        strength_score += 25
        assessment_details.append("Strong legal merit (+25)")
    elif legal_merit == 'medium':
        strength_score += 15
        assessment_details.append("Medium legal merit (+15)")
    else:
        strength_score += 5
        assessment_details.append("Weak legal merit (+5)")
    max_score += 30
    
    # Evidence quality (0-25 points)
    evidence_quality = factors.get('evidence_quality', 'medium')
    if evidence_quality == 'strong':
        strength_score += 20
        assessment_details.append("Strong evidence (+20)")
    elif evidence_quality == 'medium':
        strength_score += 12
        assessment_details.append("Medium evidence (+12)")
    else:
        strength_score += 3
        assessment_details.append("Weak evidence (+3)")
    max_score += 25
    
    # Damages clarity (0-20 points)
    damages_clear = factors.get('damages_clear', False)
    if damages_clear:
        strength_score += 15
        assessment_details.append("Clear damages (+15)")
    else:
        strength_score += 5
        assessment_details.append("Unclear damages (+5)")
    max_score += 20
    
    # Defendant's resources (0-15 points) - inverse scoring
    defendant_resources = factors.get('defendant_resources', 'medium')
    if defendant_resources == 'low':
        strength_score += 12
        assessment_details.append("Low defendant resources (+12)")
    elif defendant_resources == 'medium':
        strength_score += 8
        assessment_details.append("Medium defendant resources (+8)")
    else:
        strength_score += 3
        assessment_details.append("High defendant resources (+3)")
    max_score += 15
    
    # Case complexity (0-10 points) - inverse scoring
    complexity = factors.get('complexity', 'medium')
    if complexity == 'low':
        strength_score += 8
        assessment_details.append("Low complexity (+8)")
    elif complexity == 'medium':
        strength_score += 5
        assessment_details.append("Medium complexity (+5)")
    else:
        strength_score += 2
        assessment_details.append("High complexity (+2)")
    max_score += 10
    
    # Calculate percentage
    strength_percentage = (strength_score / max_score) * 100
    
    # Determine overall assessment
    if strength_percentage >= 80:
        overall_assessment = "Very Strong"
        recommendation = "Proceed with confidence"
    elif strength_percentage >= 65:
        overall_assessment = "Strong"
        recommendation = "Good prospects for success"
    elif strength_percentage >= 50:
        overall_assessment = "Moderate"
        recommendation = "Proceed with caution"
    elif strength_percentage >= 35:
        overall_assessment = "Weak"
        recommendation = "Consider alternatives"
    else:
        overall_assessment = "Very Weak"
        recommendation = "Reconsider pursuing this case"
    
    return {
        'strength_score': strength_score,
        'max_score': max_score,
        'strength_percentage': round(strength_percentage, 1),
        'overall_assessment': overall_assessment,
        'recommendation': recommendation,
        'assessment_details': assessment_details
    }

def create_court_calendar_event(title: str, date: datetime, 
                               duration_hours: int = 2, 
                               location: str = "") -> Dict[str, str]:
    """
    Create calendar event data for court dates
    """
    end_date = date + timedelta(hours=duration_hours)
    
    return {
        'title': title,
        'start_date': date.isoformat(),
        'end_date': end_date.isoformat(),
        'location': location,
        'description': f"Court appearance for {title}",
        'reminder_times': [
            (date - timedelta(days=7)).isoformat(),  # 1 week before
            (date - timedelta(days=1)).isoformat(),  # 1 day before
            (date - timedelta(hours=2)).isoformat()  # 2 hours before
        ]
    }

def validate_case_data(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate case data for completeness and accuracy
    """
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['name', 'type', 'plaintiff_name', 'defendant_name']
    for field in required_fields:
        if not case_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate names
    if case_data.get('plaintiff_name') and len(case_data['plaintiff_name']) < 2:
        errors.append("Plaintiff name too short")
    
    if case_data.get('defendant_name') and len(case_data['defendant_name']) < 2:
        errors.append("Defendant name too short")
    
    # Validate case type
    valid_case_types = [
        'Civil Rights Violation', 'Employment Discrimination', 'Personal Injury',
        'Contract Dispute', 'Property Dispute', 'Constitutional Rights', 'Other'
    ]
    if case_data.get('type') and case_data['type'] not in valid_case_types:
        warnings.append(f"Unusual case type: {case_data['type']}")
    
    # Validate dates
    if case_data.get('incident_date'):
        try:
            incident_date = datetime.fromisoformat(case_data['incident_date'])
            if incident_date > datetime.now():
                warnings.append("Incident date is in the future")
        except ValueError:
            errors.append("Invalid incident date format")
    
    # Validate contact information
    if case_data.get('plaintiff_email') and not validate_email(case_data['plaintiff_email']):
        errors.append("Invalid plaintiff email format")
    
    if case_data.get('plaintiff_phone') and not validate_phone(case_data['plaintiff_phone']):
        warnings.append("Plaintiff phone number format may be invalid")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'validation_date': datetime.now().isoformat()
    }

def generate_case_summary(case_data: Dict[str, Any]) -> str:
    """
    Generate a brief case summary
    """
    try:
        plaintiff = case_data.get('plaintiff_name', 'Plaintiff')
        defendant = case_data.get('defendant_name', 'Defendant')
        case_type = case_data.get('type', 'Legal Matter')
        
        summary = f"{case_type} case: {plaintiff} vs. {defendant}"
        
        if case_data.get('incident_date'):
            incident_date = datetime.fromisoformat(case_data['incident_date']).strftime('%B %d, %Y')
            summary += f" (incident: {incident_date})"
        
        if case_data.get('case_summary'):
            summary += f". {case_data['case_summary'][:200]}..."
        
        return summary
    
    except Exception:
        return "Case summary generation failed"

def extract_key_dates(text: str) -> List[Dict[str, str]]:
    """
    Extract potential key dates from text using regex
    """
    dates = []
    
    # Pattern for various date formats
    date_patterns = [
        r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',  # MM/DD/YYYY
        r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',  # YYYY-MM-DD
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b',  # Month DD, YYYY
        r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b'  # DD Month YYYY
    ]
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            dates.append({
                'date_text': match.group(0),
                'position': match.start(),
                'context': text[max(0, match.start()-50):match.end()+50]
            })
    
    return dates

def calculate_statute_of_limitations(incident_date: datetime, 
                                   violation_type: str, 
                                   state: str = 'Texas') -> Dict[str, Any]:
    """
    Calculate statute of limitations for different violation types
    """
    # Texas statute of limitations (simplified)
    texas_limitations = {
        'Civil Rights Violation': 2,  # years
        'Personal Injury': 2,
        'Contract Dispute': 4,
        'Property Damage': 2,
        'Employment Discrimination': 2,
        'Professional Malpractice': 2,
        'Fraud': 4,
        'Defamation': 1,
        'Other': 2
    }
    
    years_limit = texas_limitations.get(violation_type, texas_limitations['Other'])
    limitation_date = incident_date + timedelta(days=years_limit * 365)
    
    days_remaining = (limitation_date - datetime.now()).days
    
    status = "Active"
    if days_remaining < 0:
        status = "Expired"
    elif days_remaining < 90:
        status = "Critical"
    elif days_remaining < 180:
        status = "Warning"
    
    return {
        'incident_date': incident_date.isoformat(),
        'limitation_period_years': years_limit,
        'limitation_date': limitation_date.isoformat(),
        'days_remaining': days_remaining,
        'status': status,
        'urgency_level': 'High' if days_remaining < 90 else 'Medium' if days_remaining < 180 else 'Low'
    }
