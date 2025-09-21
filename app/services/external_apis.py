"""Real external API integrations for notifications and issue tracking."""

import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime

import structlog
from app.config import get_settings

logger = structlog.get_logger(__name__)


class SlackAPI:
    """Slack API integration for notifications."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_message(
        self, 
        channel: str, 
        message: str, 
        priority: str = "medium",
        attachments: Optional[list] = None
    ) -> Dict[str, Any]:
        """Send a message to Slack."""
        try:
            payload = {
                "channel": channel,
                "text": message,
                "username": "Data Sentinel",
                "icon_emoji": ":robot_face:",
                "attachments": attachments or []
            }
            
            # Add priority-based color
            if priority == "high":
                payload["attachments"].append({
                    "color": "danger",
                    "fields": [{"title": "Priority", "value": "HIGH", "short": True}]
                })
            elif priority == "medium":
                payload["attachments"].append({
                    "color": "warning",
                    "fields": [{"title": "Priority", "value": "MEDIUM", "short": True}]
                })
            else:
                payload["attachments"].append({
                    "color": "good",
                    "fields": [{"title": "Priority", "value": "LOW", "short": True}]
                })
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url, 
                    json=payload, 
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("Slack message sent successfully", channel=channel)
                    return {"success": True, "message": "Message sent successfully"}
                else:
                    logger.error("Slack API error", status_code=response.status_code)
                    return {"success": False, "error": f"Slack API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error("Failed to send Slack message", error=str(e))
            return {"success": False, "error": str(e)}


class JiraAPI:
    """Jira API integration for issue tracking."""
    
    def __init__(self, base_url: str, username: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.auth = (username, api_token)
    
    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Bug",
        priority: str = "Medium",
        assignee: Optional[str] = None,
        labels: Optional[list] = None
    ) -> Dict[str, Any]:
        """Create a Jira issue."""
        try:
            # Map priority to Jira priority
            priority_map = {
                "low": "Lowest",
                "medium": "Medium", 
                "high": "High",
                "critical": "Highest"
            }
            
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": issue_type},
                    "priority": {"name": priority_map.get(priority, "Medium")}
                }
            }
            
            if assignee:
                payload["fields"]["assignee"] = {"name": assignee}
            
            if labels:
                payload["fields"]["labels"] = labels
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/2/issue",
                    json=payload,
                    auth=self.auth,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    issue_data = response.json()
                    issue_key = issue_data.get("key")
                    issue_url = f"{self.base_url}/browse/{issue_key}"
                    
                    logger.info("Jira issue created", issue_key=issue_key)
                    return {
                        "success": True,
                        "issue_key": issue_key,
                        "issue_url": issue_url,
                        "message": "Issue created successfully"
                    }
                else:
                    logger.error("Jira API error", status_code=response.status_code)
                    return {"success": False, "error": f"Jira API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error("Failed to create Jira issue", error=str(e))
            return {"success": False, "error": str(e)}


class GitHubAPI:
    """GitHub API integration for issue tracking."""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[list] = None,
        assignees: Optional[list] = None
    ) -> Dict[str, Any]:
        """Create a GitHub issue."""
        try:
            payload = {
                "title": title,
                "body": body
            }
            
            if labels:
                payload["labels"] = labels
            
            if assignees:
                payload["assignees"] = assignees
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.github.com/repos/{self.owner}/{self.repo}/issues",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    issue_data = response.json()
                    issue_number = issue_data.get("number")
                    issue_url = issue_data.get("html_url")
                    
                    logger.info("GitHub issue created", issue_number=issue_number)
                    return {
                        "success": True,
                        "issue_number": issue_number,
                        "issue_url": issue_url,
                        "message": "Issue created successfully"
                    }
                else:
                    logger.error("GitHub API error", status_code=response.status_code)
                    return {"success": False, "error": f"GitHub API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error("Failed to create GitHub issue", error=str(e))
            return {"success": False, "error": str(e)}


class EmailAPI:
    """Email API integration using SendGrid."""
    
    def __init__(self, api_key: str, from_email: str):
        self.api_key = api_key
        self.from_email = from_email
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Send an email notification."""
        try:
            payload = {
                "personalizations": [{
                    "to": [{"email": to_email}],
                    "subject": subject
                }],
                "from": {"email": self.from_email},
                "content": [{
                    "type": "text/html",
                    "value": content
                }]
            }
            
            # Add priority header
            if priority == "high":
                payload["personalizations"][0]["headers"] = {
                    "X-Priority": "1",
                    "X-MSMail-Priority": "High"
                }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 202:
                    logger.info("Email sent successfully", to=to_email)
                    return {"success": True, "message": "Email sent successfully"}
                else:
                    logger.error("SendGrid API error", status_code=response.status_code)
                    return {"success": False, "error": f"SendGrid API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error("Failed to send email", error=str(e))
            return {"success": False, "error": str(e)}


class ExternalAPIManager:
    """Manager for all external API integrations."""
    
    def __init__(self):
        self.settings = get_settings()
        self._initialize_apis()
    
    def _initialize_apis(self):
        """Initialize external API clients."""
        # Slack
        if self.settings.slack_webhook_url:
            self.slack = SlackAPI(self.settings.slack_webhook_url)
        else:
            self.slack = None
        
        # Jira
        if all([self.settings.jira_base_url, self.settings.jira_username, self.settings.jira_api_token]):
            self.jira = JiraAPI(
                self.settings.jira_base_url,
                self.settings.jira_username,
                self.settings.jira_api_token
            )
        else:
            self.jira = None
        
        # GitHub
        if all([self.settings.github_token, self.settings.github_owner, self.settings.github_repo]):
            self.github = GitHubAPI(
                self.settings.github_token,
                self.settings.github_owner,
                self.settings.github_repo
            )
        else:
            self.github = None
        
        # Email
        if all([self.settings.sendgrid_api_key, self.settings.from_email]):
            self.email = EmailAPI(
                self.settings.sendgrid_api_key,
                self.settings.from_email
            )
        else:
            self.email = None
    
    async def send_notification(
        self,
        channel: str,
        message: str,
        priority: str = "medium",
        platform: str = "slack"
    ) -> Dict[str, Any]:
        """Send notification via specified platform."""
        if platform == "slack" and self.slack:
            return await self.slack.send_message(channel, message, priority)
        elif platform == "email" and self.email:
            return await self.email.send_email(channel, "Data Sentinel Alert", message, priority)
        else:
            return {"success": False, "error": f"Platform {platform} not configured"}
    
    async def create_issue(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        platform: str = "jira"
    ) -> Dict[str, Any]:
        """Create issue via specified platform."""
        if platform == "jira" and self.jira:
            return await self.jira.create_issue(
                project_key="DATA",
                summary=title,
                description=description,
                priority=priority
            )
        elif platform == "github" and self.github:
            labels = ["data-quality", "bug"]
            if priority == "high":
                labels.append("high-priority")
            return await self.github.create_issue(title, description, labels)
        else:
            return {"success": False, "error": f"Platform {platform} not configured"}
