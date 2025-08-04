"""
Enhanced Database Manager for LEGO BrickEconomy Scraper
Provides optimized database operations with indexing, validation, and backup
"""

import sqlite3
import pandas as pd
import shutil
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from contextlib import contextmanager
import threading
from dataclasses import dataclass

from exceptions import DatabaseError, DataValidationError
from logging_system import get_logger

logger = get_logger(__name__)


@dataclass
class DatabaseStats:
    """Statistics about the database"""
    total_sets: int = 0
    found_sets: int = 0
    sets_with_images: int = 0
    total_minifigs: int = 0
    found_minifigs: int = 0
    minifigs_with_images: int = 0
    unique_themes: int = 0
    unique_years: int = 0
    database_size_mb: float = 0.0
    last_updated: str = "Never"


class DatabaseManager:
    """Enhanced database manager with optimization and validation"""
    
    def __init__(self, db_path: str = "lego_database/LegoDatabase.db"):
        self.db_path = Path(db_path)
        self.backup_dir = self.db_path.parent / "backups"
        self._lock = threading.Lock()
        
        # Ensure directories exist
        self.db_path.parent.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        logger.info(f"Database manager initialized: {self.db_path}")
    
    def _initialize_database(self):
        """Initialize database with optimized schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create themes table for normalization
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS themes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create enhanced lego_sets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lego_sets (
                    lego_code TEXT PRIMARY KEY,
                    official_name TEXT,
                    number_of_pieces TEXT,
                    number_of_minifigs TEXT,
                    released TEXT,
                    retired TEXT,
                    retail_price_eur TEXT,
                    retail_price_gbp TEXT,
                    value_new_sealed TEXT,
                    value_used TEXT,
                    image_url TEXT,
                    image_path TEXT,
                    theme TEXT,
                    subtheme TEXT,
                    has_image INTEGER DEFAULT 0,
                    
                    -- Enhanced numeric fields
                    pieces_numeric INTEGER,
                    minifigs_numeric INTEGER,
                    price_eur_numeric REAL,
                    price_gbp_numeric REAL,
                    value_new_numeric REAL,
                    value_used_numeric REAL,
                    release_year INTEGER,
                    
                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_scraped TIMESTAMP,
                    scrape_success INTEGER DEFAULT 0,
                    scrape_attempts INTEGER DEFAULT 0,
                    
                    -- Data quality indicators
                    data_completeness_score REAL DEFAULT 0.0,
                    validation_status TEXT DEFAULT 'pending'
                )
            """)
            
            # Create enhanced minifig table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS minifig (
                    minifig_code TEXT PRIMARY KEY,
                    official_name TEXT,
                    year TEXT,
                    released TEXT,
                    retail_price_gbp TEXT,
                    has_image INTEGER DEFAULT 0,
                    image_path TEXT,
                    sets TEXT,
                    theme TEXT,
                    
                    -- Enhanced fields
                    year_numeric INTEGER,
                    price_gbp_numeric REAL,
                    
                    -- Metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_scraped TIMESTAMP,
                    scrape_success INTEGER DEFAULT 0,
                    scrape_attempts INTEGER DEFAULT 0,
                    
                    -- Data quality
                    data_completeness_score REAL DEFAULT 0.0,
                    validation_status TEXT DEFAULT 'pending'
                )
            """)
            
            # Create set-minifig relationship table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS set_minifig_relations (
                    set_code TEXT,
                    minifig_code TEXT,
                    quantity INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (set_code, minifig_code),
                    FOREIGN KEY (set_code) REFERENCES lego_sets(lego_code) ON DELETE CASCADE,
                    FOREIGN KEY (minifig_code) REFERENCES minifig(minifig_code) ON DELETE CASCADE
                )
            """)
            
            # Create metadata table for database management
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS database_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            self._create_indexes(cursor)
            
            # Insert initial metadata
            cursor.execute("""
                INSERT OR REPLACE INTO database_metadata (key, value) 
                VALUES ('schema_version', '2.0')
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO database_metadata (key, value) 
                VALUES ('last_optimization', ?)
            """, (datetime.now(timezone.utc).isoformat(),))
            
            conn.commit()
            logger.info("Database schema initialized successfully")
    
    def _create_indexes(self, cursor: sqlite3.Cursor):
        """Create optimized indexes for better query performance"""
        indexes = [
            # Lego sets indexes
            "CREATE INDEX IF NOT EXISTS idx_sets_lego_code ON lego_sets(lego_code)",
            "CREATE INDEX IF NOT EXISTS idx_sets_theme ON lego_sets(theme)",
            "CREATE INDEX IF NOT EXISTS idx_sets_has_image ON lego_sets(has_image)",
            "CREATE INDEX IF NOT EXISTS idx_sets_released ON lego_sets(released)",
            
            # Minifig indexes
            "CREATE INDEX IF NOT EXISTS idx_minifig_code ON minifig(minifig_code)",
            "CREATE INDEX IF NOT EXISTS idx_minifig_has_image ON minifig(has_image)",
            "CREATE INDEX IF NOT EXISTS idx_minifig_year ON minifig(year)",
            
            # Relationship indexes
            "CREATE INDEX IF NOT EXISTS idx_relations_set ON set_minifig_relations(set_code)",
            "CREATE INDEX IF NOT EXISTS idx_relations_minifig ON set_minifig_relations(minifig_code)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.Error as e:
                logger.warning(f"Could not create index: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper configuration"""
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                check_same_thread=False
            )
            # Optimize SQLite settings
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            conn.execute("PRAGMA temp_store = MEMORY")
            conn.execute("PRAGMA foreign_keys = ON")
            
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database connection error: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def backup_database(self, backup_name: str = None) -> str:
        """Create a backup of the database"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            with self._lock:
                shutil.copy2(self.db_path, backup_path)
            
            # Compress if backup is large
            backup_size = backup_path.stat().st_size
            if backup_size > 50 * 1024 * 1024:  # 50MB
                import gzip
                compressed_path = backup_path.with_suffix('.db.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path.unlink()  # Remove uncompressed version
                backup_path = compressed_path
            
            logger.info(f"Database backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            raise DatabaseError(f"Backup failed: {str(e)}", operation="backup")
    
    def validate_and_clean_data(self, data: Dict[str, Any], table: str) -> Dict[str, Any]:
        """Validate and clean data before insertion"""
        cleaned_data = data.copy()
        
        if table == "lego_sets":
            cleaned_data = self._validate_set_data(cleaned_data)
        elif table == "minifig":
            cleaned_data = self._validate_minifig_data(cleaned_data)
        
        return cleaned_data
    
    def _validate_set_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance LEGO set data"""
        # Extract numeric values
        data['pieces_numeric'] = self._extract_numeric(data.get('number_of_pieces'))
        data['minifigs_numeric'] = self._extract_numeric(data.get('number_of_minifigs'))
        data['price_eur_numeric'] = self._extract_price(data.get('retail_price_eur'))
        data['price_gbp_numeric'] = self._extract_price(data.get('retail_price_gbp'))
        data['value_new_numeric'] = self._extract_price(data.get('value_new_sealed'))
        data['value_used_numeric'] = self._extract_price(data.get('value_used'))
        data['release_year'] = self._extract_year(data.get('released'))
        
        # Set metadata
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        data['last_scraped'] = datetime.now(timezone.utc).isoformat()
        
        # Calculate data completeness score
        data['data_completeness_score'] = self._calculate_completeness_score(data, 'set')
        
        # Set validation status
        data['validation_status'] = 'validated' if data['data_completeness_score'] > 0.7 else 'incomplete'
        
        return data
    
    def _validate_minifig_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance minifig data"""
        # Extract numeric values
        data['year_numeric'] = self._extract_numeric(data.get('year'))
        data['price_gbp_numeric'] = self._extract_price(data.get('retail_price_gbp'))
        
        # Set metadata
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        data['last_scraped'] = datetime.now(timezone.utc).isoformat()
        
        # Calculate data completeness score
        data['data_completeness_score'] = self._calculate_completeness_score(data, 'minifig')
        
        # Set validation status
        data['validation_status'] = 'validated' if data['data_completeness_score'] > 0.6 else 'incomplete'
        
        return data
    
    def _extract_numeric(self, value: Any) -> Optional[int]:
        """Extract numeric value from string"""
        if not value or value in ['Not found', 'Error', '']:
            return None
        
        # Extract first number found
        numbers = re.findall(r'\d+', str(value))
        return int(numbers[0]) if numbers else None
    
    def _extract_price(self, value: Any) -> Optional[float]:
        """Extract price value from string"""
        if not value or value in ['Not found', 'Error', '']:
            return None
        
        # Remove currency symbols and extract decimal number
        price_str = re.sub(r'[£€$,\s]', '', str(value))
        numbers = re.findall(r'\d+\.?\d*', price_str)
        return float(numbers[0]) if numbers else None
    
    def _extract_year(self, value: Any) -> Optional[int]:
        """Extract year from date string"""
        if not value or value in ['Not found', 'Error', '']:
            return None
        
        # Look for 4-digit year
        years = re.findall(r'\b(19|20)\d{2}\b', str(value))
        return int(years[0]) if years else None
    
    def _calculate_completeness_score(self, data: Dict[str, Any], data_type: str) -> float:
        """Calculate data completeness score (0.0 to 1.0)"""
        if data_type == 'set':
            fields = [
                'official_name', 'number_of_pieces', 'released', 'theme',
                'retail_price_eur', 'retail_price_gbp', 'image_path'
            ]
        else:  # minifig
            fields = [
                'official_name', 'year', 'theme', 'retail_price_gbp', 'image_path'
            ]
        
        completed_fields = 0
        for field in fields:
            value = data.get(field)
            if value and value not in ['Not found', 'Error', '', None]:
                completed_fields += 1
        
        return completed_fields / len(fields)
    
    def insert_or_update_set(self, set_data: Dict[str, Any]) -> bool:
        """Insert or update a LEGO set with validation"""
        try:
            validated_data = self.validate_and_clean_data(set_data, 'lego_sets')
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if record exists
                cursor.execute("SELECT scrape_attempts FROM lego_sets WHERE lego_code = ?", 
                             (validated_data['lego_code'],))
                existing = cursor.fetchone()
                
                if existing:
                    validated_data['scrape_attempts'] = existing[0] + 1
                else:
                    validated_data['scrape_attempts'] = 1
                
                # Set success flag
                validated_data['scrape_success'] = 1 if validated_data.get('official_name') not in ['Not found', 'Error'] else 0
                
                # Prepare SQL for upsert
                columns = list(validated_data.keys())
                placeholders = ', '.join(['?' for _ in columns])
                conflict_updates = ', '.join([f"{col} = excluded.{col}" for col in columns if col != 'lego_code'])
                
                sql = f"""
                    INSERT INTO lego_sets ({', '.join(columns)}) 
                    VALUES ({placeholders})
                    ON CONFLICT(lego_code) DO UPDATE SET {conflict_updates}
                """
                
                cursor.execute(sql, list(validated_data.values()))
                conn.commit()
                
                logger.debug(f"Set {validated_data['lego_code']} saved successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to insert/update set {set_data.get('lego_code', 'unknown')}: {e}")
            raise DatabaseError(f"Set insertion failed: {str(e)}", operation="insert_set")
    
    def insert_or_update_minifig(self, minifig_data: Dict[str, Any]) -> bool:
        """Insert or update a minifig with validation"""
        try:
            validated_data = self.validate_and_clean_data(minifig_data, 'minifig')
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if record exists
                cursor.execute("SELECT scrape_attempts FROM minifig WHERE minifig_code = ?", 
                             (validated_data['minifig_code'],))
                existing = cursor.fetchone()
                
                if existing:
                    validated_data['scrape_attempts'] = existing[0] + 1
                else:
                    validated_data['scrape_attempts'] = 1
                
                # Set success flag
                validated_data['scrape_success'] = 1 if validated_data.get('official_name') not in ['Not found', 'Error'] else 0
                
                # Prepare SQL for upsert
                columns = list(validated_data.keys())
                placeholders = ', '.join(['?' for _ in columns])
                conflict_updates = ', '.join([f"{col} = excluded.{col}" for col in columns if col != 'minifig_code'])
                
                sql = f"""
                    INSERT INTO minifig ({', '.join(columns)}) 
                    VALUES ({placeholders})
                    ON CONFLICT(minifig_code) DO UPDATE SET {conflict_updates}
                """
                
                cursor.execute(sql, list(validated_data.values()))
                conn.commit()
                
                logger.debug(f"Minifig {validated_data['minifig_code']} saved successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to insert/update minifig {minifig_data.get('minifig_code', 'unknown')}: {e}")
            raise DatabaseError(f"Minifig insertion failed: {str(e)}", operation="insert_minifig")
    
    def get_comprehensive_stats(self) -> DatabaseStats:
        """Get comprehensive database statistics"""
        try:
            with self._get_connection() as conn:
                stats = DatabaseStats()
                
                # Sets statistics
                set_stats = pd.read_sql_query("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN official_name IS NOT NULL AND official_name NOT IN ('Not found', 'Error') THEN 1 ELSE 0 END) as found,
                        SUM(CASE WHEN has_image = 1 THEN 1 ELSE 0 END) as with_images,
                        COUNT(DISTINCT theme) as unique_themes,
                        'Unknown' as last_updated
                    FROM lego_sets
                """, conn).iloc[0]
                
                stats.total_sets = set_stats['total']
                stats.found_sets = set_stats['found']
                stats.sets_with_images = set_stats['with_images']
                stats.unique_themes = set_stats['unique_themes']
                
                # Minifig statistics
                minifig_stats = pd.read_sql_query("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN official_name IS NOT NULL AND official_name NOT IN ('Not found', 'Error') THEN 1 ELSE 0 END) as found,
                        SUM(CASE WHEN has_image = 1 THEN 1 ELSE 0 END) as with_images,
                        COUNT(DISTINCT year) as unique_years,
                        'Unknown' as last_updated
                    FROM minifig
                """, conn).iloc[0]
                
                stats.total_minifigs = minifig_stats['total']
                stats.found_minifigs = minifig_stats['found']
                stats.minifigs_with_images = minifig_stats['with_images']
                stats.unique_years = minifig_stats['unique_years']
                
                # Database size
                stats.database_size_mb = self.db_path.stat().st_size / (1024 * 1024)
                
                # Last updated
                last_updated = max(
                    set_stats.get('last_updated', ''),
                    minifig_stats.get('last_updated', '')
                )
                if last_updated:
                    stats.last_updated = last_updated
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return DatabaseStats()
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                logger.info("Starting database optimization...")
                
                # Analyze tables for query optimization
                cursor.execute("ANALYZE")
                
                # Vacuum to reclaim space
                cursor.execute("VACUUM")
                
                # Update metadata
                cursor.execute("""
                    INSERT OR REPLACE INTO database_metadata (key, value) 
                    VALUES ('last_optimization', ?)
                """, (datetime.now(timezone.utc).isoformat(),))
                
                conn.commit()
                logger.info("Database optimization completed")
                
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            raise DatabaseError(f"Optimization failed: {str(e)}", operation="optimize")
    
    def export_to_formats(self, output_dir: str = "exports"):
        """Export database to multiple formats"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            with self._get_connection() as conn:
                # Export sets
                sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
                sets_df.to_csv(output_path / f"lego_sets_{timestamp}.csv", index=False)
                sets_df.to_json(output_path / f"lego_sets_{timestamp}.json", orient='records', indent=2)
                
                # Export minifigs
                minifigs_df = pd.read_sql_query("SELECT * FROM minifig", conn)
                minifigs_df.to_csv(output_path / f"minifigs_{timestamp}.csv", index=False)
                minifigs_df.to_json(output_path / f"minifigs_{timestamp}.json", orient='records', indent=2)
                
                # Export with Excel if available
                try:
                    with pd.ExcelWriter(output_path / f"lego_database_{timestamp}.xlsx") as writer:
                        sets_df.to_excel(writer, sheet_name='LEGO Sets', index=False)
                        minifigs_df.to_excel(writer, sheet_name='Minifigures', index=False)
                except ImportError:
                    logger.warning("Excel export requires openpyxl package")
                
                logger.info(f"Database exported to {output_path}")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise DatabaseError(f"Export failed: {str(e)}", operation="export")


# Global database manager instance
_db_manager = None

def get_database_manager(db_path: str = "lego_database/LegoDatabase.db") -> DatabaseManager:
    """Get or create the global database manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager
