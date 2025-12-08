"""
Web Dashboard for PureSpectrum Survey Monitoring
Live dashboard that fetches data on each request
"""
from fastapi.responses import HTMLResponse
from datetime import datetime
import os
import aiohttp
from .scraper import PureSpectrumScraper

# Get credentials from environment
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


async def dashboard_home():
    """Main dashboard page with live data fetching"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""<!DOCTYPE html>
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
        
        .refresh-btn {{
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            margin-top: 12px;
            transition: background 0.2s;
        }}
        
        .refresh-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .loading {{
            text-align: center;
            padding: 60px;
            color: #64748b;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .error {{
            background: #fee2e2;
            color: #dc2626;
            padding: 16px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #dc2626;
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
            padding: 16px 0 0 0;
            border-top: 1px solid #e2e8f0;
            margin-top: 16px;
        }}
        
        .survey-row.expanded .quota-details {{
            display: block;
        }}
        
        .quota-section-title {{
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .quota-group {{
            margin-bottom: 20px;
        }}
        
        .quota-group-title {{
            font-size: 12px;
            font-weight: 600;
            color: #64748b;
            margin-bottom: 10px;
            padding-bottom: 6px;
            border-bottom: 1px solid #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .quota-table-wrapper {{
            overflow-x: auto;
            margin-top: 12px;
        }}
        
        .quota-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            font-size: 11px;
            min-width: 600px;
        }}
        
        .quota-table thead {{
            background: #f1f5f9;
        }}
        
        .quota-table th {{
            padding: 8px 10px;
            text-align: left;
            font-weight: 600;
            color: #475569;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #cbd5e1;
            white-space: nowrap;
        }}
        
        .quota-table th:not(:first-child) {{
            text-align: right;
        }}
        
        .quota-table td {{
            padding: 8px 10px;
            color: #1e293b;
            border-bottom: 1px solid #f1f5f9;
            font-size: 11px;
        }}
        
        .quota-table td:not(:first-child) {{
            text-align: right;
        }}
        
        .quota-table tbody tr:hover {{
            background: #f8fafc;
        }}
        
        .quota-table tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        .quota-name-cell {{
            font-weight: 500;
            color: #1e293b;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .quota-number {{
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
            color: #475569;
            font-size: 11px;
        }}
        
        .quota-progress-cell {{
            color: #2563eb;
            font-weight: 600;
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
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px 12px;
            }}
            
            .header h1 {{
                font-size: 22px;
            }}
            
            .active-surveys-count {{
                padding: 20px 16px;
            }}
            
            .active-surveys-count .value {{
                font-size: 28px;
            }}
            
            .survey-row {{
                padding: 16px 12px;
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            
            .survey-name {{
                font-size: 14px;
            }}
            
            .metric {{
                text-align: left;
                font-size: 13px;
            }}
            
            .metric-label {{
                font-size: 10px;
            }}
            
            .quota-table-wrapper {{
                margin: 0 -12px;
                padding: 0 12px;
            }}
            
            .quota-table {{
                font-size: 10px;
                min-width: 500px;
            }}
            
            .quota-table th,
            .quota-table td {{
                padding: 6px 8px;
                font-size: 10px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .header-bar {{
                padding: 24px 0;
            }}
            
            .header h1 {{
                font-size: 18px;
            }}
            
            .quota-table {{
                min-width: 400px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header-bar">
        <div class="container">
            <div class="header">
                <h1>PureSpectrum Survey Dashboard</h1>
                <p>Last updated: <span id="last-updated">{timestamp}</span></p>
                <button class="refresh-btn" onclick="loadSurveys()">🔄 Refresh</button>
            </div>
        </div>
    </div>
    <div class="container">
        <div id="loading" class="loading" style="display: none;">
            Loading surveys...
        </div>
        <div id="error" class="error" style="display: none;"></div>
        <div id="dashboard-content"></div>
    </div>
    
    <script>
        function formatLOI(loi) {{
            if (loi && loi > 0) {{
                return loi.toFixed(1) + " min";
            }}
            return "N/A";
        }}
        
        function formatIR(incidence) {{
            if (!incidence || incidence <= 0) {{
                return "N/A";
            }}
            if (incidence > 1 && incidence <= 100) {{
                return incidence.toFixed(1) + "%";
            }} else if (incidence > 100) {{
                return (incidence / 100).toFixed(1) + "%";
            }} else {{
                return (incidence * 100).toFixed(1) + "%";
            }}
        }}
        
        function generateQuotaName(quota) {{
            const criteria = quota.criteria || [];
            if (criteria.length === 0) {{
                return quota.quota_title || 'General Quota';
            }}
            
            const parts = [];
            criteria.forEach(criterion => {{
                const qualName = criterion.qualification_name || '';
                const conditions = criterion.condition_names || [];
                
                if (qualName === 'Gender' && conditions.length > 0) {{
                    parts.push(conditions[0]);
                }} else if (qualName === 'Age') {{
                    const rangeSets = criterion.range_sets || [];
                    if (rangeSets.length > 0) {{
                        const range = rangeSets[0];
                        const fromAge = range.from || '';
                        const toAge = range.to || '';
                        if (fromAge && toAge) {{
                            parts.push(fromAge + '-' + toAge + ' yr');
                        }}
                    }}
                }}
            }});
            
            return parts.length > 0 ? parts.join(', ') : (quota.quota_title || 'General Quota');
        }}
        
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
                
                // Load quotas if not already loaded
                if (quotaDetails && quotaDetails.innerHTML.trim() === '') {{
                    loadQuotas(surveyId);
                }}
            }}
        }}
        
        async function loadQuotas(surveyId) {{
            const quotaDetails = document.getElementById('quota-' + surveyId);
            if (!quotaDetails) return;
            
            quotaDetails.innerHTML = '<div class="quota-section-title">Loading quotas...</div>';
            
            try {{
                const response = await fetch(`/api/quotas/${{surveyId}}`);
                if (!response.ok) throw new Error('Failed to load quotas');
                
                const data = await response.json();
                if (data.error) {{
                    throw new Error(data.error);
                }}
                
                const quotas = data.quotas || [];
                if (quotas.length === 0) {{
                    quotaDetails.innerHTML = '<div class="quota-section-title" style="color: #94a3b8;">No quota data available</div>';
                    return;
                }}
                
                let html = '<div class="quota-section-title">Quota Details</div>';
                
                // Group quotas
                const grouped = {{}};
                quotas.forEach(quota => {{
                    const group = quota.group_key || 'General';
                    if (!grouped[group]) grouped[group] = [];
                    grouped[group].push(quota);
                }});
                
                for (const [groupName, groupQuotas] of Object.entries(grouped)) {{
                    html += `<div class="quota-group">`;
                    html += `<div class="quota-group-title">${{groupName}}</div>`;
                    html += `
                    <div class="quota-table-wrapper">
                        <table class="quota-table">
                            <thead>
                                <tr>
                                    <th>Quota</th>
                                    <th>Fielded</th>
                                    <th>Goal</th>
                                    <th>Progress</th>
                                    <th>Target</th>
                                    <th>Open</th>
                                    <th>In Progress</th>
                                </tr>
                            </thead>
                            <tbody>
`;
                    
                    groupQuotas.forEach(quota => {{
                        const name = generateQuotaName(quota);
                        const fielded = quota.achieved || 0;
                        const goal = quota.required_count || 0;
                        const quotaProgress = goal > 0 ? (fielded / goal * 100) : 0;
                        const currentTarget = quota.current_target || goal;
                        const currentlyOpen = quota.currently_open || 0;
                        const inProgress = quota.in_progress || 0;
                        
                        html += `
                                <tr>
                                    <td class="quota-name-cell" title="${{name}}">${{name}}</td>
                                    <td class="quota-number">${{fielded.toLocaleString()}}</td>
                                    <td class="quota-number">${{goal.toLocaleString()}}</td>
                                    <td class="quota-number quota-progress-cell">${{quotaProgress.toFixed(1)}}%</td>
                                    <td class="quota-number">${{currentTarget.toLocaleString()}}</td>
                                    <td class="quota-number">${{currentlyOpen.toLocaleString()}}</td>
                                    <td class="quota-number">${{inProgress.toLocaleString()}}</td>
                                </tr>
`;
                    }});
                    
                    html += `
                            </tbody>
                        </table>
                    </div>
`;
                    html += '</div>';
                }}
                
                quotaDetails.innerHTML = html;
            }} catch (err) {{
                quotaDetails.innerHTML = `<div class="quota-section-title" style="color: #dc2626;">Error loading quotas: ${{err.message}}</div>`;
            }}
        }}
        
        async function loadSurveys() {{
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const content = document.getElementById('dashboard-content');
            
            loading.style.display = 'block';
            error.style.display = 'none';
            content.innerHTML = '';
            
            // Update timestamp
            document.getElementById('last-updated').textContent = new Date().toLocaleString();
            
            try {{
                // Add timeout to prevent hanging
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
                
                const response = await fetch('/api/surveys', {{
                    signal: controller.signal
                }});
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {{
                    const errorText = await response.text();
                    throw new Error(`HTTP ${{response.status}}: ${{errorText || 'Failed to load surveys'}}`);
                }}
                
                const data = await response.json();
                if (data.error) {{
                    throw new Error(data.error);
                }}
                
                const surveys = data.surveys || {{}};
                const surveyIds = Object.keys(surveys);
                
                if (surveyIds.length === 0) {{
                    content.innerHTML = `
                        <div class="empty">
                            <h2>No active surveys found</h2>
                        </div>
                    `;
                    loading.style.display = 'none';
                    return;
                }}
                
                // Active surveys count
                let html = `
                    <div class="active-surveys-count">
                        <div class="label">Active Surveys</div>
                        <div class="value">${{surveyIds.length}}</div>
                    </div>
                    <div class="surveys-list">
                `;
                
                // Survey rows
                surveyIds.forEach(surveyId => {{
                    const survey = surveys[surveyId];
                    const target = survey.target || 0;
                    const completes = survey.completes || 0;
                    const progress = target > 0 ? (completes / target * 100) : 0;
                    const title = survey.title || 'Untitled Survey';
                    const cpi = survey.cpi || 0;
                    const cost = survey.currentCost || 0;
                    
                    // Get LOI and IR from raw data if needed
                    const rawData = survey._raw || {{}};
                    const loi = survey.loi || rawData.expected_loi || rawData.loi || rawData.length_of_interview || 0;
                    const incidence = survey.incidence || rawData.expected_ir || rawData.current_incidence || rawData.incidence_rate || 0;
                    
                    html += `
                        <div class="survey-row" onclick="toggleQuota('${{surveyId}}', event)">
                            <div class="survey-name">${{title}}</div>
                            <div class="survey-progress">
                                <div class="progress-text">${{completes.toLocaleString()}} / ${{target.toLocaleString()}} (${{progress.toFixed(1)}}%)</div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${{Math.min(progress, 100)}}%"></div>
                                </div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">CPI</div>
                                <div>$${{cpi.toFixed(2)}}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Cost</div>
                                <div>$${{cost.toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">LOI</div>
                                <div>${{formatLOI(loi)}}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">IR</div>
                                <div>${{formatIR(incidence)}}</div>
                            </div>
                            <div class="quota-details" id="quota-${{surveyId}}"></div>
                        </div>
                    `;
                }});
                
                html += '</div>';
                content.innerHTML = html;
                
            }} catch (err) {{
                let errorMsg = 'Error: ' + err.message;
                if (err.name === 'AbortError') {{
                    errorMsg = 'Error: Request timed out. The API is taking too long to respond. This might be due to PureSpectrum authentication. Check Render logs for details.';
                }}
                error.textContent = errorMsg;
                error.style.display = 'block';
                console.error('Dashboard error:', err);
            }} finally {{
                loading.style.display = 'none';
            }}
        }}
        
        // Load surveys on page load
        window.addEventListener('load', () => {{
            loadSurveys();
        }});
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


async def get_surveys():
    """API endpoint to get all live surveys"""
    if not PURESPECTRUM_USERNAME or not PURESPECTRUM_PASSWORD:
        return {"error": "PureSpectrum credentials not configured"}
    
    try:
        scraper = PureSpectrumScraper(PURESPECTRUM_USERNAME, PURESPECTRUM_PASSWORD)
        
        async with aiohttp.ClientSession() as session:
            if not await scraper.login(session):
                return {"error": "Failed to authenticate with PureSpectrum"}
            
            survey_data = await scraper.get_survey_data(session)
            
            return {"surveys": survey_data}
    except Exception as e:
        return {"error": str(e)}


async def get_quotas(survey_id: str):
    """API endpoint to get quotas for a specific survey"""
    if not PURESPECTRUM_USERNAME or not PURESPECTRUM_PASSWORD:
        return {"error": "PureSpectrum credentials not configured"}
    
    try:
        scraper = PureSpectrumScraper(PURESPECTRUM_USERNAME, PURESPECTRUM_PASSWORD)
        
        async with aiohttp.ClientSession() as session:
            if not await scraper.login(session):
                return {"error": "Failed to authenticate with PureSpectrum"}
            
            quotas = await scraper.get_survey_quotas(session, survey_id)
            
            return {"quotas": quotas}
    except Exception as e:
        return {"error": str(e)}
