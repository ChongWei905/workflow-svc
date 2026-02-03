"""
Pydantic data models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ProviderEnum(str, Enum):
    """LLM provider options"""
    openai = "openai"
    anthropic = "anthropic"


class ExecuteRequest(BaseModel):
    """Request model for natural language query execution"""
    query: str = Field(..., description="Natural language query to execute", min_length=1)
    provider: Optional[ProviderEnum] = Field(None, description="LLM provider override")
    verbose: bool = Field(False, description="Enable verbose output")


class ExecuteResponse(BaseModel):
    """Response model for query execution"""
    response: str = Field(..., description="AI response")
    iterations: int = Field(..., description="Number of iterations used", ge=1)
    execution_time: float = Field(..., description="Execution time in seconds", ge=0)


class SkillInfo(BaseModel):
    """Basic skill information"""
    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")
    scripts_count: int = Field(..., description="Number of scripts in this skill", ge=0)
    path: str = Field(..., description="Absolute path to skill directory")


class ScriptInfo(BaseModel):
    """Script information"""
    name: str = Field(..., description="Script name")
    language: str = Field(..., description="Script language (python, bash, etc.)")
    description: str = Field("", description="Script description")


class SkillDetail(SkillInfo):
    """Detailed skill information including content and scripts"""
    content: str = Field(..., description="Full SKILL.md content")
    scripts: List[ScriptInfo] = Field(default_factory=list, description="List of scripts")


class ExecuteScriptRequest(BaseModel):
    """Request model for script execution"""
    arguments: List[str] = Field(default_factory=list, description="Script arguments")


class ExecuteScriptResponse(BaseModel):
    """Response model for script execution"""
    result: str = Field(..., description="Script execution result")


class AuditEventType(str, Enum):
    """Audit event types"""
    script_executed = "script_executed"
    access_denied = "access_denied"
    file_read = "file_read"


class AuditLogEntry(BaseModel):
    """Audit log entry"""
    timestamp: str = Field(..., description="ISO format timestamp")
    event_type: str = Field(..., description="Type of event")
    skill_name: Optional[str] = Field(None, description="Associated skill name")
    script_name: Optional[str] = Field(None, description="Associated script name")
    exit_code: Optional[int] = Field(None, description="Script exit code (if applicable)")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional event details")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(default="1.0.0", description="API version")


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str = Field(..., description="Message type (execute, chunk, done, error)")
    content: Optional[str] = Field(None, description="Message content")
    query: Optional[str] = Field(None, description="Query for execute type")
