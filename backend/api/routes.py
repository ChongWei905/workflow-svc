"""
API route definitions
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional

from backend.schemas import (
    ExecuteRequest, ExecuteResponse,
    SkillInfo, SkillDetail, ScriptInfo,
    ExecuteScriptRequest, ExecuteScriptResponse,
    AuditLogEntry, HealthResponse
)
from backend.services.executor_service import ExecutorService, get_executor_service
from backend.services.auth import verify_api_key

router = APIRouter(prefix="/api", tags=["api"], dependencies=[Depends(verify_api_key)])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    executor: ExecutorService = Depends(get_executor_service)
):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@router.get("/skills", response_model=List[SkillInfo])
async def list_skills(
    executor: ExecutorService = Depends(get_executor_service)
):
    """Get list of all available skills"""
    return executor.list_skills()


@router.get("/skills/{skill_name}", response_model=SkillDetail)
async def get_skill(
    skill_name: str,
    executor: ExecutorService = Depends(get_executor_service)
):
    """Get detailed information about a specific skill"""
    skill = executor.get_skill(skill_name)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found"
        )
    return skill


@router.get("/skills/{skill_name}/scripts", response_model=List[ScriptInfo])
async def list_skill_scripts(
    skill_name: str,
    executor: ExecutorService = Depends(get_executor_service)
):
    """List all scripts in a specific skill"""
    try:
        return executor.list_scripts(skill_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/skills/{skill_name}/scripts/{script_name}", response_model=ExecuteScriptResponse)
async def execute_script(
    skill_name: str,
    script_name: str,
    request: ExecuteScriptRequest,
    executor: ExecutorService = Depends(get_executor_service)
):
    """Execute a specific script from a skill"""
    try:
        result = executor.execute_script(
            skill_name, script_name, request.arguments
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Script execution failed: {str(e)}"
        )


@router.post("/execute", response_model=ExecuteResponse)
async def execute_query(
    request: ExecuteRequest,
    executor: ExecutorService = Depends(get_executor_service)
):
    """Execute a natural language query using AI and available skills

    This endpoint will:
    1. Parse the natural language query
    2. Use AI to determine which skills/scripts to use
    3. Execute the appropriate scripts
    4. Return the results in natural language
    """
    try:
        result = await executor.execute(request.query, request.verbose)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


@router.get("/audit/logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    limit: int = 100,
    executor: ExecutorService = Depends(get_executor_service)
):
    """Get audit logs for security and compliance

    Returns recent audit events including:
    - Script executions
    - Access denied events
    - File read operations
    """
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 1000"
        )

    return executor.get_audit_logs(limit)


@router.get("/stats")
async def get_statistics(
    executor: ExecutorService = Depends(get_executor_service)
):
    """Get service statistics"""
    return {
        "skills_count": executor.skills_count,
        "total_scripts_count": executor.total_scripts_count,
        "provider": executor.provider
    }
