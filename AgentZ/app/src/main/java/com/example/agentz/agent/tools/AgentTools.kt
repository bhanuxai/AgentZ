package com.example.agentz.agent.tools

import com.example.agentz.data.models.RiskLevel

interface AgentTool {
    val name: String
    val description: String
    val parameterSchema: Map<String, String>
    val defaultRisk: RiskLevel

    suspend fun execute(args: Map<String, String>): ToolExecutionResult
}

data class ToolExecutionResult(
    val success: Boolean,
    val output: String,
    val data: Map<String, String> = emptyMap(),
    val error: String? = null
)

object ToolRegistry {
    private val tools = mutableMapOf<String, AgentTool>()

    fun register(tool: AgentTool) {
        tools[tool.name] = tool
    }

    fun getTool(name: String): AgentTool? = tools[name]

    fun getAllTools(): List<AgentTool> = tools.values.toList()
}
