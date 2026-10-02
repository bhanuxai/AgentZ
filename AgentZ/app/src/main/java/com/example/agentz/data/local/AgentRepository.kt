package com.example.agentz.data.local

import android.content.Context
import android.content.SharedPreferences
import com.example.agentz.data.models.ActivityLogItem
import com.example.agentz.data.models.AgentMode
import com.example.agentz.data.models.ChatMessage
import com.example.agentz.data.models.ExecutionStep
import com.example.agentz.data.models.RiskLevel
import com.example.agentz.data.models.TaskStatus
import com.example.agentz.data.models.UserMemory
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID

class AgentRepository(private val context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences("agentz_prefs", Context.MODE_PRIVATE)

    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

    private val _activityLogs = MutableStateFlow<List<ActivityLogItem>>(emptyList())
    val activityLogs: StateFlow<List<ActivityLogItem>> = _activityLogs.asStateFlow()

    private val _memories = MutableStateFlow<List<UserMemory>>(emptyList())
    val memories: StateFlow<List<UserMemory>> = _memories.asStateFlow()

    private val _agentMode = MutableStateFlow(AgentMode.MOCK_MODE)
    val agentMode: StateFlow<AgentMode> = _agentMode.asStateFlow()

    init {
        loadDefaultMemories()
        loadDefaultLogs()
    }

    private fun loadDefaultMemories() {
        val initialMemories = listOf(
            UserMemory(key = "Preferred ride", value = "Auto", category = "Transport"),
            UserMemory(key = "Preferred payment", value = "Cash", category = "Finance"),
            UserMemory(key = "College", value = "Lovely Professional University (LPU)", category = "Places"),
            UserMemory(key = "Home", value = "Model Town, Phagwara", category = "Places")
        )
        _memories.value = initialMemories
    }

    private fun loadDefaultLogs() {
        val initialLogs = listOf(
            ActivityLogItem(
                taskTitle = "Rapido Auto Booking",
                appName = "Rapido",
                status = "Completed",
                riskLevel = RiskLevel.HIGH,
                details = "Booked Auto from Current Location to LPU. Fare: ₹183, Payment: Cash.",
                permissionsUsed = listOf("Location", "Accessibility")
            ),
            ActivityLogItem(
                taskTitle = "Navigate to Airport",
                appName = "Google Maps",
                status = "Completed",
                riskLevel = RiskLevel.LOW,
                details = "Opened turn-by-turn directions to Vijayawada Airport.",
                permissionsUsed = listOf("Location")
            ),
            ActivityLogItem(
                taskTitle = "Draft WhatsApp Message",
                appName = "WhatsApp",
                status = "Cancelled by user",
                riskLevel = RiskLevel.HIGH,
                details = "Message drafting to Rahul cancelled at confirmation stage.",
                permissionsUsed = listOf("Accessibility")
            )
        )
        _activityLogs.value = initialLogs
    }

    fun addMessage(message: ChatMessage) {
        _messages.value = _messages.value + message
    }

    fun updateLastMessage(transform: (ChatMessage) -> ChatMessage) {
        val current = _messages.value
        if (current.isNotEmpty()) {
            val last = current.last()
            val updated = transform(last)
            _messages.value = current.dropLast(1) + updated
        }
    }

    fun clearMessages() {
        _messages.value = emptyList()
    }

    fun setAgentMode(mode: AgentMode) {
        _agentMode.value = mode
    }

    fun addActivityLog(log: ActivityLogItem) {
        _activityLogs.value = listOf(log) + _activityLogs.value
    }

    fun addMemory(key: String, value: String, category: String = "General") {
        val newMem = UserMemory(key = key, value = value, category = category)
        _memories.value = _memories.value + newMem
    }

    fun removeMemory(id: String) {
        _memories.value = _memories.value.filter { it.id != id }
    }

    fun clearMemories() {
        _memories.value = emptyList()
    }
}
