import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
import threading
import time

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8050"))
UPDATE_INTERVAL = 30  # seconds

# Initialize Dash app
app = dash.Dash(__name__, title="AI Interviewer Analytics")

# Global data store
dashboard_data = {}

def fetch_analytics_data():
    """Fetch analytics data from the API"""
    global dashboard_data
    try:
        # In a real implementation, you'd need authentication
        # For now, we'll simulate the data structure
        response = requests.get(f"{API_BASE_URL}/analytics/dashboard")
        if response.status_code == 200:
            dashboard_data = response.json()
        else:
            # Fallback to mock data for development
            dashboard_data = get_mock_dashboard_data()
    except Exception as e:
        print(f"Failed to fetch analytics data: {e}")
        dashboard_data = get_mock_dashboard_data()

def get_mock_dashboard_data():
    """Generate mock data for development/testing"""
    import random
    
    # Generate mock data for the last 7 days
    dates = [(datetime.now() - timedelta(days=i)) for i in range(7)]
    
    return {
        "total_users": 150,
        "active_users_today": 23,
        "total_interviews": 456,
        "successful_interviews": 398,
        "completion_rate": 87.3,
        "total_api_cost": 234.56,
        "average_interview_duration": 892.5,
        "average_editor_iterations": 2.3,
        "popular_topics": [
            {"topic": "Product Management", "count": 45},
            {"topic": "Software Engineering", "count": 38},
            {"topic": "Data Science", "count": 32},
            {"topic": "Marketing Strategy", "count": 28},
            {"topic": "User Experience", "count": 22}
        ],
        "popular_templates": [
            {"name": "Technical Interview", "count": 67},
            {"name": "Behavioral Assessment", "count": 54},
            {"name": "Case Study Analysis", "count": 43},
            {"name": "Leadership Evaluation", "count": 32},
            {"name": "Cultural Fit", "count": 28}
        ],
        "user_activity": [
            {
                "date": date.strftime("%Y-%m-%d"),
                "interviews": random.randint(10, 50),
                "active_users": random.randint(5, 25)
            }
            for date in dates
        ],
        "cost_breakdown": {
            "openai": 156.78,
            "elevenlabs": 77.78
        },
        "interviews_last_7_days": [
            {
                "id": i,
                "topic": f"Topic {i}",
                "status": random.choice(["completed", "pending", "failed"]),
                "created_at": (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
                "duration": random.randint(300, 1800)
            }
            for i in range(1, 31)
        ]
    }

# Define the layout
app.layout = html.Div([
    html.Div([
        html.H1("AI Interviewer Platform Analytics", className="dashboard-title"),
        html.P("Real-time insights and performance metrics", className="dashboard-subtitle")
    ], className="header"),
    
    # Key metrics cards
    html.Div([
        html.Div([
            html.H3("Total Users", className="metric-title"),
            html.H2(id="total-users-metric", className="metric-value")
        ], className="metric-card"),
        
        html.Div([
            html.H3("Active Today", className="metric-title"),
            html.H2(id="active-users-metric", className="metric-value")
        ], className="metric-card"),
        
        html.Div([
            html.H3("Completion Rate", className="metric-title"),
            html.H2(id="completion-rate-metric", className="metric-value")
        ], className="metric-card"),
        
        html.Div([
            html.H3("Total API Cost", className="metric-title"),
            html.H2(id="api-cost-metric", className="metric-value")
        ], className="metric-card")
    ], className="metrics-row"),
    
    # Charts row 1
    html.Div([
        html.Div([
            dcc.Graph(id="user-activity-chart")
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id="completion-rate-chart")
        ], className="chart-container")
    ], className="charts-row"),
    
    # Charts row 2
    html.Div([
        html.Div([
            dcc.Graph(id="popular-topics-chart")
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id="cost-breakdown-chart")
        ], className="chart-container")
    ], className="charts-row"),
    
    # Performance metrics
    html.Div([
        html.Div([
            dcc.Graph(id="interview-duration-chart")
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id="template-usage-chart")
        ], className="chart-container")
    ], className="charts-row"),
    
    # Auto-refresh component
    dcc.Interval(
        id='interval-component',
        interval=UPDATE_INTERVAL * 1000,  # in milliseconds
        n_intervals=0
    )
], className="dashboard-container")

