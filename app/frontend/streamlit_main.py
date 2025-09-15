"""Main Streamlit dashboard application."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Data Sentinel Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .anomaly-card {
        background-color: #fff2f2;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4444;
        margin: 0.5rem 0;
    }
    .success-card {
        background-color: #f0fff4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00aa00;
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    """Main dashboard application."""
    st.markdown(
        '<h1 class="main-header">🛡️ Data Sentinel Dashboard</h1>', unsafe_allow_html=True
    )

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview", "Datasets", "Anomalies", "Runs", "Agent Workflows", "Settings"],
    )

    # Route to appropriate page
    if page == "Overview":
        show_overview()
    elif page == "Datasets":
        show_datasets()
    elif page == "Anomalies":
        show_anomalies()
    elif page == "Runs":
        show_runs()
    elif page == "Agent Workflows":
        show_agent_workflows()
    elif page == "Settings":
        show_settings()


def show_overview():
    """Show overview dashboard."""
    st.header("📊 System Overview")

    # Health status
    col1, col2, col3, col4 = st.columns(4)

    try:
        health_response = requests.get(f"{API_BASE_URL}/health/")
        health_data = health_response.json()

        with col1:
            st.metric("System Status", health_data.get("status", "Unknown"))

        with col2:
            st.metric("Database", health_data.get("database", "Unknown"))

        with col3:
            st.metric("Redis", health_data.get("redis", "Unknown"))

        with col4:
            st.metric("LLM Service", health_data.get("llm", "Unknown"))

    except Exception as e:
        st.error(f"Failed to fetch health data: {e}")

    # Metrics summary
    st.subheader("📈 Key Metrics")

    try:
        # Get datasets
        datasets_response = requests.get(f"{API_BASE_URL}/datasets/")
        datasets = datasets_response.json()

        # Get anomalies
        anomalies_response = requests.get(f"{API_BASE_URL}/anomalies/")
        anomalies = anomalies_response.json()

        # Get runs
        runs_response = requests.get(f"{API_BASE_URL}/runs/")
        runs = runs_response.json()

        # Calculate metrics
        total_datasets = len(datasets)
        total_anomalies = len(anomalies)
        open_anomalies = len([a for a in anomalies if a.get("status") == "open"])
        avg_health_score = sum(d.get("health_score", 0) for d in datasets) / max(
            total_datasets, 1
        )

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Datasets", total_datasets)

        with col2:
            st.metric("Open Anomalies", open_anomalies)

        with col3:
            st.metric("Avg Health Score", f"{avg_health_score:.2f}")

        with col4:
            recent_runs = len(
                [
                    r
                    for r in runs
                    if datetime.fromisoformat(
                        r.get("run_time", "1970-01-01").replace("Z", "+00:00")
                    )
                    > datetime.now() - timedelta(days=1)
                ]
            )
            st.metric("Runs (24h)", recent_runs)

        # Health score distribution
        if datasets:
            st.subheader("📊 Health Score Distribution")
            health_scores = [d.get("health_score", 0) for d in datasets]

            fig = px.histogram(
                x=health_scores,
                nbins=20,
                title="Dataset Health Score Distribution",
                labels={"x": "Health Score", "y": "Count"},
            )
            st.plotly_chart(fig, use_container_width=True)

        # Recent anomalies
        if anomalies:
            st.subheader("🚨 Recent Anomalies")
            recent_anomalies = sorted(
                anomalies, key=lambda x: x.get("detected_at", ""), reverse=True
            )[:5]

            for anomaly in recent_anomalies:
                severity = anomaly.get("severity", 1)
                severity_color = (
                    "🔴" if severity >= 4 else "🟡" if severity >= 3 else "🟢"
                )

                st.markdown(
                    f"""
                <div class="anomaly-card">
                    <strong>{severity_color} {anomaly.get('issue_type', 'Unknown')}</strong><br>
                    <small>Dataset: {anomaly.get('table_name', 'Unknown')} | 
                    Column: {anomaly.get('column_name', 'N/A')} | 
                    Severity: {severity}/5</small><br>
                    <small>{anomaly.get('description', 'No description')}</small>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.error(f"Failed to fetch metrics: {e}")


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
    """Show agent workflow management page."""
    st.header("🤖 Agent Workflows")

    # Trigger new workflow
    st.subheader("Trigger New Workflow")

    try:
        # Get datasets for selection
        datasets_response = requests.get(f"{API_BASE_URL}/datasets/")
        datasets = datasets_response.json()

        if datasets:
            dataset_options = {
                f"{d['name']} (ID: {d['id']})": d["id"] for d in datasets
            }
            selected_dataset = st.selectbox(
                "Select Dataset", list(dataset_options.keys())
            )
            include_llm = st.checkbox("Include LLM Explanation", value=True)

            if st.button("Trigger Workflow"):
                dataset_id = dataset_options[selected_dataset]

                try:
                    response = requests.post(
                        f"{API_BASE_URL}/agent/workflow",
                        json={
                            "dataset_id": dataset_id,
                            "include_llm_explanation": include_llm,
                        },
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.success(
                            f"Workflow triggered! Run ID: {result.get('run_id')}"
                        )
                        st.rerun()
                    else:
                        st.error(f"Failed to trigger workflow: {response.text}")

                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No datasets available. Please add a dataset first.")

    except Exception as e:
        st.error(f"Failed to fetch datasets: {e}")

    # Workflow status
    st.subheader("Workflow Status")

    try:
        response = requests.get(f"{API_BASE_URL}/runs/")
        runs = response.json()

        if runs:
            # Filter for recent runs
            recent_runs = sorted(
                runs, key=lambda x: x.get("run_time", ""), reverse=True
            )[:10]

            for run in recent_runs:
                status = run.get("status", "Unknown")
                status_color = (
                    "🟢"
                    if status == "completed"
                    else "🟡" if status == "running" else "🔴"
                )

                with st.expander(f"{status_color} Run {run.get('id')} - {status}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Dataset ID:** {run.get('dataset_id')}")
                        st.write(f"**Status:** {status}")
                        st.write(f"**Run Time:** {run.get('run_time', 'Unknown')}")

                    with col2:
                        st.write(f"**Duration:** {run.get('duration_seconds', 'N/A')}s")
                        if run.get("summary"):
                            summary = run.get("summary", {})
                            st.write(
                                f"**Health Score:** {summary.get('health_score', 'N/A')}"
                            )
                            st.write(
                                f"**Anomalies:** {summary.get('anomalies_detected', 'N/A')}"
                            )

        else:
            st.info("No runs found.")

    except Exception as e:
        st.error(f"Failed to fetch runs: {e}")


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
