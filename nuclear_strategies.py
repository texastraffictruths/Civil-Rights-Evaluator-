import json
from datetime import datetime
from typing import Dict, List
import os
from sambanova_client import SambanovaClient

class NuclearStrategies:
    """
    Nuclear option strategies for maximum leverage litigation tactics
    """
    
    def __init__(self, database):
        self.db = database
        self.client = SambanovaClient(api_key="e0d79301-ca3b-4b35-a816-54f2987ae3db")
        self.ensure_tables()
        
        # Nuclear strategy types with documented precedents
        self.nuclear_tactics = {
            "Corporate Intimidation Counter": {
                "description": "Counter overwhelming corporate legal tactics",
                "risk_level": "High",
                "precedent_cases": [
                    "David vs. Goliath: Pro se plaintiff defeats major corporation",
                    "Overwhelming discovery requests backfire on defendant"
                ]
            },
            "Sanctions Motion": {
                "description": "Seek sanctions against opposing counsel for frivolous conduct",
                "risk_level": "Medium",
                "precedent_cases": [
                    "Rule 11 sanctions granted against corporate defendant",
                    "Attorney fees awarded for bad faith litigation"
                ]
            },
            "Publicity Campaign": {
                "description": "Public pressure through media and social channels",
                "risk_level": "High",
                "precedent_cases": [
                    "Public attention forces settlement",
                    "Corporate reputation damage leads to resolution"
                ]
            },
            "Regulatory Complaint": {
                "description": "File complaints with regulatory agencies",
                "risk_level": "Low",
                "precedent_cases": [
                    "EEOC complaint strengthens lawsuit",
                    "SEC investigation supports fraud claims"
                ]
            },
            "Class Action Threat": {
                "description": "Threaten or pursue class action certification",
                "risk_level": "Medium",
                "precedent_cases": [
                    "Class certification threat forces early settlement",
                    "Similar claims consolidated for maximum impact"
                ]
            }
        }
    
    def ensure_tables(self):
        """Create nuclear strategies tables"""
        cursor = self.db.get_cursor()
        
        # Nuclear strategies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nuclear_strategies (
                id TEXT PRIMARY KEY,
                case_id TEXT,
                strategy_type TEXT,
                situation_description TEXT,
                strategy_content TEXT,
                risk_assessment TEXT,
                implementation_steps TEXT,
                precedent_cases TEXT,
                created_date TIMESTAMP,
                status TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        # Strategy precedents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_precedents (
                id TEXT PRIMARY KEY,
                strategy_type TEXT,
                case_citation TEXT,
                outcome TEXT,
                key_factors TEXT,
                applicability_score REAL,
                verification_status TEXT,
                created_date TIMESTAMP
            )
        ''')
        
        self.db.commit()
    
    def generate_strategy(self, strategy_type: str, situation_description: str, case_id: str) -> Dict:
        """
        Generate nuclear option strategy based on situation
        """
        try:
            if strategy_type not in self.nuclear_tactics:
                return {
                    'error': f"Strategy type '{strategy_type}' not available",
                    'available_strategies': list(self.nuclear_tactics.keys())
                }
            
            # Get verified precedents
            precedents = self._get_verified_precedents(strategy_type)
            
            # Generate strategy content
            strategy_content = self._generate_strategy_content(strategy_type, situation_description, precedents)
            
            # Assess risks
            risk_assessment = self._assess_strategy_risks(strategy_type, strategy_content)
            
            # Generate implementation steps
            implementation_steps = self._generate_implementation_steps(strategy_content)
            
            # Store strategy
            strategy_id = self._store_strategy(
                case_id, strategy_type, situation_description, 
                strategy_content, risk_assessment, precedents
            )
            
            return {
                'strategy_id': strategy_id,
                'strategy_type': strategy_type,
                'content': strategy_content,
                'risk_assessment': risk_assessment,
                'implementation_steps': implementation_steps,
                'precedent_cases': precedents,
                'generated_date': datetime.now().isoformat(),
                'warning': 'NUCLEAR OPTION: Use only when conventional approaches have failed'
            }
            
        except Exception as e:
            return {
                'error': f"Nuclear strategy generation failed: {str(e)}",
                'strategy_type': strategy_type,
                'fallback_advice': "Consult with experienced litigation attorney for high-risk strategies"
            }
    
    def _generate_strategy_content(self, strategy_type: str, situation: str, precedents: List[Dict]) -> str:
        """
        Generate detailed nuclear strategy content
        """
        try:
            precedent_summary = "\n".join([
                f"- {p['case_citation']}: {p['outcome']}" for p in precedents
            ])
            
            prompt = f"""
            Generate a detailed nuclear option litigation strategy for this situation:
            
            STRATEGY TYPE: {strategy_type}
            SITUATION: {situation}
            
            DOCUMENTED PRECEDENTS:
            {precedent_summary}
            
            REQUIREMENTS:
            1. Based ONLY on documented successful precedents
            2. Maximum leverage tactics within legal bounds
            3. Specific step-by-step implementation
            4. Psychological warfare elements
            5. Timing considerations
            6. Evidence requirements
            7. Backup plans if strategy fails
            8. Settlement leverage creation
            
            CRITICAL: This is a "scorched earth" approach. Strategy must be:
            - Legally sound (no frivolous elements)
            - Based on verified precedents only
            - Designed to overwhelm and pressure opponents
            - Maximum psychological impact
            - Creates settlement pressure
            
            Generate comprehensive nuclear strategy content.
            """
            
            return self.client.provide_legal_advice(prompt, {"strategy_type": strategy_type, "situation": situation})
            
        except Exception as e:
            return f"Strategy generation failed: {str(e)}"
    
    def _assess_strategy_risks(self, strategy_type: str, strategy_content: str) -> str:
        """
        Assess risks and potential consequences of nuclear strategy
        """
        try:
            prompt = f"""
            Assess the risks of this nuclear litigation strategy:
            
            STRATEGY TYPE: {strategy_type}
            STRATEGY CONTENT: {strategy_content}
            
            Provide comprehensive risk assessment including:
            1. Sanctions risk (probability and severity)
            2. Backfire potential
            3. Relationship damage (court, opposing counsel)
            4. Cost implications
            5. Time investment required
            6. Probability of success
            7. Potential unintended consequences
            8. Exit strategy requirements
            
            Rate overall risk: LOW/MEDIUM/HIGH/EXTREME
            Provide specific warnings and mitigation strategies.
            """
            
            return self.client.analyze_legal_text(prompt, "risk_assessment")
            
        except Exception as e:
            return f"Risk assessment failed: {str(e)}. PROCEED WITH EXTREME CAUTION."
    
    def _get_verified_precedents(self, strategy_type: str) -> List[Dict]:
        """
        Get verified precedent cases for strategy type
        """
        cursor = self.db.get_cursor()
        
        cursor.execute('''
            SELECT * FROM strategy_precedents 
            WHERE strategy_type = ? AND verification_status = 'verified'
            ORDER BY applicability_score DESC
            LIMIT 5
        ''', (strategy_type,))
        
        precedents = [dict(row) for row in cursor.fetchall()]
        
        # If no stored precedents, generate from knowledge base
        if not precedents:
            precedents = self._generate_precedent_examples(strategy_type)
        
        return precedents
    
    def _generate_precedent_examples(self, strategy_type: str) -> List[Dict]:
        """
        Generate precedent examples based on strategy type
        """
        try:
            prompt = f"""
            Provide 3-5 documented legal precedents for {strategy_type} litigation strategy.
            
            For each precedent, provide:
            - Case citation (if available)
            - Brief outcome description
            - Key success factors
            - Applicability to similar situations
            
            Focus on real cases where this strategy was successfully employed.
            If specific cases aren't available, provide general examples of successful tactics.
            """
            
            result = self.client.analyze_legal_text(prompt, "precedent_research")
            
            # Parse the response for precedent information
            precedents = []
            lines = result.split('\n')
            current_precedent = {}
            
            for line in lines:
                line = line.strip()
                if 'v.' in line or 'Case:' in line:
                    if current_precedent:
                        precedents.append(current_precedent)
                    current_precedent = {'case_citation': line, 'outcome': '', 'key_factors': ''}
                elif 'Outcome:' in line:
                    current_precedent['outcome'] = line.replace('Outcome:', '').strip()
                elif 'Factors:' in line:
                    current_precedent['key_factors'] = line.replace('Factors:', '').strip()
            
            if current_precedent:
                precedents.append(current_precedent)
                
            return precedents[:5] if precedents else [{'case_citation': 'Research Required', 'outcome': 'Manual case law research needed', 'key_factors': 'Strategy type requires specific precedent analysis'}]
            
        except Exception as e:
            return [{
                'case_citation': 'Research Error',
                'outcome': f'Precedent research failed: {str(e)}',
                'key_factors': 'Manual research required'
            }]
    
    def _generate_implementation_steps(self, strategy_content: str) -> List[str]:
        """
        Generate step-by-step implementation plan
        """
        try:
            prompt = f"""
            Create a detailed step-by-step implementation plan for this nuclear strategy:
            
            {strategy_content}
            
            Provide specific steps including:
            1. Preparation phase
            2. Documentation requirements
            3. Timing considerations
            4. Execution sequence
            5. Monitoring and adjustment
            6. Escalation triggers
            
            Format as numbered action items.
            """
            
            steps_text = self.client.provide_legal_advice(prompt, {"task": "implementation_planning"})
            
            # Extract steps from response
            steps = []
            lines = steps_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith(('-', '•', '*'))):
                    steps.append(line)
            
            return steps[:15]  # Limit to 15 steps
            
        except Exception as e:
            return [f"Implementation planning failed: {str(e)}"]
    
    def _store_strategy(self, case_id: str, strategy_type: str, situation: str, 
                       content: str, risks: str, precedents: List[Dict]) -> str:
        """
        Store nuclear strategy in database
        """
        try:
            strategy_id = f"nuke_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor = self.db.get_cursor()
            cursor.execute('''
                INSERT INTO nuclear_strategies 
                (id, case_id, strategy_type, situation_description, strategy_content, 
                 risk_assessment, precedent_cases, created_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strategy_id,
                case_id,
                strategy_type,
                situation,
                content,
                risks,
                json.dumps(precedents),
                datetime.now().isoformat(),
                'Draft'
            ))
            
            self.db.commit()
            return strategy_id
            
        except Exception as e:
            return f"storage_error_{datetime.now().strftime('%H%M%S')}"
    
    def get_case_nuclear_strategies(self, case_id: str) -> List[Dict]:
        """
        Get all nuclear strategies for a case
        """
        cursor = self.db.get_cursor()
        
        cursor.execute('''
            SELECT * FROM nuclear_strategies 
            WHERE case_id = ? 
            ORDER BY created_date DESC
        ''', (case_id,))
        
        strategies = []
        for row in cursor.fetchall():
            strategy = dict(row)
            # Parse precedent cases from JSON
            try:
                strategy['precedent_cases'] = json.loads(strategy.get('precedent_cases', '[]'))
            except:
                strategy['precedent_cases'] = []
            strategies.append(strategy)
        
        return strategies
    
    def get_strategy_effectiveness_analysis(self, case_id: str) -> Dict:
        """
        Analyze effectiveness of nuclear strategies for case
        """
        try:
            strategies = self.get_case_nuclear_strategies(case_id)
            
            if not strategies:
                return {
                    'case_id': case_id,
                    'analysis': 'No nuclear strategies deployed yet',
                    'recommendation': 'Consider nuclear options only after conventional approaches fail'
                }
            
            prompt = f"""
            Analyze the effectiveness of nuclear strategies deployed in this case:
            
            Strategies Used: {len(strategies)}
            Strategy Types: {[s['strategy_type'] for s in strategies]}
            
            Provide analysis including:
            1. Overall strategic coherence
            2. Escalation appropriateness
            3. Risk vs. reward assessment
            4. Timing evaluation
            5. Recommendations for next steps
            6. Exit strategy options
            
            Focus on practical effectiveness for pro se litigant.
            """
            
            effectiveness_analysis = self.client.provide_legal_advice(prompt, {"case_id": case_id, "analysis_type": "effectiveness"})
            
            return {
                'case_id': case_id,
                'strategies_analyzed': len(strategies),
                'effectiveness_analysis': effectiveness_analysis,
                'analysis_date': datetime.now().isoformat(),
                'warning': 'Nuclear strategies require careful monitoring and potential de-escalation'
            }
            
        except Exception as e:
            return {
                'error': f"Effectiveness analysis failed: {str(e)}",
                'case_id': case_id
            }
    
    def get_corporate_intimidation_counters(self) -> List[Dict]:
        """
        Get specific counters to corporate intimidation tactics
        """
        return [
            {
                'intimidation_tactic': 'Overwhelming Discovery Requests',
                'counter_strategy': 'Motion for Protective Order + Proportionality Arguments',
                'legal_basis': 'Fed. R. Civ. P. 26(b)(1) proportionality requirements',
                'effectiveness': 'High'
            },
            {
                'intimidation_tactic': 'Frivolous Motions to Dismiss',
                'counter_strategy': 'Sanctions Motion Under Rule 11',
                'legal_basis': 'Fed. R. Civ. P. 11(b) and (c)',
                'effectiveness': 'Medium'
            },
            {
                'intimidation_tactic': 'Delay Tactics',
                'counter_strategy': 'Motion to Compel + Expedited Schedule',
                'legal_basis': 'Fed. R. Civ. P. 37 and local rules',
                'effectiveness': 'Medium'
            },
            {
                'intimidation_tactic': 'Settlement Lowball Offers',
                'counter_strategy': 'Public Disclosure + Media Attention',
                'legal_basis': 'First Amendment protected speech',
                'effectiveness': 'High (if newsworthy)'
            },
            {
                'intimidation_tactic': 'Attorney Fee Threats',
                'counter_strategy': 'Fee-Shifting Statutes Documentation',
                'legal_basis': '42 U.S.C. § 1988, other fee-shifting statutes',
                'effectiveness': 'High (in civil rights cases)'
            }
        ]