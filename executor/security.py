"""安全配置和审计日志模块

符合 Anthropic Agent Skills 安全语义规范
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from enum import Enum


class AuditLevel(Enum):
    """审计级别"""
    NONE = "none"       # 不记录
    BASIC = "basic"     # 记录基本操作
    DETAILED = "detailed"  # 记录详细信息


@dataclass
class SecurityConfig:
    """安全配置

    符合 Anthropic Agent Skills 安全建议：
    - allowlist/denylist
    - 审计日志
    - 路径限制
    - 执行时间限制
    """

    # 路径控制
    allowed_script_paths: list[Path] | None = None  # 允许执行脚本的路径白名单
    denied_script_patterns: list[str] | None = None  # 禁止的脚本模式黑名单

    # 执行限制
    max_execution_time: int = 300  # 最大执行时间（秒）
    max_output_size: int = 1024 * 1024  # 最大输出大小（1MB）

    # 网络控制
    enable_network: bool = False  # 是否允许网络访问

    # 审计日志
    audit_level: AuditLevel = AuditLevel.BASIC
    audit_log_file: str | None = None  # 审计日志文件路径
    audit_to_console: bool = False  # 是否输出到控制台

    def __post_init__(self):
        """初始化后处理"""
        # 设置日志
        self._setup_logging()

        # 转换路径
        if self.allowed_script_paths:
            self.allowed_script_paths = [Path(p) if isinstance(p, str) else p
                                        for p in self.allowed_script_paths]

    def _setup_logging(self):
        """设置审计日志"""
        self.logger = logging.getLogger("skill_executor.audit")

        # 设置日志级别
        if self.audit_level == AuditLevel.NONE:
            self.logger.setLevel(logging.CRITICAL + 1)  # 禁用所有日志
        elif self.audit_level == AuditLevel.DETAILED:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        # 清除现有处理器
        self.logger.handlers.clear()

        # 添加文件处理器
        if self.audit_log_file:
            file_handler = logging.FileHandler(self.audit_log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(file_handler)

        # 添加控制台处理器
        if self.audit_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(console_handler)

    def is_path_allowed(self, path: Path) -> bool:
        """检查路径是否在允许列表中"""
        if not self.allowed_script_paths:
            return True  # 没有配置白名单，允许所有路径

        path = path.resolve()
        for allowed_path in self.allowed_script_paths:
            if allowed_path in path.parents or path == allowed_path.resolve():
                return True
        return False

    def is_script_denied(self, script_name: str) -> bool:
        """检查脚本是否在黑名单中"""
        if not self.denied_script_patterns:
            return False

        import re
        for pattern in self.denied_script_patterns:
            if re.search(pattern, script_name):
                return True
        return False


@dataclass
class AuditEvent:
    """审计事件"""
    timestamp: str
    event_type: str  # "skill_loaded", "script_executed", "file_read", "file_denied"
    skill_name: str | None = None
    script_name: str | None = None
    file_path: str | None = None
    exit_code: int | None = None
    execution_time: float | None = None
    output_size: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "skill_name": self.skill_name,
            "script_name": self.script_name,
            "file_path": str(self.file_path) if self.file_path else None,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,
            "output_size": self.output_size,
            "metadata": self.metadata
        }


class Auditor:
    """审计员"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.events: list[AuditEvent] = []

    def log_skill_loaded(self, skill_name: str, skill_path: Path, script_count: int):
        """记录 skill 加载"""
        if self.config.audit_level == AuditLevel.NONE:
            return

        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="skill_loaded",
            skill_name=skill_name,
            file_path=str(skill_path),
            metadata={"script_count": script_count}
        )
        self._log_event(event)

    def log_script_executed(
        self,
        skill_name: str,
        script_name: str,
        script_path: Path,
        exit_code: int,
        execution_time: float,
        output_size: int
    ):
        """记录脚本执行"""
        if self.config.audit_level == AuditLevel.NONE:
            return

        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="script_executed",
            skill_name=skill_name,
            script_name=script_name,
            file_path=str(script_path),
            exit_code=exit_code,
            execution_time=execution_time,
            output_size=output_size
        )
        self._log_event(event)

    def log_file_read(self, skill_name: str, file_path: Path, file_size: int):
        """记录文件读取"""
        if self.config.audit_level == AuditLevel.DETAILED:
            event = AuditEvent(
                timestamp=datetime.now().isoformat(),
                event_type="file_read",
                skill_name=skill_name,
                file_path=str(file_path),
                metadata={"file_size": file_size}
            )
            self._log_event(event)

    def log_file_write(self, file_path: Path, file_size: int, skill_name: str | None = None):
        """记录文件写入"""
        if self.config.audit_level == AuditLevel.NONE:
            return

        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="file_write",
            skill_name=skill_name,
            file_path=str(file_path),
            metadata={"file_size": file_size}
        )
        self._log_event(event)

    def log_access_denied(self, resource_type: str, resource_name: str, reason: str):
        """记录访问拒绝"""
        if self.config.audit_level == AuditLevel.NONE:
            return

        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_type="access_denied",
            metadata={
                "resource_type": resource_type,
                "resource_name": resource_name,
                "reason": reason
            }
        )
        self._log_event(event)

    def _log_event(self, event: AuditEvent):
        """记录事件"""
        self.events.append(event)

        # 记录到日志
        log_msg = f"{event.event_type}"
        if event.skill_name:
            log_msg += f" | skill: {event.skill_name}"
        if event.script_name:
            log_msg += f" | script: {event.script_name}"
        if event.exit_code is not None:
            log_msg += f" | exit_code: {event.exit_code}"

        self.config.logger.info(log_msg)

        # 详细模式：记录完整 JSON
        if self.config.audit_level == AuditLevel.DETAILED:
            self.config.logger.debug(json.dumps(event.to_dict()))
