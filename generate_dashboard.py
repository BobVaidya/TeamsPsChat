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
            background: #f8fafc;
            min-height: 100vh;
            padding: 0;
            color: #1e293b;
        }}
        
        .header-bar {{
            background: #1e293b;
            color: white;
            padding: 32px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .header {{
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
            color: white;
        }}
        
        .header p {{
            font-size: 13px;
            color: rgba(255,255,255,0.8);
        }}
        
        .active-surveys-count {{
            background: white;
            padding: 24px 32px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 24px;
            text-align: center;
        }}
        
        .active-surveys-count .label {{
            font-size: 14px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .active-surveys-count .value {{
            font-size: 36px;
            font-weight: 700;
            color: #1e293b;
        }}
        
        .surveys-list {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .survey-row {{
            border-bottom: 1px solid #e2e8f0;
            padding: 20px 24px;
            cursor: pointer;
            transition: background 0.2s;
            display: grid;
            grid-template-columns: 2fr 1fr 100px 120px 80px 80px;
            gap: 20px;
            align-items: center;
        }}
        
        .survey-row:hover {{
            background: #f8fafc;
        }}
        
        .survey-row:last-child {{
            border-bottom: none;
        }}
        
        .survey-row.expanded {{
            background: #f1f5f9;
        }}
        
        .survey-name {{
            font-weight: 600;
            color: #1e293b;
            font-size: 15px;
        }}
        
        .survey-progress {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 24px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }}
        
        .progress-fill {{
            height: 100%;
            background: #2563eb;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 11px;
            font-weight: 600;
            transition: width 0.3s ease;
        }}
        
        .progress-text {{
            font-size: 12px;
            color: #64748b;
        }}
        
        .metric {{
            text-align: right;
            font-size: 14px;
            color: #1e293b;
            font-weight: 500;
        }}
        
        .metric-label {{
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .quota-details {{
            display: none;
            grid-column: 1 / -1;
            padding: 24px 0 0 0;
            border-top: 2px solid #e2e8f0;
            margin-top: 20px;
        }}
        
        .survey-row.expanded .quota-details {{
            display: block;
        }}
        
        .quota-section-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 16px;
        }}
        
        .quota-group {{
            margin-bottom: 24px;
        }}
        
        .quota-group-title {{
            font-size: 14px;
            font-weight: 600;
            color: #475569;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .quota-item {{
            padding: 16px;
            margin-bottom: 12px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #2563eb;
        }}
        
        .quota-name {{
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 12px;
            font-size: 14px;
        }}
        
        .quota-progress {{
            font-size: 12px;
            color: #64748b;
            margin-top: 8px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .quota-progress span {{
            display: inline-block;
        }}
        
        .empty {{
            background: white;
            padding: 60px;
            border-radius: 8px;
            text-align: center;
            color: #64748b;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .empty h2 {{
            font-size: 20px;
            margin-bottom: 8px;
            color: #1e293b;
        }}
        
        @media (max-width: 1200px) {{
            .survey-row {{
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            
            .metric {{
                text-align: left;
            }}
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
        # Count active surveys
        total_surveys = len(surveys)
        
        # Active surveys count
        html += f"""
        <div class="active-surveys-count">
            <div class="label">Active Surveys</div>
            <div class="value">{total_surveys}</div>
        </div>
"""
        
        # Surveys list
        html += '<div class="surveys-list">'
        
        for survey_id, survey in surveys.items():
            target = survey.get('target', 0)
            completes = survey.get('completes', 0)
            progress = (completes / target * 100) if target > 0 else 0
            title = survey.get('title', 'Untitled Survey')
            cpi = survey.get('cpi', 0)
            cost = survey.get('currentCost', 0)
            loi = survey.get('loi', 0)
            incidence = survey.get('incidence', 0)
            
            # Format LOI (Length of Interview) - usually in minutes
            loi_display = f"{loi:.1f} min" if loi > 0 else "N/A"
            
            # Format IR (Incidence Rate) - usually as percentage
            ir_display = f"{incidence * 100:.1f}%" if incidence > 0 else "N/A"
            
            html += f"""
            <div class="survey-row" onclick="toggleQuota('{survey_id}', event)">
                <div class="survey-name">{title}</div>
                <div class="survey-progress">
                    <div class="progress-text">{completes:,} / {target:,} ({progress:.1f}%)</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(progress, 100)}%"></div>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">CPI</div>
                    <div>${cpi:.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Cost</div>
                    <div>${cost:,.2f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">LOI</div>
                    <div>{loi_display}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">IR</div>
                    <div>{ir_display}</div>
                </div>
                <div class="quota-details" id="quota-{survey_id}">
"""
            
            # Add quota details for this survey
            quotas = quotas_data.get(survey_id, [])
            if quotas:
                html += '<div class="quota-section-title">Quota Details</div>'
                
                # Group quotas
                grouped = {}
                for quota in quotas:
                    group = quota.get('group_key', 'General')
                    if group not in grouped:
                        grouped[group] = []
                    grouped[group].append(quota)
                
                for group_name, group_quotas in grouped.items():
                    html += f'<div class="quota-group">'
                    html += f'<div class="quota-group-title">{group_name}</div>'
                    
                    for quota in group_quotas:
                        name = generate_quota_name(quota)
                        fielded = quota.get('achieved', 0)
                        goal = quota.get('required_count', 0)
                        quota_progress = (fielded / goal * 100) if goal > 0 else 0
                        current_target = quota.get('current_target', goal)
                        currently_open = quota.get('currently_open', 0)
                        in_progress = quota.get('in_progress', 0)
                        
                        html += f"""
                        <div class="quota-item">
                            <div class="quota-name">{name}</div>
                            <div class="progress-bar" style="margin: 8px 0;">
                                <div class="progress-fill" style="width: {min(quota_progress, 100)}%"></div>
                            </div>
                            <div class="quota-progress">
                                <span><strong>Fielded:</strong> {fielded:,} / {goal:,} ({quota_progress:.1f}%)</span>
                                <span><strong>Target:</strong> {current_target:,}</span>
                                <span><strong>Open:</strong> {currently_open:,}</span>
                                <span><strong>In Progress:</strong> {in_progress:,}</span>
                            </div>
                        </div>
"""
                    
                    html += '</div>'
            else:
                html += '<div class="quota-section-title">No quota data available</div>'
            
            html += """
                </div>
            </div>
"""
        
        html += '</div>'
    
    html += f"""
    </div>
    <script>
        function toggleQuota(surveyId, event) {{
            event.stopPropagation();
            const row = event.currentTarget || event.target.closest('.survey-row');
            const quotaDetails = document.getElementById('quota-' + surveyId);
            
            if (row.classList.contains('expanded')) {{
                row.classList.remove('expanded');
            }} else {{
                // Close all other expanded rows
                document.querySelectorAll('.survey-row.expanded').forEach(r => {{
                    r.classList.remove('expanded');
                }});
                row.classList.add('expanded');
            }}
        }}
    </script>
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

