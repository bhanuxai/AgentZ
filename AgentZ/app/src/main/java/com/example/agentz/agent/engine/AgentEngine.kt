package com.example.agentz.agent.engine

import android.content.Context
import com.example.agentz.agent.planner.AgentPlanner
import com.example.agentz.agent.planner.PlanResult
import com.example.agentz.android.apps.AppRegistry
import com.example.agentz.android.apps.MockRapidoAdapter
import com.example.agentz.android.apps.RapidoAdapter
import com.example.agentz.android.apps.RideBookingAdapter
import com.example.agentz.android.location.AgentLocationProvider
import com.example.agentz.core.security.ActionPolicyEngine
import com.example.agentz.data.local.AgentRepository
import com.example.agentz.data.models.ActivityLogItem
import com.example.agentz.data.models.AgentMode
import com.example.agentz.data.models.ChatMessage
import com.example.agentz.data.models.ConfirmationDetails
import com.example.agentz.data.models.ExecutionStep
import com.example.agentz.data.models.RiskLevel
import com.example.agentz.data.models.StepStatus
import com.example.agentz.data.models.TaskStatus
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class AgentEngine(
    private val context: Context,
    private val repository: AgentRepository,
    private val scope: CoroutineScope
) {

    private val planner = AgentPlanner()
    private val appRegistry = AppRegistry(context)
    private val mockAdapter = MockRapidoAdapter()
    private val rapidoAdapter = RapidoAdapter(context, appRegistry, mockAdapter)
    private val locationProvider = AgentLocationProvider(context)

    private val _taskStatus = MutableStateFlow(TaskStatus.IDLE)
    val taskStatus: StateFlow<TaskStatus> = _taskStatus.asStateFlow()

    private val _currentSteps = MutableStateFlow<List<ExecutionStep>>(emptyList())
    val currentSteps: StateFlow<List<ExecutionStep>> = _currentSteps.asStateFlow()

    private val _currentConfirmation = MutableStateFlow<ConfirmationDetails?>(null)
    val currentConfirmation: StateFlow<ConfirmationDetails?> = _currentConfirmation.asStateFlow()

    private var executionJob: Job? = null
    private var pendingHighRiskStep: ExecutionStep? = null
    private var activePlanResult: PlanResult? = null

    fun resetConversation() {
        stopExecution()
        planner.reset()
        _taskStatus.value = TaskStatus.IDLE
        _currentSteps.value = emptyList()
        _currentConfirmation.value = null
        repository.clearMessages()
    }

    fun handleUserMessage(messageText: String) {
        // Add user message to UI
        repository.addMessage(ChatMessage(text = messageText, isUser = true))

        // Get saved memory preferences
        val memories = repository.memories.value.associate { it.key to it.value }

        // Plan
        _taskStatus.value = TaskStatus.UNDERSTANDING
        val plan = planner.plan(messageText, memories)
        activePlanResult = plan

        if (plan.missingParameters.isNotEmpty()) {
            // Need more information
            _taskStatus.value = TaskStatus.COLLECTING_INFORMATION
            repository.addMessage(
                ChatMessage(
                    text = plan.questionToUser ?: plan.responseText,
                    isUser = false,
                    suggestedReplies = plan.suggestedOptions,
                    taskStatus = TaskStatus.COLLECTING_INFORMATION,
                    thinkingProcess = plan.thinkingProcess,
                    intentCategory = plan.intentCategory,
                    latencyMs = plan.latencyMs
                )
            )
            return
        }

        if (plan.steps.isEmpty()) {
            // General query / completed
            _taskStatus.value = TaskStatus.COMPLETED
            repository.addMessage(
                ChatMessage(
                    text = plan.responseText,
                    isUser = false,
                    taskStatus = TaskStatus.COMPLETED,
                    thinkingProcess = plan.thinkingProcess,
                    intentCategory = plan.intentCategory,
                    latencyMs = plan.latencyMs
                )
            )
            return
        }

        // Ready to execute plan!
        _taskStatus.value = TaskStatus.PLANNING
        _currentSteps.value = plan.steps

        // Emit initial agent progress card
        repository.addMessage(
            ChatMessage(
                text = plan.responseText,
                isUser = false,
                steps = plan.steps,
                taskStatus = TaskStatus.EXECUTING,
                isExecutionActive = true,
                currentActionDescription = "Understanding request",
                thinkingProcess = plan.thinkingProcess,
                intentCategory = plan.intentCategory,
                latencyMs = plan.latencyMs
            )
        )

        executePlanSteps(plan)
    }

    private fun executePlanSteps(plan: PlanResult) {
        executionJob?.cancel()
        executionJob = scope.launch(Dispatchers.Main) {
            _taskStatus.value = TaskStatus.EXECUTING
            val steps = plan.steps.toMutableList()
            val adapter: RideBookingAdapter = when (repository.agentMode.value) {
                AgentMode.MOCK_MODE -> mockAdapter
                AgentMode.DEVICE_MODE -> rapidoAdapter
                AgentMode.DEMO_MODE -> mockAdapter
            }

            for (i in steps.indices) {
                val step = steps[i]

                // Policy Engine Check
                val policyCheck = ActionPolicyEngine.validateAction(
                    actionType = step.tool,
                    targetName = step.title,
                    isUserConfirmed = false,
                    parameters = step.toolArgs
                )

                if (policyCheck.requiresConfirmation && policyCheck.riskLevel == RiskLevel.HIGH) {
                    // STOP and gate on User Confirmation Card!
                    _taskStatus.value = TaskStatus.WAITING_FOR_CONFIRMATION
                    pendingHighRiskStep = step
                    _currentConfirmation.value = plan.confirmationCard

                    repository.updateLastMessage { msg ->
                        msg.copy(
                            steps = steps.toList(),
                            taskStatus = TaskStatus.WAITING_FOR_CONFIRMATION,
                            isExecutionActive = false,
                            confirmationCard = plan.confirmationCard,
                            currentActionDescription = "Security gate: Waiting for user authorization"
                        )
                    }
                    return@launch
                }

                // Execute low/medium risk step
                step.status = StepStatus.RUNNING
                updateStepInState(step, steps, "Executing ${step.title}")

                val pacingDelay = if (repository.agentMode.value == AgentMode.DEMO_MODE) 450L else 750L
                delay(pacingDelay)

                // Perform tool logic
                val success = when (step.tool) {
                    "internal_parse" -> true
                    "get_current_location" -> {
                        locationProvider.getCurrentLocation()
                        true
                    }
                    "open_app" -> adapter.openProvider()
                    "type_text" -> {
                        val field = step.toolArgs["field"] ?: ""
                        val value = step.toolArgs["value"] ?: ""
                        if (field == "pickup") adapter.setPickup(value) else adapter.setDestination(value)
                    }
                    "click_ui_element" -> adapter.selectVehicle(step.toolArgs["target"] ?: "Auto")
                    "read_screen" -> {
                        val fare = adapter.readFare()
                        step.resultText = "Fare read: $fare"
                        true
                    }
                    else -> true
                }

                if (success) {
                    step.status = StepStatus.SUCCESS
                    updateStepInState(step, steps, "Completed ${step.title}")
                } else {
                    step.status = StepStatus.FAILED
                    _taskStatus.value = TaskStatus.EXECUTION_FAILED
                    updateStepInState(step, steps, "Failed at ${step.title}")
                    return@launch
                }
            }
        }
    }

    fun confirmConsequentialAction(confirmed: Boolean) {
        if (_taskStatus.value != TaskStatus.WAITING_FOR_CONFIRMATION) return

        if (!confirmed) {
            _taskStatus.value = TaskStatus.CANCELLED
            repository.updateLastMessage { msg ->
                msg.copy(
                    taskStatus = TaskStatus.CANCELLED,
                    confirmationCard = null,
                    isExecutionActive = false,
                    currentActionDescription = "Action rejected by user"
                )
            }
            repository.addMessage(
                ChatMessage(
                    text = "❌ **Booking cancelled**\n\nExecution was aborted safely. No transaction was made.",
                    isUser = false,
                    taskStatus = TaskStatus.CANCELLED
                )
            )
            repository.addActivityLog(
                ActivityLogItem(
                    taskTitle = "Rapido Booking",
                    appName = "Rapido",
                    status = "Cancelled by user",
                    riskLevel = RiskLevel.HIGH,
                    details = "User declined booking confirmation card.",
                    permissionsUsed = listOf("Location")
                )
            )
            return
        }

        // User confirmed!
        _taskStatus.value = TaskStatus.FINALIZING
        _currentConfirmation.value = null

        scope.launch(Dispatchers.Main) {
            val steps = _currentSteps.value.toMutableList()
            val step = pendingHighRiskStep ?: steps.lastOrNull()

            if (step != null) {
                step.status = StepStatus.RUNNING
                updateStepInState(step, steps, "Placing confirmed booking...")

                val adapter: RideBookingAdapter = if (repository.agentMode.value == AgentMode.DEVICE_MODE) rapidoAdapter else mockAdapter
                val booked = adapter.confirmBooking()
                delay(600)

                if (booked) {
                    _taskStatus.value = TaskStatus.VERIFYING
                    updateStepInState(step, steps, "Verifying ride booking status...")
                    val verified = adapter.verifyBooking()
                    delay(500)

                    if (verified) {
                        step.status = StepStatus.SUCCESS
                        _taskStatus.value = TaskStatus.COMPLETED
                        updateStepInState(step, steps, "Booking verified")

                        repository.updateLastMessage { msg ->
                            msg.copy(
                                steps = steps.toList(),
                                taskStatus = TaskStatus.COMPLETED,
                                confirmationCard = null,
                                isExecutionActive = false,
                                currentActionDescription = "Ride confirmed!"
                            )
                        }

                        val vehicle = activePlanResult?.entities?.get("vehicle") ?: "Auto"
                        val fare = activePlanResult?.confirmationCard?.fare ?: "₹183"

                        repository.addMessage(
                            ChatMessage(
                                text = "✅ **Booking confirmed**\n\nYour Rapido **$vehicle** has been booked successfully!\n• Estimated fare: **$fare**\n• Payment: **Cash**\n• Status: Captain is en route to your location.",
                                isUser = false,
                                taskStatus = TaskStatus.COMPLETED,
                                intentCategory = "Ride Automation",
                                latencyMs = 120
                            )
                        )

                        repository.addActivityLog(
                            ActivityLogItem(
                                taskTitle = "Rapido $vehicle Booking",
                                appName = "Rapido",
                                status = "Completed",
                                riskLevel = RiskLevel.HIGH,
                                details = "Successfully booked $vehicle to Lovely Professional University. Fare: $fare.",
                                permissionsUsed = listOf("Location", "Accessibility")
                            )
                        )
                    }
                }
            }
        }
    }

    fun stopExecution() {
        executionJob?.cancel()
        executionJob = null
        if (_taskStatus.value == TaskStatus.EXECUTING || _taskStatus.value == TaskStatus.WAITING_FOR_CONFIRMATION) {
            _taskStatus.value = TaskStatus.CANCELLED
            repository.updateLastMessage { msg ->
                msg.copy(
                    taskStatus = TaskStatus.CANCELLED,
                    isExecutionActive = false,
                    currentActionDescription = "Agent execution stopped by user"
                )
            }
            repository.addMessage(
                ChatMessage(
                    text = "🛑 **Agent stopped**\n\nExecution was halted safely.",
                    isUser = false,
                    taskStatus = TaskStatus.CANCELLED
                )
            )
        }
    }

    private fun updateStepInState(step: ExecutionStep, steps: List<ExecutionStep>, actionDescription: String) {
        _currentSteps.value = steps.toList()
        repository.updateLastMessage { msg ->
            msg.copy(
                steps = steps.toList(),
                currentActionDescription = actionDescription
            )
        }
    }
}
