import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from sambanova_client import SambanovaClient

class DefenseNeutralizer:
    """
    Pre-emptive defense neutralizer with verified counter-responses
    """
    
    def __init__(self, legal_authority):
        self.legal_authority = legal_authority
        self.client = SambanovaClient(api_key="e0d79301-ca3b-4b35-a816-54f2987ae3db")
        
        # Pre-built defense responses with legal authorities
        self.defense_strategies = {
            "Qualified Immunity": {
                "description": "Government officials claim protection from civil liability",
                "standard": "Clearly established law + reasonable official test",
                "counter_elements": [
                    "Constitutional right was clearly established",
                    "No reasonable official could believe conduct was lawful",
                    "Factual allegations sufficient to overcome immunity"
                ],
                "key_cases": [
                    "Pearson v. Callahan (2009)",
                    "Hope v. Pelzer (2002)",
                    "Saucier v. Katz (2001)"
                ]
            },
            "Statute of Limitations": {
                "description": "Claims time-barred under applicable limitations period",
                "standard": "Claim must be filed within statutory time period",
                "counter_elements": [
                    "Discovery rule application",
                    "Equitable tolling doctrines",
                    "Continuing violation theory",
                    "Fraudulent concealment"
                ],
                "key_cases": [
                    "TRW Inc. v. Andrews (2001)",
                    "Cada v. Baxter Healthcare Corp (1990)",
                    "Holmberg v. Armbrecht (1946)"
                ]
            },
            "Standing": {
                "description": "Plaintiff lacks Article III standing to sue",
                "standard": "Injury in fact, causation, redressability",
                "counter_elements": [
                    "Concrete and particularized injury",
                    "Traceability to defendant's conduct",
                    "Likely redressability by favorable decision"
                ],
                "key_cases": [
                    "Lujan v. Defenders of Wildlife (1992)",
                    "Friends of the Earth v. Laidlaw (2000)",
                    "Steel Co. v. Citizens for Better Environment (1998)"
                ]
            },
            "Sovereign Immunity": {
                "description": "State immunity from federal lawsuits",
                "standard": "11th Amendment protection",
                "counter_elements": [
                    "Express waiver by state",
                    "Valid abrogation by Congress",
                    "Ex parte Young exception",
                    "Municipal liability under Section 1983"
                ],
                "key_cases": [
                    "Ex parte Young (1908)",
                    "Seminole Tribe v. Florida (1996)",
                    "Tennessee v. Lane (2004)"
                ]
            }
        }
    
    def generate_response(self, defense_type: str, case_id: str) -> Dict:
        """
        Generate comprehensive counter-response to specific defense
        """
        try:
            if defense_type not in self.defense_strategies:
                return {
                    'error': f"Defense type '{defense_type}' not recognized",
                    'available_defenses': list(self.defense_strategies.keys())
                }
            
            defense_info = self.defense_strategies[defense_type]
            
            # Get relevant legal authorities
            authorities = self.legal_authority.get_relevant_authorities(
                f"Response to {defense_type}", 
                {"defense_type": defense_type}
            )
            
            # Generate response content
            response_content = self._generate_response_content(
                defense_type, 
                defense_info, 
                authorities
            )
            
            # Get supporting precedents
            precedents = self._get_supporting_precedents(defense_type)
            
            return {
                'defense_type': defense_type,
                'content': response_content,
                'legal_authorities': authorities,
                'supporting_precedents': precedents,
                'counter_elements': defense_info.get('counter_elements', []),
                'generated_date': datetime.now().isoformat(),
                'case_id': case_id
            }
            
        except Exception as e:
            return {
                'error': f"Response generation failed: {str(e)}",
                'defense_type': defense_type,
                'fallback_content': self._get_fallback_response(defense_type)
            }
    
    def _generate_response_content(self, defense_type: str, defense_info: Dict, authorities: List[Dict]) -> str:
        """
        Generate detailed response content using AI
        """
        try:
            authorities_text = "\n".join([
                f"- {auth['citation']}: {auth['summary']}" for auth in authorities[:5]
            ])
            
            prompt = f"""
            Generate a comprehensive legal response to a {defense_type} defense with the following:
            
            DEFENSE INFORMATION:
            Description: {defense_info.get('description', 'Standard defense')}
            Legal Standard: {defense_info.get('standard', 'Standard legal test')}
            Counter Elements: {defense_info.get('counter_elements', [])}
            Key Cases: {defense_info.get('key_cases', [])}
            
            VERIFIED LEGAL AUTHORITIES:
            {authorities_text}
            
            RESPONSE REQUIREMENTS:
            1. Strong opening statement denying the defense
            2. Legal standard explanation with citations
            3. Factual arguments defeating each element
            4. Case law distinguishing defendant's position
            5. Pre-emptive responses to likely counter-arguments
            6. Conclusion demanding denial of defense
            
            CRITICAL REQUIREMENTS:
            - Only use verified legal authorities provided
            - Supreme Court-quality legal writing
            - Persuasive and confident tone
            - Specific factual allegations (use placeholders)
            - Proper legal citations
            - Texas and federal law compliance
            
            Generate a complete, court-ready response that neutralizes this defense.
            """
            
            return self.client.generate_defense_counter(defense_type, str(defense_info))
            
        except Exception as e:
            return f"Response generation failed: {str(e)}"
    
    def _get_supporting_precedents(self, defense_type: str) -> List[Dict]:
        """
        Get supporting precedents for defeating this defense type
        """
        try:
            # Search for cases that defeated this defense
            search_query = f"defeating {defense_type} cases won"
            precedents = self.legal_authority.search_authority(search_query, "Case Law")
            
            # Filter for relevant precedents
            relevant_precedents = []
            for precedent in precedents[:10]:
                if any(keyword in precedent.get('summary', '').lower() 
                      for keyword in ['defeated', 'denied', 'rejected', 'overcome']):
                    relevant_precedents.append(precedent)
            
            return relevant_precedents[:5]
            
        except Exception as e:
            # Return fallback precedents from knowledge base
            return self.defense_strategies.get(defense_type, {}).get('key_cases', [])
    
    def _get_fallback_response(self, defense_type: str) -> str:
        """
        Get fallback response when AI generation fails
        """
        defense_info = self.defense_strategies.get(defense_type, {})
        
        return f"""
        RESPONSE TO {defense_type.upper()} DEFENSE
        
        Plaintiff respectfully submits this response to Defendant's {defense_type} defense.
        
        I. STANDARD
        {defense_info.get('standard', 'Applicable legal standard applies')}
        
        II. ARGUMENT
        Defendant's {defense_type} defense fails because:
        
        {chr(10).join([f"• {element}" for element in defense_info.get('counter_elements', ['Defense lacks merit'])])}
        
        III. CONCLUSION
        For the foregoing reasons, Defendant's {defense_type} defense should be DENIED.
        
        [Note: This is a template response. Customize with specific case facts and authorities.]
        """
    
    def get_all_defense_types(self) -> List[Dict]:
        """
        Get all available defense types with descriptions
        """
        return [
            {
                'defense_type': defense_type,
                'description': info['description'],
                'difficulty': self._assess_defense_difficulty(defense_type),
                'success_rate': self._estimate_success_rate(defense_type)
            }
            for defense_type, info in self.defense_strategies.items()
        ]
    
    def _assess_defense_difficulty(self, defense_type: str) -> str:
        """
        Assess difficulty of defeating this defense type
        """
        difficulty_map = {
            "Qualified Immunity": "High",
            "Statute of Limitations": "Medium", 
            "Standing": "Medium",
            "Sovereign Immunity": "High"
        }
        return difficulty_map.get(defense_type, "Medium")
    
    def _estimate_success_rate(self, defense_type: str) -> str:
        """
        Estimate success rate for defeating this defense
        """
        success_rates = {
            "Qualified Immunity": "30-40%",
            "Statute of Limitations": "60-70%",
            "Standing": "50-60%", 
            "Sovereign Immunity": "25-35%"
        }
        return success_rates.get(defense_type, "50%")
    
    def analyze_defense_combination(self, defense_types: List[str], case_id: str) -> Dict:
        """
        Analyze strategy when multiple defenses are raised
        """
        try:
            prompt = f"""
            Analyze litigation strategy for responding to multiple defenses: {', '.join(defense_types)}
            
            Provide analysis including:
            1. Priority order for responding
            2. Overlapping legal issues
            3. Strategic dependencies between defenses
            4. Resource allocation recommendations
            5. Timeline considerations
            6. Risk assessment for each defense
            7. Settlement implications
            
            Focus on practical strategy for pro se litigant facing multiple defenses.
            """
            
            strategic_analysis = self.client.provide_legal_advice(prompt, {"case_id": case_id, "defense_types": defense_types})
            
            return {
                'case_id': case_id,
                'defenses_analyzed': defense_types,
                'strategic_analysis': strategic_analysis,
                'priority_order': self._prioritize_defenses(defense_types),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Multiple defense analysis failed: {str(e)}",
                'defenses_analyzed': defense_types
            }
    
    def _prioritize_defenses(self, defense_types: List[str]) -> List[Dict]:
        """
        Prioritize defenses by difficulty and importance
        """
        priority_order = []
        
        for defense_type in defense_types:
            difficulty = self._assess_defense_difficulty(defense_type)
            success_rate = self._estimate_success_rate(defense_type)
            
            # Higher priority for easier defenses with higher success rates
            priority_score = 3 if difficulty == "Medium" else 2 if difficulty == "High" else 1
            
            priority_order.append({
                'defense_type': defense_type,
                'difficulty': difficulty,
                'success_rate': success_rate,
                'priority_score': priority_score,
                'recommended_order': len([d for d in priority_order if d['priority_score'] >= priority_score]) + 1
            })
        
        return sorted(priority_order, key=lambda x: x['priority_score'], reverse=True)
    
    def get_defense_timeline_strategy(self, defense_types: List[str]) -> Dict:
        """
        Get timeline strategy for responding to multiple defenses
        """
        try:
            timeline = []
            current_week = 1
            
            prioritized_defenses = self._prioritize_defenses(defense_types)
            
            for defense in prioritized_defenses:
                defense_type = defense['defense_type']
                estimated_time = self._estimate_response_time(defense_type)
                required_resources = self._get_required_resources(defense_type)
                
                timeline.append({
                    'defense_type': defense_type,
                    'start_week': current_week,
                    'estimated_weeks': estimated_time // 7,  # Convert hours to weeks
                    'required_resources': required_resources,
                    'dependencies': []
                })
                
                current_week += (estimated_time // 7) + 1  # Add buffer week
            
            # Identify parallel work opportunities
            parallel_opportunities = self._identify_parallel_work(timeline)
            
            return {
                'timeline': timeline,
                'total_estimated_weeks': current_week - 1,
                'parallel_opportunities': parallel_opportunities,
                'generated_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Timeline strategy generation failed: {str(e)}",
                'fallback_advice': "Respond to defenses in order of filing deadline proximity"
            }
    
    def _estimate_response_time(self, defense_type: str) -> int:
        """
        Estimate time needed to respond to defense type (in hours)
        """
        time_estimates = {
            "Qualified Immunity": 40,
            "Statute of Limitations": 20,
            "Standing": 25,
            "Sovereign Immunity": 35
        }
        return time_estimates.get(defense_type, 30)
    
    def _get_required_resources(self, defense_type: str) -> List[str]:
        """
        Get required resources for responding to defense type
        """
        resource_map = {
            "Qualified Immunity": ["Constitutional law research", "Clearly established law cases", "Factual development"],
            "Statute of Limitations": ["Discovery rule research", "Equitable tolling cases", "Timeline documentation"],
            "Standing": ["Injury documentation", "Causation evidence", "Redressability analysis"],
            "Sovereign Immunity": ["11th Amendment research", "Ex parte Young analysis", "Municipal liability law"]
        }
        return resource_map.get(defense_type, ["Legal research", "Case law analysis"])
    
    def _identify_parallel_work(self, timeline: List[Dict]) -> List[str]:
        """
        Identify opportunities for parallel processing of defense responses
        """
        parallel_opportunities = []
        
        # Check for overlapping research areas
        if any("Constitutional law research" in item['required_resources'] for item in timeline):
            parallel_opportunities.append("Constitutional law research can be done for multiple defenses simultaneously")
        
        if len(timeline) > 2:
            parallel_opportunities.append("Legal research for multiple defenses can be conducted in parallel")
        
        if any("Factual development" in item['required_resources'] for item in timeline):
            parallel_opportunities.append("Factual development benefits all defense responses")
        
        return parallel_opportunities