import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from sambanova_client import SambanovaClient
import re

class LegalAuthority:
    """
    Legal authority verification system with real-time verification
    """
    
    def __init__(self, database):
        self.db = database
        self.client = SambanovaClient(api_key="e0d79301-ca3b-4b35-a816-54f2987ae3db")
        self.ensure_tables()
        
        # Legal databases for verification
        self.verification_sources = {
            "justia": "https://law.justia.com/",
            "google_scholar": "https://scholar.google.com/",
            "courtlistener": "https://www.courtlistener.com/",
            "texas_gov": "https://statutes.capitol.texas.gov/"
        }
    
    def ensure_tables(self):
        """Create legal authority tables"""
        cursor = self.db.get_cursor()
        
        # Legal authorities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legal_authorities (
                id TEXT PRIMARY KEY,
                citation TEXT UNIQUE,
                title TEXT,
                summary TEXT,
                full_text TEXT,
                source_url TEXT,
                verification_status TEXT,
                authority_type TEXT,
                jurisdiction TEXT,
                relevance_score REAL,
                last_verified TIMESTAMP,
                created_date TIMESTAMP
            )
        ''')
        
        # Authority usage tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authority_usage (
                id TEXT PRIMARY KEY,
                authority_id TEXT,
                case_id TEXT,
                document_type TEXT,
                usage_context TEXT,
                used_date TIMESTAMP,
                FOREIGN KEY (authority_id) REFERENCES legal_authorities (id)
            )
        ''')
        
        self.db.commit()
    
    def search_authority(self, query: str, search_type: str) -> List[Dict]:
        """
        Search for legal authorities with verification
        """
        try:
            # First search local database
            local_results = self._search_local_database(query, search_type)
            
            # If insufficient local results, search online
            if len(local_results) < 5:
                online_results = self._search_online_authorities(query, search_type)
                
                # Combine and deduplicate results
                all_results = local_results + online_results
                seen_citations = set()
                unique_results = []
                
                for result in all_results:
                    citation = result.get('citation', '').strip()
                    if citation and citation not in seen_citations:
                        seen_citations.add(citation)
                        unique_results.append(result)
                
                return unique_results[:10]
            
            return local_results
            
        except Exception as e:
            return [{'error': f"Authority search failed: {str(e)}"}]
    
    def verify_citation(self, citation: str) -> Dict:
        """
        Verify if a citation is accurate and current
        """
        try:
            # Check local database first
            cursor = self.db.get_cursor()
            cursor.execute('''
                SELECT * FROM legal_authorities 
                WHERE citation = ? AND verification_status = 'verified'
            ''', (citation,))
            
            local_result = cursor.fetchone()
            if local_result:
                return {
                    'citation': citation,
                    'verified': True,
                    'source': 'local_database',
                    'last_verified': dict(local_result)['last_verified'],
                    'authority_data': dict(local_result)
                }
            
            # Verify online
            verification_result = self._verify_citation_online(citation)
            
            # Store verified citation
            if verification_result.get('verified'):
                self._add_authority_to_database(verification_result)
            
            return verification_result
            
        except Exception as e:
            return {
                'citation': citation,
                'verified': False,
                'error': f"Verification failed: {str(e)}"
            }
    
    def get_relevant_authorities(self, doc_type: str, case_params: Dict) -> List[Dict]:
        """
        Get relevant legal authorities for document generation
        """
        try:
            # Build search queries based on document type and case parameters
            search_queries = self._build_search_query(doc_type, case_params)
            
            all_authorities = []
            for query in search_queries:
                authorities = self.search_authority(query, "Case Law")
                all_authorities.extend(authorities)
            
            # Remove duplicates and rank by relevance
            unique_authorities = []
            seen_citations = set()
            
            for authority in all_authorities:
                citation = authority.get('citation', '')
                if citation and citation not in seen_citations:
                    seen_citations.add(citation)
                    # Calculate relevance score
                    relevance = self._calculate_relevance(' '.join(search_queries), authority.get('summary', ''))
                    authority['relevance_score'] = relevance
                    unique_authorities.append(authority)
            
            # Sort by relevance and return top results
            unique_authorities.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            return unique_authorities[:8]
            
        except Exception as e:
            return [{'error': f"Authority retrieval failed: {str(e)}"}]
    
    def _search_local_database(self, query: str, search_type: str) -> List[Dict]:
        """
        Search local legal authority database
        """
        cursor = self.db.get_cursor()
        
        # Search by citation, title, or summary
        cursor.execute('''
            SELECT * FROM legal_authorities 
            WHERE (citation LIKE ? OR title LIKE ? OR summary LIKE ?) 
            AND authority_type = ?
            AND verification_status = 'verified'
            ORDER BY relevance_score DESC, last_verified DESC
            LIMIT 10
        ''', (f"%{query}%", f"%{query}%", f"%{query}%", search_type))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _search_online_authorities(self, query: str, search_type: str) -> List[Dict]:
        """
        Search online legal databases (simulated for demo)
        """
        try:
            prompt = f"""
            Find legal authorities for: {query}
            Search Type: {search_type}
            
            Provide real, verifiable legal authorities including:
            1. Accurate case citations
            2. Brief case summaries
            3. Relevance to the search query
            4. Court and jurisdiction information
            
            CRITICAL: Only provide real, verifiable legal authorities. Do not create fictional cases.
            """
            
            result = self.client.analyze_legal_text(prompt, "legal_research")
            
            # Parse authorities from response
            authorities = []
            lines = result.split('\n')
            current_authority = {}
            
            for line in lines:
                line = line.strip()
                if 'v.' in line or 'Citation:' in line:
                    if current_authority:
                        authorities.append(current_authority)
                    current_authority = {'citation': line.replace('Citation:', '').strip(), 'summary': '', 'relevance': 'medium'}
                elif 'Summary:' in line or 'Description:' in line:
                    current_authority['summary'] = line.replace('Summary:', '').replace('Description:', '').strip()
                elif 'Relevance:' in line:
                    current_authority['relevance'] = line.replace('Relevance:', '').strip()
            
            if current_authority:
                authorities.append(current_authority)
                
            return authorities[:10] if authorities else []
            
        except Exception as e:
            return []
    
    def _verify_citation_online(self, citation: str) -> Dict:
        """
        Verify citation against online sources
        """
        try:
            # Simulate verification process
            # In production, this would check against Westlaw, Lexis, Google Scholar, etc.
            
            prompt = f"""
            Verify this legal citation: {citation}
            
            Determine if this is a real, accurate citation and provide:
            1. Verification status (verified/not found/incorrect format)
            2. Correct citation format if different
            3. Case summary if verified
            4. Court and date information
            5. Current legal status (good law/overruled/questioned)
            """
            
            verification_text = self.client.analyze_legal_text(prompt, "citation_verification")
            
            # Parse verification result
            verified = 'verified' in verification_text.lower() and 'not found' not in verification_text.lower()
            
            return {
                'citation': citation,
                'verified': verified,
                'verification_details': verification_text,
                'verification_date': datetime.now().isoformat(),
                'source': 'online_verification'
            }
            
        except Exception as e:
            return {
                'citation': citation,
                'verified': False,
                'error': f"Online verification failed: {str(e)}"
            }
    
    def _build_search_query(self, doc_type: str, case_params: Dict) -> List[str]:
        """
        Build search queries based on document type and case parameters
        """
        base_queries = {
            "Complaint": ["civil rights violations", "section 1983", "constitutional claims"],
            "Motion to Dismiss": ["motion to dismiss standards", "12(b)(6) motion", "failure to state claim"],
            "Motion for Summary Judgment": ["summary judgment standards", "genuine issue material fact", "Fed Rule 56"],
            "Response": ["response brief", "opposition motion", "counter-arguments"],
            "Discovery": ["discovery rules", "interrogatories", "document requests"]
        }
        
        queries = base_queries.get(doc_type, ["legal precedent", "case law"])
        
        # Add case-specific terms
        case_type = case_params.get('case_type', '')
        if case_type:
            queries.append(case_type)
        
        jurisdiction = case_params.get('jurisdiction', 'Texas')
        if jurisdiction:
            queries.append(f"{jurisdiction} law")
        
        return queries
    
    def _calculate_relevance(self, query: str, text: str) -> float:
        """
        Calculate relevance score between query and text
        """
        if not query or not text:
            return 0.0
        
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0.0
        
        # Calculate word overlap
        common_words = query_words.intersection(text_words)
        relevance = len(common_words) / len(query_words)
        
        return min(relevance, 1.0)
    
    def _add_authority_to_database(self, authority: Dict):
        """
        Add verified authority to local database
        """
        try:
            authority_id = f"auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor = self.db.get_cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO legal_authorities 
                (id, citation, title, summary, source_url, verification_status, 
                 authority_type, jurisdiction, relevance_score, last_verified, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                authority_id,
                authority.get('citation', ''),
                authority.get('title', ''),
                authority.get('summary', ''),
                authority.get('source_url', ''),
                'verified' if authority.get('verified') else 'unverified',
                authority.get('authority_type', 'Case Law'),
                authority.get('jurisdiction', 'Unknown'),
                authority.get('relevance_score', 0.5),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            self.db.commit()
            
        except Exception as e:
            pass  # Silently handle database errors
    
    def get_sanctions_prevention_check(self, content: str) -> Dict:
        """
        Check content for potential sanctions issues
        """
        try:
            prompt = f"""
            Review this legal content for potential sanctions issues under Rule 11 and similar rules:
            
            Content: {content[:2000]}  # First 2000 characters
            
            Check for:
            1. Frivolous legal arguments
            2. Factual assertions without evidentiary support
            3. Improper legal citations
            4. Harassment or bad faith elements
            5. Compliance with legal and ethical standards
            
            Provide specific warnings about potential sanctions risks and recommendations for improvement.
            Rate overall sanctions risk: LOW/MEDIUM/HIGH
            """
            
            sanctions_analysis = self.client.analyze_legal_text(prompt, "sanctions_review")
            
            # Extract risk level
            risk_level = "MEDIUM"  # Default
            if "low" in sanctions_analysis.lower():
                risk_level = "LOW"
            elif "high" in sanctions_analysis.lower():
                risk_level = "HIGH"
            
            return {
                'sanctions_risk': risk_level,
                'analysis': sanctions_analysis,
                'review_date': datetime.now().isoformat(),
                'recommendations': self._extract_recommendations(sanctions_analysis)
            }
            
        except Exception as e:
            return {
                'sanctions_risk': 'UNKNOWN',
                'error': f"Sanctions check failed: {str(e)}",
                'recommendation': 'Manual review recommended'
            }
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """
        Extract recommendations from sanctions analysis
        """
        recommendations = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')) or 'recommend' in line.lower():
                recommendations.append(line)
        
        return recommendations[:10]  # Limit to 10 recommendations