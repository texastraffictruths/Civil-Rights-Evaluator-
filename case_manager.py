import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import os

class CaseManager:
    """
    Manages multiple cases with complete isolation between cases
    """
    
    def __init__(self, database):
        self.db = database
        self.ensure_tables()
    
    def ensure_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.db.get_cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                created_date TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
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
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_documents (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_date TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        self.db.commit()
    
    def create_case(self, name: str, case_type: str) -> str:
        """Create a new case with unique ID"""
        case_id = str(uuid.uuid4())
        cursor = self.db.get_cursor()
        
        cursor.execute('''
            INSERT INTO cases (id, name, type, created_date, last_modified)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            case_id,
            name,
            case_type,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        self.db.commit()
        return case_id
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """Get case information by ID"""
        cursor = self.db.get_cursor()
        
        cursor.execute('SELECT * FROM cases WHERE id = ?', (case_id,))
        case_row = cursor.fetchone()
        
        if not case_row:
            return None
        
        # Get case files
        cursor.execute('SELECT * FROM case_files WHERE case_id = ?', (case_id,))
        files = [dict(row) for row in cursor.fetchall()]
        
        # Get case documents
        cursor.execute('SELECT * FROM case_documents WHERE case_id = ?', (case_id,))
        documents = [dict(row) for row in cursor.fetchall()]
        
        case_data = dict(case_row)
        case_data['files'] = files
        case_data['documents'] = documents
        case_data['metadata'] = json.loads(case_data.get('metadata', '{}'))
        
        return case_data
    
    def get_all_cases(self) -> List[Dict]:
        """Get all cases"""
        cursor = self.db.get_cursor()
        
        cursor.execute('SELECT * FROM cases ORDER BY last_modified DESC')
        cases = [dict(row) for row in cursor.fetchall()]
        
        for case in cases:
            case['metadata'] = json.loads(case.get('metadata', '{}'))
        
        return cases
    
    def update_case(self, case_id: str, updates: Dict) -> bool:
        """Update case information"""
        cursor = self.db.get_cursor()
        
        # Build update query dynamically
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'metadata':
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        set_clauses.append("last_modified = ?")
        values.append(datetime.now().isoformat())
        values.append(case_id)
        
        query = f"UPDATE cases SET {', '.join(set_clauses)} WHERE id = ?"
        
        cursor.execute(query, values)
        self.db.commit()
        
        return cursor.rowcount > 0
    
    def delete_case(self, case_id: str) -> bool:
        """Delete a case and all associated data"""
        cursor = self.db.get_cursor()
        
        # Delete in order due to foreign key constraints
        cursor.execute('DELETE FROM case_files WHERE case_id = ?', (case_id,))
        cursor.execute('DELETE FROM case_documents WHERE case_id = ?', (case_id,))
        cursor.execute('DELETE FROM cases WHERE id = ?', (case_id,))
        
        self.db.commit()
        return cursor.rowcount > 0
    
    def add_file_to_case(self, case_id: str, filename: str, file_type: str, 
                        file_size: int, file_path: str = None) -> str:
        """Add a file to a case"""
        file_id = str(uuid.uuid4())
        cursor = self.db.get_cursor()
        
        cursor.execute('''
            INSERT INTO case_files (id, case_id, filename, file_type, file_size, upload_date, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            case_id,
            filename,
            file_type,
            file_size,
            datetime.now().isoformat(),
            file_path
        ))
        
        # Update case last modified
        cursor.execute('UPDATE cases SET last_modified = ? WHERE id = ?', 
                      (datetime.now().isoformat(), case_id))
        
        self.db.commit()
        return file_id
    
    def get_case_files(self, case_id: str) -> List[Dict]:
        """Get all files for a case"""
        cursor = self.db.get_cursor()
        
        cursor.execute('SELECT * FROM case_files WHERE case_id = ? ORDER BY upload_date DESC', (case_id,))
        files = [dict(row) for row in cursor.fetchall()]
        
        for file in files:
            file['analysis_data'] = json.loads(file.get('analysis_data', '{}'))
        
        return files
    
    def add_document_to_case(self, case_id: str, document_type: str, 
                            title: str, content: str) -> str:
        """Add a generated document to a case"""
        doc_id = str(uuid.uuid4())
        cursor = self.db.get_cursor()
        
        cursor.execute('''
            INSERT INTO case_documents (id, case_id, document_type, title, content, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            case_id,
            document_type,
            title,
            content,
            datetime.now().isoformat()
        ))
        
        # Update case last modified
        cursor.execute('UPDATE cases SET last_modified = ? WHERE id = ?', 
                      (datetime.now().isoformat(), case_id))
        
        self.db.commit()
        return doc_id
    
    def get_case_documents(self, case_id: str) -> List[Dict]:
        """Get all documents for a case"""
        cursor = self.db.get_cursor()
        
        cursor.execute('SELECT * FROM case_documents WHERE case_id = ? ORDER BY created_date DESC', (case_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def search_cases(self, query: str) -> List[Dict]:
        """Search cases by name or content"""
        cursor = self.db.get_cursor()
        
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM cases 
            WHERE name LIKE ? OR type LIKE ?
            ORDER BY last_modified DESC
        ''', (search_term, search_term))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_case_statistics(self, case_id: str) -> Dict:
        """Get statistical summary of a case"""
        cursor = self.db.get_cursor()
        
        # Count files
        cursor.execute('SELECT COUNT(*) as file_count FROM case_files WHERE case_id = ?', (case_id,))
        file_count = cursor.fetchone()['file_count']
        
        # Count documents
        cursor.execute('SELECT COUNT(*) as doc_count FROM case_documents WHERE case_id = ?', (case_id,))
        doc_count = cursor.fetchone()['doc_count']
        
        # Get case creation date
        cursor.execute('SELECT created_date FROM cases WHERE id = ?', (case_id,))
        created_date = cursor.fetchone()['created_date']
        
        return {
            'file_count': file_count,
            'document_count': doc_count,
            'created_date': created_date,
            'days_active': (datetime.now() - datetime.fromisoformat(created_date)).days
        }
