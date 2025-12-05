"""
Standalone Dashboard Generator
Creates a self-contained HTML file with all survey data
Run this script, it will create dashboard.html that you can open in any browser
"""
import os
import asyncio
import aiohttp
import json
from datetime import datetime
from app.scraper import PureSpectrumScraper
from dotenv import load_dotenv

load_dotenv()

PURESPECTRUM_USERNAME = os.getenv("PURESPECTRUM_USERNAME", "")
PURESPECTRUM_PASSWORD = os.getenv("PURESPECTRUM_PASSWORD", "")


def generate_quota_name(quota):
    """Generate meaningful quota name from criteria"""
    criteria = quota.get('criteria', [])
    if not criteria:
        return quota.get('quota_title', 'General Quota')
    
    parts = []
    for criterion in criteria:
        qual_name = criterion.get('qualification_name', '')
        conditions = criterion.get('condition_names', [])
        
        if qual_name == 'Gender' and conditions:
            parts.append(conditions[0])
        elif qual_name == 'Age':
            range_sets = criterion.get('range_sets', [])
            if range_sets:
                range = range_sets[0]
                from_age = range.get('from', '')
                to_age = range.get('to', '')
                if from_age and to_age:
                    parts.append(f"{from_age}-{to_age} yr")
    
    return ', '.join(parts) if parts else quota.get('quota_title', 'General Quota')


async def fetch_data():
    """Fetch all survey and quota data"""
    if not PURESPECTRUM_USERNAME or not PURESPECTRUM_PASSWORD:
        print("Error: PureSpectrum credentials not set in .env file")
        return None, None
    
    scraper = PureSpectrumScraper(PURESPECTRUM_USERNAME, PURESPECTRUM_PASSWORD)
    
    async with aiohttp.ClientSession() as session:
        if not await scraper.login(session):
            print("Error: Failed to authenticate with PureSpectrum")
            return None, None
        
        # Get all surveys
        surveys = await scraper.get_survey_data(session)
        
        # Get quotas for each survey
        quotas_data = {}
        for survey_id in surveys.keys():
            quotas = await scraper.get_survey_quotas(session, survey_id)
            quotas_data[survey_id] = quotas
        
        return surveys, quotas_data


