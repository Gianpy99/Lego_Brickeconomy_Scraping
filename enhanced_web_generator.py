"""
Enhanced Web Interface Generator
Creates responsive, searchable web interfaces with advanced features
"""

import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from logging_system import get_logger
from database_manager import get_database_manager

logger = get_logger(__name__)


class ResponsiveWebGenerator:
    """Generates responsive web interfaces with modern features"""
    
    def __init__(self, db_path: str = "lego_database/LegoDatabase.db", output_dir: str = "lego_database"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.db_manager = get_database_manager(db_path)
        
    def generate_enhanced_main_page(self) -> str:
        """Generate enhanced main page with search and filters"""
        stats = self.db_manager.get_comprehensive_stats()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧱 LEGO Brickeconomy Database</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Enhanced responsive styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #3498db;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --text-color: #2c3e50;
            --light-bg: #f8fafc;
            --card-shadow: 0 4px 16px rgba(44, 62, 80, 0.08);
            --border-radius: 12px;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            min-height: 100vh;
            color: var(--text-color);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Header styles */
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            animation: fadeInDown 0.8s ease-out;
        }}
        
        .header h1 {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: clamp(1rem, 3vw, 1.3rem);
            opacity: 0.9;
        }}
        
        /* Search and filter section */
        .search-section {{
            background: rgba(255,255,255,0.95);
            border-radius: var(--border-radius);
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: var(--card-shadow);
            animation: fadeInUp 0.8s ease-out;
        }}
        
        .search-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            gap: 10px;
        }}
        
        .search-controls {{
            display: grid;
            grid-template-columns: 1fr auto auto auto;
            gap: 15px;
            align-items: center;
        }}
        
        .search-input {{
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
            background: white;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }}
        
        .filter-select {{
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            background: white;
            font-size: 14px;
            cursor: pointer;
        }}
        
        .btn {{
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        
        .btn-primary {{
            background: var(--accent-color);
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #2980b9;
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: var(--light-bg);
            color: var(--text-color);
            border: 2px solid #e1e8ed;
        }}
        
        .btn-secondary:hover {{
            background: #e1e8ed;
        }}
        
        /* Stats grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .stats-card {{
            background: rgba(255,255,255,0.95);
            border-radius: var(--border-radius);
            padding: 30px;
            text-align: center;
            box-shadow: var(--card-shadow);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: fadeInUp 1s ease-out;
        }}
        
        .stats-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .stats-card h2 {{
            color: var(--text-color);
            margin-bottom: 20px;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        
        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin: 12px 0;
            padding: 8px 0;
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
            color: var(--text-color);
            font-size: 1.1em;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e1e8ed;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--success-color), var(--accent-color));
            transition: width 1s ease-out;
        }}
        
        /* Navigation grid */
        .navigation-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .nav-card {{
            background: rgba(255,255,255,0.97);
            border-radius: var(--border-radius);
            box-shadow: var(--card-shadow);
            padding: 28px 24px;
            text-align: center;
            text-decoration: none;
            color: var(--text-color);
            transition: all 0.3s ease;
            display: block;
            border: 1px solid #eee;
        }}
        
        .nav-card:hover {{
            box-shadow: 0 8px 32px rgba(44,62,80,0.18);
            transform: translateY(-4px);
            background: var(--light-bg);
        }}
        
        .nav-card .icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
            display: block;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .nav-card h3 {{
            margin-bottom: 10px;
            font-size: 1.3rem;
        }}
        
        .nav-card p {{
            color: #666;
            font-size: 0.95rem;
        }}
        
        /* Quick actions */
        .quick-actions {{
            margin-top: 40px;
            background: rgba(255,255,255,0.97);
            border-radius: var(--border-radius);
            padding: 28px 24px;
            box-shadow: var(--card-shadow);
        }}
        
        .action-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
            margin-top: 20px;
        }}
        
        .action-btn {{
            background: var(--accent-color);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 16px 0;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(52,152,219,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        
        .action-btn:hover {{
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(52,152,219,0.3);
        }}
        
        .action-btn.secondary {{
            background: var(--light-bg);
            color: var(--text-color);
            border: 2px solid #e1e8ed;
        }}
        
        .action-btn.secondary:hover {{
            background: #e1e8ed;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
        }}
        
        /* Animations */
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
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .search-controls {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .navigation-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .action-grid {{
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            
            .nav-card {{
                padding: 20px;
            }}
            
            .stats-card {{
                padding: 20px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .search-section {{
                padding: 16px;
            }}
            
            .nav-card .icon {{
                font-size: 2rem;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
        
        /* Loading states */
        .loading {{
            opacity: 0.6;
            pointer-events: none;
        }}
        
        .skeleton {{
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
        }}
        
        @keyframes skeleton-loading {{
            0% {{
                background-position: 200% 0;
            }}
            100% {{
                background-position: -200% 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-cubes"></i> LEGO Brickeconomy Database</h1>
            <p>Comprehensive Lord of the Rings LEGO Collection Database</p>
        </div>
        
        <!-- Enhanced Search Section -->
        <div class="search-section">
            <div class="search-header">
                <i class="fas fa-search" style="color: var(--accent-color); font-size: 1.5rem;"></i>
                <h2 style="margin: 0;">Search & Filter</h2>
            </div>
            <div class="search-controls">
                <input type="text" id="globalSearch" class="search-input" placeholder="🔍 Search sets, minifigs, themes...">
                <select id="categoryFilter" class="filter-select">
                    <option value="">All Categories</option>
                    <option value="sets">Sets Only</option>
                    <option value="minifigs">Minifigs Only</option>
                </select>
                <select id="themeFilter" class="filter-select">
                    <option value="">All Themes</option>
                    <option value="The Hobbit">The Hobbit</option>
                    <option value="The Lord of the Rings">Lord of the Rings</option>
                    <option value="Dimensions">Dimensions</option>
                </select>
                <button class="btn btn-secondary" onclick="clearAllFilters()">
                    <i class="fas fa-times"></i> Clear
                </button>
            </div>
        </div>
        
        <!-- Enhanced Stats Grid -->
        <div class="stats-grid">
            <div class="stats-card">
                <h2><i class="fas fa-boxes"></i> LEGO Sets</h2>
                <div class="stat-item">
                    <span class="stat-label">Total Processed:</span>
                    <span class="stat-value">{stats.total_sets:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Successfully Found:</span>
                    <span class="stat-value">{stats.found_sets:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">With Images:</span>
                    <span class="stat-value">{stats.sets_with_images:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Unique Themes:</span>
                    <span class="stat-value">{stats.unique_themes:,}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(stats.found_sets/stats.total_sets*100) if stats.total_sets > 0 else 0:.1f}%"></div>
                </div>
                <div style="font-size: 0.9rem; color: #666; margin-top: 10px;">
                    Success Rate: {(stats.found_sets/stats.total_sets*100) if stats.total_sets > 0 else 0:.1f}%
                </div>
            </div>
            
            <div class="stats-card">
                <h2><i class="fas fa-users"></i> Minifigures</h2>
                <div class="stat-item">
                    <span class="stat-label">Total Processed:</span>
                    <span class="stat-value">{stats.total_minifigs:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Successfully Found:</span>
                    <span class="stat-value">{stats.found_minifigs:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">With Images:</span>
                    <span class="stat-value">{stats.minifigs_with_images:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Unique Years:</span>
                    <span class="stat-value">{stats.unique_years:,}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(stats.found_minifigs/stats.total_minifigs*100) if stats.total_minifigs > 0 else 0:.1f}%"></div>
                </div>
                <div style="font-size: 0.9rem; color: #666; margin-top: 10px;">
                    Success Rate: {(stats.found_minifigs/stats.total_minifigs*100) if stats.total_minifigs > 0 else 0:.1f}%
                </div>
            </div>
            
            <div class="stats-card">
                <h2><i class="fas fa-database"></i> Database Info</h2>
                <div class="stat-item">
                    <span class="stat-label">Total Records:</span>
                    <span class="stat-value">{stats.total_sets + stats.total_minifigs:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Database Size:</span>
                    <span class="stat-value">{stats.database_size_mb:.1f} MB</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Last Updated:</span>
                    <span class="stat-value" style="font-size: 0.9rem;">{stats.last_updated}</span>
                </div>
            </div>
        </div>
        
        <!-- Enhanced Navigation -->
        <div class="navigation-grid">
            <a href="sets.html" class="nav-card">
                <i class="fas fa-boxes icon"></i>
                <h3>LEGO Sets Database</h3>
                <p>Browse the complete collection of Lord of the Rings LEGO sets with detailed information, advanced search, and pricing data.</p>
            </a>
            
            <a href="minifigs.html" class="nav-card">
                <i class="fas fa-users icon"></i>
                <h3>Minifigures Database</h3>
                <p>Explore all Lord of the Rings minifigures with character details, appearance years, and interactive filtering.</p>
            </a>
            
            <a href="analytics.html" class="nav-card">
                <i class="fas fa-chart-line icon"></i>
                <h3>Analytics Dashboard</h3>
                <p>View advanced statistics, trends, and interactive visualizations for your LEGO collection data.</p>
            </a>
        </div>
        
        <!-- Quick Actions -->
        <div class="quick-actions">
            <h2><i class="fas fa-bolt" style="color: var(--accent-color);"></i> Quick Actions</h2>
            <div class="action-grid">
                <button class="action-btn" onclick="refreshData()">
                    <i class="fas fa-sync-alt"></i> Refresh Data
                </button>
                <button class="action-btn" onclick="exportData()">
                    <i class="fas fa-download"></i> Export Data
                </button>
                <button class="action-btn secondary" onclick="optimizeDatabase()">
                    <i class="fas fa-cogs"></i> Optimize DB
                </button>
                <button class="action-btn secondary" onclick="viewLogs()">
                    <i class="fas fa-file-alt"></i> View Logs
                </button>
            </div>
        </div>
        
        <div class="footer">
            <p><i class="fas fa-cubes"></i> LEGO Brickeconomy Database System</p>
            <p>Data sourced from BrickEconomy.com | Enhanced with modern web technologies</p>
            <p style="margin-top: 10px; font-size: 0.8rem;">
                <i class="fas fa-clock"></i> Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
    </div>
    
    <script>
        // Enhanced JavaScript functionality
        let searchTimeout;
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {{
            initializeSearch();
            animateCounters();
            setupProgressBars();
        }});
        
        function initializeSearch() {{
            const searchInput = document.getElementById('globalSearch');
            const categoryFilter = document.getElementById('categoryFilter');
            const themeFilter = document.getElementById('themeFilter');
            
            // Debounced search
            searchInput.addEventListener('input', function() {{
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {{
                    performSearch();
                }}, 300);
            }});
            
            // Filter change handlers
            categoryFilter.addEventListener('change', performSearch);
            themeFilter.addEventListener('change', performSearch);
        }}
        
        function performSearch() {{
            const searchTerm = document.getElementById('globalSearch').value.toLowerCase();
            const category = document.getElementById('categoryFilter').value;
            const theme = document.getElementById('themeFilter').value;
            
            // Show loading state
            document.querySelector('.navigation-grid').classList.add('loading');
            
            // Simulate search (in real implementation, this would query the database)
            setTimeout(() => {{
                console.log('Searching for:', {{ searchTerm, category, theme }});
                document.querySelector('.navigation-grid').classList.remove('loading');
                
                // Update results count or show filtered content
                updateSearchResults(searchTerm, category, theme);
            }}, 500);
        }}
        
        function updateSearchResults(searchTerm, category, theme) {{
            // Placeholder for search results update
            console.log('Search completed:', {{ searchTerm, category, theme }});
        }}
        
        function clearAllFilters() {{
            document.getElementById('globalSearch').value = '';
            document.getElementById('categoryFilter').value = '';
            document.getElementById('themeFilter').value = '';
            performSearch();
        }}
        
        function animateCounters() {{
            const statValues = document.querySelectorAll('.stat-value');
            statValues.forEach(stat => {{
                const finalValue = parseInt(stat.textContent.replace(/,/g, ''));
                if (!isNaN(finalValue) && finalValue > 0) {{
                    let currentValue = 0;
                    const increment = finalValue / 60; // 60 frames for smooth animation
                    const timer = setInterval(() => {{
                        currentValue += increment;
                        if (currentValue >= finalValue) {{
                            currentValue = finalValue;
                            clearInterval(timer);
                        }}
                        stat.textContent = Math.floor(currentValue).toLocaleString();
                    }}, 16); // ~60fps
                }}
            }});
        }}
        
        function setupProgressBars() {{
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {{
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {{
                    bar.style.width = width;
                }}, 500);
            }});
        }}
        
        // Quick action functions
        function refreshData() {{
            showNotification('🔄 Data refresh started...', 'info');
            // Implement data refresh logic
        }}
        
        function exportData() {{
            showNotification('📁 Preparing data export...', 'info');
            // Implement export logic
        }}
        
        function optimizeDatabase() {{
            showNotification('⚡ Database optimization started...', 'info');
            // Implement optimization logic
        }}
        
        function viewLogs() {{
            window.open('logs.html', '_blank');
        }}
        
        function showNotification(message, type = 'info') {{
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${{type === 'info' ? 'var(--accent-color)' : 'var(--success-color)'}};
                color: white;
                padding: 16px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.2);
                z-index: 1000;
                animation: slideInRight 0.3s ease-out;
                max-width: 300px;
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                notification.style.animation = 'slideOutRight 0.3s ease-out';
                setTimeout(() => notification.remove(), 300);
            }}, 3000);
        }}
        
        // Add CSS for notification animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {{
                from {{ transform: translateX(100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            @keyframes slideOutRight {{
                from {{ transform: translateX(0); opacity: 1; }}
                to {{ transform: translateX(100%); opacity: 0; }}
            }}
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>
        """
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Enhanced main page generated: {output_file}")
        return str(output_file)
    
    def generate_sets_page_with_search(self) -> str:
        """Generate enhanced sets page with search and filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                sets_df = pd.read_sql_query("SELECT * FROM lego_sets ORDER BY lego_code", conn)
                
            # Generate sets data as JSON for JavaScript
            sets_data = []
            for _, row in sets_df.iterrows():
                # Fix image path for web (convert backslashes to forward slashes)
                image_path = row['image_path'] if pd.notna(row['image_path']) else ''
                if image_path:
                    image_path = image_path.replace('\\', '/')
                
                sets_data.append({
                    'code': row['lego_code'],
                    'name': row['official_name'],
                    'pieces': row['number_of_pieces'],
                    'minifigs': row['number_of_minifigs'],
                    'released': row['released'],
                    'theme': row['theme'],
                    'price_eur': row['retail_price_eur'],
                    'price_gbp': row['retail_price_gbp'],
                    'image_path': image_path,
                    'has_image': bool(row['has_image'])
                })
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📦 LEGO Sets Database</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Enhanced responsive styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #3498db;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --text-color: #2c3e50;
            --light-bg: #f8fafc;
            --card-shadow: 0 4px 16px rgba(44, 62, 80, 0.08);
            --border-radius: 12px;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            min-height: 100vh;
            color: var(--text-color);
            line-height: 1.6;
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
            animation: fadeInDown 0.8s ease-out;
        }}
        
        .header h1 {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .search-section {{
            background: rgba(255,255,255,0.95);
            border-radius: var(--border-radius);
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: var(--card-shadow);
        }}
        
        .search-controls {{
            display: grid;
            grid-template-columns: 1fr auto auto auto;
            gap: 15px;
            align-items: center;
        }}
        
        .search-input {{
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
            background: white;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }}
        
        .filter-select {{
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            background: white;
            font-size: 14px;
            cursor: pointer;
        }}
        
        .btn {{
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        
        .btn-secondary {{
            background: var(--light-bg);
            color: var(--text-color);
            border: 2px solid #e1e8ed;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
        }}
        
        .results-info {{
            text-align: center;
            color: white;
            margin: 20px 0;
            font-size: 1.1rem;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
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
        
        .sets-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .set-card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .set-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        }}
        
        .set-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #f8f9fa;
        }}
        
        .set-info {{
            padding: 20px;
        }}
        
        .set-title {{
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        
        .set-details {{
            color: #666;
            font-size: 0.9rem;
            margin: 5px 0;
        }}
        
        .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin: 40px 0;
        }}
        
        .page-btn {{
            padding: 8px 16px;
            border: 2px solid #e1e8ed;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .page-btn:hover, .page-btn.active {{
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}
        
        .loading-skeleton {{
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-boxes"></i> LEGO Sets Database</h1>
            <p>Browse and search through {len(sets_df)} LEGO sets</p>
        </div>
        
        <div class="search-section">
            <div class="search-controls">
                <input type="text" id="setSearch" class="search-input" placeholder="🔍 Search sets by name, code, or theme...">
                <select id="themeFilter" class="filter-select">
                    <option value="">All Themes</option>
                </select>
                <select id="yearFilter" class="filter-select">
                    <option value="">All Years</option>
                </select>
                <select id="sortBy" class="filter-select">
                    <option value="code">Sort by Code</option>
                    <option value="name">Sort by Name</option>
                    <option value="pieces">Sort by Pieces</option>
                    <option value="released">Sort by Release Date</option>
                </select>
            </div>
        </div>
        
        <div id="resultsInfo" class="results-info"></div>
        <div id="setsGrid" class="sets-grid"></div>
        <div id="pagination" class="pagination"></div>
        
        <div class="footer">
            <a href="index.html" class="btn btn-secondary">
                <i class="fas fa-arrow-left"></i> Back to Main
            </a>
        </div>
    </div>
    
    <script>
        const setsData = {json.dumps(sets_data, ensure_ascii=False)};
        let filteredData = [...setsData];
        let currentPage = 1;
        const itemsPerPage = 12;
        
        document.addEventListener('DOMContentLoaded', function() {{
            initializeFilters();
            renderSets();
        }});
        
        function initializeFilters() {{
            // Populate theme filter
            const themes = [...new Set(setsData.map(set => set.theme).filter(Boolean))];
            const themeFilter = document.getElementById('themeFilter');
            themes.forEach(theme => {{
                const option = document.createElement('option');
                option.value = theme;
                option.textContent = theme;
                themeFilter.appendChild(option);
            }});
            
            // Populate year filter
            const years = [...new Set(setsData.map(set => {{
                const match = set.released.match(/\\d{{4}}/);
                return match ? match[0] : '';
            }}))].filter(Boolean).sort().reverse();
            
            const yearFilter = document.getElementById('yearFilter');
            years.forEach(year => {{
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                yearFilter.appendChild(option);
            }});
            
            // Add event listeners
            document.getElementById('setSearch').addEventListener('input', filterSets);
            document.getElementById('themeFilter').addEventListener('change', filterSets);
            document.getElementById('yearFilter').addEventListener('change', filterSets);
            document.getElementById('sortBy').addEventListener('change', filterSets);
        }}
        
        function filterSets() {{
            const searchTerm = document.getElementById('setSearch').value.toLowerCase();
            const themeFilter = document.getElementById('themeFilter').value;
            const yearFilter = document.getElementById('yearFilter').value;
            const sortBy = document.getElementById('sortBy').value;
            
            filteredData = setsData.filter(set => {{
                const matchesSearch = !searchTerm || 
                    set.name.toLowerCase().includes(searchTerm) ||
                    set.code.toLowerCase().includes(searchTerm) ||
                    set.theme.toLowerCase().includes(searchTerm);
                    
                const matchesTheme = !themeFilter || set.theme === themeFilter;
                const matchesYear = !yearFilter || set.released.includes(yearFilter);
                
                return matchesSearch && matchesTheme && matchesYear;
            }});
            
            // Sort data
            filteredData.sort((a, b) => {{
                switch(sortBy) {{
                    case 'name': return a.name.localeCompare(b.name);
                    case 'pieces': return (parseInt(a.pieces) || 0) - (parseInt(b.pieces) || 0);
                    case 'released': return new Date(a.released) - new Date(b.released);
                    default: return a.code.localeCompare(b.code);
                }}
            }});
            
            currentPage = 1;
            renderSets();
        }}
        
        function renderSets() {{
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const pageData = filteredData.slice(startIndex, endIndex);
            
            const grid = document.getElementById('setsGrid');
            
            if (pageData.length === 0) {{
                grid.innerHTML = `
                    <div class="no-results">
                        <i class="fas fa-search" style="font-size: 3rem; color: #ccc; margin-bottom: 20px;"></i>
                        <h3>No sets found</h3>
                        <p>Try adjusting your search criteria</p>
                    </div>
                `;
            }} else {{
                grid.innerHTML = pageData.map(set => `
                    <div class="set-card">
                        ${{set.has_image ? 
                            `<img src="${{set.image_path}}" alt="LEGO ${{set.code}}" class="set-image" loading="lazy">` :
                            `<div class="set-image" style="display: flex; align-items: center; justify-content: center; background: #f8f9fa; color: #666;">
                                <i class="fas fa-image" style="font-size: 2rem;"></i>
                            </div>`
                        }}
                        <div class="set-info">
                            <div class="set-title">${{set.code}}: ${{set.name}}</div>
                            <div class="set-details"><i class="fas fa-puzzle-piece"></i> ${{set.pieces}} pieces</div>
                            <div class="set-details"><i class="fas fa-users"></i> ${{set.minifigs}} minifigs</div>
                            <div class="set-details"><i class="fas fa-calendar"></i> ${{set.released}}</div>
                            <div class="set-details"><i class="fas fa-tag"></i> ${{set.theme}}</div>
                            ${{set.price_gbp ? `<div class="set-details"><i class="fas fa-pound-sign"></i> ${{set.price_gbp}}</div>` : ''}}
                        </div>
                    </div>
                `).join('');
            }}
            
            renderPagination();
            updateResultsInfo();
        }}
        
        function renderPagination() {{
            const totalPages = Math.ceil(filteredData.length / itemsPerPage);
            const pagination = document.getElementById('pagination');
            
            if (totalPages <= 1) {{
                pagination.innerHTML = '';
                return;
            }}
            
            let paginationHTML = '';
            
            // Previous button
            if (currentPage > 1) {{
                paginationHTML += `<button class="page-btn" onclick="changePage(${{currentPage - 1}})">
                    <i class="fas fa-chevron-left"></i>
                </button>`;
            }}
            
            // Page numbers
            for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {{
                paginationHTML += `<button class="page-btn ${{i === currentPage ? 'active' : ''}}" onclick="changePage(${{i}})">
                    ${{i}}
                </button>`;
            }}
            
            // Next button
            if (currentPage < totalPages) {{
                paginationHTML += `<button class="page-btn" onclick="changePage(${{currentPage + 1}})">
                    <i class="fas fa-chevron-right"></i>
                </button>`;
            }}
            
            pagination.innerHTML = paginationHTML;
        }}
        
        function changePage(page) {{
            currentPage = page;
            renderSets();
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        function updateResultsInfo() {{
            const startIndex = (currentPage - 1) * itemsPerPage + 1;
            const endIndex = Math.min(currentPage * itemsPerPage, filteredData.length);
            const total = filteredData.length;
            
            document.getElementById('resultsInfo').innerHTML = `
                <p style="text-align: center; color: #666; margin: 20px 0;">
                    Showing ${{startIndex}}-${{endIndex}} of ${{total}} sets
                </p>
            `;
        }}
    </script>
</body>
</html>
            """
            
            output_file = self.output_dir / "sets.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Enhanced sets page generated: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to generate sets page: {e}")
            return ""


def generate_enhanced_web_interface():
    """Generate the enhanced web interface with all features"""
    try:
        generator = ResponsiveWebGenerator()
        
        # Generate main page
        main_page = generator.generate_enhanced_main_page()
        print(f"✅ Enhanced main page created: {main_page}")
        
        # Generate sets page
        sets_page = generator.generate_sets_page_with_search()
        if sets_page:
            print(f"✅ Enhanced sets page created: {sets_page}")
        
        return main_page
        
    except Exception as e:
        logger.error(f"Failed to generate enhanced web interface: {e}")
        return ""
