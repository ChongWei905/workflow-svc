"""
Executor service - wraps existing SkillExecutor logic for API use
"""

import asyncio
import os
import time
from pathlib import Path
from typing import List, AsyncIterator, Dict, Any, Optional

from loaders import SkillLoader
from llm import create_llm, LLMAdapter
from executor import SkillExecutor, SecurityConfig, Auditor, AuditLevel


class ExecutorService:
    """Execution service - wraps existing logic for API"""

    def __init__(
        self,
        skills_dir: str = "./skills",
        provider: str = "openai",
        model: Optional[str] = None,
        max_execution_time: int = 300,
        audit_level: str = "basic",
        allowed_paths: Optional[List[str]] = None
    ):
        """Initialize the executor service

        Args:
            skills_dir: Path to skills directory
            provider: LLM provider (openai or anthropic)
            model: Optional model name override
            max_execution_time: Maximum script execution time in seconds
            audit_level: Audit logging level (none, basic, detailed)
            allowed_paths: Optional whitelist of allowed script paths
        """
        # Initialize security configuration
        security_kwargs = {
            "max_execution_time": max_execution_time,
            "audit_level": AuditLevel(audit_level),
            "audit_to_console": True,  # Log to console by default
        }

        if allowed_paths:
            security_kwargs["allowed_script_paths"] = [Path(p) for p in allowed_paths]

        self.security = SecurityConfig(**security_kwargs)
        self.auditor = Auditor(self.security)

        # Load skills
        self.skills_dir = Path(skills_dir).expanduser()
        self.loader = SkillLoader(self.skills_dir, auditor=self.auditor)

        try:
            self.skills = self.loader.load_all()
        except FileNotFoundError:
            self.skills = {}

        # Create LLM and executor
        llm_kwargs = {}
        if model:
            llm_kwargs["model"] = model

        # Add base_url for OpenAI if configured
        if provider == "openai":
            base_url = os.getenv("OPENAI_BASE_URL")
            if base_url:
                llm_kwargs["base_url"] = base_url

        self.llm = create_llm(provider, **llm_kwargs)
        self.executor = SkillExecutor(
            self.llm,
            self.skills,
            security_config=self.security,
            auditor=self.auditor  # 传递同一个 auditor 实例
        )

        self.provider = provider

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all skills"""
        return [
            {
                "name": name,
                "description": skill.description,
                "scripts_count": len(skill.scripts),
                "path": str(skill.path)
            }
            for name, skill in sorted(self.skills.items())
        ]

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """Get skill details"""
        skill = self.skills.get(name)
        if not skill:
            return None

        return {
            "name": skill.name,
            "description": skill.description,
            "content": skill.content,
            "scripts_count": len(skill.scripts),
            "scripts": [
                {
                    "name": s.name,
                    "language": s.language,
                    "description": s.description
                }
                for s in skill.scripts
            ],
            "path": str(skill.path)
        }

    def list_scripts(self, skill_name: str) -> List[Dict[str, Any]]:
        """List scripts in a skill"""
        skill = self.skills.get(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")

        return [
            {
                "name": s.name,
                "language": s.language,
                "description": s.description
            }
            for s in skill.scripts
        ]

    def execute_script(
        self,
        skill_name: str,
        script_name: str,
        arguments: List[str]
    ) -> Dict[str, str]:
        """Execute a specific script"""
        result = self.executor._execute_script(
            skill_name, script_name, arguments, verbose=True
        )
        return {"result": result}

    async def execute(self, query: str, verbose: bool = False) -> Dict[str, Any]:
        """Execute a natural language query"""
        start_time = time.time()

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.executor.execute(query, verbose=verbose)
        )

        return {
            "response": response,
            "iterations": 1,  # Could be tracked from executor internals
            "execution_time": time.time() - start_time
        }

    async def stream_execute(self, query: str) -> AsyncIterator[str]:
        """Stream execution results (for WebSocket)

        Yields chunks of the response as they're generated
        """
        yield "Processing query..."

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.executor.execute(query, verbose=False)
        )

        # For now, yield the complete result
        # Could be enhanced to implement true streaming if LLM adapter supports it
        yield result

    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs"""
        events = self.auditor.events[-limit:] if self.auditor.events else []
        return [e.to_dict() for e in events]

    async def shutdown(self):
        """Shutdown the service"""
        # Cleanup any resources if needed
        pass

    @property
    def skills_count(self) -> int:
        """Get number of loaded skills"""
        return len(self.skills)

    @property
    def total_scripts_count(self) -> int:
        """Get total number of scripts across all skills"""
        return sum(len(skill.scripts) for skill in self.skills.values())


# Global service instance
_executor_service: Optional[ExecutorService] = None


def get_executor_service() -> ExecutorService:
    """Get the global executor service instance"""
    global _executor_service
    if _executor_service is None:
        raise RuntimeError("Executor service not initialized. Call startup_executor_service first.")
    return _executor_service


async def startup_executor_service(
    skills_dir: str = "./skills",
    provider: str = "openai",
    model: Optional[str] = None,
    max_execution_time: int = 300,
    audit_level: str = "basic",
    allowed_paths: Optional[List[str]] = None
) -> ExecutorService:
    """Initialize the global executor service"""
    global _executor_service

    _executor_service = ExecutorService(
        skills_dir=skills_dir,
        provider=provider,
        model=model,
        max_execution_time=max_execution_time,
        audit_level=audit_level,
        allowed_paths=allowed_paths
    )

    return _executor_service


async def shutdown_executor_service():
    """Shutdown the global executor service"""
    global _executor_service
    if _executor_service:
        await _executor_service.shutdown()
        _executor_service = None
