"""
Enhanced Analytics Dashboard Generator
Creates interactive analytics with charts and visualizations
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import Counter
from logging_system import get_logger

logger = get_logger(__name__)


def generate_analytics_page():
    """Generate enhanced analytics dashboard with interactive charts"""
    try:
        db_path = "lego_database/LegoDatabase.db"
        output_dir = Path("lego_database")
        
        with sqlite3.connect(db_path) as conn:
            # Get sets data
            sets_df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
            minifigs_df = pd.read_sql_query("SELECT * FROM minifig", conn)
            
        # Calculate analytics data
        analytics_data = calculate_analytics(sets_df, minifigs_df)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 LEGO Analytics Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        
        /* Dashboard grid */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .chart-card {{
            background: rgba(255,255,255,0.97);
            border-radius: var(--border-radius);
            padding: 28px 24px;
            box-shadow: var(--card-shadow);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .chart-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(44,62,80,0.15);
        }}
        
        .chart-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            gap: 10px;
        }}
        
        .chart-header h3 {{
            color: var(--text-color);
            margin: 0;
            font-size: 1.3rem;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            width: 100%;
        }}
        
        /* Summary stats */
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.97);
            border-radius: var(--border-radius);
            padding: 24px;
            text-align: center;
            box-shadow: var(--card-shadow);
            border-left: 4px solid var(--accent-color);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--accent-color);
            margin-bottom: 8px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Table styles */
        .data-table {{
            background: rgba(255,255,255,0.97);
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--card-shadow);
            margin-bottom: 30px;
        }}
        
        .table-header {{
            background: var(--accent-color);
            color: white;
            padding: 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .table-content {{
            max-height: 400px;
            overflow-y: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: var(--text-color);
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        /* Filter controls */
        .filter-section {{
            background: rgba(255,255,255,0.95);
            border-radius: var(--border-radius);
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: var(--card-shadow);
        }}
        
        .filter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            align-items: center;
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
        
        .btn-primary {{
            background: var(--accent-color);
            color: white;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
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
            .dashboard-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .summary-stats {{
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }}
            
            .chart-container {{
                height: 250px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> Analytics Dashboard</h1>
            <p>Comprehensive analysis of your LEGO collection data</p>
        </div>
        
        <!-- Summary Statistics -->
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{analytics_data['total_sets']}</div>
                <div class="stat-label">Total Sets</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{analytics_data['total_minifigs']}</div>
                <div class="stat-label">Total Minifigs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{analytics_data['avg_pieces']:.0f}</div>
                <div class="stat-label">Avg Pieces</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">£{analytics_data['avg_price']:.0f}</div>
                <div class="stat-label">Avg Price</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{analytics_data['years_span']}</div>
                <div class="stat-label">Years Span</div>
            </div>
        </div>
        
        <!-- Filter Section -->
        <div class="filter-section">
            <h3><i class="fas fa-filter"></i> Dashboard Filters</h3>
            <div class="filter-grid">
                <select id="themeFilter" class="filter-select">
                    <option value="">All Themes</option>
                </select>
                <select id="yearFilter" class="filter-select">
                    <option value="">All Years</option>
                </select>
                <button class="btn btn-primary" onclick="updateCharts()">
                    <i class="fas fa-sync-alt"></i> Update Charts
                </button>
                <button class="btn btn-secondary" onclick="exportData()">
                    <i class="fas fa-download"></i> Export
                </button>
            </div>
        </div>
        
        <!-- Dashboard Charts -->
        <div class="dashboard-grid">
            <!-- Sets by Theme Chart -->
            <div class="chart-card">
                <div class="chart-header">
                    <i class="fas fa-chart-pie" style="color: var(--accent-color);"></i>
                    <h3>Sets by Theme</h3>
                </div>
                <div class="chart-container">
                    <canvas id="themeChart"></canvas>
                </div>
            </div>
            
            <!-- Sets by Year Chart -->
            <div class="chart-card">
                <div class="chart-header">
                    <i class="fas fa-chart-bar" style="color: var(--success-color);"></i>
                    <h3>Sets by Release Year</h3>
                </div>
                <div class="chart-container">
                    <canvas id="yearChart"></canvas>
                </div>
            </div>
            
            <!-- Pieces Distribution -->
            <div class="chart-card">
                <div class="chart-header">
                    <i class="fas fa-chart-line" style="color: var(--warning-color);"></i>
                    <h3>Pieces Distribution</h3>
                </div>
                <div class="chart-container">
                    <canvas id="piecesChart"></canvas>
                </div>
            </div>
            
            <!-- Price Analysis -->
            <div class="chart-card">
                <div class="chart-header">
                    <i class="fas fa-chart-area" style="color: var(--danger-color);"></i>
                    <h3>Price Analysis</h3>
                </div>
                <div class="chart-container">
                    <canvas id="priceChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Top Sets Table -->
        <div class="data-table">
            <div class="table-header">
                <i class="fas fa-trophy"></i>
                <span>Top Sets by Pieces</span>
            </div>
            <div class="table-content">
                <table>
                    <thead>
                        <tr>
                            <th>Set Code</th>
                            <th>Name</th>
                            <th>Pieces</th>
                            <th>Theme</th>
                            <th>Price (GBP)</th>
                        </tr>
                    </thead>
                    <tbody id="topSetsTable">
                        {generate_top_sets_table(analytics_data['top_sets'])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <a href="index.html" class="btn btn-secondary">
                <i class="fas fa-arrow-left"></i> Back to Main
            </a>
        </div>
    </div>
    
    <script>
        // Analytics data
        const analyticsData = {json.dumps(analytics_data, ensure_ascii=False)};
        
        // Chart instances
        let themeChart, yearChart, piecesChart, priceChart;
        
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
            populateFilters();
        }});
        
        function initializeCharts() {{
            // Theme distribution chart
            const themeCtx = document.getElementById('themeChart').getContext('2d');
            themeChart = new Chart(themeCtx, {{
                type: 'doughnut',
                data: {{
                    labels: analyticsData.theme_distribution.labels,
                    datasets: [{{
                        data: analyticsData.theme_distribution.values,
                        backgroundColor: [
                            '#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6',
                            '#1abc9c', '#34495e', '#f1c40f', '#e67e22', '#95a5a6'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            
            // Year distribution chart
            const yearCtx = document.getElementById('yearChart').getContext('2d');
            yearChart = new Chart(yearCtx, {{
                type: 'bar',
                data: {{
                    labels: analyticsData.year_distribution.labels,
                    datasets: [{{
                        label: 'Sets Released',
                        data: analyticsData.year_distribution.values,
                        backgroundColor: '#2ecc71',
                        borderColor: '#27ae60',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            
            // Pieces distribution chart
            const piecesCtx = document.getElementById('piecesChart').getContext('2d');
            piecesChart = new Chart(piecesCtx, {{
                type: 'line',
                data: {{
                    labels: analyticsData.pieces_distribution.labels,
                    datasets: [{{
                        label: 'Number of Sets',
                        data: analyticsData.pieces_distribution.values,
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            
            // Price analysis chart
            const priceCtx = document.getElementById('priceChart').getContext('2d');
            priceChart = new Chart(priceCtx, {{
                type: 'scatter',
                data: {{
                    datasets: [{{
                        label: 'Price vs Pieces',
                        data: analyticsData.price_pieces_correlation,
                        backgroundColor: '#e74c3c',
                        borderColor: '#c0392b'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'Number of Pieces'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: 'Price (GBP)'
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        function populateFilters() {{
            // Populate theme filter
            const themes = [...new Set(analyticsData.theme_distribution.labels)];
            const themeFilter = document.getElementById('themeFilter');
            themes.forEach(theme => {{
                const option = document.createElement('option');
                option.value = theme;
                option.textContent = theme;
                themeFilter.appendChild(option);
            }});
            
            // Populate year filter
            const years = analyticsData.year_distribution.labels;
            const yearFilter = document.getElementById('yearFilter');
            years.forEach(year => {{
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                yearFilter.appendChild(option);
            }});
        }}
        
        function updateCharts() {{
            // Placeholder for chart updates based on filters
            const theme = document.getElementById('themeFilter').value;
            const year = document.getElementById('yearFilter').value;
            
            console.log('Updating charts with filters:', {{ theme, year }});
            // In a real implementation, this would filter and update chart data
        }}
        
        function exportData() {{
            // Create and download analytics report
            const dataStr = JSON.stringify(analyticsData, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'lego_analytics_' + new Date().toISOString().split('T')[0] + '.json';
            link.click();
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
        """
        
        output_file = output_dir / "analytics.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Enhanced analytics page generated: {output_file}")
        return str(output_file)
        
    except Exception as e:
        logger.error(f"Failed to generate analytics page: {e}")
        return ""


