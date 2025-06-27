import json
from datetime import datetime, date
from typing import Dict, List, Optional
import os
from sambanova_client import SambanovaClient

class ViolationTracker:
    """
    Track legal violations with Texas statute codes and supporting evidence
    """
    
    def __init__(self, database):
        self.db = database
        self.client = SambanovaClient(api_key="e0d79301-ca3b-4b35-a816-54f2987ae3db")
        self.ensure_tables()
        
        # Texas statute violation categories
        self.violation_categories = {
            "Civil Rights": {
                "federal_statutes": ["42 U.S.C. § 1983", "42 U.S.C. § 1981", "42 U.S.C. § 1985"],
                "texas_statutes": ["Texas Civil Practice and Remedies Code Chapter 106"],
                "common_violations": ["Due Process", "Equal Protection", "First Amendment", "Fourth Amendment"]
            },
            "Employment": {
                "federal_statutes": ["Title VII", "ADA", "ADEA", "FLSA"],
                "texas_statutes": ["Texas Labor Code", "Texas Commission on Human Rights Act"],
                "common_violations": ["Discrimination", "Harassment", "Wage Theft", "Wrongful Termination"]
            },
            "Consumer Protection": {
                "federal_statutes": ["FDCPA", "FCRA", "TCPA"],
                "texas_statutes": ["Texas Deceptive Trade Practices Act", "Texas Finance Code"],
                "common_violations": ["Deceptive Practices", "Debt Collection", "Credit Reporting", "Telemarketing"]
            },
            "Property Rights": {
                "federal_statutes": ["Fair Housing Act", "ADA"],
                "texas_statutes": ["Texas Property Code", "Texas Fair Housing Act"],
                "common_violations": ["Housing Discrimination", "Landlord-Tenant", "Property Damage", "Trespass"]
            },
            "Government Accountability": {
                "federal_statutes": ["42 U.S.C. § 1983", "First Amendment"],
                "texas_statutes": ["Texas Government Code", "Texas Public Information Act"],
                "common_violations": ["Public Records", "Open Meetings", "Government Transparency", "Official Misconduct"]
            }
        }
    
    def ensure_tables(self):
        """Create violation tracking tables"""
        cursor = self.db.get_cursor()
        
        # Violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                id TEXT PRIMARY KEY,
                case_id TEXT,
                violation_type TEXT,
                statute_code TEXT,
                description TEXT,
                violation_date DATE,
                evidence_summary TEXT,
                damages_claimed REAL,
                status TEXT,
                created_date TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        # Evidence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violation_evidence (
                id TEXT PRIMARY KEY,
                violation_id TEXT,
                evidence_type TEXT,
                description TEXT,
                file_path TEXT,
                credibility_score INTEGER,
                created_date TIMESTAMP,
                FOREIGN KEY (violation_id) REFERENCES violations (id)
            )
        ''')
        
        # Timeline table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violation_timeline (
                id TEXT PRIMARY KEY,
                violation_id TEXT,
                event_date DATE,
                event_description TEXT,
                supporting_evidence TEXT,
                created_date TIMESTAMP,
                FOREIGN KEY (violation_id) REFERENCES violations (id)
            )
        ''')
        
        self.db.commit()
    
    def add_violation(self, case_id: str, violation_data: Dict) -> str:
        """Add a new violation to the case"""
        try:
            violation_id = f"viol_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Analyze violation for legal merit
            analysis = self._analyze_violation_merit(violation_data)
            
            # Get suggested statute codes
            statute_codes = self._get_applicable_statutes(
                violation_data.get('violation_type', ''),
                violation_data.get('description', '')
            )
            
            cursor = self.db.get_cursor()
            cursor.execute('''
                INSERT INTO violations 
                (id, case_id, violation_type, legal_codes, description, date_occurred, 
                 person_involved, damages_estimate, created_date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                violation_id,
                case_id,
                violation_data.get('violation_type', ''),
                ', '.join(statute_codes),
                violation_data.get('description', ''),
                violation_data.get('violation_date', date.today().isoformat()),
                violation_data.get('person_involved', 'Unknown'),
                violation_data.get('damages_claimed', 0.0),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            self.db.commit()
            
            return violation_id
            
        except Exception as e:
            return f"Error adding violation: {str(e)}"
    
    def _analyze_violation_merit(self, violation_data: Dict) -> Dict:
        """Analyze violation for legal merit and strength"""
        try:
            prompt = f"""
            Analyze this legal violation for merit and strength:
            
            Violation Type: {violation_data.get('violation_type', 'Unknown')}
            Description: {violation_data.get('description', 'No description')}
            Date: {violation_data.get('violation_date', 'Unknown')}
            Evidence: {violation_data.get('evidence_summary', 'No evidence summary')}
            
            Provide analysis including:
            1. Legal merit assessment (Strong/Medium/Weak)
            2. Required elements for this type of violation
            3. Evidence gaps that need to be filled
            4. Potential damages calculation
            5. Statute of limitations considerations
            6. Likelihood of success rating
            """
            
            analysis_result = self.client.analyze_legal_text(prompt, "violation_analysis")
            
            return {
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f"Violation analysis failed: {str(e)}"}
    
    def _get_applicable_statutes(self, violation_type: str, description: str) -> List[str]:
        """Get applicable statutes for violation type"""
        try:
            # Look up predefined statutes for violation category
            for category, info in self.violation_categories.items():
                if violation_type.lower() in category.lower() or any(
                    violation.lower() in violation_type.lower() 
                    for violation in info['common_violations']
                ):
                    return info['federal_statutes'] + info['texas_statutes']
            
            # If no predefined match, use AI analysis
            prompt = f"""
            Identify applicable federal and Texas statutes for this violation:
            
            Type: {violation_type}
            Description: {description}
            
            Provide specific statute citations that would apply to this violation.
            Focus on commonly used statutes for this type of legal claim.
            """
            
            analysis = self.client.analyze_legal_text(prompt, "statute_identification")
            
            # Extract statute codes from analysis
            statutes = []
            lines = analysis.split('\n')
            for line in lines:
                if 'U.S.C.' in line or 'Texas' in line and 'Code' in line:
                    statutes.append(line.strip())
            
            return statutes[:5] if statutes else ["Research Required"]
            
        except Exception as e:
            return [f"Statute research failed: {str(e)}"]
    
    def get_case_violations(self, case_id: str) -> List[Dict]:
        """Get all violations for a case"""
        cursor = self.db.get_cursor()
        
        cursor.execute('''
            SELECT * FROM violations 
            WHERE case_id = ? 
            ORDER BY date_occurred DESC
        ''', (case_id,))
        
        violations = []
        for row in cursor.fetchall():
            violation = dict(row)
            
            # Get associated evidence
            cursor.execute('''
                SELECT * FROM violation_evidence 
                WHERE violation_id = ?
            ''', (violation['id'],))
            violation['evidence'] = [dict(ev_row) for ev_row in cursor.fetchall()]
            
            # Get timeline events
            cursor.execute('''
                SELECT * FROM violation_timeline 
                WHERE violation_id = ? 
                ORDER BY event_date
            ''', (violation['id'],))
            violation['timeline'] = [dict(tl_row) for tl_row in cursor.fetchall()]
            
            violations.append(violation)
        
        return violations
    
    def calculate_damages(self, violation_id: str, damages_data: Dict) -> Dict:
        """Calculate damages for a violation"""
        try:
            prompt = f"""
            Calculate damages for this legal violation:
            
            Damages Data: {json.dumps(damages_data, indent=2)}
            
            Calculate and provide:
            1. Economic damages (actual losses)
            2. Non-economic damages (pain and suffering)
            3. Punitive damages (if applicable)
            4. Attorney fees (if recoverable)
            5. Court costs and expenses
            6. Total damages range (low/high estimates)
            
            Provide realistic estimates based on similar cases and applicable law.
            Include methodology for calculations.
            """
            
            damages_analysis = self.client.analyze_legal_text(prompt, "damages_calculation")
            
            # Store damages calculation
            cursor = self.db.get_cursor()
            cursor.execute('''
                UPDATE violations 
                SET damages_estimate = ? 
                WHERE id = ?
            ''', (damages_data.get('total_claimed', 0.0), violation_id or ''))
            
            self.db.commit()
            
            return {
                'violation_id': violation_id,
                'damages_analysis': damages_analysis,
                'calculation_date': datetime.now().isoformat(),
                'damages_data': damages_data
            }
            
        except Exception as e:
            return {'error': f"Damages calculation failed: {str(e)}"}
    
    def add_evidence(self, violation_id: str, evidence_data: Dict) -> str:
        """Add evidence to a violation"""
        try:
            evidence_id = f"evid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor = self.db.get_cursor()
            cursor.execute('''
                INSERT INTO violation_evidence 
                (id, violation_id, evidence_type, description, file_path, credibility_score, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                evidence_id,
                violation_id,
                evidence_data.get('evidence_type', ''),
                evidence_data.get('description', ''),
                evidence_data.get('file_path', ''),
                evidence_data.get('credibility_score', 5),
                datetime.now().isoformat()
            ))
            
            self.db.commit()
            return evidence_id
            
        except Exception as e:
            return f"Error adding evidence: {str(e)}"
    
    def create_violation_timeline(self, violation_id: str, events: List[Dict]) -> Dict:
        """Create chronological timeline for a violation"""
        try:
            cursor = self.db.get_cursor()
            
            for event in events:
                timeline_id = f"tl_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len([e for e in events if e])}"
                
                cursor.execute('''
                    INSERT INTO violation_timeline 
                    (id, violation_id, event_date, event_description, supporting_evidence, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    timeline_id,
                    violation_id,
                    event.get('event_date', date.today().isoformat()),
                    event.get('description', ''),
                    event.get('evidence', ''),
                    datetime.now().isoformat()
                ))
            
            self.db.commit()
            
            # Get complete timeline
            cursor.execute('''
                SELECT * FROM violation_timeline 
                WHERE violation_id = ? 
                ORDER BY event_date
            ''', (violation_id,))
            
            timeline = [dict(row) for row in cursor.fetchall()]
            
            return {
                'violation_id': violation_id,
                'timeline': timeline,
                'total_events': len(timeline),
                'created_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f"Timeline creation failed: {str(e)}"}
    
    def get_violation_summary(self, case_id: str) -> Dict:
        """Get summary of all violations for a case"""
        try:
            violations = self.get_case_violations(case_id)
            
            total_damages = sum(float(v.get('damages_estimate', 0)) for v in violations)
            violation_types = list(set(v.get('violation_type', '') for v in violations))
            
            # Count evidence by type
            evidence_counts = {}
            for violation in violations:
                for evidence in violation.get('evidence', []):
                    evidence_type = evidence.get('evidence_type', 'Unknown')
                    evidence_counts[evidence_type] = evidence_counts.get(evidence_type, 0) + 1
            
            return {
                'case_id': case_id,
                'total_violations': len(violations),
                'violation_types': violation_types,
                'total_damages_claimed': total_damages,
                'evidence_summary': evidence_counts,
                'active_violations': len(violations),
                'summary_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f"Summary generation failed: {str(e)}"}
    
    def search_violations(self, search_query: str, case_id: Optional[str] = None) -> List[Dict]:
        """Search violations by description or type"""
        cursor = self.db.get_cursor()
        
        if case_id:
            cursor.execute('''
                SELECT * FROM violations 
                WHERE case_id = ? AND (
                    description LIKE ? OR 
                    violation_type LIKE ? OR 
                    statute_code LIKE ?
                )
                ORDER BY violation_date DESC
            ''', (case_id, f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute('''
                SELECT * FROM violations 
                WHERE description LIKE ? OR 
                      violation_type LIKE ? OR 
                      statute_code LIKE ?
                ORDER BY violation_date DESC
            ''', (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statute_guidance(self, statute_code: str) -> Dict:
        """Get guidance on a specific statute"""
        try:
            prompt = f"""
            Provide comprehensive guidance on {statute_code}:
            
            Include:
            1. Purpose and scope of the statute
            2. Key elements that must be proven
            3. Common defenses defendants raise
            4. Damages available under this statute
            5. Statute of limitations
            6. Recent important case law
            7. Practical tips for pro se litigants
            
            Focus on actionable guidance for someone using this statute in litigation.
            """
            
            guidance = self.client.analyze_legal_text(prompt, "statute_guidance")
            
            return {
                'statute_code': statute_code,
                'guidance': guidance,
                'generated_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Statute guidance generation failed: {str(e)}",
                'statute_code': statute_code
            }