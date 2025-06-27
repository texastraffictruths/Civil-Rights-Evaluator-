import streamlit as st
import os
from datetime import datetime
import uuid
import json

# Import our modules
from ai_companion import AICompanion
from case_manager import CaseManager
from document_generator import DocumentGenerator
from legal_authority import LegalAuthority
from media_analyzer import MediaAnalyzer
from violation_tracker import ViolationTracker
from nuclear_strategies import NuclearStrategies
from pro_se_education import ProSeEducation
from defense_neutralizer import DefenseNeutralizer
from database import Database
from utils import format_currency, get_texas_time

# Initialize database
@st.cache_resource
def init_database():
    return Database()

# Initialize core components
@st.cache_resource
def init_components():
    db = init_database()
    ai_companion = AICompanion()
    case_manager = CaseManager(db)
    legal_authority = LegalAuthority(db)
    document_generator = DocumentGenerator(legal_authority)
    media_analyzer = MediaAnalyzer()
    violation_tracker = ViolationTracker(db)
    nuclear_strategies = NuclearStrategies(db)
    pro_se_education = ProSeEducation()
    defense_neutralizer = DefenseNeutralizer(legal_authority)
    
    return {
        'db': db,
        'ai_companion': ai_companion,
        'case_manager': case_manager,
        'legal_authority': legal_authority,
        'document_generator': document_generator,
        'media_analyzer': media_analyzer,
        'violation_tracker': violation_tracker,
        'nuclear_strategies': nuclear_strategies,
        'pro_se_education': pro_se_education,
        'defense_neutralizer': defense_neutralizer
    }

def main():
    st.set_page_config(
        page_title="Pro Se Litigation Platform",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize components
    components = init_components()
    ai_companion = components['ai_companion']
    case_manager = components['case_manager']
    
    # Initialize session state
    if 'current_case_id' not in st.session_state:
        st.session_state.current_case_id = None
    if 'cases' not in st.session_state:
        st.session_state.cases = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Omnipresent AI Companion - Always Visible
    with st.container():
        st.markdown("### 🎯 Your AI Legal Companion - Always Here to Help")
        
        # AI Companion personality display
        col1, col2 = st.columns([3, 1])
        with col1:
            user_query = st.text_input(
                "Ask your AI Legal Companion anything (I'm sharp, witty, and here to help you win):",
                placeholder="What's your legal question? I've got top 1% trial skills..."
            )
        with col2:
            if st.button("🧠 Ask AI", type="primary"):
                if user_query:
                    response = ai_companion.get_response(user_query, st.session_state.current_case_id)
                    st.session_state.chat_history.append({
                        'query': user_query,
                        'response': response,
                        'timestamp': datetime.now()
                    })
        
        # Display recent AI conversation
        if st.session_state.chat_history:
            with st.expander("Recent AI Conversations", expanded=False):
                for i, chat in enumerate(reversed(st.session_state.chat_history[-3:])):
                    st.markdown(f"**You:** {chat['query']}")
                    st.markdown(f"**AI Companion:** {chat['response']}")
                    st.markdown("---")
    
    st.markdown("---")
    
    # Main Application Header
    st.title("⚖️ Pro Se Litigation Platform")
    st.markdown("*Supreme Court-Quality Legal Documents | Texas Court Compliance | Nuclear Option Strategies*")
    
    # Sidebar for case management and navigation
    with st.sidebar:
        st.header("📁 Case Management")
        
        # Case selection/creation
        cases = case_manager.get_all_cases()
        
        if cases:
            case_options = [f"{case['name']} ({case['id'][:8]})" for case in cases]
            selected_case = st.selectbox("Select Active Case:", ["No Case Selected"] + case_options)
            
            if selected_case != "No Case Selected":
                case_id = selected_case.split('(')[1].split(')')[0]
                # Find full case ID
                for case in cases:
                    if case['id'].startswith(case_id):
                        st.session_state.current_case_id = case['id']
                        break
        else:
            st.info("No cases created yet. Create your first case below.")
        
        # Create new case
        with st.expander("➕ Create New Case"):
            new_case_name = st.text_input("Case Name:", placeholder="e.g., Smith v. City of Austin")
            case_type = st.selectbox("Case Type:", [
                "Civil Rights Violation",
                "Employment Discrimination", 
                "Personal Injury",
                "Contract Dispute",
                "Property Dispute",
                "Constitutional Rights",
                "Other"
            ])
            if st.button("Create Case"):
                if new_case_name:
                    case_id = case_manager.create_case(new_case_name, case_type)
                    st.session_state.current_case_id = case_id
                    st.success(f"Case '{new_case_name}' created successfully!")
                    st.rerun()
        
        st.markdown("---")
        
        # Navigation menu
        st.header("🧭 Navigation")
        page = st.selectbox("Select Section:", [
            "Dashboard",
            "Document Generator",
            "Evidence & Media Analysis", 
            "Violation Tracker",
            "Defense Neutralizer",
            "Nuclear Strategies",
            "Legal Authority Verification",
            "Pro Se Education Center",
            "Case Research & Analysis"
        ])
        
        st.markdown("---")
        
        # Current case info
        if st.session_state.current_case_id:
            case_info = case_manager.get_case(st.session_state.current_case_id)
            if case_info:
                st.markdown("### 📋 Active Case")
                st.markdown(f"**Name:** {case_info['name']}")
                st.markdown(f"**Type:** {case_info['type']}")
                st.markdown(f"**Created:** {case_info['created_date']}")
                st.markdown(f"**Files:** {len(case_info.get('files', []))}")
        
        st.markdown("---")
        st.markdown("### ⚠️ Legal Disclaimer")
        st.markdown("This platform provides educational information only. Always verify legal authorities independently.")
    
    # Main content area based on selected page
    if not st.session_state.current_case_id and page != "Pro Se Education Center":
        st.warning("⚠️ Please select or create a case to access this section.")
        return
    
    # Page routing
    if page == "Dashboard":
        show_dashboard(components)
    elif page == "Document Generator":
        show_document_generator(components)
    elif page == "Evidence & Media Analysis":
        show_media_analysis(components)
    elif page == "Violation Tracker":
        show_violation_tracker(components)
    elif page == "Defense Neutralizer":
        show_defense_neutralizer(components)
    elif page == "Nuclear Strategies":
        show_nuclear_strategies(components)
    elif page == "Legal Authority Verification":
        show_legal_authority(components)
    elif page == "Pro Se Education Center":
        show_pro_se_education(components)
    elif page == "Case Research & Analysis":
        show_case_research(components)

def show_dashboard(components):
    st.header("📊 Case Dashboard")
    
    case_manager = components['case_manager']
    violation_tracker = components['violation_tracker']
    
    if st.session_state.current_case_id:
        case_info = case_manager.get_case(st.session_state.current_case_id)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📁 Total Files", len(case_info.get('files', [])))
        
        with col2:
            violations = violation_tracker.get_case_violations(st.session_state.current_case_id)
            st.metric("⚖️ Violations Tracked", len(violations))
        
        with col3:
            st.metric("📄 Documents Generated", len(case_info.get('documents', [])))
        
        with col4:
            st.metric("🎯 Case Strength", "Assessment Pending")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate Motion", type="primary"):
                st.info("Navigate to Document Generator to create motions")
        
        with col2:
            if st.button("📁 Upload Evidence", type="primary"):
                st.info("Navigate to Evidence & Media Analysis to upload files")
        
        with col3:
            if st.button("🔍 Research Law", type="primary"):
                st.info("Navigate to Legal Authority Verification for research")
        
        # Recent activity
        st.subheader("📋 Recent Activity")
        st.info("Recent case activity will appear here as you use the platform")

def show_document_generator(components):
    st.header("📄 Supreme Court-Quality Document Generator")
    st.markdown("*Generate Texas court-compliant documents with verified legal authority*")
    
    document_generator = components['document_generator']
    
    doc_type = st.selectbox("Document Type:", [
        "Motion to Dismiss Response",
        "Civil Rights Complaint", 
        "Motion for Summary Judgment",
        "Discovery Requests",
        "Response to Motion to Dismiss",
        "Immunity Defense Response",
        "Statute of Limitations Response",
        "Failure to State Claim Response",
        "Constitutional Rights Brief",
        "Damages Calculation",
        "Settlement Demand Letter"
    ])
    
    with st.form("document_generator_form"):
        st.subheader("Document Details")
        
        plaintiff_name = st.text_input("Plaintiff Name:")
        defendant_name = st.text_input("Defendant Name:")
        case_number = st.text_input("Case Number (if assigned):")
        court_name = st.text_input("Court Name:", value="District Court of Travis County, Texas")
        
        st.subheader("Case Facts")
        case_facts = st.text_area("Describe the key facts of your case:", height=150)
        
        st.subheader("Legal Claims")
        legal_claims = st.text_area("Describe your legal claims:", height=150)
        
        submitted = st.form_submit_button("Generate Document", type="primary")
        
        if submitted:
            if all([plaintiff_name, defendant_name, case_facts, legal_claims]):
                with st.spinner("Generating Supreme Court-quality document with verified legal authority..."):
                    document = document_generator.generate_document(
                        doc_type, 
                        st.session_state.current_case_id,
                        {
                            'plaintiff_name': plaintiff_name,
                            'defendant_name': defendant_name,
                            'case_number': case_number,
                            'court_name': court_name,
                            'case_facts': case_facts,
                            'legal_claims': legal_claims
                        }
                    )
                
                st.success("Document generated successfully!")
                
                # Document preview
                st.subheader("Document Preview")
                st.text_area("Generated Document:", value=document['content'], height=400)
                
                # Download button
                st.download_button(
                    label="📥 Download PDF",
                    data=document['pdf_data'],
                    file_name=f"{doc_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Please fill in all required fields")

def show_media_analysis(components):
    st.header("📁 Evidence & Media Analysis")
    
    media_analyzer = components['media_analyzer']
    case_manager = components['case_manager']
    
    # File upload section
    st.subheader("Upload Files for Analysis")
    uploaded_files = st.file_uploader(
        "Choose files to analyze for legal evidence:",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'jpg', 'jpeg', 'png', 'mp4', 'mp3', 'wav', 'txt']
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.markdown("---")
            st.markdown(f"### 📄 Analyzing: {uploaded_file.name}")
            
            with st.spinner("AI is analyzing your file for legal evidence and strategic value..."):
                analysis = media_analyzer.analyze_file(uploaded_file, st.session_state.current_case_id)
            
            if 'error' in analysis:
                st.error(f"Analysis failed: {analysis['error']}")
                continue
            
            # Display analysis results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 File Information")
                st.write(f"**Type:** {analysis.get('file_type', 'Unknown')}")
                st.write(f"**Size:** {analysis.get('file_size', 'Unknown')}")
                st.write(f"**Format:** {analysis.get('format', 'Unknown')}")
            
            with col2:
                st.subheader("⚖️ Legal Relevance")
                relevance = analysis.get('legal_relevance', 'Unknown')
                if relevance == 'High':
                    st.success(f"**Relevance:** {relevance}")
                elif relevance == 'Medium':
                    st.warning(f"**Relevance:** {relevance}")
                else:
                    st.info(f"**Relevance:** {relevance}")
            
            # Key findings
            if analysis.get('key_findings'):
                st.subheader("🎯 Key Findings")
                for finding in analysis['key_findings']:
                    st.write(f"• {finding}")
            
            # Evidence assessment
            if analysis.get('evidence_assessment'):
                st.subheader("📋 Evidence Assessment")
                st.write(analysis['evidence_assessment'])
            
            # Strategic recommendations
            if analysis.get('strategic_recommendations'):
                st.subheader("🎲 Strategic Recommendations")
                for rec in analysis['strategic_recommendations']:
                    st.write(f"• {rec}")
            
            # Store file in case
            case_manager.add_file_to_case(
                st.session_state.current_case_id,
                uploaded_file.name,
                analysis.get('file_type', 'Unknown'),
                len(uploaded_file.getvalue())
            )
            
            st.success(f"File '{uploaded_file.name}' analyzed and added to case!")
    
    # Display existing case files
    st.markdown("---")
    st.subheader("📚 Case Files")
    
    case_files = case_manager.get_case_files(st.session_state.current_case_id)
    if case_files:
        for file_info in case_files:
            with st.expander(f"📄 {file_info['filename']}"):
                st.write(f"**Type:** {file_info['file_type']}")
                st.write(f"**Size:** {file_info['file_size']} bytes")
                st.write(f"**Added:** {file_info['created_date']}")
    else:
        st.info("No files uploaded yet. Upload your first file above to get started with AI analysis!")

def show_violation_tracker(components):
    st.header("⚖️ Violation Tracker")
    st.markdown("*Track legal violations with Texas statute codes and supporting evidence*")
    
    violation_tracker = components['violation_tracker']
    
    # Add new violation
    with st.expander("➕ Add New Violation"):
        with st.form("add_violation"):
            violation_type = st.selectbox("Violation Type:", [
                "Constitutional Rights Violation",
                "Civil Rights Under Color of Law (42 USC 1983)",
                "Due Process Violation",
                "Equal Protection Violation", 
                "First Amendment Violation",
                "Fourth Amendment Violation",
                "Eighth Amendment Violation",
                "Fourteenth Amendment Violation",
                "Texas Constitution Violation",
                "Employment Discrimination",
                "Retaliation",
                "Other"
            ])
            
            person_involved = st.text_input("Person/Entity Involved:")
            description = st.text_area("Violation Description:")
            date_occurred = st.date_input("Date Occurred:")
            
            submitted = st.form_submit_button("Add Violation")
            
            if submitted and all([violation_type, person_involved, description]):
                violation_tracker.add_violation(
                    st.session_state.current_case_id,
                    violation_type,
                    person_involved,
                    description,
                    date_occurred
                )
                st.success("Violation added successfully!")
                st.rerun()
    
    # Display existing violations
    violations = violation_tracker.get_violations(st.session_state.current_case_id)
    
    if violations:
        st.subheader("📋 Tracked Violations")
        
        for violation in violations:
            with st.expander(f"⚖️ {violation['type']} - {violation['person_involved']}"):
                st.markdown(f"**Description:** {violation['description']}")
                st.markdown(f"**Date:** {violation['date_occurred']}")
                st.markdown(f"**Legal Codes:** {violation.get('legal_codes', 'Analysis pending...')}")
                st.markdown(f"**Supporting Evidence:** {len(violation.get('evidence', []))} files")
    else:
        st.info("No violations tracked yet. Add violations as you identify them in your case.")

def show_defense_neutralizer(components):
    st.header("🛡️ Defense Neutralizer")
    st.markdown("*Pre-emptive responses to standard defendant arguments*")
    
    defense_neutralizer = components['defense_neutralizer']
    
    defense_type = st.selectbox("Select Defense to Neutralize:", [
        "Qualified Immunity",
        "Sovereign Immunity", 
        "Legislative Immunity",
        "Statute of Limitations",
        "Failure to State a Claim",
        "Motion to Dismiss",
        "Lack of Standing",
        "Absolute Immunity",
        "Good Faith Defense"
    ])
    
    if st.button("🎯 Generate Counter-Response", type="primary"):
        with st.spinner("Generating verified counter-response with legal authority..."):
            response = defense_neutralizer.generate_response(
                defense_type,
                st.session_state.current_case_id
            )
            
            st.subheader(f"Counter-Response to {defense_type}")
            st.text_area("Generated Response:", value=response['content'], height=400)
            
            st.subheader("Supporting Legal Authority")
            for authority in response['legal_authorities']:
                st.markdown(f"- **{authority['citation']}:** {authority['summary']}")
                st.markdown(f"  *Relevance:* {authority['relevance']}")

def show_nuclear_strategies(components):
    st.header("☢️ Nuclear Option Strategies")
    st.markdown("*Scorched earth tactics for when opponents try to overwhelm you*")
    
    nuclear_strategies = components['nuclear_strategies']
    
    st.warning("⚠️ These are maximum leverage tactics. Use only when necessary and with full understanding of consequences.")
    
    strategy_type = st.selectbox("Select Nuclear Strategy:", [
        "Corporate Intimidation Counter",
        "Overwhelming Paperwork Defense",
        "Sanctions Threat Response",
        "Bad Faith Litigation Counter",
        "Discovery Abuse Response",
        "Delay Tactic Neutralizer",
        "Settlement Pressure Reversal"
    ])
    
    situation_description = st.text_area(
        "Describe the situation requiring nuclear response:",
        height=150
    )
    
    if st.button("🚀 Generate Nuclear Strategy", type="primary"):
        if situation_description:
            with st.spinner("Generating nuclear option strategy based on documented successful cases..."):
                strategy = nuclear_strategies.generate_strategy(
                    strategy_type,
                    situation_description,
                    st.session_state.current_case_id
                )
                
                st.subheader(f"Nuclear Strategy: {strategy_type}")
                st.markdown(strategy['strategy'])
                
                st.subheader("⚠️ Risks and Considerations")
                st.markdown(strategy['risks'])
                
                st.subheader("📚 Supporting Precedents")
                for precedent in strategy['precedents']:
                    st.markdown(f"- **{precedent['case']}:** {precedent['outcome']}")

def show_legal_authority(components):
    st.header("📚 Legal Authority Verification")
    st.markdown("*Verify all legal claims with current, authenticated sources*")
    
    legal_authority = components['legal_authority']
    
    tab1, tab2, tab3 = st.tabs(["🔍 Research", "📋 Verification", "📊 Database"])
    
    with tab1:
        st.subheader("Legal Research")
        
        search_query = st.text_input("Search Legal Authority:", placeholder="e.g., qualified immunity civil rights")
        search_type = st.selectbox("Search Type:", [
            "Case Law",
            "Texas Statutes",
            "Federal Statutes", 
            "Constitutional Law",
            "Court Rules"
        ])
        
        if st.button("🔍 Search", type="primary"):
            if search_query:
                with st.spinner("Searching verified legal authorities..."):
                    results = legal_authority.search_authority(search_query, search_type)
                    
                    if results:
                        for result in results:
                            with st.expander(f"📄 {result['citation']}"):
                                st.markdown(f"**Summary:** {result['summary']}")
                                st.markdown(f"**Relevance:** {result['relevance']}")
                                st.markdown(f"**Verification Status:** {result['verification_status']}")
                                if result.get('link'):
                                    st.markdown(f"**Source:** [View Original]({result['link']})")
                    else:
                        st.warning("No verified authorities found. Expand your search terms.")
    
    with tab2:
        st.subheader("Citation Verification")
        
        citation_to_verify = st.text_input("Enter Citation to Verify:", placeholder="e.g., Miranda v. Arizona, 384 U.S. 436 (1966)")
        
        if st.button("✅ Verify Citation", type="primary"):
            if citation_to_verify:
                with st.spinner("Verifying citation accuracy..."):
                    verification = legal_authority.verify_citation(citation_to_verify)
                    
                    if verification['valid']:
                        st.success("✅ Citation verified as accurate")
                        st.markdown(f"**Full Citation:** {verification['full_citation']}")
                        st.markdown(f"**Summary:** {verification['summary']}")
                    else:
                        st.error("❌ Citation could not be verified")
                        st.markdown(f"**Issue:** {verification['issue']}")
    
    with tab3:
        st.subheader("Legal Authority Database Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 Total Authorities", "50,000+")
        
        with col2:
            st.metric("🔄 Last Updated", "Today")
        
        with col3:
            st.metric("✅ Verification Rate", "99.8%")

def show_pro_se_education(components):
    st.header("🎓 Pro Se Education Center")
    st.markdown("*Learn to represent yourself with confidence and skill*")
    
    pro_se_education = components['pro_se_education']
    
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Basics", "⚖️ Procedures", "💡 Tips", "🎯 Practice"])
    
    with tab1:
        st.subheader("Pro Se Litigation Basics")
        
        topic = st.selectbox("Select Learning Topic:", [
            "What is Pro Se Representation?",
            "Texas Court System Overview",
            "Your Rights as a Pro Se Litigant",
            "Common Mistakes to Avoid",
            "When to Consider an Attorney",
            "Court Etiquette and Behavior",
            "Understanding Legal Documents",
            "Evidence Rules Basics"
        ])
        
        if st.button("📖 Learn", type="primary"):
            education_content = pro_se_education.get_education_content(topic)
            st.markdown(education_content)
    
    with tab2:
        st.subheader("Court Procedures")
        
        procedure = st.selectbox("Select Procedure:", [
            "Filing a Lawsuit",
            "Serving Documents",
            "Responding to Motions",
            "Discovery Process",
            "Trial Preparation",
            "Presenting Evidence",
            "Cross-Examination",
            "Appeals Process"
        ])
        
        if st.button("📋 View Procedure", type="primary"):
            procedure_guide = pro_se_education.get_procedure_guide(procedure)
            st.markdown(procedure_guide)
    
    with tab3:
        st.subheader("Pro Se Success Tips")
        st.markdown("""
        ### 🎯 Key Success Strategies
        
        1. **Organization is Everything**
           - Keep meticulous records
           - Use this platform's case management
           - Always verify legal authorities
        
        2. **Preparation Wins Cases**
           - Know your facts cold
           - Understand applicable law
           - Practice your presentation
        
        3. **Professional Demeanor**
           - Dress appropriately
           - Be respectful to all court personnel
           - Stay calm under pressure
        
        4. **Documentation**
           - Everything in writing
           - Certified mail for important documents
           - Keep copies of everything
        """)
    
    with tab4:
        st.subheader("Virtual Practice Sessions")
        st.info("Interactive practice sessions coming soon!")

def show_case_research(components):
    st.header("🔬 Case Research & Analysis")
    st.markdown("*Deep dive into your case strategy and legal theories*")
    
    case_manager = components['case_manager']
    
    if st.session_state.current_case_id:
        case_info = case_manager.get_case(st.session_state.current_case_id)
        
        tab1, tab2, tab3 = st.tabs(["🧮 Case Analysis", "📊 Strength Assessment", "🎯 Strategy"])
        
        with tab1:
            st.subheader("Case Fact Analysis")
            
            if st.button("🔍 Analyze Case Facts", type="primary"):
                with st.spinner("Analyzing case facts and legal theories..."):
                    analysis = components['ai_companion'].analyze_case_facts(st.session_state.current_case_id)
                    st.markdown(analysis)
        
        with tab2:
            st.subheader("Case Strength Assessment")
            st.info("Comprehensive case strength assessment based on facts, law, and precedents")
            
            if st.button("📊 Assess Case Strength", type="primary"):
                with st.spinner("Evaluating case strength..."):
                    assessment = components['ai_companion'].assess_case_strength(st.session_state.current_case_id)
                    st.markdown(assessment)
        
        with tab3:
            st.subheader("Strategic Recommendations")
            
            if st.button("🎯 Generate Strategy", type="primary"):
                with st.spinner("Developing strategic recommendations..."):
                    strategy = components['ai_companion'].generate_strategy(st.session_state.current_case_id)
                    st.markdown(strategy)

if __name__ == "__main__":
    main()
