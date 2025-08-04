"""
Enhanced Minifigures Web Interface
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from logging_system import get_logger

logger = get_logger(__name__)


def generate_minifigs_page():
    """Generate enhanced minifigures page with search and filtering"""
    try:
        db_path = "lego_database/LegoDatabase.db"
        output_dir = Path("lego_database")
        
        with sqlite3.connect(db_path) as conn:
            minifigs_df = pd.read_sql_query("SELECT * FROM minifig ORDER BY minifig_code", conn)
            
        # Generate minifigs data as JSON for JavaScript
        minifigs_data = []
        for _, row in minifigs_df.iterrows():
            # Fix image path for web (convert backslashes to forward slashes)
            image_path = row['image_path'] if pd.notna(row['image_path']) else ''
            if image_path:
                image_path = image_path.replace('\\', '/')
                
            minifigs_data.append({
                'code': row['minifig_code'],
                'name': row['official_name'],
                'character': row.get('official_name', ''),
                'theme': 'Lord of the Rings',  # Default theme
                'years': row.get('year', ''),
                'sets': row.get('sets', ''),
                'image_path': image_path,
                'has_image': bool(row['has_image'])
            })
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧑‍🚀 LEGO Minifigures Database</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Responsive CSS (same as main page) */
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
        
        .minifigs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .minifig-card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .minifig-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        }}
        
        .minifig-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #f8f9fa;
        }}
        
        .minifig-info {{
            padding: 20px;
        }}
        
        .minifig-title {{
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        
        .minifig-details {{
            color: #666;
            font-size: 0.9rem;
            margin: 5px 0;
        }}
        
        .character-badge {{
            background: var(--accent-color);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            display: inline-block;
            margin-top: 10px;
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
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: rgba(255,255,255,0.8);
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
        
        @media (max-width: 768px) {{
            .search-controls {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
            
            .minifigs-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-users"></i> LEGO Minifigures Database</h1>
            <p>Browse and search through {len(minifigs_df)} Lord of the Rings minifigures</p>
        </div>
        
        <div class="search-section">
            <div class="search-controls">
                <input type="text" id="minifigSearch" class="search-input" placeholder="🔍 Search minifigures by name, code, or character...">
                <select id="themeFilter" class="filter-select">
                    <option value="">All Themes</option>
                </select>
                <select id="sortBy" class="filter-select">
                    <option value="code">Sort by Code</option>
                    <option value="name">Sort by Name</option>
                    <option value="character">Sort by Character</option>
                </select>
                <button class="btn btn-secondary" onclick="clearAllFilters()">
                    <i class="fas fa-times"></i> Clear
                </button>
            </div>
        </div>
        
        <div id="resultsInfo" class="results-info"></div>
        <div id="minifigsGrid" class="minifigs-grid"></div>
        <div id="pagination" class="pagination"></div>
        
        <div class="footer">
            <a href="index.html" class="btn btn-secondary">
                <i class="fas fa-arrow-left"></i> Back to Main
            </a>
        </div>
    </div>
    
    <script>
        const minifigsData = {json.dumps(minifigs_data, ensure_ascii=False)};
        let filteredData = [...minifigsData];
        let currentPage = 1;
        const itemsPerPage = 12;
        
        document.addEventListener('DOMContentLoaded', function() {{
            initializeFilters();
            renderMinifigs();
        }});
        
        function initializeFilters() {{
            // Populate theme filter
            const themes = [...new Set(minifigsData.map(minifig => minifig.theme).filter(Boolean))];
            const themeFilter = document.getElementById('themeFilter');
            themes.forEach(theme => {{
                const option = document.createElement('option');
                option.value = theme;
                option.textContent = theme;
                themeFilter.appendChild(option);
            }});
            
            // Add event listeners
            document.getElementById('minifigSearch').addEventListener('input', filterMinifigs);
            document.getElementById('themeFilter').addEventListener('change', filterMinifigs);
            document.getElementById('sortBy').addEventListener('change', filterMinifigs);
        }}
        
        function filterMinifigs() {{
            const searchTerm = document.getElementById('minifigSearch').value.toLowerCase();
            const themeFilter = document.getElementById('themeFilter').value;
            const sortBy = document.getElementById('sortBy').value;
            
            filteredData = minifigsData.filter(minifig => {{
                const matchesSearch = !searchTerm || 
                    minifig.name.toLowerCase().includes(searchTerm) ||
                    minifig.code.toLowerCase().includes(searchTerm) ||
                    minifig.character.toLowerCase().includes(searchTerm) ||
                    minifig.theme.toLowerCase().includes(searchTerm);
                    
                const matchesTheme = !themeFilter || minifig.theme === themeFilter;
                
                return matchesSearch && matchesTheme;
            }});
            
            // Sort data
            filteredData.sort((a, b) => {{
                switch(sortBy) {{
                    case 'name': return a.name.localeCompare(b.name);
                    case 'character': return a.character.localeCompare(b.character);
                    default: return a.code.localeCompare(b.code);
                }}
            }});
            
            currentPage = 1;
            renderMinifigs();
        }}
        
        function renderMinifigs() {{
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const pageData = filteredData.slice(startIndex, endIndex);
            
            const grid = document.getElementById('minifigsGrid');
            
            if (pageData.length === 0) {{
                grid.innerHTML = `
                    <div class="no-results">
                        <i class="fas fa-search" style="font-size: 3rem; color: #ccc; margin-bottom: 20px;"></i>
                        <h3>No minifigures found</h3>
                        <p>Try adjusting your search criteria</p>
                    </div>
                `;
            }} else {{
                grid.innerHTML = pageData.map(minifig => `
                    <div class="minifig-card">
                        ${{minifig.has_image ? 
                            `<img src="${{minifig.image_path}}" alt="LEGO ${{minifig.code}}" class="minifig-image" loading="lazy">` :
                            `<div class="minifig-image" style="display: flex; align-items: center; justify-content: center; background: #f8f9fa; color: #666;">
                                <i class="fas fa-user" style="font-size: 2rem;"></i>
                            </div>`
                        }}
                        <div class="minifig-info">
                            <div class="minifig-title">${{minifig.code}}: ${{minifig.name}}</div>
                            ${{minifig.character ? `<div class="character-badge">${{minifig.character}}</div>` : ''}}
                            ${{minifig.theme ? `<div class="minifig-details"><i class="fas fa-tag"></i> ${{minifig.theme}}</div>` : ''}}
                            ${{minifig.years ? `<div class="minifig-details"><i class="fas fa-calendar"></i> ${{minifig.years}}</div>` : ''}}
                            ${{minifig.sets ? `<div class="minifig-details"><i class="fas fa-boxes"></i> Sets: ${{minifig.sets}}</div>` : ''}}
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
            
            if (currentPage > 1) {{
                paginationHTML += `<button class="page-btn" onclick="changePage(${{currentPage - 1}})">
                    <i class="fas fa-chevron-left"></i>
                </button>`;
            }}
            
            for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {{
                paginationHTML += `<button class="page-btn ${{i === currentPage ? 'active' : ''}}" onclick="changePage(${{i}})">
                    ${{i}}
                </button>`;
            }}
            
            if (currentPage < totalPages) {{
                paginationHTML += `<button class="page-btn" onclick="changePage(${{currentPage + 1}})">
                    <i class="fas fa-chevron-right"></i>
                </button>`;
            }}
            
            pagination.innerHTML = paginationHTML;
        }}
        
        function changePage(page) {{
            currentPage = page;
            renderMinifigs();
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        function updateResultsInfo() {{
            const startIndex = (currentPage - 1) * itemsPerPage + 1;
            const endIndex = Math.min(currentPage * itemsPerPage, filteredData.length);
            const total = filteredData.length;
            
            document.getElementById('resultsInfo').innerHTML = `
                <p style="text-align: center; color: #666; margin: 20px 0;">
                    Showing ${{startIndex}}-${{endIndex}} of ${{total}} minifigures
                </p>
            `;
        }}
        
        function clearAllFilters() {{
            document.getElementById('minifigSearch').value = '';
            document.getElementById('themeFilter').value = '';
            filterMinifigs();
        }}
    </script>
</body>
</html>
        """
        
        output_file = output_dir / "minifigs.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Enhanced minifigures page generated: {output_file}")
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Failed to generate minifigures page: {e}")
        return ""


if __name__ == "__main__":
    minifigs_page = generate_minifigs_page()
    print(f"✅ Enhanced minifigures page created: {minifigs_page}")