def calculate_analytics(sets_df, minifigs_df):
    """Calculate comprehensive analytics from the data"""
    try:
        # Basic statistics
        total_sets = len(sets_df)
        total_minifigs = len(minifigs_df)
        
        # Convert numeric columns
        sets_df['pieces_num'] = pd.to_numeric(sets_df['pieces_numeric'], errors='coerce').fillna(0)
        sets_df['price_gbp_num'] = pd.to_numeric(sets_df['retail_price_gbp'].str.replace('£', '').str.replace(',', ''), errors='coerce').fillna(0)
        
        avg_pieces = sets_df['pieces_num'].mean()
        avg_price = sets_df[sets_df['price_gbp_num'] > 0]['price_gbp_num'].mean()
        
        # Extract years
        sets_df['year'] = sets_df['released'].str.extract(r'(\d{4})')[0]
        years = sets_df['year'].dropna().unique()
        years_span = len(years)
        
        # Theme distribution
        theme_counts = sets_df['theme'].value_counts()
        theme_distribution = {
            'labels': theme_counts.index.tolist(),
            'values': theme_counts.values.tolist()
        }
        
        # Year distribution
        year_counts = sets_df['year'].value_counts().sort_index()
        year_distribution = {
            'labels': year_counts.index.tolist(),
            'values': year_counts.values.tolist()
        }
        
        # Pieces distribution (grouped)
        pieces_ranges = ['0-100', '101-300', '301-500', '501-1000', '1000+']
        pieces_counts = []
        for i, range_label in enumerate(pieces_ranges):
            if i == 0:
                count = len(sets_df[sets_df['pieces_num'] <= 100])
            elif i == 1:
                count = len(sets_df[(sets_df['pieces_num'] > 100) & (sets_df['pieces_num'] <= 300)])
            elif i == 2:
                count = len(sets_df[(sets_df['pieces_num'] > 300) & (sets_df['pieces_num'] <= 500)])
            elif i == 3:
                count = len(sets_df[(sets_df['pieces_num'] > 500) & (sets_df['pieces_num'] <= 1000)])
            else:
                count = len(sets_df[sets_df['pieces_num'] > 1000])
            pieces_counts.append(count)
        
        pieces_distribution = {
            'labels': pieces_ranges,
            'values': pieces_counts
        }
        
        # Price vs pieces correlation
        valid_data = sets_df[(sets_df['pieces_num'] > 0) & (sets_df['price_gbp_num'] > 0)]
        price_pieces_correlation = [
            {'x': row['pieces_num'], 'y': row['price_gbp_num']} 
            for _, row in valid_data.iterrows()
        ]
        
        # Top sets by pieces
        top_sets = sets_df.nlargest(10, 'pieces_num')[['lego_code', 'official_name', 'pieces_num', 'theme', 'retail_price_gbp']].to_dict('records')
        
        return {
            'total_sets': total_sets,
            'total_minifigs': total_minifigs,
            'avg_pieces': avg_pieces if not pd.isna(avg_pieces) else 0,
            'avg_price': avg_price if not pd.isna(avg_price) else 0,
            'years_span': years_span,
            'theme_distribution': theme_distribution,
            'year_distribution': year_distribution,
            'pieces_distribution': pieces_distribution,
            'price_pieces_correlation': price_pieces_correlation,
            'top_sets': top_sets
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate analytics: {e}")
        return {
            'total_sets': 0,
            'total_minifigs': 0,
            'avg_pieces': 0,
            'avg_price': 0,
            'years_span': 0,
            'theme_distribution': {'labels': [], 'values': []},
            'year_distribution': {'labels': [], 'values': []},
            'pieces_distribution': {'labels': [], 'values': []},
            'price_pieces_correlation': [],
            'top_sets': []
        }


def generate_top_sets_table(top_sets):
    """Generate HTML table rows for top sets"""
    if not top_sets:
        return "<tr><td colspan='5'>No data available</td></tr>"
    
    rows = []
    for set_data in top_sets:
        rows.append(f"""
            <tr>
                <td>{set_data.get('lego_code', 'N/A')}</td>
                <td>{set_data.get('official_name', 'N/A')}</td>
                <td>{set_data.get('pieces_num', 0):,.0f}</td>
                <td>{set_data.get('theme', 'N/A')}</td>
                <td>{set_data.get('retail_price_gbp', 'N/A')}</td>
            </tr>
        """)
    
    return ''.join(rows)


if __name__ == "__main__":
    analytics_page = generate_analytics_page()
    print(f"✅ Enhanced analytics page created: {analytics_page}")