# Callbacks for updating metrics
@app.callback(
    [Output('total-users-metric', 'children'),
     Output('active-users-metric', 'children'),
     Output('completion-rate-metric', 'children'),
     Output('api-cost-metric', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    if not dashboard_data:
        return "0", "0", "0%", "$0.00"
    
    return (
        str(dashboard_data.get('total_users', 0)),
        str(dashboard_data.get('active_users_today', 0)),
        f"{dashboard_data.get('completion_rate', 0):.1f}%",
        f"${dashboard_data.get('total_api_cost', 0):.2f}"
    )

@app.callback(
    Output('user-activity-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_user_activity_chart(n):
    if not dashboard_data or 'user_activity' not in dashboard_data:
        return {}
    
    df = pd.DataFrame(dashboard_data['user_activity'])
    df['date'] = pd.to_datetime(df['date'])
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['interviews'], 
                  name="Interviews", line=dict(color='#1f77b4')),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['active_users'], 
                  name="Active Users", line=dict(color='#ff7f0e')),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Interviews", secondary_y=False)
    fig.update_yaxes(title_text="Active Users", secondary_y=True)
    
    fig.update_layout(
        title="User Activity Over Time",
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

@app.callback(
    Output('completion-rate-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_completion_rate_chart(n):
    if not dashboard_data:
        return {}
    
    total = dashboard_data.get('total_interviews', 0)
    successful = dashboard_data.get('successful_interviews', 0)
    failed = total - successful
    
    fig = go.Figure(data=[go.Pie(
        labels=['Completed', 'Failed'],
        values=[successful, failed],
        hole=0.4,
        marker_colors=['#2ecc71', '#e74c3c']
    )])
    
    fig.update_layout(
        title="Interview Completion Rate",
        template='plotly_white',
        annotations=[dict(text=f'{dashboard_data.get("completion_rate", 0):.1f}%', 
                         x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return fig

@app.callback(
    Output('popular-topics-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_popular_topics_chart(n):
    if not dashboard_data or 'popular_topics' not in dashboard_data:
        return {}
    
    topics_data = dashboard_data['popular_topics'][:5]  # Top 5
    
    fig = px.bar(
        x=[item['count'] for item in topics_data],
        y=[item['topic'] for item in topics_data],
        orientation='h',
        title="Most Popular Interview Topics",
        labels={'x': 'Number of Interviews', 'y': 'Topic'}
    )
    
    fig.update_layout(
        template='plotly_white',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

@app.callback(
    Output('cost-breakdown-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_cost_breakdown_chart(n):
    if not dashboard_data or 'cost_breakdown' not in dashboard_data:
        return {}
    
    cost_data = dashboard_data['cost_breakdown']
    
    fig = go.Figure(data=[go.Pie(
        labels=list(cost_data.keys()),
        values=list(cost_data.values()),
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:.2f}'
    )])
    
    fig.update_layout(
        title="API Cost Breakdown",
        template='plotly_white'
    )
    
    return fig

@app.callback(
    Output('interview-duration-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_interview_duration_chart(n):
    if not dashboard_data or 'interviews_last_7_days' not in dashboard_data:
        return {}
    
    interviews = dashboard_data['interviews_last_7_days']
    durations = [interview.get('duration', 0) / 60 for interview in interviews if interview.get('duration')]
    
    if not durations:
        return {}
    
    fig = px.histogram(
        x=durations,
        title="Interview Duration Distribution",
        labels={'x': 'Duration (minutes)', 'y': 'Count'},
        nbins=20
    )
    
    fig.update_layout(template='plotly_white')
    
    return fig

@app.callback(
    Output('template-usage-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_template_usage_chart(n):
    if not dashboard_data or 'popular_templates' not in dashboard_data:
        return {}
    
    templates_data = dashboard_data['popular_templates'][:5]  # Top 5
    
    fig = px.bar(
        x=[item['name'] for item in templates_data],
        y=[item['count'] for item in templates_data],
        title="Most Used Interview Templates",
        labels={'x': 'Template', 'y': 'Usage Count'}
    )
    
    fig.update_layout(
        template='plotly_white',
        xaxis_tickangle=-45
    )
    
    return fig

# CSS styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                background-color: #f8f9fa;
            }
            .dashboard-container {
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
            }
            .dashboard-title {
                margin: 0;
                font-size: 2.5rem;
                font-weight: 300;
            }
            .dashboard-subtitle {
                margin: 10px 0 0 0;
                font-size: 1.2rem;
                opacity: 0.9;
            }
            .metrics-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .metric-card {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 4px solid #667eea;
            }
            .metric-title {
                margin: 0 0 10px 0;
                color: #666;
                font-size: 1rem;
                font-weight: 500;
            }
            .metric-value {
                margin: 0;
                color: #333;
                font-size: 2.2rem;
                font-weight: 600;
            }
            .charts-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }
            .chart-container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 20px;
            }
            @media (max-width: 768px) {
                .charts-row {
                    grid-template-columns: 1fr;
                }
                .metrics-row {
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def run_data_updater():
    """Background thread to update data periodically"""
    while True:
        fetch_analytics_data()
        time.sleep(UPDATE_INTERVAL)

def run_dashboard():
    """Run the dashboard application"""
    # Initial data fetch
    fetch_analytics_data()
    
    # Start background data updater
    updater_thread = threading.Thread(target=run_data_updater, daemon=True)
    updater_thread.start()
    
    # Run the Dash app
    app.run_server(
        debug=False,
        host='0.0.0.0',
        port=DASHBOARD_PORT,
        dev_tools_hot_reload=False
    )

if __name__ == '__main__':
    run_dashboard() 