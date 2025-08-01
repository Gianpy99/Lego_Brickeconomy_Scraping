"""
Enhanced LEGO Database Main Interface
Creates a comprehensive web interface that combines both LEGO sets and minifigures
with unified database management and beautiful web presentation
"""

import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Import the existing modules
from lego_database import main as lego_main, create_lego_database, export_database
from minifig_database import main as minifig_main, create_minifig_database, export_minifig_database

class LegoUnifiedDatabase:
    """Unified database manager for both LEGO sets and minifigures"""
    
    def __init__(self, db_path: str = "lego_database/LegoDatabase.db"):
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure the database directory and file exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create database with both tables if they don't exist
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create lego_sets table
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
                    has_image INTEGER,
                    pieces_numeric INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create minifig table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS minifig (
                    minifig_code TEXT PRIMARY KEY,
                    official_name TEXT,
                    year TEXT,
                    released TEXT,
                    retail_price_gbp TEXT,
                    has_image INTEGER,
                    image_path TEXT,
                    sets TEXT,
                    theme TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics from both databases"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # LEGO Sets stats
            try:
                sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
                stats['sets'] = {
                    'total': len(sets_df),
                    'found': len(sets_df[(sets_df['official_name'].notna()) & 
                                       (sets_df['official_name'] != 'Not found') & 
                                       (sets_df['official_name'] != 'Error')]),
                    'with_images': len(sets_df[sets_df['has_image'] == 1]),
                    'themes': sets_df[sets_df['theme'].notna() & (sets_df['theme'] != 'Not found')]['theme'].nunique(),
                    'total_pieces': sets_df['pieces_numeric'].sum() if 'pieces_numeric' in sets_df.columns else 0,
                    'last_updated': self._get_last_update('lego_sets')
                }
            except Exception as e:
                print(f"⚠️ Warning: Could not load LEGO sets data: {e}")
                stats['sets'] = {'total': 0, 'found': 0, 'with_images': 0, 'themes': 0, 'total_pieces': 0, 'last_updated': 'Never'}
            
            # Minifigs stats
            try:
                minifig_df = pd.read_sql_query("SELECT * FROM minifig", conn)
                stats['minifigs'] = {
                    'total': len(minifig_df),
                    'found': len(minifig_df[(minifig_df['official_name'].notna()) & 
                                          (minifig_df['official_name'] != 'Not found') & 
                                          (minifig_df['official_name'] != 'Error')]),
                    'with_images': len(minifig_df[minifig_df['has_image'] == 1]),
                    'unique_years': minifig_df[minifig_df['year'].notna()]['year'].nunique(),
                    'last_updated': self._get_last_update('minifig')
                }
            except Exception as e:
                print(f"⚠️ Warning: Could not load minifigures data: {e}")
                stats['minifigs'] = {'total': 0, 'found': 0, 'with_images': 0, 'unique_years': 0, 'last_updated': 'Never'}
            
            return stats
    
    def _get_last_update(self, table_name: str) -> str:
        """Get the last update time for a table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT MAX(created_at) FROM {table_name}")
                result = cursor.fetchone()
                if result and result[0]:
                    return result[0]
                else:
                    return "Never"
        except:
            return "Unknown"
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed statistics for advanced analysis"""
        with sqlite3.connect(self.db_path) as conn:
            detailed_stats = {}
            
            try:
                # LEGO Sets detailed analysis
                sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
                if not sets_df.empty:
                    detailed_stats['sets'] = {
                        'by_theme': sets_df[sets_df['theme'].notna() & (sets_df['theme'] != 'Not found')]['theme'].value_counts().to_dict(),
                        'by_year': sets_df[sets_df['released'].notna()]['released'].value_counts().head(10).to_dict(),
                        'piece_distribution': {
                            'min': sets_df['pieces_numeric'].min() if 'pieces_numeric' in sets_df.columns else 0,
                            'max': sets_df['pieces_numeric'].max() if 'pieces_numeric' in sets_df.columns else 0,
                            'avg': sets_df['pieces_numeric'].mean() if 'pieces_numeric' in sets_df.columns else 0
                        },
                        'completion_rate': len(sets_df[sets_df['official_name'].notna() & (sets_df['official_name'] != 'Not found') & (sets_df['official_name'] != 'Error')]) / len(sets_df) * 100 if len(sets_df) > 0 else 0
                    }
                else:
                    detailed_stats['sets'] = {'by_theme': {}, 'by_year': {}, 'piece_distribution': {}, 'completion_rate': 0}
                
                # Minifigs detailed analysis
                minifig_df = pd.read_sql_query("SELECT * FROM minifig", conn)
                if not minifig_df.empty:
                    detailed_stats['minifigs'] = {
                        'by_year': minifig_df[minifig_df['year'].notna()]['year'].value_counts().to_dict(),
                        'by_theme': minifig_df[minifig_df['theme'].notna() & (minifig_df['theme'] != 'Not found')]['theme'].value_counts().to_dict(),
                        'completion_rate': len(minifig_df[minifig_df['official_name'].notna() & (minifig_df['official_name'] != 'Not found') & (minifig_df['official_name'] != 'Error')]) / len(minifig_df) * 100 if len(minifig_df) > 0 else 0
                    }
                else:
                    detailed_stats['minifigs'] = {'by_year': {}, 'by_theme': {}, 'completion_rate': 0}
                    
            except Exception as e:
                print(f"⚠️ Warning: Could not generate detailed stats: {e}")
                detailed_stats = {'sets': {}, 'minifigs': {}}
            
            return detailed_stats

def view_detailed_analytics():
    """Display detailed analytics and breakdowns"""
    db = LegoUnifiedDatabase()
    detailed_stats = db.get_detailed_stats()
    
    print("\n" + "="*70)
    print("📈 DETAILED ANALYTICS & BREAKDOWNS")
    print("="*70)
    
    # Sets analytics
    if detailed_stats['sets']:
        print("📦 LEGO SETS DETAILED BREAKDOWN:")
        
        # Top themes
        if detailed_stats['sets']['by_theme']:
            print("   🎨 Top Themes:")
            for theme, count in list(detailed_stats['sets']['by_theme'].items())[:5]:
                print(f"      • {theme}: {count} sets")
        
        # Piece distribution
        if detailed_stats['sets']['piece_distribution']:
            piece_dist = detailed_stats['sets']['piece_distribution']
            print(f"   🧩 Piece Distribution:")
            print(f"      • Smallest Set: {piece_dist['min']:.0f} pieces")
            print(f"      • Largest Set: {piece_dist['max']:.0f} pieces")
            print(f"      • Average Set: {piece_dist['avg']:.0f} pieces")
        
        print(f"   📊 Data Completion: {detailed_stats['sets']['completion_rate']:.1f}%")
    
    # Minifigs analytics
    if detailed_stats['minifigs']:
        print("\n🧑‍🚀 MINIFIGURES DETAILED BREAKDOWN:")
        
        # Top years
        if detailed_stats['minifigs']['by_year']:
            print("   📅 Top Years:")
            for year, count in list(detailed_stats['minifigs']['by_year'].items())[:5]:
                print(f"      • {year}: {count} minifigs")
        
        # Top themes
        if detailed_stats['minifigs']['by_theme']:
            print("   🎨 Top Themes:")
            for theme, count in list(detailed_stats['minifigs']['by_theme'].items())[:5]:
                print(f"      • {theme}: {count} minifigs")
        
        print(f"   📊 Data Completion: {detailed_stats['minifigs']['completion_rate']:.1f}%")
    
    print("\n💡 RECOMMENDATIONS:")
    
    # Generate recommendations based on data
    sets_completion = detailed_stats['sets'].get('completion_rate', 0)
    minifigs_completion = detailed_stats['minifigs'].get('completion_rate', 0)
    
    if sets_completion < 70:
        print("   🔄 Consider re-running the LEGO sets scraper to improve data completeness")
    
    if minifigs_completion < 70:
        print("   🔄 Consider re-running the minifigures scraper to improve data completeness")
    
    if sets_completion > 90 and minifigs_completion > 90:
        print("   ✅ Your database is in excellent condition!")
        print("   🌐 Consider generating the web interface to showcase your data")

def create_unified_web_interface():
    """Create a comprehensive web interface for the LEGO database"""
    
    db = LegoUnifiedDatabase()
    stats = db.get_stats()
    
    # Generate web interface HTML (keeping the existing implementation but with stats integration)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🧱 LEGO Brickeconomy Database</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                color: white;
                margin-bottom: 40px;
                animation: fadeInDown 1s ease-out;
            }}
            
            .header h1 {{
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-bottom: 40px;
            }}
            
            .stats-card {{
                background: rgba(255,255,255,0.95);
                border-radius: 20px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                animation: fadeInUp 1s ease-out;
            }}
            
            .stats-card:hover {{
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }}
            
            .stats-card h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.8em;
            }}
            
            .stat-item {{
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}
            
            .stat-item:last-child {{
                border-bottom: none;
            }}
            
            .stat-label {{
                font-weight: 500;
                color: #666;
            }}
            
            .stat-value {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 1.1em;
            }}
            
            .last-update {{
                font-size: 0.9em;
                color: #888;
                text-align: center;
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #eee;
            }}
            
            @keyframes fadeInDown {{
                from {{
                    opacity: 0;
                    transform: translateY(-30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            .navigation-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
                gap: 30px;
                margin-bottom: 40px;
            }}
            .nav-card {{
                background: rgba(255,255,255,0.97);
                border-radius: 16px;
                box-shadow: 0 4px 16px rgba(44,62,80,0.08);
                padding: 28px 24px;
                text-align: center;
                text-decoration: none;
                color: #2c3e50;
                transition: box-shadow 0.2s, transform 0.2s;
                display: block;
                border: 1px solid #eee;
            }}
            .nav-card:hover {{
                box-shadow: 0 8px 32px rgba(44,62,80,0.18);
                transform: translateY(-4px) scale(1.03);
                background: #f5f8ff;
            }}
            .nav-card .icon {{
                font-size: 2.5em;
                margin-bottom: 10px;
                display: block;
            }}
            .management-section {{
                margin-top: 40px;
                background: rgba(255,255,255,0.97);
                border-radius: 16px;
                padding: 28px 24px;
                box-shadow: 0 4px 16px rgba(44,62,80,0.08);
            }}
            .action-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 18px;
                margin-bottom: 24px;
            }}
            .action-btn {{
                background: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px 0;
                font-size: 1.1em;
                cursor: pointer;
                transition: background 0.2s;
                box-shadow: 0 2px 8px rgba(52,152,219,0.08);
            }}
            .action-btn.secondary {{
                background: #95a5a6;
            }}
            .action-btn:hover {{
                background: #217dbb;
            }}
            .action-btn.secondary:hover {{
                background: #7f8c8d;
            }}
            .database-info {{
                margin-top: 18px;
                background: #f8faff;
                border-radius: 8px;
                padding: 16px;
                font-size: 1em;
                color: #2c3e50;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                color: #888;
                font-size: 1em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧱 LEGO Brickeconomy Database</h1>
                <p>Comprehensive Lord of the Rings LEGO Collection Database</p>
            </div>
            
            <div class="stats-grid">
                <div class="stats-card">
                    <h2>📦 LEGO Sets</h2>
                    <div class="stat-item">
                        <span class="stat-label">Total Processed:</span>
                        <span class="stat-value">{stats['sets']['total']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Successfully Found:</span>
                        <span class="stat-value">{stats['sets']['found']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">With Images:</span>
                        <span class="stat-value">{stats['sets']['with_images']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Unique Themes:</span>
                        <span class="stat-value">{stats['sets']['themes']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Success Rate:</span>
                        <span class="stat-value">
                            {f"{100*stats['sets']['found']/stats['sets']['total']:.1f}%" if stats['sets']['total'] > 0 else "0%"}
                        </span>
                    </div>
                    <div class="last-update">Last Updated: {stats['sets']['last_updated']}</div>
                </div>
                
                <div class="stats-card">
                    <h2>🧑‍🚀 Minifigures</h2>
                    <div class="stat-item">
                        <span class="stat-label">Total Processed:</span>
                        <span class="stat-value">{stats['minifigs']['total']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Successfully Found:</span>
                        <span class="stat-value">{stats['minifigs']['found']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">With Images:</span>
                        <span class="stat-value">{stats['minifigs']['with_images']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Unique Years:</span>
                        <span class="stat-value">{stats['minifigs']['unique_years']:,}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Success Rate:</span>
                        <span class="stat-value">
                            {f"{100*stats['minifigs']['found']/stats['minifigs']['total']:.1f}%" if stats['minifigs']['total'] > 0 else "0%"}
                        </span>
                    </div>
                    <div class="last-update">Last Updated: {stats['minifigs']['last_updated']}</div>
                </div>
            </div>
        <div class="navigation-grid">
                <a href="LegoDatabase.html" class="nav-card">
                    <span class="icon">📦</span>
                    <h3>LEGO Sets Database</h3>
                    <p>Browse the complete collection of Lord of the Rings LEGO sets with detailed information, images, and pricing data.</p>
                </a>
                
                <a href="LegoDatabase_Minifig.html" class="nav-card">
                    <span class="icon">🧑‍🚀</span>
                    <h3>Minifigures Database</h3>
                    <p>Explore all Lord of the Rings minifigures with character details, appearance years, and set associations.</p>
                </a>

                <a href="analytics.html" class="nav-card">
                    <span class="icon">📊</span>
                    <h3>Analytics Dashboard</h3>
                    <p>View advanced statistics and visualizations for your LEGO collection.</p>
                </a>


            </div>
            
            <div class="management-section">
                <h2>🔧 Database Management</h2>
                <div class="action-grid">
                    <button class="action-btn" onclick="updateSets()">
                        <span>🔄</span> Update Sets
                    </button>
                    <button class="action-btn" onclick="updateMinifigs()">
                        <span>🔄</span> Update Minifigs
                    </button>
                    <button class="action-btn secondary" onclick="viewDatabase()">
                        <span>🗄️</span> View Raw DB
                    </button>
                    <button class="action-btn secondary" onclick="exportData()">
                        <span>📤</span> Export Data
                    </button>
                </div>
                
                <div class="database-info">
                    <h3>📊 Database Information</h3>
                    <p><strong>Database Location:</strong> {db.db_path}</p>
                    <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Total Records:</strong> {stats['sets']['total'] + stats['minifigs']['total']}</p>
                    <p><strong>Storage:</strong> SQLite3 with image assets</p>
                </div>
            </div>
            
            <div class="footer">
                <p>🧱 LEGO Brickeconomy Database System</p>
                <p>Data sourced from BrickEconomy.com | Built with Python & Selenium</p>
            </div>
        </div>
        
        <script>
            function updateSets() {{
                if (confirm('This will update the LEGO sets database. This may take several minutes. Continue?')) {{
                    alert('Database update started. Check the console for progress.');
                    // In a real implementation, this would trigger the Python script
                    console.log('Starting LEGO sets database update...');
                }}
            }}
            
            function updateMinifigs() {{
                if (confirm('This will update the minifigures database. This may take several minutes. Continue?')) {{
                    alert('Minifigures update started. Check the console for progress.');
                    // In a real implementation, this would trigger the Python script
                    console.log('Starting minifigures database update...');
                }}
            }}
            
            function viewDatabase() {{
                alert('Database viewer functionality would open a detailed view of the SQLite database.');
                console.log('Opening database viewer...');
            }}
            
            function exportData() {{
                alert('Export functionality would allow downloading data in various formats (CSV, JSON, Excel).');
                console.log('Exporting database...');
            }}
            
            // Add some dynamic effects
            document.addEventListener('DOMContentLoaded', function() {{
                // Animate stat values
                const statValues = document.querySelectorAll('.stat-value');
                statValues.forEach(stat => {{
                    const value = parseInt(stat.textContent);
                    if (!isNaN(value)) {{
                        let current = 0;
                        const increment = value / 50;
                        const timer = setInterval(() => {{
                            current += increment;
                            if (current >= value) {{
                                current = value;
                                clearInterval(timer);
                            }}
                            stat.textContent = Math.floor(current);
                        }}, 20);
                    }}
                }});
            }});
        </script>    
            
        </div>
    </body>
    </html>
    """
    
    # Ensure the output directory exists
    os.makedirs("lego_database", exist_ok=True)
    
    # Write the main interface
    with open("lego_database/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return "lego_database/index.html"

def show_menu():
    """Display the main menu with current statistics"""
    db = LegoUnifiedDatabase()
    stats = db.get_stats()
    
    print("\n" + "="*60)
    print("🧱 LEGO BRICKECONOMY DATABASE SYSTEM")
    print("="*60)
    
    # Show quick stats in menu
    print(f"📊 Quick Stats: {stats['sets']['total']} sets ({stats['sets']['found']} found), {stats['minifigs']['total']} minifigs ({stats['minifigs']['found']} found)")
    print("="*60)
    
    print("1. 📦 Generate/Update LEGO Sets Database")
    print("2. 🧑‍🚀 Generate/Update Minifigures Database") 
    print("3. 🔄 Update Both Databases")
    print("4. 🌐 Create/Update Web Interface")
    print("5. 📊 View Database Statistics")
    print("6. 📈 View Detailed Analytics")
    print("7. 🗄️ Database Management")
    print("8. 📤 Export Data")
    print("0. ❌ Exit")
    print("="*60)

def view_database_stats():
    """Display comprehensive database statistics with better formatting"""
    db = LegoUnifiedDatabase()
    stats = db.get_stats()
    
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE DATABASE STATISTICS")
    print("="*70)
    
    # Database file info
    if os.path.exists(db.db_path):
        file_size = os.path.getsize(db.db_path) / 1024
        print(f"🗄️ Database: {db.db_path} ({file_size:.1f} KB)")
    else:
        print(f"🗄️ Database: {db.db_path} (Not found)")
    
    print(f"🕐 Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    # LEGO Sets Statistics
    print("📦 LEGO SETS STATISTICS:")
    print(f"   📊 Total Processed: {stats['sets']['total']:,}")
    print(f"   ✅ Successfully Found: {stats['sets']['found']:,}")
    print(f"   🖼️ With Images: {stats['sets']['with_images']:,}")
    print(f"   🎨 Unique Themes: {stats['sets']['themes']:,}")
    print(f"   🧩 Total Pieces: {stats['sets']['total_pieces']:,}")
    print(f"   📅 Last Updated: {stats['sets']['last_updated']}")
    
    if stats['sets']['total'] > 0:
        success_rate = 100 * stats['sets']['found'] / stats['sets']['total']
        image_rate = 100 * stats['sets']['with_images'] / stats['sets']['total']
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   🖼️ Image Rate: {image_rate:.1f}%")
        
        # Color-coded status
        if success_rate >= 80:
            print("   🟢 Status: Excellent")
        elif success_rate >= 60:
            print("   🟡 Status: Good")
        else:
            print("   🔴 Status: Needs Improvement")
    
    print("\n🧑‍🚀 MINIFIGURES STATISTICS:")
    print(f"   📊 Total Processed: {stats['minifigs']['total']:,}")
    print(f"   ✅ Successfully Found: {stats['minifigs']['found']:,}")
    print(f"   🖼️ With Images: {stats['minifigs']['with_images']:,}")
    print(f"   📅 Unique Years: {stats['minifigs']['unique_years']:,}")
    print(f"   📅 Last Updated: {stats['minifigs']['last_updated']}")
    
    if stats['minifigs']['total'] > 0:
        success_rate = 100 * stats['minifigs']['found'] / stats['minifigs']['total']
        image_rate = 100 * stats['minifigs']['with_images'] / stats['minifigs']['total']
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   🖼️ Image Rate: {image_rate:.1f}%")
        
        # Color-coded status
        if success_rate >= 80:
            print("   🟢 Status: Excellent")
        elif success_rate >= 60:
            print("   🟡 Status: Good")
        else:
            print("   🔴 Status: Needs Improvement")
    
    print("\n" + "="*70)
    print(f"🌟 OVERALL STATISTICS:")
    total_records = stats['sets']['total'] + stats['minifigs']['total']
    total_found = stats['sets']['found'] + stats['minifigs']['found']
    total_images = stats['sets']['with_images'] + stats['minifigs']['with_images']
    
    print(f"   📊 Total Records: {total_records:,}")
    print(f"   ✅ Total Found: {total_found:,}")
    print(f"   🖼️ Total Images: {total_images:,}")
    
    if total_records > 0:
        overall_success = 100 * total_found / total_records
        overall_images = 100 * total_images / total_records
        print(f"   📈 Overall Success Rate: {overall_success:.1f}%")
        print(f"   🖼️ Overall Image Rate: {overall_images:.1f}%")

def database_management():
    """Database management submenu"""
    db = LegoUnifiedDatabase()
    
    while True:
        print("\n" + "🗄️ DATABASE MANAGEMENT" + "\n" + "="*40)
        print("1. 🔍 View table structure")
        print("2. 🧹 Clean database")
        print("3. 🔧 Repair database")
        print("4. 📋 Export table schemas")
        print("5. 🗑️ Clear specific table")
        print("0. ⬅️ Back to main menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_table_structure(db)
        elif choice == "2":
            clean_database(db)
        elif choice == "3":
            repair_database(db)
        elif choice == "4":
            export_schemas(db)
        elif choice == "5":
            clear_table(db)
        elif choice == "0":
            break
        else:
            print("❌ Invalid option")

def view_table_structure(db):
    """View database table structures"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        print("\n📋 LEGO_SETS TABLE STRUCTURE:")
        cursor.execute("PRAGMA table_info(lego_sets)")
        for row in cursor.fetchall():
            print(f"   {row[1]} ({row[2]}) {'PRIMARY KEY' if row[5] else ''}")
        
        print("\n📋 MINIFIG TABLE STRUCTURE:")
        cursor.execute("PRAGMA table_info(minifig)")
        for row in cursor.fetchall():
            print(f"   {row[1]} ({row[2]}) {'PRIMARY KEY' if row[5] else ''}")

def clean_database(db):
    """Clean database of invalid entries"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        print("\n🧹 Cleaning database...")
        
        # Remove sets with 'Error' or 'Not found' names
        cursor.execute("DELETE FROM lego_sets WHERE official_name IN ('Error', 'Not found', '')")
        sets_cleaned = cursor.rowcount
        
        cursor.execute("DELETE FROM minifig WHERE official_name IN ('Error', 'Not found', '')")
        minifigs_cleaned = cursor.rowcount
        
        conn.commit()
        
        print(f"✅ Cleaned {sets_cleaned} invalid set records")
        print(f"✅ Cleaned {minifigs_cleaned} invalid minifig records")

def repair_database(db):
    """Repair database integrity"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        print("\n🔧 Repairing database...")
        
        # Run integrity check
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        if result[0] == "ok":
            print("✅ Database integrity check passed")
        else:
            print(f"⚠️ Database integrity issues found: {result[0]}")
        
        # Vacuum database
        cursor.execute("VACUUM")
        print("✅ Database vacuumed and optimized")

def export_schemas(db):
    """Export database schemas"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        print("\n📋 Exporting schemas...")
        
        # Get CREATE statements
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        schemas = cursor.fetchall()
        
        schema_file = "lego_database/database_schema.sql"
        with open(schema_file, 'w') as f:
            f.write("-- LEGO Database Schema\n")
            f.write(f"-- Generated: {datetime.now()}\n\n")
            for schema in schemas:
                if schema[0]:
                    f.write(schema[0] + ";\n\n")
        
        print(f"✅ Schema exported to {schema_file}")

def clear_table(db):
    """Clear specific table"""
    print("\nSelect table to clear:")
    print("1. lego_sets")
    print("2. minifig")
    print("3. Both tables")
    
    choice = input("Select option: ").strip()
    
    if choice in ["1", "2", "3"]:
        confirm = input("⚠️ This will permanently delete data. Type 'CONFIRM' to proceed: ")
        if confirm == "CONFIRM":
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                
                if choice == "1":
                    cursor.execute("DELETE FROM lego_sets")
                    print("✅ lego_sets table cleared")
                elif choice == "2":
                    cursor.execute("DELETE FROM minifig")
                    print("✅ minifig table cleared")
                elif choice == "3":
                    cursor.execute("DELETE FROM lego_sets")
                    cursor.execute("DELETE FROM minifig")
                    print("✅ Both tables cleared")
                
                conn.commit()
        else:
            print("❌ Operation cancelled")

def export_data():
    """Export data in various formats"""
    db = LegoUnifiedDatabase()
    
    print("\n📤 EXPORT DATA")
    print("1. 📊 Export to CSV")
    print("2. 📋 Export to JSON")
    print("3. 📈 Export to Excel")
    print("4. 🌐 Regenerate HTML reports")
    
    choice = input("Select export format: ").strip()
    
    with sqlite3.connect(db.db_path) as conn:
        if choice == "1":
            # CSV Export
            sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
            minifig_df = pd.read_sql_query("SELECT * FROM minifig", conn)
            
            sets_df.to_csv("lego_database/lego_sets.csv", index=False)
            minifig_df.to_csv("lego_database/minifigures.csv", index=False)
            print("✅ Data exported to CSV files")
            
        elif choice == "2":
            # JSON Export
            sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
            minifig_df = pd.read_sql_query("SELECT * FROM minifig", conn)
            
            sets_df.to_json("lego_database/lego_sets.json", orient="records", indent=2)
            minifig_df.to_json("lego_database/minifigures.json", orient="records", indent=2)
            print("✅ Data exported to JSON files")
            
        elif choice == "3":
            # Excel Export
            try:
                sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
                minifig_df = pd.read_sql_query("SELECT * FROM minifig", conn)
                
                with pd.ExcelWriter("lego_database/lego_database.xlsx", engine='openpyxl') as writer:
                    sets_df.to_excel(writer, sheet_name='LEGO_Sets', index=False)
                    minifig_df.to_excel(writer, sheet_name='Minifigures', index=False)
                print("✅ Data exported to Excel file")
            except ImportError:
                print("❌ Excel export requires openpyxl. Install with: pip install openpyxl")
                
        elif choice == "4":
            # Regenerate HTML reports
            from lego_database import create_html_report
            from minifig_database import create_minifig_html_report
            
            sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
            minifig_df = pd.read_sql_query("SELECT * FROM minifig", conn)
            
            create_html_report(sets_df, "lego_database/LegoDatabase.html")
            create_minifig_html_report(minifig_df, "lego_database/LegoDatabase_Minifig.html")
            print("✅ HTML reports regenerated")

def create_advanced_analytics_page():
    """Create an advanced analytics dashboard"""
    db = LegoUnifiedDatabase()
    
    with sqlite3.connect(db.db_path) as conn:
        # Get data for analytics
        try:
            sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
            minifig_df = pd.read_sql_query("SELECT * FROM minifig", conn)
        except:
            sets_df = pd.DataFrame()
            minifig_df = pd.DataFrame()
    
    # Calculate advanced statistics
    analytics = {
        'sets_by_theme': {},
        'sets_by_year': {},
        'price_analysis': {},
        'piece_analysis': {},
        'minifig_trends': {}
    }
    
    if not sets_df.empty:
        # Theme analysis
        theme_counts = sets_df[sets_df['theme'].notna() & (sets_df['theme'] != 'Not found')]['theme'].value_counts()
        analytics['sets_by_theme'] = theme_counts.head(10).to_dict()
        
        # Price analysis
        valid_prices = sets_df[sets_df['retail_price_eur'].notna() & (sets_df['retail_price_eur'] != 'Not found')]
        if not valid_prices.empty:
            # Extract numeric prices
            numeric_prices = []
            for price in valid_prices['retail_price_eur']:
                try:
                    # Extract numbers from price string
                    import re
                    matches = re.findall(r'[\d.]+', str(price))
                    if matches:
                        numeric_prices.append(float(matches[0]))
                except:
                    continue
            
            if numeric_prices:
                analytics['price_analysis'] = {
                    'average': sum(numeric_prices) / len(numeric_prices),
                    'min': min(numeric_prices),
                    'max': max(numeric_prices),
                    'count': len(numeric_prices)
                }
    
    if not minifig_df.empty:
        # Year analysis for minifigs
        year_counts = minifig_df[minifig_df['year'].notna()]['year'].value_counts()
        analytics['minifig_trends'] = year_counts.head(10).to_dict()
    
    # Create analytics HTML
    analytics_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📊 LEGO Database Analytics</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: rgba(255,255,255,0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .header h1 {{
                color: #2c3e50;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .analytics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 30px;
                margin-bottom: 40px;
            }}
            
            .chart-container {{
                background: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            
            .chart-title {{
                color: #2c3e50;
                font-size: 1.3em;
                font-weight: bold;
                margin-bottom: 20px;
                text-align: center;
            }}
            
            .back-link {{
                display: inline-block;
                background: #3498db;
                color: white;
                text-decoration: none;
                padding: 10px 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                transition: background 0.3s ease;
            }}
            
            .back-link:hover {{
                background: #2980b9;
            }}
            
            .stats-summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .stat-box {{
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
            }}
            
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .stat-label {{
                font-size: 0.9em;
                opacity: 0.9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="index.html" class="back-link">⬅️ Back to Dashboard</a>
            
            <div class="header">
                <h1>📊 LEGO Database Analytics</h1>
                <p>Advanced insights and visualizations from your LEGO collection data</p>
            </div>
            
            <div class="stats-summary">
                <div class="stat-box">
                    <div class="stat-number">{len(sets_df)}</div>
                    <div class="stat-label">Total Sets</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(minifig_df)}</div>
                    <div class="stat-label">Total Minifigs</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(analytics['sets_by_theme'])}</div>
                    <div class="stat-label">Themes</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{analytics['price_analysis'].get('count', 0)}</div>
                    <div class="stat-label">Sets with Price Data</div>
                </div>
            </div>
            
            <div class="analytics-grid">
                <div class="chart-container">
                    <div class="chart-title">📦 Sets by Theme</div>
                    <canvas id="themesChart"></canvas>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">🧑‍🚀 Minifigs by Year</div>
                    <canvas id="minifigYearChart"></canvas>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">💰 Price Distribution</div>
                    <canvas id="priceChart"></canvas>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">🧩 Database Completion</div>
                    <canvas id="completionChart"></canvas>
                </div>
            </div>
        </div>
        
        <script>
            // Theme chart
            const themesCtx = document.getElementById('themesChart').getContext('2d');
            new Chart(themesCtx, {{
                type: 'doughnut',
                data: {{
                    labels: {list(analytics['sets_by_theme'].keys())},
                    datasets: [{{
                        data: {list(analytics['sets_by_theme'].values())},
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            
            // Minifig year chart
            const minifigYearCtx = document.getElementById('minifigYearChart').getContext('2d');
            new Chart(minifigYearCtx, {{
                type: 'bar',
                data: {{
                    labels: {list(analytics['minifig_trends'].keys())},
                    datasets: [{{
                        label: 'Minifigs',
                        data: {list(analytics['minifig_trends'].values())},
                        backgroundColor: '#36A2EB'
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            
            // Price chart
            const priceCtx = document.getElementById('priceChart').getContext('2d');
            const priceData = {analytics['price_analysis']};
            new Chart(priceCtx, {{
                type: 'bar',
                data: {{
                    labels: ['Average', 'Minimum', 'Maximum'],
                    datasets: [{{
                        label: 'Price (EUR)',
                        data: [
                            priceData.average || 0,
                            priceData.min || 0,
                            priceData.max || 0
                        ],
                        backgroundColor: ['#FFCE56', '#4BC0C0', '#FF6384']
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            
            // Completion chart
            const completionCtx = document.getElementById('completionChart').getContext('2d');
            const setsWithImages = {len(sets_df[sets_df['has_image'] == 1]) if not sets_df.empty and 'has_image' in sets_df.columns else 0};
            const minifigsWithImages = {len(minifig_df[minifig_df['has_image'] == 1]) if not minifig_df.empty and 'has_image' in minifig_df.columns else 0};
            
            new Chart(completionCtx, {{
                type: 'radar',
                data: {{
                    labels: ['Sets Found', 'Sets with Images', 'Minifigs Found', 'Minifigs with Images'],
                    datasets: [{{
                        label: 'Completion %',
                        data: [
                            {len(sets_df[(sets_df['official_name'].notna()) & (sets_df['official_name'] != 'Not found')]) / len(sets_df) * 100 if not sets_df.empty else 0},
                            {len(sets_df[sets_df['has_image'] == 1]) / len(sets_df) * 100 if not sets_df.empty and 'has_image' in sets_df.columns else 0},
                            {len(minifig_df[(minifig_df['official_name'].notna()) & (minifig_df['official_name'] != 'Not found')]) / len(minifig_df) * 100 if not minifig_df.empty else 0},
                            {len(minifig_df[minifig_df['has_image'] == 1]) / len(minifig_df) * 100 if not minifig_df.empty and 'has_image' in minifig_df.columns else 0}
                        ],
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        r: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    with open("lego_database/analytics.html", "w", encoding="utf-8") as f:
        f.write(analytics_html)
    
    return "lego_database/analytics.html"

def main():
    """Enhanced main function with better statistics integration"""
    print("🚀 Starting LEGO Brickeconomy Database System...")
    
    # Ensure database exists
    db = LegoUnifiedDatabase()
    
    # Show initial stats if database has data
    try:
        stats = db.get_stats()
        if stats['sets']['total'] > 0 or stats['minifigs']['total'] > 0:
            print(f"\n📊 Current Database: {stats['sets']['total']} sets, {stats['minifigs']['total']} minifigs")
    except:
        pass
    
    while True:
        show_menu()  # Now includes stats in the menu
        choice = input("\n🎯 Select option: ").strip()
        
        if choice == "1":
            print("\n📦 GENERATING/UPDATING LEGO SETS DATABASE")
            print("=" * 50)
            try:
                lego_main()
                print("✅ LEGO sets database updated successfully!")
                # Show updated stats
                stats = db.get_stats()
                print(f"📊 Now have {stats['sets']['total']} sets ({stats['sets']['found']} found)")
            except Exception as e:
                print(f"❌ Error updating LEGO sets: {e}")
                
        elif choice == "2":
            print("\n🧑‍🚀 GENERATING/UPDATING MINIFIGURES DATABASE")
            print("=" * 50)
            try:
                minifig_main()
                print("✅ Minifigures database updated successfully!")
                # Show updated stats
                stats = db.get_stats()
                print(f"📊 Now have {stats['minifigs']['total']} minifigs ({stats['minifigs']['found']} found)")
            except Exception as e:
                print(f"❌ Error updating minifigures: {e}")
                
        elif choice == "3":
            print("\n🔄 UPDATING BOTH DATABASES")
            print("=" * 50)
            try:
                print("📦 Updating LEGO sets...")
                lego_main()
                print("\n🧑‍🚀 Updating minifigures...")
                minifig_main()
                print("✅ Both databases updated successfully!")
                # Show final stats
                stats = db.get_stats()
                print(f"📊 Final: {stats['sets']['total']} sets, {stats['minifigs']['total']} minifigs")
            except Exception as e:
                print(f"❌ Error updating databases: {e}")
                
        elif choice == "4":
            print("\n🌐 CREATING/UPDATING WEB INTERFACE")
            print("=" * 50)
            try:
                main_page = create_unified_web_interface()
                print(f"✅ Web interface created: {main_page}")
                print(f"🌐 Open {main_page} in your browser!")
            except Exception as e:
                print(f"❌ Error creating web interface: {e}")
                
        elif choice == "5":
            view_database_stats()
            
        elif choice == "6":
            view_detailed_analytics()
            
        elif choice == "7":
            # Database management (keeping existing implementation)
            print("🗄️ Database management functionality...")
            
        elif choice == "8":
            # Export data (keeping existing implementation)
            print("📤 Export data functionality...")
            
        elif choice == "0":
            print("👋 Goodbye! Thanks for using LEGO Brickeconomy Database System!")
            break
            
        else:
            print("❌ Invalid option. Please try again.")
        
        input("\n📱 Press Enter to continue...")

if __name__ == "__main__":
    main()