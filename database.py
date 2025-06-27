import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
from contextlib import contextmanager

class Database:
    """
    Centralized database management for the pro se litigation platform
    """
    
    def __init__(self, db_path: str = "proselit.db"):
        self.db_path = db_path
        self.connection = None
        self._lock = threading.Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self._create_all_tables()
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            raise
    
    def _create_all_tables(self):
        """Create all necessary tables for the platform"""
        cursor = self.connection.cursor()
        
        # Cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                created_date TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                metadata TEXT DEFAULT '{}',
                plaintiff_info TEXT DEFAULT '{}',
                defendant_info TEXT DEFAULT '{}',
                court_info TEXT DEFAULT '{}',
                case_summary TEXT DEFAULT '',
                estimated_value REAL DEFAULT 0.0,
                priority_level INTEGER DEFAULT 3
            )
        ''')
        
        # Case files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_files (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                upload_date TEXT NOT NULL,
                file_path TEXT,
                analysis_data TEXT DEFAULT '{}',
                content_hash TEXT,
                file_category TEXT DEFAULT 'general',
                FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE
            )
        ''')
        
        # Case documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_documents (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_date TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                template_used TEXT,
                legal_authorities TEXT DEFAULT '[]',
                status TEXT DEFAULT 'draft',
                filing_date TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE
            )
        ''')
        
        # Legal authorities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legal_authorities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                citation TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                court TEXT,
                year INTEGER,
                summary TEXT,
                full_text TEXT,
                verification_status TEXT DEFAULT 'pending',
                verification_date TEXT,
                source_url TEXT,
                authority_type TEXT NOT NULL,
                jurisdiction TEXT,
                created_date TEXT NOT NULL,
                relevance_score REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Citation verifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS citation_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                citation TEXT NOT NULL,
                verification_result TEXT NOT NULL,
                verification_date TEXT NOT NULL,
                source_checked TEXT NOT NULL,
                is_valid BOOLEAN NOT NULL,
                error_message TEXT,
                verification_method TEXT DEFAULT 'automated'
            )
        ''')
        
        # Violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                violation_type TEXT NOT NULL,
                person_involved TEXT NOT NULL,
                description TEXT NOT NULL,
                date_occurred TEXT NOT NULL,
                legal_codes TEXT,
                evidence_ids TEXT DEFAULT '[]',
                statute_analysis TEXT,
                elements_analysis TEXT,
                created_date TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                severity_level INTEGER DEFAULT 3,
                damages_estimate REAL DEFAULT 0.0,
                FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE
            )
        ''')
        
        # Person violations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS person_violations (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                person_name TEXT NOT NULL,
                person_role TEXT,
                person_title TEXT,
                organization TEXT,
                total_violations INTEGER DEFAULT 0,
                violation_ids TEXT DEFAULT '[]',
                timeline_data TEXT DEFAULT '{}',
                contact_info TEXT DEFAULT '{}',
                created_date TEXT NOT NULL,
                liability_assessment TEXT DEFAULT 'pending',
                FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE
            )
        ''')
        
        # Nuclear strategies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nuclear_strategies (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                strategy_type TEXT NOT NULL,
                situation_description TEXT NOT NULL,
                strategy_content TEXT NOT NULL,
                risk_assessment TEXT NOT NULL,
                precedent_cases TEXT,
                implementation_steps TEXT,
                created_date TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                effectiveness_rating INTEGER DEFAULT 0,
                last_reviewed TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE
            )
        ''')
        
        # Strategy precedents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_precedents (
                id TEXT PRIMARY KEY,
                strategy_type TEXT NOT NULL,
                case_citation TEXT NOT NULL,
                court TEXT NOT NULL,
                outcome TEXT NOT NULL,
                key_factors TEXT,
                applicability_score REAL DEFAULT 0.0,
                verification_status TEXT DEFAULT 'pending',
                created_date TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0
            )
        ''')
        
        # AI interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                user_query TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                model_used TEXT DEFAULT 'gpt-4o',
                satisfaction_rating INTEGER,
                FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE SET NULL
            )
        ''')
        
        # Deadlines and reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deadlines (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                deadline_type TEXT NOT NULL,
                description TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority_level INTEGER DEFAULT 3,
                status TEXT DEFAULT 'pending',
                reminder_dates TEXT DEFAULT '[]',
                completion_date TEXT,
                notes TEXT DEFAULT '',
                created_date TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases (id) ON DELETE CASCADE
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_key TEXT UNIQUE NOT NULL,
                preference_value TEXT NOT NULL,
                preference_type TEXT NOT NULL,
                created_date TEXT NOT NULL,
                last_modified TEXT NOT NULL
            )
        ''')
        
        # System logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_level TEXT NOT NULL,
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                case_id TEXT,
                user_action TEXT,
                error_details TEXT
            )
        ''')
        
        self.connection.commit()
    
    @contextmanager
    def get_transaction(self):
        """Context manager for database transactions"""
        with self._lock:
            try:
                yield self.connection
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                raise e
    
    def get_cursor(self):
        """Get database cursor with thread safety"""
        return self.connection.cursor()
    
    def commit(self):
        """Commit current transaction"""
        with self._lock:
            self.connection.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        with self._lock:
            self.connection.rollback()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a SELECT query and return results as dictionaries"""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows"""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute query with multiple parameter sets"""
        with self._lock:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            return cursor.rowcount
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """Get table schema information"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in database"""
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = self.execute_query(query)
        return [row['name'] for row in results]
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            with self._lock:
                backup_conn = sqlite3.connect(backup_path)
                self.connection.backup(backup_conn)
                backup_conn.close()
                return True
        except Exception as e:
            self.log_error("database", f"Backup failed: {str(e)}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                return False
            
            with self._lock:
                # Close current connection
                self.connection.close()
                
                # Replace current database with backup
                if os.path.exists(self.db_path):
                    os.rename(self.db_path, f"{self.db_path}.old")
                
                # Copy backup to main database
                import shutil
                shutil.copy2(backup_path, self.db_path)
                
                # Reinitialize connection
                self._initialize_database()
                return True
                
        except Exception as e:
            self.log_error("database", f"Restore failed: {str(e)}")
            return False
    
    def optimize_database(self) -> bool:
        """Optimize database performance"""
        try:
            with self._lock:
                cursor = self.connection.cursor()
                
                # Analyze all tables
                cursor.execute("ANALYZE")
                
                # Vacuum database
                cursor.execute("VACUUM")
                
                # Reindex
                cursor.execute("REINDEX")
                
                self.connection.commit()
                return True
                
        except Exception as e:
            self.log_error("database", f"Optimization failed: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {}
            
            # Get table row counts
            for table in self.get_all_tables():
                if not table.startswith('sqlite_'):
                    query = f"SELECT COUNT(*) as count FROM {table}"
                    result = self.execute_query(query)
                    stats[f"{table}_count"] = result[0]['count'] if result else 0
            
            # Get database size
            if os.path.exists(self.db_path):
                stats['database_size_bytes'] = os.path.getsize(self.db_path)
                stats['database_size_mb'] = round(stats['database_size_bytes'] / (1024 * 1024), 2)
            
            # Get creation date
            if os.path.exists(self.db_path):
                stats['created_date'] = datetime.fromtimestamp(
                    os.path.getctime(self.db_path)
                ).isoformat()
            
            stats['last_analyzed'] = datetime.now().isoformat()
            
            return stats
            
        except Exception as e:
            return {'error': f"Stats collection failed: {str(e)}"}
    
    def search_across_tables(self, search_term: str, tables: List[str] = None) -> Dict:
        """Search for term across multiple tables"""
        if not tables:
            tables = ['cases', 'case_documents', 'violations', 'legal_authorities']
        
        results = {}
        search_pattern = f"%{search_term}%"
        
        try:
            for table in tables:
                if table == 'cases':
                    query = "SELECT * FROM cases WHERE name LIKE ? OR case_summary LIKE ?"
                    results[table] = self.execute_query(query, (search_pattern, search_pattern))
                
                elif table == 'case_documents':
                    query = "SELECT * FROM case_documents WHERE title LIKE ? OR content LIKE ?"
                    results[table] = self.execute_query(query, (search_pattern, search_pattern))
                
                elif table == 'violations':
                    query = "SELECT * FROM violations WHERE description LIKE ? OR person_involved LIKE ?"
                    results[table] = self.execute_query(query, (search_pattern, search_pattern))
                
                elif table == 'legal_authorities':
                    query = "SELECT * FROM legal_authorities WHERE citation LIKE ? OR title LIKE ? OR summary LIKE ?"
                    results[table] = self.execute_query(query, (search_pattern, search_pattern, search_pattern))
            
            return results
            
        except Exception as e:
            return {'error': f"Search failed: {str(e)}"}
    
    def log_ai_interaction(self, case_id: str, user_query: str, ai_response: str, 
                          interaction_type: str, tokens_used: int = 0) -> bool:
        """Log AI interaction for analysis"""
        try:
            query = '''
                INSERT INTO ai_interactions 
                (case_id, user_query, ai_response, interaction_type, timestamp, tokens_used)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            self.execute_update(query, (
                case_id, user_query, ai_response, interaction_type, 
                datetime.now().isoformat(), tokens_used
            ))
            return True
        except Exception as e:
            self.log_error("ai_interaction", f"Logging failed: {str(e)}")
            return False
    
    def log_error(self, module: str, message: str, case_id: str = None, 
                  error_details: str = None) -> bool:
        """Log system error"""
        try:
            query = '''
                INSERT INTO system_logs 
                (log_level, module, message, timestamp, case_id, error_details)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            self.execute_update(query, (
                'ERROR', module, message, datetime.now().isoformat(), 
                case_id, error_details
            ))
            return True
        except Exception:
            # Can't log the logging error - just return False
            return False
    
    def log_info(self, module: str, message: str, case_id: str = None, 
                 user_action: str = None) -> bool:
        """Log system information"""
        try:
            query = '''
                INSERT INTO system_logs 
                (log_level, module, message, timestamp, case_id, user_action)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            self.execute_update(query, (
                'INFO', module, message, datetime.now().isoformat(), 
                case_id, user_action
            ))
            return True
        except Exception:
            return False
    
    def get_user_preference(self, key: str, default_value: Any = None) -> Any:
        """Get user preference value"""
        try:
            query = "SELECT preference_value, preference_type FROM user_preferences WHERE preference_key = ?"
            results = self.execute_query(query, (key,))
            
            if results:
                value = results[0]['preference_value']
                pref_type = results[0]['preference_type']
                
                # Convert based on type
                if pref_type == 'json':
                    return json.loads(value)
                elif pref_type == 'int':
                    return int(value)
                elif pref_type == 'float':
                    return float(value)
                elif pref_type == 'bool':
                    return value.lower() == 'true'
                else:
                    return value
            
            return default_value
            
        except Exception as e:
            self.log_error("preferences", f"Get preference failed: {str(e)}")
            return default_value
    
    def set_user_preference(self, key: str, value: Any) -> bool:
        """Set user preference value"""
        try:
            # Determine type and convert value
            if isinstance(value, dict) or isinstance(value, list):
                pref_type = 'json'
                pref_value = json.dumps(value)
            elif isinstance(value, int):
                pref_type = 'int'
                pref_value = str(value)
            elif isinstance(value, float):
                pref_type = 'float'
                pref_value = str(value)
            elif isinstance(value, bool):
                pref_type = 'bool'
                pref_value = str(value).lower()
            else:
                pref_type = 'string'
                pref_value = str(value)
            
            # Insert or update preference
            query = '''
                INSERT OR REPLACE INTO user_preferences 
                (preference_key, preference_value, preference_type, created_date, last_modified)
                VALUES (?, ?, ?, ?, ?)
            '''
            current_time = datetime.now().isoformat()
            self.execute_update(query, (key, pref_value, pref_type, current_time, current_time))
            
            return True
            
        except Exception as e:
            self.log_error("preferences", f"Set preference failed: {str(e)}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()
