"""MCP (Model Context Protocol) service for GitHub integration only."""

import httpx
from typing import Dict, Any, Optional

import structlog

from app.config import get_settings

logger = structlog.get_logger(__name__)


class MCPService:
    """Service for MCP-based GitHub integration."""

    def __init__(self):
        self.settings = get_settings()

    async def create_github_issue(
        self, repo: str, title: str, description: str, labels: Optional[list] = None
    ) -> Dict[str, Any]:
        """Create issue in GitHub."""
        try:
            if not all([
                self.settings.github_token,
                self.settings.github_owner,
                self.settings.github_repo
            ]):
                logger.warning("GitHub credentials not configured")
                return {"success": False, "message": "GitHub not configured"}

            # Use configured repo or the provided one
            target_repo = repo or f"{self.settings.github_owner}/{self.settings.github_repo}"
            
            headers = {
                "Authorization": f"token {self.settings.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            payload = {
                "title": title,
                "body": description
            }
            
            if labels:
                payload["labels"] = labels
            else:
                # Default labels for data quality issues
                payload["labels"] = ["data-quality", "bug", "automated"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.github.com/repos/{target_repo}/issues",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    issue_data = response.json()
                    logger.info("GitHub issue created successfully", 
                              issue_number=issue_data.get("number"),
                              repo=target_repo)
                    return {
                        "success": True,
                        "issue_number": issue_data.get("number"),
                        "issue_url": issue_data.get("html_url"),
                        "message": "Issue created successfully"
                    }
                else:
                    logger.error("GitHub issue creation failed", 
                               status_code=response.status_code,
                               response=response.text)
                    return {
                        "success": False,
                        "error": f"GitHub API error: {response.status_code}",
                        "message": response.text
                    }
                    
        except Exception as e:
            logger.error("Failed to create GitHub issue", error=str(e))
            return {"success": False, "error": str(e)}

    async def execute_mcp_action(self, mcp_action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP action based on tool type."""
        try:
            tool = mcp_action.get("tool")
            action = mcp_action.get("action")
            payload = mcp_action.get("payload", {})
            
            if tool == "github":
                if action == "create_issue":
                    return await self.create_github_issue(
                        repo=payload.get("repo"),
                        title=payload.get("title"),
                        description=payload.get("description"),
                        labels=payload.get("labels")
                    )
                else:
                    return {"success": False, "error": f"Unknown GitHub action: {action}"}
            else:
                return {"success": False, "error": f"Unknown tool: {tool}. Supported tools: github"}
                
        except Exception as e:
            logger.error("Failed to execute MCP action", error=str(e))
            return {"success": False, "error": str(e)}