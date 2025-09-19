"""Enhanced Streamlit dashboard application for Data Sentinel."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json
import time
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="Data Sentinel Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-org/data-sentinel',
        'Report a bug': "https://github.com/your-org/data-sentinel/issues",
        'About': "Data Sentinel v1.0 - AI-Powered Data Quality Monitoring"
    }
)

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1"

# Enhanced Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .metric-card h3 {
        color: white;
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .anomaly-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(255,107,107,0.3);
    }
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,184,148,0.3);
    }
    .warning-card {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(253,203,110,0.3);
    }
    .info-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(116,185,255,0.3);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-healthy { background-color: #00b894; }
    .status-warning { background-color: #fdcb6e; }
    .status-critical { background-color: #ff6b6b; }
    .status-unknown { background-color: #636e72; }
</style>
""",
    unsafe_allow_html=True,
)


# Utility functions
@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_data(endpoint: str, params: Dict = None) -> Dict:
    """Fetch data from API with caching."""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data from {endpoint}: {e}")
        return {}

def get_status_indicator(status: str) -> str:
    """Get status indicator HTML."""
    status_map = {
        "healthy": "status-healthy",
        "completed": "status-healthy", 
        "open": "status-critical",
        "failed": "status-critical",
        "running": "status-warning",
        "pending": "status-warning",
        "resolved": "status-healthy",
        "investigating": "status-warning"
    }
    css_class = status_map.get(status.lower(), "status-unknown")
    return f'<span class="status-indicator {css_class}"></span>'

