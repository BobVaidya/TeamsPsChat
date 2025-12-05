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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 14px;
        }}
        
        .survey-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .survey-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .survey-card h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        .survey-id {{
            color: #667eea;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 25px;
            background: #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }}
        
        .stat {{
            text-align: center;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 5px;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        
        .quota-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .quota-group {{
            margin-bottom: 25px;
        }}
        
        .quota-group h4 {{
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .quota-item {{
            padding: 15px;
            margin-bottom: 10px;
            background: #f9f9f9;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        
        .quota-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }}
        
        .quota-progress {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        
        .empty {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PureSpectrum Survey Dashboard</h1>
            <p>Last updated: {timestamp}</p>
        </div>
"""
    
    if not surveys or len(surveys) == 0:
        html += """
        <div class="empty">
            <h2>No active surveys found</h2>
        </div>
"""
    else:
        html += '<div class="survey-grid">'
        
        for survey_id, survey in surveys.items():
            target = survey.get('target', 0)
            completes = survey.get('completes', 0)
            target = survey.get('target', 0)
            completes = survey.get('completes', 0)
            progress = (completes / target * 100) if target > 0 else 0
            title = survey.get('title', 'Untitled Survey')
            status = survey.get('status', 'Unknown')
            cpi = survey.get('cpi', 0)
            cost = survey.get('currentCost', 0)
            
            html += f"""
            <div class="survey-card">
                <div class="survey-id">Survey ID: {survey_id}</div>
                <h3>{title}</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%">
                        {progress:.1f}%
                    </div>
                </div>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-label">Status</div>
                        <div class="stat-value">{status}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Progress</div>
                        <div class="stat-value">{completes}/{target}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">CPI</div>
                        <div class="stat-value">${cpi:.2f}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Cost</div>
                        <div class="stat-value">${cost:.2f}</div>
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
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress}%">
                                {progress:.1f}%
                            </div>
                        </div>
                        <div class="quota-progress">
                            Fielded: {fielded}/{goal} | Target: {current_target} | 
                            Open: {currently_open} | In Progress: {in_progress}
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

