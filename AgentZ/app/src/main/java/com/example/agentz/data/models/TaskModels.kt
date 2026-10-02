package com.example.agentz.data.models

import java.util.UUID

enum class RiskLevel {
    LOW,
    MEDIUM,
    HIGH
}

enum class TaskStatus {
    IDLE,
    UNDERSTANDING,
    COLLECTING_INFORMATION,
    PLANNING,
    WAITING_FOR_PERMISSION,
    EXECUTING,
    WAITING_FOR_CONFIRMATION,
    FINALIZING,
    VERIFYING,
    COMPLETED,
    EXECUTION_FAILED,
    CANCELLED
}

enum class StepStatus {
    PENDING,
    RUNNING,
    SUCCESS,
    FAILED,
    CANCELLED
}

enum class AgentMode {
    MOCK_MODE,    // Uses simulated sandbox apps for reliable verification
    DEVICE_MODE,  // Uses real Android applications via AccessibilityService
    DEMO_MODE     // Controlled presentation flow with visual highlights
}

data class ExecutionStep(
    val id: String = UUID.randomUUID().toString().take(8),
    val title: String,
    val description: String = "",
    val tool: String,
    val toolArgs: Map<String, String> = emptyMap(),
    val riskLevel: RiskLevel = RiskLevel.LOW,
    var status: StepStatus = StepStatus.PENDING,
    var resultText: String? = null,
    var errorText: String? = null,
    val durationMs: Long = 0
)

data class ConfirmationDetails(
    val title: String = "Confirm booking",
    val provider: String = "Rapido",
    val vehicle: String = "Auto",
    val pickup: String = "Current location",
    val destination: String = "Lovely Professional University (LPU)",
    val fare: String = "₹183",
    val paymentMethod: String = "Cash",
    val riskLevel: RiskLevel = RiskLevel.HIGH,
    val message: String = "Please confirm the booking details before proceeding."
)

data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val text: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis(),
    val options: List<String> = emptyMap<String, String>().keys.toList(),
    val suggestedReplies: List<String> = emptyList(),
    val confirmationCard: ConfirmationDetails? = null,
    val steps: List<ExecutionStep> = emptyList(),
    val taskStatus: TaskStatus = TaskStatus.IDLE,
    val isExecutionActive: Boolean = false,
    val currentActionDescription: String? = null,
    val thinkingProcess: String? = null,
    val intentCategory: String? = null,
    val latencyMs: Long = 0
)

data class ActivityLogItem(
    val id: String = UUID.randomUUID().toString().take(8),
    val timestamp: Long = System.currentTimeMillis(),
    val taskTitle: String,
    val appName: String,
    val status: String,
    val riskLevel: RiskLevel,
    val details: String,
    val permissionsUsed: List<String> = emptyList()
)

data class UserMemory(
    val id: String = UUID.randomUUID().toString().take(8),
    val key: String,
    val value: String,
    val category: String = "General"
)