def create_metric_card(title: str, value: Any, delta: str = None, card_type: str = "metric") -> str:
    """Create a metric card HTML."""
    delta_html = f'<div style="font-size: 0.8rem; opacity: 0.8;">{delta}</div>' if delta else ""
    return f"""
    <div class="{card_type}-card">
        <h3>{title}</h3>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def main():
    """Main dashboard application."""
    st.markdown(
        '<h1 class="main-header">🛡️ Data Sentinel Dashboard</h1>', unsafe_allow_html=True
    )

    # Sidebar navigation with enhanced styling
    st.sidebar.markdown("## 🧭 Navigation")
    
    # Add refresh button
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📊 Overview", "📁 Datasets", "🚨 Anomalies", "🔄 Runs", "🤖 Agent Workflows", "⚙️ Settings"],
    )

    # Add system status in sidebar
    try:
        health_data = fetch_data("health/")
        if health_data:
            st.sidebar.markdown("## 🏥 System Status")
            st.sidebar.markdown(f"**API:** {get_status_indicator(health_data.get('status', 'unknown'))} {health_data.get('status', 'Unknown')}")
            st.sidebar.markdown(f"**Database:** {get_status_indicator(health_data.get('database', 'unknown'))} {health_data.get('database', 'Unknown')}")
            st.sidebar.markdown(f"**LLM:** {get_status_indicator(health_data.get('llm', 'unknown'))} {health_data.get('llm', 'Unknown')}")
    except:
        st.sidebar.markdown("## 🏥 System Status")
        st.sidebar.error("Unable to connect to API")

    # Route to appropriate page
    if "Overview" in page:
        show_overview()
    elif "Datasets" in page:
        show_datasets()
    elif "Anomalies" in page:
        show_anomalies()
    elif "Runs" in page:
        show_runs()
    elif "Agent Workflows" in page:
        show_agent_workflows()
    elif "Settings" in page:
        show_settings()


def show_overview():
    """Show enhanced overview dashboard."""
    st.header("📊 System Overview")
    
    # Add auto-refresh option
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Real-time Data Quality Monitoring")
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        if auto_refresh:
            time.sleep(30)
            st.rerun()

    # Health status with enhanced cards
    st.subheader("🏥 System Health")
    health_data = fetch_data("health/")
    
    if health_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status = health_data.get("status", "Unknown")
            st.markdown(create_metric_card(
                "System Status", 
                f"{get_status_indicator(status)} {status.title()}",
                card_type="success" if status == "healthy" else "warning"
            ), unsafe_allow_html=True)
        
        with col2:
            db_status = health_data.get("database", "Unknown")
            st.markdown(create_metric_card(
                "Database", 
                f"{get_status_indicator(db_status)} {db_status.title()}",
                card_type="success" if db_status == "healthy" else "warning"
            ), unsafe_allow_html=True)
        
        with col3:
            llm_status = health_data.get("llm", "Unknown")
            st.markdown(create_metric_card(
                "LLM Service", 
                f"{get_status_indicator(llm_status)} {llm_status.title()}",
                card_type="success" if llm_status == "healthy" else "warning"
            ), unsafe_allow_html=True)
        
        with col4:
            version = health_data.get("version", "v1.0")
            st.markdown(create_metric_card(
                "Version", 
                f"🛡️ {version}",
                card_type="info"
            ), unsafe_allow_html=True)

    # Enhanced metrics with better visualizations
    st.subheader("📈 Key Metrics")
    
    # Fetch all data
    datasets = fetch_data("datasets/")
    anomalies = fetch_data("anomalies/")
    runs = fetch_data("runs/")
    
    if datasets and anomalies and runs:
        # Calculate enhanced metrics
        total_datasets = len(datasets)
        total_anomalies = len(anomalies)
        open_anomalies = len([a for a in anomalies if a.get("status") == "open"])
        high_severity = len([a for a in anomalies if a.get("severity", 0) >= 4])
        avg_health_score = sum(d.get("health_score", 0) for d in datasets) / max(total_datasets, 1)
        
        # Recent runs (last 24h)
        recent_runs = len([
            r for r in runs
            if datetime.fromisoformat(r.get("run_time", "1970-01-01").replace("Z", "+00:00"))
            > datetime.now() - timedelta(days=1)
        ])
        
        # Success rate
        completed_runs = len([r for r in runs if r.get("status") == "completed"])
        success_rate = (completed_runs / max(len(runs), 1)) * 100

        # Display enhanced metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card(
                "Total Datasets", 
                total_datasets,
                f"📊 {total_datasets} active",
                card_type="info"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card(
                "Open Anomalies", 
                open_anomalies,
                f"🚨 {high_severity} critical" if high_severity > 0 else "✅ All good",
                card_type="anomaly" if open_anomalies > 0 else "success"
            ), unsafe_allow_html=True)
        
        with col3:
            health_color = "success" if avg_health_score >= 0.8 else "warning" if avg_health_score >= 0.6 else "anomaly"
            st.markdown(create_metric_card(
                "Avg Health Score", 
                f"{avg_health_score:.2f}",
                f"📈 {avg_health_score*100:.0f}% healthy",
                card_type=health_color
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card(
                "Success Rate", 
                f"{success_rate:.1f}%",
                f"🔄 {recent_runs} runs (24h)",
                card_type="success" if success_rate >= 90 else "warning"
            ), unsafe_allow_html=True)

        # Enhanced visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Health score distribution with better styling
            st.subheader("📊 Health Score Distribution")
            health_scores = [d.get("health_score", 0) for d in datasets]
            
            fig = px.histogram(
                x=health_scores,
                nbins=20,
                title="Dataset Health Score Distribution",
                labels={"x": "Health Score", "y": "Count"},
                color_discrete_sequence=['#667eea'],
                opacity=0.8
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Anomaly severity pie chart
            st.subheader("🚨 Anomaly Severity Breakdown")
            severity_counts = {}
            for anomaly in anomalies:
                severity = anomaly.get("severity", 1)
                severity_counts[f"Level {severity}"] = severity_counts.get(f"Level {severity}", 0) + 1
            
            if severity_counts:
                colors = ['#00b894', '#fdcb6e', '#e17055', '#ff6b6b', '#d63031']
                fig = px.pie(
                    values=list(severity_counts.values()),
                    names=list(severity_counts.keys()),
                    title="Anomaly Severity Distribution",
                    color_discrete_sequence=colors[:len(severity_counts)]
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(create_metric_card(
                    "No Anomalies", 
                    "🎉 All systems healthy!",
                    card_type="success"
                ), unsafe_allow_html=True)

        # Recent anomalies with enhanced display
        if anomalies:
            st.subheader("🚨 Recent Anomalies")
            recent_anomalies = sorted(
                anomalies, key=lambda x: x.get("detected_at", ""), reverse=True
            )[:5]

            for i, anomaly in enumerate(recent_anomalies):
                severity = anomaly.get("severity", 1)
                severity_emoji = "🔴" if severity >= 4 else "🟡" if severity >= 3 else "🟢"
                
                # Create expandable anomaly card
                with st.expander(f"{severity_emoji} {anomaly.get('issue_type', 'Unknown')} - {anomaly.get('table_name', 'Unknown')}", expanded=i<2):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {anomaly.get('description', 'No description')}")
                        st.write(f"**Column:** {anomaly.get('column_name', 'N/A')}")
                        st.write(f"**Severity:** {severity}/5")
                        st.write(f"**Status:** {anomaly.get('status', 'Unknown')}")
                    
                    with col2:
                        st.write(f"**Detected:** {anomaly.get('detected_at', 'Unknown')}")
                        st.write(f"**Action:** {anomaly.get('action_taken', 'None')}")
                        
                        if anomaly.get("llm_explanation"):
                            st.write("**AI Explanation:**")
                            st.info(anomaly.get("llm_explanation"))
                        
                        if anomaly.get("suggested_sql"):
                            st.write("**Suggested Fix:**")
                            st.code(anomaly.get("suggested_sql"), language="sql")
    else:
        st.error("Failed to fetch system data. Please check API connection.")


def show_datasets():
    """Show datasets management page."""
    st.header("📁 Dataset Management")

    # Add new dataset
    with st.expander("Add New Dataset"):
        with st.form("add_dataset"):
            name = st.text_input("Dataset Name")
            owner = st.text_input("Owner")
            source = st.text_input("Source")

            if st.form_submit_button("Add Dataset"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/datasets/",
                        json={"name": name, "owner": owner, "source": source},
                    )
                    if response.status_code == 201:
                        st.success("Dataset added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to add dataset: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # List datasets
    try:
        response = requests.get(f"{API_BASE_URL}/datasets/")
        datasets = response.json()

        if datasets:
            # Create DataFrame for better display
            df = pd.DataFrame(datasets)

            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Datasets", len(datasets))
            with col2:
                avg_health = df["health_score"].mean()
                st.metric("Average Health Score", f"{avg_health:.2f}")
            with col3:
                unhealthy = len(df[df["health_score"] < 0.8])
                st.metric("Unhealthy Datasets", unhealthy)

            # Health score chart
            fig = px.bar(
                df,
                x="name",
                y="health_score",
                title="Dataset Health Scores",
                color="health_score",
                color_continuous_scale="RdYlGn",
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

            # Dataset table
            st.subheader("Dataset Details")
            st.dataframe(df, use_container_width=True)

        else:
            st.info("No datasets found. Add a dataset to get started.")

    except Exception as e:
        st.error(f"Failed to fetch datasets: {e}")


def show_anomalies():
    """Show anomalies management page."""
    st.header("🚨 Anomaly Management")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status", ["All", "open", "investigating", "resolved", "ignored"]
        )

    with col2:
        severity_filter = st.selectbox("Min Severity", [1, 2, 3, 4, 5])

    with col3:
        dataset_filter = st.selectbox("Dataset", ["All"])

    # Get anomalies
    try:
        params = {}
        if status_filter != "All":
            params["status"] = status_filter
        if severity_filter:
            params["severity_min"] = severity_filter

        response = requests.get(f"{API_BASE_URL}/anomalies/", params=params)
        anomalies = response.json()

        if anomalies:
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Anomalies", len(anomalies))

            with col2:
                open_count = len([a for a in anomalies if a.get("status") == "open"])
                st.metric("Open Anomalies", open_count)

            with col3:
                high_severity = len([a for a in anomalies if a.get("severity", 0) >= 4])
                st.metric("High Severity", high_severity)

            with col4:
                resolved_count = len(
                    [a for a in anomalies if a.get("status") == "resolved"]
                )
                st.metric("Resolved", resolved_count)

            # Severity distribution
            severity_counts = {}
            for anomaly in anomalies:
                severity = anomaly.get("severity", 1)
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            fig = px.pie(
                values=list(severity_counts.values()),
                names=[f"Severity {k}" for k in severity_counts.keys()],
                title="Anomaly Severity Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Anomaly details
            st.subheader("Anomaly Details")
            for anomaly in anomalies:
                severity = anomaly.get("severity", 1)
                severity_color = (
                    "🔴" if severity >= 4 else "🟡" if severity >= 3 else "🟢"
                )

                with st.expander(
                    f"{severity_color} {anomaly.get('issue_type', 'Unknown')} - {anomaly.get('table_name', 'Unknown')}"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(
                            f"**Description:** {anomaly.get('description', 'No description')}"
                        )
                        st.write(f"**Column:** {anomaly.get('column_name', 'N/A')}")
                        st.write(f"**Severity:** {severity}/5")
                        st.write(f"**Status:** {anomaly.get('status', 'Unknown')}")

                    with col2:
                        st.write(
                            f"**Detected:** {anomaly.get('detected_at', 'Unknown')}"
                        )
                        st.write(
                            f"**Action Taken:** {anomaly.get('action_taken', 'None')}"
                        )

                        if anomaly.get("llm_explanation"):
                            st.write("**LLM Explanation:**")
                            st.write(anomaly.get("llm_explanation"))

                        if anomaly.get("suggested_sql"):
                            st.write("**Suggested SQL:**")
                            st.code(anomaly.get("suggested_sql"))

                    # Action buttons
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("Resolve", key=f"resolve_{anomaly.get('id')}"):
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/anomalies/{anomaly.get('id')}/resolve"
                                )
                                if response.status_code == 200:
                                    st.success("Anomaly resolved!")
                                    st.rerun()
                                else:
                                    st.error("Failed to resolve anomaly")
                            except Exception as e:
                                st.error(f"Error: {e}")

                    with col2:
                        if st.button(
                            "Get LLM Explanation", key=f"explain_{anomaly.get('id')}"
                        ):
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/agent/explain",
                                    json={"anomaly_id": anomaly.get("id")},
                                )
                                if response.status_code == 200:
                                    st.success("LLM explanation generated!")
                                    st.rerun()
                                else:
                                    st.error("Failed to generate explanation")
                            except Exception as e:
                                st.error(f"Error: {e}")

        else:
            st.info("No anomalies found.")

    except Exception as e:
        st.error(f"Failed to fetch anomalies: {e}")


def show_runs():
    """Show validation runs page."""
    st.header("🔄 Validation Runs")

    try:
        response = requests.get(f"{API_BASE_URL}/runs/")
        runs = response.json()

        if runs:
            # Create DataFrame
            df = pd.DataFrame(runs)
            df["run_time"] = pd.to_datetime(df["run_time"])

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Runs", len(runs))

            with col2:
                completed = len(df[df["status"] == "completed"])
                st.metric("Completed", completed)

            with col3:
                failed = len(df[df["status"] == "failed"])
                st.metric("Failed", failed)

            with col4:
                avg_duration = df["duration_seconds"].mean()
                st.metric(
                    "Avg Duration",
                    f"{avg_duration:.1f}s" if pd.notna(avg_duration) else "N/A",
                )

            # Status distribution
            status_counts = df["status"].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Run Status Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Run timeline
            fig = px.scatter(
                df,
                x="run_time",
                y="duration_seconds",
                color="status",
                title="Run Timeline",
                labels={
                    "run_time": "Run Time",
                    "duration_seconds": "Duration (seconds)",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

            # Run details table
            st.subheader("Run Details")
            st.dataframe(df, use_container_width=True)

        else:
            st.info("No runs found.")

    except Exception as e:
        st.error(f"Failed to fetch runs: {e}")


def show_agent_workflows():
    """Show enhanced agent workflow management page."""
    st.header("🤖 Agent Workflows")
    
    # Add tabs for better organization
    tab1, tab2, tab3 = st.tabs(["🚀 Trigger Workflow", "📊 Workflow Status", "📈 Analytics"])
    
    with tab1:
        st.subheader("Trigger New Workflow")
        
        # Enhanced workflow trigger form
        with st.form("workflow_trigger"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Get datasets for selection
                datasets = fetch_data("datasets/")
                
                if datasets:
                    dataset_options = {
                        f"{d['name']} (Health: {d.get('health_score', 0):.2f})": d["id"] 
                        for d in datasets
                    }
                    selected_dataset = st.selectbox(
                        "Select Dataset", 
                        list(dataset_options.keys()),
                        help="Choose a dataset to run quality checks on"
                    )
                else:
                    st.warning("No datasets available. Please add a dataset first.")
                    selected_dataset = None
            
            with col2:
                include_llm = st.checkbox("Include LLM Explanation", value=True, 
                                        help="Generate AI-powered explanations for detected anomalies")
                force_run = st.checkbox("Force Run", value=False,
                                      help="Run even if dataset was recently checked")
            
            # Advanced options
            with st.expander("Advanced Options"):
                col1, col2 = st.columns(2)
                with col1:
                    validation_rules = st.multiselect(
                        "Validation Rules",
                        ["null_check", "uniqueness", "range_check", "pattern_match"],
                        default=["null_check", "uniqueness"],
                        help="Select specific validation rules to apply"
                    )
                with col2:
                    sample_size = st.number_input(
                        "Sample Size", 
                        min_value=100, 
                        max_value=10000, 
                        value=1000,
                        help="Number of rows to sample for validation"
                    )
            
            if st.form_submit_button("🚀 Trigger Workflow", use_container_width=True):
                if selected_dataset:
                    dataset_id = dataset_options[selected_dataset]
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        status_text.text("🔄 Triggering workflow...")
                        progress_bar.progress(25)
                        
                        response = requests.post(
                            f"{API_BASE_URL}/agent/workflow",
                            json={
                                "dataset_id": dataset_id,
                                "include_llm_explanation": include_llm,
                                "force_run": force_run,
                            },
                            timeout=30
                        )
                        
                        progress_bar.progress(75)
                        status_text.text("✅ Processing response...")
                        
                        if response.status_code == 200:
                            result = response.json()
                            progress_bar.progress(100)
                            status_text.text("🎉 Workflow completed successfully!")
                            
                            st.success(f"Workflow triggered! Run ID: {result.get('run_id')}")
                            
                            # Show results summary
                            if result.get("summary"):
                                summary = result.get("summary", {})
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Health Score", f"{summary.get('health_score', 0):.2f}")
                                with col2:
                                    st.metric("Anomalies Detected", summary.get('anomalies_detected', 0))
                                with col3:
                                    st.metric("Actions Taken", summary.get('actions_taken', 0))
                            
                            st.rerun()
                        else:
                            st.error(f"Failed to trigger workflow: {response.text}")
                            
                    except requests.exceptions.Timeout:
                        st.error("Workflow timed out. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please select a dataset first.")
    
    with tab2:
        st.subheader("Workflow Status & History")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status Filter", ["All", "completed", "failed", "running", "pending"])
        with col2:
            time_filter = st.selectbox("Time Range", ["All", "Last 24h", "Last 7 days", "Last 30 days"])
        with col3:
            if st.button("🔄 Refresh Status"):
                st.cache_data.clear()
                st.rerun()
        
        # Get runs with filters
        runs = fetch_data("runs/")
        
        if runs:
            # Apply filters
            filtered_runs = runs.copy()
            
            if status_filter != "All":
                filtered_runs = [r for r in filtered_runs if r.get("status") == status_filter]
            
            if time_filter != "All":
                now = datetime.now()
                if time_filter == "Last 24h":
                    cutoff = now - timedelta(days=1)
                elif time_filter == "Last 7 days":
                    cutoff = now - timedelta(days=7)
                elif time_filter == "Last 30 days":
                    cutoff = now - timedelta(days=30)
                
                filtered_runs = [
                    r for r in filtered_runs
                    if datetime.fromisoformat(r.get("run_time", "1970-01-01").replace("Z", "+00:00")) > cutoff
                ]
            
            # Sort by run time
            filtered_runs = sorted(filtered_runs, key=lambda x: x.get("run_time", ""), reverse=True)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Runs", len(filtered_runs))
            with col2:
                completed = len([r for r in filtered_runs if r.get("status") == "completed"])
                st.metric("Completed", completed)
            with col3:
                failed = len([r for r in filtered_runs if r.get("status") == "failed"])
                st.metric("Failed", failed)
            with col4:
                avg_duration = sum(r.get("duration_seconds", 0) for r in filtered_runs if r.get("duration_seconds")) / max(len([r for r in filtered_runs if r.get("duration_seconds")]), 1)
                st.metric("Avg Duration", f"{avg_duration:.1f}s")
            
            # Display runs
            for run in filtered_runs[:20]:  # Show last 20 runs
                status = run.get("status", "Unknown")
                status_emoji = "🟢" if status == "completed" else "🟡" if status == "running" else "🔴"
                
                with st.expander(f"{status_emoji} Run {run.get('id')} - {status.title()}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Dataset ID:** {run.get('dataset_id')}")
                        st.write(f"**Status:** {status}")
                        st.write(f"**Run Time:** {run.get('run_time', 'Unknown')}")
                        st.write(f"**Duration:** {run.get('duration_seconds', 'N/A')}s")
                    
                    with col2:
                        if run.get("summary"):
                            summary = run.get("summary", {})
                            st.write(f"**Health Score:** {summary.get('health_score', 'N/A')}")
                            st.write(f"**Anomalies Detected:** {summary.get('anomalies_detected', 'N/A')}")
                            st.write(f"**Actions Taken:** {summary.get('actions_taken', 'N/A')}")
                            
                            if summary.get("error"):
                                st.error(f"Error: {summary.get('error')}")
        else:
            st.info("No runs found.")
    
    with tab3:
        st.subheader("Workflow Analytics")
        
        runs = fetch_data("runs/")
        
        if runs and len(runs) > 0:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(runs)
            df["run_time"] = pd.to_datetime(df["run_time"])
            df["date"] = df["run_time"].dt.date
            
            # Success rate over time
            daily_stats = df.groupby("date").agg({
                "status": lambda x: (x == "completed").sum() / len(x) * 100,
                "duration_seconds": "mean",
                "id": "count"
            }).reset_index()
            daily_stats.columns = ["Date", "Success Rate (%)", "Avg Duration (s)", "Run Count"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Success Rate Over Time")
                fig = px.line(daily_stats, x="Date", y="Success Rate (%)", 
                            title="Daily Success Rate", markers=True)
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Run Duration Trends")
                fig = px.line(daily_stats, x="Date", y="Avg Duration (s)", 
                            title="Average Run Duration", markers=True)
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            # Status distribution
            st.subheader("Run Status Distribution")
            status_counts = df["status"].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, 
                        title="Run Status Distribution")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("No runs available for analytics.")


def show_settings():
    """Show settings page."""
    st.header("⚙️ Settings")

    st.subheader("System Configuration")

    # Display current settings (read-only for now)
    settings_info = {
        "API Base URL": API_BASE_URL,
        "Database": "PostgreSQL",
        "Cache": "Redis",
        "LLM Provider": "OpenAI",
        "Monitoring": "Prometheus + Grafana",
    }

    for key, value in settings_info.items():
        st.write(f"**{key}:** {value}")

    st.subheader("Data Warehouse Configuration")
    st.info("Configure your data warehouse connection in the environment variables.")

    st.subheader("External Integrations")
    st.info(
        "Configure Slack, Jira, and other integrations in the environment variables."
    )


if __name__ == "__main__":
    main()
