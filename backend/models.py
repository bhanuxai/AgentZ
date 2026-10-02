from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TaskStatus(str, Enum):
    IDLE = "IDLE"
    UNDERSTANDING = "UNDERSTANDING"
    COLLECTING_INFORMATION = "COLLECTING_INFORMATION"
    PLANNING = "PLANNING"
    WAITING_FOR_PERMISSION = "WAITING_FOR_PERMISSION"
    EXECUTING = "EXECUTING"
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    FINALIZING = "FINALIZING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    CANCELLED = "CANCELLED"

class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class DeviceTarget(str, Enum):
    LAPTOP = "LAPTOP"
    ANDROID = "ANDROID"
    AUTO = "AUTO"

class ExecutionStep(BaseModel):
    id: str
    title: str
    description: str = ""
    tool: str
    tool_args: Dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ConfirmationCard(BaseModel):
    title: str = "Confirm Action"
    provider: str = "Rapido"
    service_type: str = "Auto"
    pickup: str = "Current location"
    destination: str = ""
    fare: str = "₹183"
    payment_method: str = "Cash"
    risk_level: RiskLevel = RiskLevel.HIGH
    message: str = "Please confirm the action details before proceeding."
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PlanRequest(BaseModel):
    conversation_id: Optional[str] = "default_conv"
    user_message: Optional[str] = None
    message: Optional[str] = None
    user_text: Optional[str] = None
    prompt: Optional[str] = None
    query: Optional[str] = None
    text: Optional[str] = None
    device_target: Optional[str] = "AUTO"  # "LAPTOP", "ANDROID", or "AUTO"
    is_voice: Optional[bool] = False
    history: List[Dict[str, str]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)

    def get_text(self) -> str:
        return (self.user_message or self.message or self.user_text or self.prompt or self.query or self.text or "").strip()

    def get_conversation_id(self) -> str:
        return self.conversation_id or "default_conv"

class PlanResponse(BaseModel):
    conversation_id: str
    task_id: str
    intent: str
    device_target: str = "LAPTOP"
    entities: Dict[str, Any] = Field(default_factory=dict)
    missing_information: List[str] = Field(default_factory=list)
    question_to_user: Optional[str] = None
    suggested_options: List[str] = Field(default_factory=list)
    steps: List[ExecutionStep] = Field(default_factory=list)
    status: TaskStatus
    requires_confirmation: bool = False
    confirmation: Optional[ConfirmationCard] = None
    message: str = ""
    spoken_response: Optional[str] = None

class ExecuteRequest(BaseModel):
    task_id: Optional[str] = None
    taskId: Optional[str] = None
    id: Optional[str] = None
    current_step_id: Optional[str] = None
    step_result: Optional[Dict[str, Any]] = None
    is_voice: Optional[bool] = False

    def get_task_id(self) -> str:
        return self.task_id or self.taskId or self.id or ""

class ExecuteResponse(BaseModel):
    task_id: str
    status: TaskStatus
    next_step: Optional[ExecutionStep] = None
    requires_confirmation: bool = False
    confirmation: Optional[ConfirmationCard] = None
    is_completed: bool = False
    message: str
    spoken_response: Optional[str] = None
    desktop_result: Optional[Dict[str, Any]] = None

class ConfirmRequest(BaseModel):
    task_id: Optional[str] = None
    taskId: Optional[str] = None
    id: Optional[str] = None
    confirmed: bool = True
    user_note: Optional[str] = None

    def get_task_id(self) -> str:
        return self.task_id or self.taskId or self.id or ""

class ConfirmResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str

class CancelRequest(BaseModel):
    task_id: Optional[str] = None
    taskId: Optional[str] = None
    id: Optional[str] = None
    reason: Optional[str] = None

    def get_task_id(self) -> str:
        return self.task_id or self.taskId or self.id or ""
