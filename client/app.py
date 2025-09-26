"""Streamlit client application for Data Sentinel."""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_option_menu import option_menu

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .anomaly-card {
        background: #fff5f5;
        border: 1px solid #fed7d7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .severity-1 { border-left: 4px solid #28a745; }
    .severity-2 { border-left: 4px solid #ffc107; }
    .severity-3 { border-left: 4px solid #fd7e14; }
    .severity-4 { border-left: 4px solid #dc3545; }
    .severity-5 { border-left: 4px solid #6f42c1; }
    
    .workflow-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-align: center;
    }
    
    .status-running { background: #e3f2fd; color: #1976d2; }
    .status-completed { background: #e8f5e8; color: #2e7d32; }
    .status-failed { background: #ffebee; color: #c62828; }
    .status-pending { background: #fff3e0; color: #f57c00; }
</style>
""", unsafe_allow_html=True)

def check_server_status():
    """Check if the server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_severity_color(severity):
    """Get color for severity level."""
    colors = {
        1: "#28a745",  # Green
        2: "#ffc107",  # Yellow
        3: "#fd7e14",  # Orange
        4: "#dc3545",  # Red
        5: "#6f42c1"   # Purple
    }
    return colors.get(severity, "#6c757d")

def get_status_badge(status):
    """Get status badge HTML."""
    status_colors = {
        "completed": "status-completed",
        "running": "status-running",
        "failed": "status-failed",
        "pending": "status-pending"
    }
    color_class = status_colors.get(status.lower(), "status-pending")
    return f'<span class="workflow-status {color_class}">{status.upper()}</span>'

def format_timestamp(timestamp):
    """Format timestamp for display."""
    if not timestamp:
        return "N/A"
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Data Sentinel",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Modern header
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ Data Sentinel</h1>
        <p style="margin: 0; font-size: 1.2rem;">AI-Powered Data Quality Monitoring & Anomaly Detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with modern navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        page = option_menu(
            menu_title=None,
            options=["Dashboard", "Datasets", "Workflows", "Anomalies", "Analytics", "Agent Dashboard", "Settings"],
            icons=["speedometer2", "database", "diagram-3", "exclamation-triangle", "graph-up", "robot", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#667eea", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )
        
        # Server status indicator
        st.markdown("---")
        st.markdown("### 🔗 Server Status")
        server_status = check_server_status()
        if server_status:
            st.success("🟢 Server Connected")
        else:
            st.error("🔴 Server Disconnected")
            st.warning("Please ensure the server is running on port 8000")
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Datasets":
        show_datasets()
    elif page == "Workflows":
        show_workflows()
    elif page == "Anomalies":
        show_anomalies()
    elif page == "Analytics":
        show_analytics()
    elif page == "Agent Dashboard":
        show_agent_dashboard()
    elif page == "Settings":
        show_settings()


def show_dashboard():
    """Show enhanced dashboard page."""
    st.markdown("### 📊 System Overview")
    
    # Auto-refresh toggle
    col1, col2 = st.columns([1, 4])
    with col1:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
    with col2:
        if auto_refresh:
            st.info("Dashboard will refresh every 30 seconds")
            time.sleep(30)
            st.rerun()
    
    # Get summary statistics with loading states
    with st.spinner("Loading dashboard data..."):
        try:
            # Get datasets count
            datasets_response = requests.get(f"{API_BASE_URL}/datasets", timeout=10)
            datasets = (
                datasets_response.json()
                if datasets_response.status_code == 200
                else []
            )
            
            # Get runs count
            runs_response = requests.get(f"{API_BASE_URL}/runs", timeout=10)
            runs = (
                runs_response.json()
                if runs_response.status_code == 200
                else []
            )
            
            # Get anomalies count
            anomalies_response = requests.get(f"{API_BASE_URL}/anomalies", timeout=10)
            anomalies = (
                anomalies_response.json()
                if anomalies_response.status_code == 200
                else []
            )
            
            # Enhanced metrics with icons and colors
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: #667eea;">📁</h3>
                    <h2 style="margin: 0; color: #333;">{len(datasets)}</h2>
                    <p style="margin: 0; color: #666;">Total Datasets</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: #28a745;">🏃</h3>
                    <h2 style="margin: 0; color: #333;">{len(runs)}</h2>
                    <p style="margin: 0; color: #666;">Total Runs</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                completed_runs = [r for r in runs if r.get("status") == "completed"]
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: #17a2b8;">✅</h3>
                    <h2 style="margin: 0; color: #333;">{len(completed_runs)}</h2>
                    <p style="margin: 0; color: #666;">Completed</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: #dc3545;">🚨</h3>
                    <h2 style="margin: 0; color: #333;">{len(anomalies)}</h2>
                    <p style="margin: 0; color: #666;">Anomalies</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                high_severity = [a for a in anomalies if a.get("severity", 0) >= 4]
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0; color: #6f42c1;">⚠️</h3>
                    <h2 style="margin: 0; color: #333;">{len(high_severity)}</h2>
                    <p style="margin: 0; color: #666;">High Severity</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts section
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Run Status Distribution")
                if runs:
                    run_status_counts = pd.Series([r.get("status", "unknown") for r in runs]).value_counts()
                    fig = px.pie(
                        values=run_status_counts.values,
                        names=run_status_counts.index,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(height=300, showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No run data available")
            
            with col2:
                st.markdown("### 🚨 Anomaly Severity Distribution")
                if anomalies:
                    anomaly_severity = [a.get("severity", 1) for a in anomalies]
                    severity_counts = pd.Series(anomaly_severity).value_counts().sort_index()
                    fig = px.bar(
                        x=severity_counts.index,
                        y=severity_counts.values,
                        color=severity_counts.index,
                        color_continuous_scale="Reds"
                    )
                    fig.update_layout(
                        height=300,
                        xaxis_title="Severity Level",
                        yaxis_title="Count",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No anomaly data available")
            
            # Recent activity section
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔍 Recent Anomalies")
                if anomalies:
                    recent_anomalies = anomalies[:5]
                    for anomaly in recent_anomalies:
                        severity = anomaly.get("severity", 1)
                        color = get_severity_color(severity)
                        st.markdown(f"""
                        <div class="anomaly-card severity-{severity}">
                            <strong>{anomaly.get('anomaly_type', 'Unknown')}</strong>
                            <br>
                            <small>Severity: {severity} | {format_timestamp(anomaly.get('detected_at'))}</small>
                            <br>
                            <span style="color: #666;">{anomaly.get('description', 'No description')[:100]}...</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recent anomalies found")
            
            with col2:
                st.markdown("### 📊 Recent Runs")
                if runs:
                    recent_runs = runs[:5]
                    for run in recent_runs:
                        status = run.get("status", "unknown")
                        status_badge = get_status_badge(status)
                        st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <strong>Run #{run.get('id', 'N/A')}</strong>
                            <br>
                            {status_badge}
                            <br>
                            <small>Started: {format_timestamp(run.get('started_at'))}</small>
                            <br>
                            <small>Dataset ID: {run.get('dataset_id', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recent runs found")
                    
        except Exception as e:
            st.error(f"Failed to load dashboard data: {str(e)}")
            st.info("Please ensure the server is running and accessible.")


def show_datasets():
    """Show enhanced datasets page."""
    st.markdown("### 📁 Dataset Management")
    
    # Add new dataset form with better UI
    with st.expander("➕ Add New Dataset", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Dataset Name", placeholder="e.g., Sales Data Q4 2024")
            description = st.text_area("Description", placeholder="Brief description of the dataset")
            source_type = st.selectbox("Source Type", ["file", "database", "api"])
            
            # File upload option for file type
            uploaded_file = None
            if source_type == "file":
                st.markdown("**📁 File Upload (Optional)**")
                uploaded_file = st.file_uploader(
                    "Upload a file", 
                    type=['csv', 'parquet', 'json', 'xlsx'],
                    help="Upload a file to automatically configure the source"
                )
                if uploaded_file:
                    st.success(f"✅ File uploaded: {uploaded_file.name}")
                    st.info("💡 The file will be saved to the data directory and the path will be auto-configured")
        
        with col2:
            st.markdown("**Source Configuration**")
            
            # Dynamic source config based on source type
            if source_type == "file":
                # Auto-configure if file is uploaded
                if uploaded_file:
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    default_config = f'''{{
  "file_path": "data/{uploaded_file.name}",
  "file_type": "{file_extension}",
  "delimiter": ",",
  "encoding": "utf-8"
}}'''
                    help_text = f"Auto-configured for uploaded file: {uploaded_file.name}"
                else:
                    default_config = '''{
  "file_path": "/path/to/your/file.csv",
  "file_type": "csv",
  "delimiter": ",",
  "encoding": "utf-8"
}'''
                    help_text = "File configuration: file_path, file_type (csv/parquet/json), delimiter, encoding"
            elif source_type == "database":
                default_config = '''{
  "host": "localhost",
  "port": 5432,
  "database": "your_database",
  "username": "your_username",
  "password": "your_password",
  "table": "your_table",
  "query": "SELECT * FROM your_table"
}'''
                help_text = "Database configuration: host, port, database, username, password, table/query"
            else:  # api
                default_config = '''{
  "url": "https://api.example.com/data",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer your_token"
  },
  "params": {
    "limit": 1000
  }
}'''
                help_text = "API configuration: url, method, headers, params, authentication"
            
            source_config = st.text_area(
                f"Source Config (JSON) - {source_type.upper()}", 
                value=default_config,
                height=150,
                help=help_text
            )
        
        # Submit button outside the columns
        if st.button("🚀 Add Dataset", type="primary"):
            if name and description:
                try:
                    config = json.loads(source_config) if source_config else {}
                    
                    # Handle file upload if present
                    if source_type == "file" and uploaded_file:
                        # Save uploaded file to data directory
                        import os
                        os.makedirs("data", exist_ok=True)
                        file_path = f"data/{uploaded_file.name}"
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Update config with actual file path
                        config["file_path"] = file_path
                        config["file_type"] = uploaded_file.name.split('.')[-1].lower()
                        
                        st.info(f"📁 File saved to: {file_path}")
                    
                    response = requests.post(f"{API_BASE_URL}/datasets", json={
                        "name": name,
                        "description": description,
                        "source_type": source_type,
                        "source_config": config
                    })
                    
                    if response.status_code == 200:
                        st.success("✅ Dataset added successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to add dataset: {response.text}")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON in source configuration")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please fill in all required fields")
    
    # List datasets with enhanced UI
    try:
        with st.spinner("Loading datasets..."):
            response = requests.get(f"{API_BASE_URL}/datasets", timeout=10)
            if response.status_code == 200:
                datasets = response.json()
                
                if datasets:
                    st.markdown(f"**Found {len(datasets)} dataset(s)**")
                    
                    # Display datasets in cards
                    for i, dataset in enumerate(datasets):
                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <h4 style="margin: 0; color: #333;">{dataset.get('name', 'Unnamed')}</h4>
                                    <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">{dataset.get('description', 'No description')}</p>
                                    <small style="color: #999;">ID: {dataset.get('id')} | Type: {dataset.get('source_type', 'unknown')}</small>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                if st.button(f"🔍 View Details", key=f"view_{dataset['id']}"):
                                    st.session_state[f"view_dataset_{dataset['id']}"] = True
                            
                            with col3:
                                if st.button(f"🚀 Run", key=f"run_{dataset['id']}"):
                                    run_workflow(dataset['id'])
                            
                            with col4:
                                if st.button(f"📊 Stats", key=f"stats_{dataset['id']}"):
                                    show_dataset_stats(dataset['id'])
                            
                            # Show dataset details if requested
                            if st.session_state.get(f"view_dataset_{dataset['id']}", False):
                                with st.expander(f"Dataset Details: {dataset.get('name')}", expanded=True):
                                    st.json(dataset)
                                    if st.button(f"Close", key=f"close_{dataset['id']}"):
                                        st.session_state[f"view_dataset_{dataset['id']}"] = False
                                        st.rerun()
                else:
                    st.info("📭 No datasets found. Create your first dataset using the form above.")
            else:
                st.error(f"❌ Failed to load datasets: {response.text}")
    except Exception as e:
        st.error(f"❌ Error loading datasets: {str(e)}")

def show_dataset_stats(dataset_id):
    """Show statistics for a specific dataset."""
    try:
        # Get runs for this dataset
        runs_response = requests.get(f"{API_BASE_URL}/runs", timeout=10)
        if runs_response.status_code == 200:
            runs = runs_response.json()
            dataset_runs = [r for r in runs if r.get('dataset_id') == dataset_id]
            
            if dataset_runs:
                st.markdown(f"### 📊 Statistics for Dataset {dataset_id}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Runs", len(dataset_runs))
                with col2:
                    completed = len([r for r in dataset_runs if r.get('status') == 'completed'])
                    st.metric("Completed", completed)
                with col3:
                    success_rate = (completed / len(dataset_runs)) * 100 if dataset_runs else 0
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                # Show recent runs
                st.markdown("**Recent Runs:**")
                for run in dataset_runs[:5]:
                    status = run.get('status', 'unknown')
                    status_badge = get_status_badge(status)
                    st.markdown(f"""
                    <div style="background: white; padding: 0.5rem; border-radius: 4px; margin: 0.25rem 0;">
                        Run #{run.get('id')} - {status_badge} - {format_timestamp(run.get('started_at'))}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No runs found for this dataset")
    except Exception as e:
        st.error(f"Error loading dataset stats: {str(e)}")


def show_workflows():
    """Show enhanced workflows page."""
    st.markdown("### 🔄 Workflow Management")
    
    # Workflow controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**Active Workflows & Run History**")
    with col2:
        if st.button("🔄 Refresh", type="secondary"):
            st.rerun()
    with col3:
        if st.button("📊 View Analytics", type="secondary"):
            st.session_state.show_workflow_analytics = True
    
    try:
        with st.spinner("Loading workflow data..."):
            # Get runs
            runs_response = requests.get(f"{API_BASE_URL}/runs", timeout=10)
            runs = runs_response.json() if runs_response.status_code == 200 else []
            
            # Get agent status
            agents_response = requests.get(f"{API_BASE_URL}/agents/status", timeout=10)
            agents_status = agents_response.json() if agents_response.status_code == 200 else {}
            
            if runs:
                st.markdown(f"**Found {len(runs)} workflow run(s)**")
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_filter = st.selectbox("Filter by Status", ["All", "completed", "running", "failed", "pending"])
                with col2:
                    dataset_filter = st.selectbox("Filter by Dataset", ["All"] + list(set([str(r.get('dataset_id', 'Unknown')) for r in runs])))
                with col3:
                    sort_by = st.selectbox("Sort by", ["started_at", "completed_at", "status", "dataset_id"])
                
                # Apply filters
                filtered_runs = runs
                if status_filter != "All":
                    filtered_runs = [r for r in filtered_runs if r.get('status') == status_filter]
                if dataset_filter != "All":
                    filtered_runs = [r for r in filtered_runs if str(r.get('dataset_id')) == dataset_filter]
                
                # Sort runs
                if sort_by == "started_at":
                    filtered_runs.sort(key=lambda x: x.get('started_at', ''), reverse=True)
                elif sort_by == "completed_at":
                    filtered_runs.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
                elif sort_by == "status":
                    filtered_runs.sort(key=lambda x: x.get('status', ''))
                elif sort_by == "dataset_id":
                    filtered_runs.sort(key=lambda x: x.get('dataset_id', 0))
                
                # Display runs
                for run in filtered_runs:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            status = run.get('status', 'unknown')
                            status_badge = get_status_badge(status)
                            st.markdown(f"""
                            <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <h4 style="margin: 0; color: #333;">Workflow Run #{run.get('id', 'N/A')}</h4>
                                <p style="margin: 0.5rem 0; color: #666;">
                                    Dataset ID: {run.get('dataset_id', 'N/A')} | 
                                    Started: {format_timestamp(run.get('started_at'))}
                                </p>
                                {status_badge}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button(f"🔍 Details", key=f"details_{run['id']}"):
                                st.session_state[f"show_run_details_{run['id']}"] = True
                        
                        with col3:
                            if run.get('status') == 'running':
                                if st.button(f"⏹️ Cancel", key=f"cancel_{run['id']}"):
                                    cancel_workflow(run['id'])
                        
                        with col4:
                            if st.button(f"📊 Logs", key=f"logs_{run['id']}"):
                                show_workflow_logs(run['id'])
                        
                        # Show run details if requested
                        if st.session_state.get(f"show_run_details_{run['id']}", False):
                            with st.expander(f"Run Details: #{run.get('id')}", expanded=True):
                                st.json(run)
                                if st.button(f"Close", key=f"close_details_{run['id']}"):
                                    st.session_state[f"show_run_details_{run['id']}"] = False
                                    st.rerun()
                
                # Agent status section
                if agents_status:
                    st.markdown("---")
                    st.markdown("### 🤖 Agent Status")
                    agents = agents_status.get('agents', {})
                    if agents:
                        col1, col2, col3, col4 = st.columns(4)
                        for i, (agent_name, stats) in enumerate(agents.items()):
                            col = [col1, col2, col3, col4][i % 4]
                            with col:
                                st.markdown(f"""
                                <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <h5 style="margin: 0; color: #333;">{agent_name}</h5>
                                    <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">
                                        Status: {stats.get('status', 'unknown')}
                                    </p>
                                    <small style="color: #999;">
                                        Runs: {stats.get('total_runs', 0)} | 
                                        Success: {stats.get('successful_runs', 0)}
                                    </small>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("📭 No workflow runs found. Start a workflow from the Datasets page.")
                
    except Exception as e:
        st.error(f"❌ Error loading workflow data: {str(e)}")

def show_workflow_logs(run_id):
    """Show logs for a specific workflow run."""
    st.markdown(f"### 📋 Logs for Run #{run_id}")
    st.info("Log viewing functionality will be implemented in future versions.")
    # TODO: Implement log viewing when backend supports it

def cancel_workflow(workflow_id):
    """Cancel a running workflow."""
    try:
        response = requests.post(f"{API_BASE_URL}/workflows/{workflow_id}/cancel", timeout=10)
        if response.status_code == 200:
            st.success("✅ Workflow cancelled successfully!")
            st.rerun()
        else:
            st.error(f"❌ Failed to cancel workflow: {response.text}")
    except Exception as e:
        st.error(f"❌ Error cancelling workflow: {str(e)}")


def show_anomalies():
    """Show enhanced anomalies page."""
    st.markdown("### 🚨 Anomaly Detection & Analysis")
    
    try:
        with st.spinner("Loading anomaly data..."):
            response = requests.get(f"{API_BASE_URL}/anomalies", timeout=10)
            if response.status_code == 200:
                anomalies = response.json()
                
                if anomalies:
                    st.markdown(f"**Found {len(anomalies)} anomaly(ies)**")
                    
                    # Filter and search options
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        severity_filter = st.selectbox("Filter by Severity", ["All", "1", "2", "3", "4", "5"])
                    with col2:
                        type_filter = st.selectbox("Filter by Type", ["All"] + list(set([a.get('anomaly_type', 'Unknown') for a in anomalies])))
                    with col3:
                        search_term = st.text_input("Search Description", placeholder="Search in descriptions...")
                    with col4:
                        sort_by = st.selectbox("Sort by", ["detected_at", "severity", "anomaly_type", "confidence"])
                    
                    # Apply filters
                    filtered_anomalies = anomalies
                    if severity_filter != "All":
                        filtered_anomalies = [a for a in filtered_anomalies if a.get('severity') == int(severity_filter)]
                    if type_filter != "All":
                        filtered_anomalies = [a for a in filtered_anomalies if a.get('anomaly_type') == type_filter]
                    if search_term:
                        filtered_anomalies = [a for a in filtered_anomalies if search_term.lower() in a.get('description', '').lower()]
                    
                    # Sort anomalies
                    if sort_by == "detected_at":
                        filtered_anomalies.sort(key=lambda x: x.get('detected_at', ''), reverse=True)
                    elif sort_by == "severity":
                        filtered_anomalies.sort(key=lambda x: x.get('severity', 0), reverse=True)
                    elif sort_by == "anomaly_type":
                        filtered_anomalies.sort(key=lambda x: x.get('anomaly_type', ''))
                    elif sort_by == "confidence":
                        filtered_anomalies.sort(key=lambda x: x.get('confidence', 0), reverse=True)
                    
                    # Display anomalies in cards
                    for anomaly in filtered_anomalies:
                        severity = anomaly.get('severity', 1)
                        color = get_severity_color(severity)
                        
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div class="anomaly-card severity-{severity}">
                                    <div style="display: flex; justify-content: space-between; align-items: start;">
                                        <div>
                                            <h4 style="margin: 0; color: #333;">{anomaly.get('anomaly_type', 'Unknown Anomaly')}</h4>
                                            <p style="margin: 0.5rem 0; color: #666;">
                                                {anomaly.get('description', 'No description available')}
                                            </p>
                                            <div style="display: flex; gap: 1rem; font-size: 0.9rem; color: #666;">
                                                <span>Severity: <strong style="color: {color};">{severity}</strong></span>
                                                <span>Confidence: <strong>{anomaly.get('confidence', 'N/A')}</strong></span>
                                                <span>Detected: {format_timestamp(anomaly.get('detected_at'))}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                if st.button(f"🔍 Details", key=f"anomaly_details_{anomaly['id']}"):
                                    st.session_state[f"show_anomaly_details_{anomaly['id']}"] = True
                            
                            # Show anomaly details if requested
                            if st.session_state.get(f"show_anomaly_details_{anomaly['id']}", False):
                                with st.expander(f"Anomaly Details: {anomaly.get('anomaly_type')}", expanded=True):
                                    st.json(anomaly)
                                    if st.button(f"Close", key=f"close_anomaly_{anomaly['id']}"):
                                        st.session_state[f"show_anomaly_details_{anomaly['id']}"] = False
                                        st.rerun()
                    
                    # Anomaly analytics
                    st.markdown("---")
                    st.markdown("### 📊 Anomaly Analytics")
                    
                    if filtered_anomalies:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Anomaly type distribution
                            anomaly_types = [a.get('anomaly_type', 'Unknown') for a in filtered_anomalies]
                            type_counts = pd.Series(anomaly_types).value_counts()
                            
                            fig = px.pie(
                                values=type_counts.values,
                                names=type_counts.index,
                                title="Anomaly Types Distribution",
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Severity distribution
                            severities = [a.get('severity', 1) for a in filtered_anomalies]
                            severity_counts = pd.Series(severities).value_counts().sort_index()
                            
                            fig = px.bar(
                                x=severity_counts.index,
                                y=severity_counts.values,
                                title="Severity Distribution",
                                color=severity_counts.index,
                                color_continuous_scale="Reds"
                            )
                            fig.update_layout(
                                height=400,
                                xaxis_title="Severity Level",
                                yaxis_title="Count",
                                showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Timeline analysis
                        st.markdown("### 📈 Anomaly Timeline")
                        if len(filtered_anomalies) > 1:
                            timeline_data = []
                            for anomaly in filtered_anomalies:
                                timeline_data.append({
                                    'date': anomaly.get('detected_at', ''),
                                    'severity': anomaly.get('severity', 1),
                                    'type': anomaly.get('anomaly_type', 'Unknown')
                                })
                            
                            df_timeline = pd.DataFrame(timeline_data)
                            df_timeline['date'] = pd.to_datetime(df_timeline['date'], errors='coerce')
                            df_timeline = df_timeline.dropna()
                            
                            if not df_timeline.empty:
                                fig = px.scatter(
                                    df_timeline,
                                    x='date',
                                    y='severity',
                                    color='type',
                                    size='severity',
                                    title="Anomaly Timeline by Severity",
                                    hover_data=['type', 'severity']
                                )
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("🎉 No anomalies found! Your data quality looks good.")
            else:
                st.error(f"❌ Failed to load anomalies: {response.text}")
    except Exception as e:
        st.error(f"❌ Error loading anomalies: {str(e)}")

def show_analytics():
    """Show analytics page with comprehensive insights."""
    st.markdown("### 📊 Advanced Analytics & Insights")
    
    try:
        with st.spinner("Loading analytics data..."):
            # Get all data
            datasets_response = requests.get(f"{API_BASE_URL}/datasets", timeout=10)
            runs_response = requests.get(f"{API_BASE_URL}/runs", timeout=10)
            anomalies_response = requests.get(f"{API_BASE_URL}/anomalies", timeout=10)
            
            datasets = datasets_response.json() if datasets_response.status_code == 200 else []
            runs = runs_response.json() if runs_response.status_code == 200 else []
            anomalies = anomalies_response.json() if anomalies_response.status_code == 200 else []
            
            if not any([datasets, runs, anomalies]):
                st.info("📭 No data available for analytics. Please run some workflows first.")
                return
            
            # Key Performance Indicators
            st.markdown("### 🎯 Key Performance Indicators")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_runs = len(runs)
                completed_runs = len([r for r in runs if r.get('status') == 'completed'])
                success_rate = (completed_runs / total_runs * 100) if total_runs > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%", delta=f"{completed_runs}/{total_runs}")
            
            with col2:
                avg_anomalies_per_run = len(anomalies) / total_runs if total_runs > 0 else 0
                st.metric("Avg Anomalies/Run", f"{avg_anomalies_per_run:.1f}")
            
            with col3:
                high_severity_anomalies = len([a for a in anomalies if a.get('severity', 0) >= 4])
                st.metric("High Severity Issues", high_severity_anomalies)
            
            with col4:
                unique_anomaly_types = len(set([a.get('anomaly_type', 'Unknown') for a in anomalies]))
                st.metric("Anomaly Types", unique_anomaly_types)
            
            # Performance Trends
            st.markdown("---")
            st.markdown("### 📈 Performance Trends")
            
            if runs:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Run status over time
                    run_data = []
                    for run in runs:
                        run_data.append({
                            'date': run.get('started_at', ''),
                            'status': run.get('status', 'unknown'),
                            'dataset_id': run.get('dataset_id', 0)
                        })
                    
                    df_runs = pd.DataFrame(run_data)
                    df_runs['date'] = pd.to_datetime(df_runs['date'], errors='coerce')
                    df_runs = df_runs.dropna()
                    
                    if not df_runs.empty:
                        status_counts = df_runs.groupby([df_runs['date'].dt.date, 'status']).size().unstack(fill_value=0)
                        fig = px.area(
                            status_counts,
                            title="Run Status Over Time",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Dataset performance
                    dataset_performance = {}
                    for run in runs:
                        dataset_id = run.get('dataset_id', 0)
                        if dataset_id not in dataset_performance:
                            dataset_performance[dataset_id] = {'total': 0, 'completed': 0}
                        dataset_performance[dataset_id]['total'] += 1
                        if run.get('status') == 'completed':
                            dataset_performance[dataset_id]['completed'] += 1
                    
                    if dataset_performance:
                        perf_data = []
                        for dataset_id, stats in dataset_performance.items():
                            success_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                            perf_data.append({
                                'Dataset ID': dataset_id,
                                'Success Rate': success_rate,
                                'Total Runs': stats['total']
                            })
                        
                        df_perf = pd.DataFrame(perf_data)
                        fig = px.bar(
                            df_perf,
                            x='Dataset ID',
                            y='Success Rate',
                            title="Dataset Performance",
                            color='Total Runs',
                            color_continuous_scale="Viridis"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
            # Anomaly Analysis
            if anomalies:
                st.markdown("---")
                st.markdown("### 🚨 Anomaly Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Anomaly severity heatmap
                    anomaly_data = []
                    for anomaly in anomalies:
                        anomaly_data.append({
                            'type': anomaly.get('anomaly_type', 'Unknown'),
                            'severity': anomaly.get('severity', 1),
                            'confidence': anomaly.get('confidence', 0)
                        })
                    
                    df_anomalies = pd.DataFrame(anomaly_data)
                    severity_pivot = df_anomalies.groupby(['type', 'severity']).size().unstack(fill_value=0)
                    
                    if not severity_pivot.empty:
                        fig = px.imshow(
                            severity_pivot.values,
                            x=severity_pivot.columns,
                            y=severity_pivot.index,
                            title="Anomaly Type vs Severity Heatmap",
                            color_continuous_scale="Reds"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Confidence vs Severity scatter
                    fig = px.scatter(
                        df_anomalies,
                        x='confidence',
                        y='severity',
                        color='type',
                        size='severity',
                        title="Confidence vs Severity",
                        hover_data=['type']
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.markdown("---")
            st.markdown("### 💡 Recommendations")
            
            recommendations = []
            
            if len(anomalies) > 0:
                high_severity = [a for a in anomalies if a.get('severity', 0) >= 4]
                if high_severity:
                    recommendations.append("🔴 **High Priority**: Address high-severity anomalies immediately")
                
                anomaly_types = [a.get('anomaly_type', 'Unknown') for a in anomalies]
                most_common = pd.Series(anomaly_types).mode().iloc[0] if len(anomaly_types) > 0 else None
                if most_common:
                    recommendations.append(f"📊 **Focus Area**: '{most_common}' is the most common anomaly type")
            
            if total_runs > 0 and success_rate < 80:
                recommendations.append("⚠️ **Performance**: Success rate is below 80%, investigate failed runs")
            
            if len(datasets) > 0 and total_runs == 0:
                recommendations.append("🚀 **Action**: Start running workflows on your datasets")
            
            if not recommendations:
                recommendations.append("🎉 **Great Job**: Your data quality monitoring is performing well!")
            
            for rec in recommendations:
                st.markdown(rec)
                
    except Exception as e:
        st.error(f"❌ Error loading analytics: {str(e)}")


def show_agent_dashboard():
    """Show agent-specific dashboard with performance metrics."""
    st.markdown("## 🤖 Agent Performance Dashboard")
    
    try:
        # Get recent runs for agent analysis
        runs_response = requests.get(f"{API_BASE_URL}/runs", timeout=10)
        runs = runs_response.json() if runs_response.status_code == 200 else []
        
        if not runs:
            st.info("🤖 No workflow runs available for agent analysis. Run some workflows first!")
            return
        
        # Agent Performance Overview
        st.markdown("### 📊 Agent Performance Overview")
        
        # Calculate agent performance metrics
        agent_metrics = {}
        agent_names = ["data_loading", "validation", "anomaly_detection", "remediation", "notification", "learning"]
        
        for agent_name in agent_names:
            agent_metrics[agent_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "avg_confidence": 0.0,
                "total_time": 0.0
            }
        
        # Analyze runs for agent performance
        for run in runs:
            if run.get('results'):
                try:
                    results = json.loads(run['results']) if isinstance(run['results'], str) else run['results']
                    
                    for agent_name in agent_names:
                        if agent_name in results:
                            agent_result = results[agent_name]
                            agent_metrics[agent_name]["total_executions"] += 1
                            
                            if agent_result.get("status") == "completed":
                                agent_metrics[agent_name]["successful_executions"] += 1
                            else:
                                agent_metrics[agent_name]["failed_executions"] += 1
                            
                            confidence = agent_result.get("confidence", 0.0)
                            agent_metrics[agent_name]["avg_confidence"] += confidence
                            
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Calculate averages
        for agent_name in agent_names:
            total = agent_metrics[agent_name]["total_executions"]
            if total > 0:
                agent_metrics[agent_name]["avg_confidence"] /= total
                agent_metrics[agent_name]["success_rate"] = agent_metrics[agent_name]["successful_executions"] / total
            else:
                agent_metrics[agent_name]["success_rate"] = 0.0
        
        # Display agent performance cards
        cols = st.columns(3)
        for i, (agent_name, metrics) in enumerate(agent_metrics.items()):
            with cols[i % 3]:
                success_rate = metrics["success_rate"]
                avg_confidence = metrics["avg_confidence"]
                total_executions = metrics["total_executions"]
                
                # Status color
                if success_rate >= 0.9:
                    status_color = "#28a745"
                    status_icon = "✅"
                elif success_rate >= 0.7:
                    status_color = "#ffc107"
                    status_icon = "⚠️"
                else:
                    status_color = "#dc3545"
                    status_icon = "❌"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{status_icon} {agent_name.replace('_', ' ').title()}</h4>
                    <p><strong>Success Rate:</strong> <span style="color: {status_color}">{success_rate:.1%}</span></p>
                    <p><strong>Avg Confidence:</strong> {avg_confidence:.1%}</p>
                    <p><strong>Total Executions:</strong> {total_executions}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Agent Performance Chart
        st.markdown("### 📈 Agent Success Rates")
        
        agent_df = pd.DataFrame([
            {
                "Agent": agent_name.replace('_', ' ').title(),
                "Success Rate": metrics["success_rate"],
                "Avg Confidence": metrics["avg_confidence"],
                "Total Executions": metrics["total_executions"]
            }
            for agent_name, metrics in agent_metrics.items()
            if metrics["total_executions"] > 0
        ])
        
        if not agent_df.empty:
            fig = px.bar(
                agent_df,
                x="Agent",
                y="Success Rate",
                title="Agent Success Rates",
                color="Success Rate",
                color_continuous_scale="RdYlGn"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Agent performance table
            st.markdown("### 📋 Detailed Agent Performance")
            st.dataframe(agent_df, use_container_width=True)
        
        # Real-time Agent Status
        st.markdown("### 🔴 Real-time Agent Status")
        
        # Simulate real-time status (in a real implementation, this would be WebSocket or polling)
        agent_status = {}
        for agent_name in agent_names:
            # Simulate status based on recent performance
            if agent_metrics[agent_name]["total_executions"] > 0:
                if agent_metrics[agent_name]["success_rate"] >= 0.9:
                    status = "🟢 Healthy"
                elif agent_metrics[agent_name]["success_rate"] >= 0.7:
                    status = "🟡 Warning"
                else:
                    status = "🔴 Critical"
            else:
                status = "⚪ Idle"
            
            agent_status[agent_name] = status
        
        # Display status grid
        status_cols = st.columns(3)
        for i, (agent_name, status) in enumerate(agent_status.items()):
            with status_cols[i % 3]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{agent_name.replace('_', ' ').title()}</h4>
                    <p><strong>Status:</strong> {status}</p>
                    <p><strong>Last Check:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Agent Recommendations
        st.markdown("### 💡 Agent Recommendations")
        
        recommendations = []
        
        for agent_name, metrics in agent_metrics.items():
            if metrics["total_executions"] > 0:
                if metrics["success_rate"] < 0.7:
                    recommendations.append(f"🔧 **{agent_name.replace('_', ' ').title()}**: Low success rate ({metrics['success_rate']:.1%}). Consider reviewing configuration.")
                
                if metrics["avg_confidence"] < 0.6:
                    recommendations.append(f"📊 **{agent_name.replace('_', ' ').title()}**: Low confidence ({metrics['avg_confidence']:.1%}). Consider improving data quality.")
        
        if not recommendations:
            recommendations.append("✅ All agents are performing well!")
        
        for rec in recommendations:
            st.markdown(rec)
        
        # Auto-refresh button
        if st.button("🔄 Refresh Agent Status"):
            st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error loading agent dashboard: {str(e)}")

def show_settings():
    """Show enhanced settings page."""
    st.markdown("### ⚙️ Settings & Configuration")
    
    # API Configuration
    st.markdown("#### 🔗 API Configuration")
    col1, col2 = st.columns([2, 1])
    with col1:
        api_url = st.text_input("API Base URL", value=API_BASE_URL, disabled=True)
    with col2:
        if st.button("Test Connection"):
            if check_server_status():
                st.success("✅ Connection successful!")
            else:
                st.error("❌ Connection failed!")
    
    # Display Configuration
    st.markdown("#### 🎨 Display Configuration")
    col1, col2 = st.columns(2)
    with col1:
        auto_refresh_interval = st.slider("Auto-refresh interval (seconds)", 10, 300, 30)
        st.session_state.auto_refresh_interval = auto_refresh_interval
    with col2:
        items_per_page = st.selectbox("Items per page", [10, 25, 50, 100], index=1)
        st.session_state.items_per_page = items_per_page
    
    # Data Configuration
    st.markdown("#### 📊 Data Configuration")
    col1, col2 = st.columns(2)
    with col1:
        default_severity_threshold = st.slider("Default severity threshold", 1, 5, 3)
        st.session_state.severity_threshold = default_severity_threshold
    with col2:
        show_confidence_scores = st.checkbox("Show confidence scores", value=True)
        st.session_state.show_confidence = show_confidence_scores
    
    # LLM Configuration
    st.markdown("#### 🤖 LLM Configuration")
    st.info("💡 LLM settings are configured on the server side. Contact your administrator to modify these settings.")
    
    # System Information
    st.markdown("#### ℹ️ System Information")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Version Information:**
        - Data Sentinel: v0.1.0
        - Frontend: Streamlit
        - Backend: FastAPI
        - Database: SQLite
        """)
    with col2:
        st.markdown("""
        **Features:**
        - AI-powered anomaly detection
        - Real-time data quality monitoring
        - Interactive visualizations
        - Workflow management
        - Advanced analytics
        """)
    
    # Export/Import Settings
    st.markdown("#### 📤 Export/Import")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Settings"):
            settings = {
                "auto_refresh_interval": st.session_state.get("auto_refresh_interval", 30),
                "items_per_page": st.session_state.get("items_per_page", 25),
                "severity_threshold": st.session_state.get("severity_threshold", 3),
                "show_confidence": st.session_state.get("show_confidence", True)
            }
            st.download_button(
                label="Download Settings JSON",
                data=json.dumps(settings, indent=2),
                file_name="data_sentinel_settings.json",
                mime="application/json"
            )
    with col2:
        uploaded_file = st.file_uploader("Import Settings", type=['json'])
        if uploaded_file:
            try:
                settings = json.load(uploaded_file)
                st.session_state.update(settings)
                st.success("✅ Settings imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error importing settings: {str(e)}")
    
    # About Section
    st.markdown("---")
    st.markdown("#### 🛡️ About Data Sentinel")
    st.markdown("""
    **Data Sentinel** is an AI-powered data quality monitoring and anomaly detection platform.
    
    **Key Features:**
    - 🔍 Intelligent anomaly detection using machine learning
    - 📊 Real-time data quality monitoring
    - 🚀 Automated workflow orchestration
    - 📈 Advanced analytics and reporting
    - 🎯 Customizable alerting and notifications
    
    **Technology Stack:**
    - Backend: FastAPI, SQLAlchemy, LangChain
    - Frontend: Streamlit, Plotly
    - AI/ML: OpenAI GPT, scikit-learn
    - Database: SQLite (development), PostgreSQL (production)
    
    For support and documentation, please contact your system administrator.
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Data Sentinel v0.1.0 | Built with ❤️ for data quality monitoring
    </div>
    """, unsafe_allow_html=True)


def create_data_loading_display(data_loading_result):
    """Create display for data loading results."""
    def display():
        if not data_loading_result:
            st.info("No data loading results available.")
            return
        
        status = data_loading_result.get("status", "unknown")
        data = data_loading_result.get("data", {})
        confidence = data_loading_result.get("confidence", 0.0)
        
        # Status indicator
        if status == "completed":
            st.success("✅ Data loaded successfully")
        else:
            st.error(f"❌ Data loading failed: {status}")
        
        # Data info
        if data:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", data.get("data_info", {}).get("rows", "N/A"))
            with col2:
                st.metric("Columns", data.get("data_info", {}).get("columns", "N/A"))
            with col3:
                st.metric("Confidence", f"{confidence:.1%}")
            
            # Data types
            if "data_info" in data and "data_types" in data["data_info"]:
                st.markdown("**Data Types:**")
                data_types = data["data_info"]["data_types"]
                if isinstance(data_types, dict):
                    types_df = pd.DataFrame([
                        {"Column": col, "Type": str(dtype)}
                        for col, dtype in data_types.items()
                    ])
                    st.dataframe(types_df, use_container_width=True)
            
            # Sample data
            if "data_info" in data and "sample_data" in data["data_info"]:
                st.markdown("**Sample Data:**")
                sample_data = data["data_info"]["sample_data"]
                if isinstance(sample_data, list) and sample_data:
                    sample_df = pd.DataFrame(sample_data)
                    st.dataframe(sample_df, use_container_width=True)
        
        # Raw result
        with st.expander("Raw Data Loading Result"):
            st.json(data_loading_result)
    
    return display

def create_validation_display(validation_result):
    """Create display for validation results."""
    def display():
        if not validation_result:
            st.info("No validation results available.")
            return
        
        st.success("✅ Validation completed")
        
        # Validation summary
        if isinstance(validation_result, dict):
            # Basic checks
            if "basic_checks" in validation_result:
                basic_checks = validation_result["basic_checks"]
                st.markdown("**Basic Data Quality Checks:**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    missing_values = basic_checks.get("missing_values", {})
                    total_missing = sum(missing_values.values()) if isinstance(missing_values, dict) else 0
                    st.metric("Missing Values", total_missing)
                
                with col2:
                    duplicates = basic_checks.get("duplicate_rows", 0)
                    st.metric("Duplicate Rows", duplicates)
                
                with col3:
                    empty_cols = len(basic_checks.get("empty_columns", []))
                    st.metric("Empty Columns", empty_cols)
            
            # Anomalies
            if "anomalies" in validation_result:
                anomalies = validation_result["anomalies"]
                if anomalies:
                    st.markdown("**Validation Anomalies:**")
                    for i, anomaly in enumerate(anomalies):
                        severity = anomaly.get("severity", "unknown")
                        anomaly_type = anomaly.get("type", "unknown")
                        description = anomaly.get("description", "No description")
                        
                        st.markdown(f"""
                        <div class="anomaly-card severity-{severity}">
                            <strong>{anomaly_type.replace('_', ' ').title()}</strong><br>
                            {description}
                        </div>
                        """, unsafe_allow_html=True)
        
        # Raw result
        with st.expander("Raw Validation Result"):
            st.json(validation_result)
    
    return display

def create_anomaly_display(explanations):
    """Create display for anomaly detection results."""
    def display():
        if not explanations:
            st.info("No anomalies detected.")
            return
        
        st.warning(f"🚨 {len(explanations)} anomalies detected")
        
        if isinstance(explanations, list):
            for i, explanation in enumerate(explanations):
                st.markdown(f"**Anomaly {i+1}:**")
                if isinstance(explanation, dict):
                    # Extract key information
                    anomaly_type = explanation.get("anomaly_type", "unknown")
                    severity = explanation.get("severity", 1)
                    description = explanation.get("description", "No description")
                    confidence = explanation.get("confidence", 0.0)
                    
                    # Display anomaly card
                    st.markdown(f"""
                    <div class="anomaly-card severity-{severity}">
                        <strong>Type:</strong> {anomaly_type.replace('_', ' ').title()}<br>
                        <strong>Severity:</strong> {severity}/5<br>
                        <strong>Confidence:</strong> {confidence:.1%}<br>
                        <strong>Description:</strong> {description}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show details if available
                    if "details" in explanation:
                        with st.expander(f"Details for Anomaly {i+1}"):
                            st.json(explanation["details"])
                else:
                    st.write(explanation)
        else:
            st.json(explanations)
    
    return display

def create_remediation_display(remediation_result):
    """Create display for remediation results."""
    def display():
        if not remediation_result:
            st.info("No remediation results available.")
            return
        
        status = remediation_result.get("status", "unknown")
        data = remediation_result.get("data", {})
        
        if status == "completed":
            st.success("✅ Remediation completed")
        else:
            st.error(f"❌ Remediation failed: {status}")
        
        if data:
            # Remediation summary
            if "remediation_plans" in data:
                plans = data["remediation_plans"]
                st.markdown(f"**Remediation Plans: {len(plans)}**")
                
                for i, plan in enumerate(plans):
                    action = plan.get("action", "unknown")
                    risk_level = plan.get("risk_level", "unknown")
                    description = plan.get("description", "No description")
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Plan {i+1}: {action.replace('_', ' ').title()}</h4>
                        <p><strong>Risk Level:</strong> {risk_level}</p>
                        <p><strong>Description:</strong> {description}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Execution results
            if "execution_results" in data:
                results = data["execution_results"]
                st.markdown(f"**Execution Results: {len(results)}**")
                
                for i, result in enumerate(results):
                    plan_id = result.get("plan_id", f"plan_{i+1}")
                    exec_status = result.get("status", "unknown")
                    
                    if exec_status == "completed":
                        st.success(f"✅ {plan_id}: Completed")
                    else:
                        st.error(f"❌ {plan_id}: {exec_status}")
        
        # Raw result
        with st.expander("Raw Remediation Result"):
            st.json(remediation_result)
    
    return display

def create_notification_display(notification_result):
    """Create display for notification results."""
    def display():
        if not notification_result:
            st.info("No notification results available.")
            return
        
        status = notification_result.get("status", "unknown")
        data = notification_result.get("data", {})
        
        if status == "completed":
            st.success("✅ Notifications sent")
        else:
            st.error(f"❌ Notifications failed: {status}")
        
        if data:
            # Notification summary
            notifications_sent = data.get("notifications_sent", 0)
            escalations_processed = data.get("escalations_processed", 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Notifications Sent", notifications_sent)
            with col2:
                st.metric("Escalations Processed", escalations_processed)
            
            # Notification results
            if "notification_results" in data:
                results = data["notification_results"]
                st.markdown("**Notification Results:**")
                
                for result in results:
                    anomaly_id = result.get("anomaly_id", "unknown")
                    status = result.get("status", "unknown")
                    channels = result.get("channels", [])
                    
                    if status == "sent":
                        st.success(f"✅ Anomaly {anomaly_id}: Sent via {len(channels)} channels")
                    else:
                        st.error(f"❌ Anomaly {anomaly_id}: {status}")
            
            # Escalation results
            if "escalation_results" in data:
                escalations = data["escalation_results"]
                if escalations:
                    st.markdown("**Escalation Results:**")
                    for escalation in escalations:
                        escalation_id = escalation.get("escalation_id", "unknown")
                        level = escalation.get("level", "unknown")
                        status = escalation.get("status", "unknown")
                        
                        if status == "completed":
                            st.warning(f"🚨 {escalation_id}: Escalated to {level}")
                        else:
                            st.error(f"❌ {escalation_id}: {status}")
        
        # Raw result
        with st.expander("Raw Notification Result"):
            st.json(notification_result)
    
    return display

def create_learning_display(learning_result):
    """Create display for learning results."""
    def display():
        if not learning_result:
            st.info("No learning results available.")
            return
        
        status = learning_result.get("status", "unknown")
        data = learning_result.get("data", {})
        
        if status == "completed":
            st.success("✅ Learning completed")
        else:
            st.error(f"❌ Learning failed: {status}")
        
        if data:
            # Learning summary
            total_insights = data.get("total_insights", 0)
            model_updates = data.get("model_updates_count", 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Learning Insights", total_insights)
            with col2:
                st.metric("Model Updates", model_updates)
            
            # Learning insights
            if "learning_insights" in data:
                insights = data["learning_insights"]
                if insights:
                    st.markdown("**Learning Insights:**")
                    
                    for insight in insights:
                        insight_type = insight.get("insight_type", "unknown")
                        description = insight.get("description", "No description")
                        confidence = insight.get("confidence", 0.0)
                        impact_score = insight.get("impact_score", 0.0)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{insight_type.replace('_', ' ').title()}</h4>
                            <p><strong>Description:</strong> {description}</p>
                            <p><strong>Confidence:</strong> {confidence:.1%}</p>
                            <p><strong>Impact Score:</strong> {impact_score:.1%}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Model updates
            if "model_updates" in data:
                updates = data["model_updates"]
                if updates:
                    st.markdown("**Model Updates:**")
                    
                    for update in updates:
                        model_name = update.get("model_name", "unknown")
                        update_type = update.get("update_type", "unknown")
                        validation_score = update.get("validation_score", 0.0)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{model_name.replace('_', ' ').title()}</h4>
                            <p><strong>Update Type:</strong> {update_type}</p>
                            <p><strong>Validation Score:</strong> {validation_score:.1%}</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Raw result
        with st.expander("Raw Learning Result"):
            st.json(learning_result)
    
    return display

def run_workflow(dataset_id: int):
    """Run enhanced workflow for a dataset."""
    try:
        # Create a progress container
        progress_container = st.container()
        with progress_container:
            st.markdown(f"### 🚀 Running Workflow for Dataset {dataset_id}")
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Initializing
            status_text.text("🔄 Initializing workflow...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            # Step 2: Starting workflow
            status_text.text("🚀 Starting data quality analysis...")
            progress_bar.progress(30)
            
            response = requests.post(f"{API_BASE_URL}/workflow", json={
                "dataset_id": dataset_id,
                "include_llm_explanation": True
            }, timeout=60)
            
            # Step 3: Processing results
            status_text.text("📊 Processing results...")
            progress_bar.progress(80)
            
            if response.status_code == 200:
                result = response.json()
                
                # Step 4: Complete
                status_text.text("✅ Workflow completed successfully!")
                progress_bar.progress(100)
                time.sleep(1)
                
                # Clear progress indicators
                progress_container.empty()
                
                # Show results
                st.success(f"🎉 Workflow completed! Run ID: {result.get('run_id')}")
                
                # Display agent status overview
                if result.get("agent_status"):
                    st.markdown("### 🤖 Agent Execution Status")
                    agent_status = result["agent_status"]
                    
                    # Create columns for agent status cards
                    cols = st.columns(len(agent_status))
                    for i, (agent_name, status_info) in enumerate(agent_status.items()):
                        with cols[i]:
                            status = status_info.get("status", "unknown")
                            confidence = status_info.get("confidence", 0.0)
                            exec_time = status_info.get("execution_time", 0.0)
                            
                            # Status color
                            if status == "completed":
                                status_color = "#28a745"
                                status_icon = "✅"
                            elif status == "failed":
                                status_color = "#dc3545"
                                status_icon = "❌"
                            else:
                                status_color = "#ffc107"
                                status_icon = "⏳"
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>{status_icon} {agent_name.replace('_', ' ').title()}</h4>
                                <p><strong>Status:</strong> <span style="color: {status_color}">{status}</span></p>
                                <p><strong>Confidence:</strong> {confidence:.1%}</p>
                                <p><strong>Time:</strong> {exec_time:.2f}s</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Display performance metrics
                if result.get("performance_metrics"):
                    with st.expander("⏱️ Performance Metrics", expanded=False):
                        perf_metrics = result["performance_metrics"]
                        if perf_metrics:
                            # Create performance chart
                            agents = list(perf_metrics.keys())
                            times = list(perf_metrics.values())
                            
                            fig = px.bar(
                                x=agents, 
                                y=times,
                                title="Agent Execution Times",
                                labels={"x": "Agent", "y": "Execution Time (seconds)"}
                            )
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Performance table
                            perf_df = pd.DataFrame([
                                {"Agent": agent, "Time (s)": time}
                                for agent, time in perf_metrics.items()
                            ])
                            st.dataframe(perf_df, use_container_width=True)
                
                # Display all agent results in tabs
                st.markdown("### 📊 Detailed Agent Results")
                
                # Create tabs for each agent
                tab_names = []
                tab_contents = []
                
                # Data Loading Results
                if result.get("data_loading_result"):
                    tab_names.append("📁 Data Loading")
                    tab_contents.append(create_data_loading_display(result["data_loading_result"]))
                
                # Validation Results
                if result.get("validation_result"):
                    tab_names.append("📋 Validation")
                    tab_contents.append(create_validation_display(result["validation_result"]))
                
                # Anomaly Detection Results
                if result.get("explanations"):
                    tab_names.append("🚨 Anomaly Detection")
                    tab_contents.append(create_anomaly_display(result["explanations"]))
                
                # Remediation Results
                if result.get("remediation_result"):
                    tab_names.append("🔧 Remediation")
                    tab_contents.append(create_remediation_display(result["remediation_result"]))
                
                # Notification Results
                if result.get("notification_result"):
                    tab_names.append("📢 Notifications")
                    tab_contents.append(create_notification_display(result["notification_result"]))
                
                # Learning Results
                if result.get("learning_result"):
                    tab_names.append("🧠 Learning")
                    tab_contents.append(create_learning_display(result["learning_result"]))
                
                # Display tabs if we have content
                if tab_names:
                    tabs = st.tabs(tab_names)
                    for i, (tab, content) in enumerate(zip(tabs, tab_contents)):
                        with tab:
                            content()
                
                # Show summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Status", result.get("status", "Unknown"))
                with col2:
                    st.metric("Run ID", result.get("run_id", "N/A"))
                with col3:
                    explanations_count = len(result.get("explanations", []))
                    st.metric("Anomalies", explanations_count)
                with col4:
                    total_time = sum(result.get("performance_metrics", {}).values())
                    st.metric("Total Time", f"{total_time:.2f}s")
                
                # Auto-refresh the page to show updated data
                st.rerun()
                
            else:
                # Clear progress indicators
                progress_container.empty()
                st.error(f"❌ Workflow failed: {response.text}")
                
    except requests.exceptions.Timeout:
        st.error("⏰ Workflow timed out. Please try again or check server status.")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error. Please ensure the server is running.")
    except Exception as e:
        st.error(f"❌ Error running workflow: {str(e)}")
        st.info("💡 Try refreshing the page or checking the server status.")


if __name__ == "__main__":
    main()