def generate_html(surveys, quotas_data):
    """Generate standalone HTML dashboard"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PureSpectrum Survey Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            padding: 0;
            color: #2c3e50;
        }}
        
        .header-bar {{
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            color: white;
            padding: 24px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
            color: white;
        }}
        
        .header p {{
            font-size: 14px;
            color: rgba(255,255,255,0.9);
            opacity: 0.9;
        }}
        
        .stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #2563eb;
        }}
        
        .summary-label {{
            font-size: 13px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .summary-value {{
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
        }}
        
        .survey-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 24px;
            margin-bottom: 30px;
        }}
        
        .survey-card {{
            background: white;
            padding: 28px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
            border-top: 4px solid #2563eb;
        }}
        
        .survey-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}
        
        .survey-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 16px;
        }}
        
        .survey-id {{
            color: #2563eb;
            font-weight: 600;
            font-size: 13px;
            background: #eff6ff;
            padding: 4px 12px;
            border-radius: 6px;
            display: inline-block;
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-active {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .survey-card h3 {{
            color: #1e293b;
            margin: 16px 0;
            font-size: 20px;
            font-weight: 600;
            line-height: 1.4;
        }}
        
        .progress-container {{
            margin: 20px 0;
        }}
        
        .progress-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
            color: #64748b;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 32px;
            background: #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 13px;
            font-weight: 600;
            transition: width 0.3s ease;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }}
        
        .stat {{
            text-align: center;
            padding: 12px;
            background: #f8fafc;
            border-radius: 8px;
        }}
        
        .stat-label {{
            font-size: 11px;
            color: #64748b;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        
        .stat-value {{
            font-size: 20px;
            font-weight: 700;
            color: #1e293b;
        }}
        
        .quota-section {{
            background: white;
            padding: 32px;
            border-radius: 12px;
            margin-top: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .quota-section h3 {{
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .quota-group {{
            margin-bottom: 32px;
        }}
        
        .quota-group h4 {{
            color: #1e293b;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #2563eb;
            font-size: 18px;
            font-weight: 600;
        }}
        
        .quota-item {{
            padding: 18px;
            margin-bottom: 12px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
            transition: background 0.2s;
        }}
        
        .quota-item:hover {{
            background: #f1f5f9;
        }}
        
        .quota-name {{
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 12px;
            font-size: 15px;
        }}
        
        .quota-progress {{
            font-size: 13px;
            color: #64748b;
            margin-top: 8px;
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }}
        
        .quota-progress span {{
            display: inline-block;
        }}
        
        .empty {{
            background: white;
            padding: 60px;
            border-radius: 12px;
            text-align: center;
            color: #64748b;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .empty h2 {{
            font-size: 24px;
            margin-bottom: 8px;
            color: #1e293b;
        }}
    </style>
</head>
<body>
    <div class="header-bar">
        <div class="container">
            <div class="header">
                <h1>PureSpectrum Survey Dashboard</h1>
                <p>Last updated: {timestamp}</p>
            </div>
        </div>
    </div>
    <div class="container">
"""
    
    if not surveys or len(surveys) == 0:
        html += """
        <div class="empty">
            <h2>No active surveys found</h2>
        </div>
"""
    else:
        # Calculate summary stats
        total_surveys = len(surveys)
        total_completes = sum(s.get('completes', 0) for s in surveys.values())
        total_target = sum(s.get('target', 0) for s in surveys.values())
        total_cost = sum(s.get('currentCost', 0) for s in surveys.values())
        overall_progress = (total_completes / total_target * 100) if total_target > 0 else 0
        
        # Summary section
        html += f"""
        <div class="stats-summary">
            <div class="summary-card">
                <div class="summary-label">Active Surveys</div>
                <div class="summary-value">{total_surveys}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Overall Progress</div>
                <div class="summary-value">{overall_progress:.1f}%</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Total Completes</div>
                <div class="summary-value">{total_completes:,}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Total Cost</div>
                <div class="summary-value">${total_cost:,.2f}</div>
            </div>
        </div>
"""
        
        html += '<div class="survey-grid">'
        
        for survey_id, survey in surveys.items():
            target = survey.get('target', 0)
            completes = survey.get('completes', 0)
            progress = (completes / target * 100) if target > 0 else 0
            title = survey.get('title', 'Untitled Survey')
            status = survey.get('status', 'Unknown')
            cpi = survey.get('cpi', 0)
            cost = survey.get('currentCost', 0)
            
            status_class = 'status-active' if status.lower() == 'active' else ''
            
            html += f"""
            <div class="survey-card">
                <div class="survey-header">
                    <div class="survey-id">ID: {survey_id}</div>
                    <div class="status-badge {status_class}">{status}</div>
                </div>
                <h3>{title}</h3>
                <div class="progress-container">
                    <div class="progress-header">
                        <span>Progress</span>
                        <span><strong>{completes:,}</strong> / {target:,} ({progress:.1f}%)</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress}%">
                            {progress:.1f}%
                        </div>
                    </div>
                </div>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-label">CPI</div>
                        <div class="stat-value">${cpi:.2f}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Cost</div>
                        <div class="stat-value">${cost:,.2f}</div>
                    </div>
                </div>
            </div>
"""
        
        html += '</div>'
        
        # Add quota sections
        for survey_id, quotas in quotas_data.items():
            if not quotas:
                continue
            
            html += f'<div class="quota-section">'
            html += f'<h3>Quota Details for Survey {survey_id}</h3>'
            
            # Group quotas
            grouped = {}
            for quota in quotas:
                group = quota.get('group_key', 'General')
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(quota)
            
            for group_name, group_quotas in grouped.items():
                html += f'<div class="quota-group">'
                html += f'<h4>{group_name}</h4>'
                
                for quota in group_quotas:
                    name = generate_quota_name(quota)
                    fielded = quota.get('achieved', 0)
                    goal = quota.get('required_count', 0)
                    progress = (fielded / goal * 100) if goal > 0 else 0
                    current_target = quota.get('current_target', goal)
                    currently_open = quota.get('currently_open', 0)
                    in_progress = quota.get('in_progress', 0)
                    
                    html += f"""
                    <div class="quota-item">
                        <div class="quota-name">{name}</div>
                        <div class="progress-container">
                            <div class="progress-header">
                                <span>Fielded</span>
                                <span><strong>{fielded:,}</strong> / {goal:,} ({progress:.1f}%)</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {progress}%">
                                    {progress:.1f}%
                                </div>
                            </div>
                        </div>
                        <div class="quota-progress">
                            <span><strong>Target:</strong> {current_target:,}</span>
                            <span><strong>Open:</strong> {currently_open:,}</span>
                            <span><strong>In Progress:</strong> {in_progress:,}</span>
                        </div>
                    </div>
"""
                
                html += '</div>'
            
            html += '</div>'
    
    html += """
    </div>
</body>
</html>
"""
    
    return html


async def main():
    """Main function to generate dashboard"""
    print("Fetching survey data from PureSpectrum...")
    surveys, quotas_data = await fetch_data()
    
    if surveys is None:
        print("Failed to fetch data. Check your credentials and try again.")
        return
    
    print(f"Found {len(surveys)} active surveys")
    print("Generating HTML dashboard...")
    
    html = generate_html(surveys, quotas_data)
    
    output_file = "dashboard.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Dashboard generated successfully!")
    print(f"Open {output_file} in your browser to view it.")
    print(f"\nYou can share this file with your team or host it anywhere.")


if __name__ == "__main__":
    asyncio.run(main())

