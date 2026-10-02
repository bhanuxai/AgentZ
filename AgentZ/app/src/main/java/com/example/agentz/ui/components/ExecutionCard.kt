package com.example.agentz.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ElectricBolt
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.agentz.data.models.ExecutionStep
import com.example.agentz.data.models.RiskLevel
import com.example.agentz.data.models.StepStatus
import com.example.agentz.data.models.TaskStatus
import com.example.agentz.theme.AgentCyan
import com.example.agentz.theme.AgentViolet
import com.example.agentz.theme.NeonAmber
import com.example.agentz.theme.NeonGreen
import com.example.agentz.theme.NeonRose

@Composable
fun ExecutionCard(
    steps: List<ExecutionStep>,
    taskStatus: TaskStatus,
    currentAction: String?,
    isExecutionActive: Boolean,
    onStopClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    val completedCount = steps.count { it.status == StepStatus.SUCCESS }
    val totalCount = steps.size
    val progress = if (totalCount > 0) completedCount.toFloat() / totalCount else 0f

    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.4f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(800, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "hudPulse"
    )

    Surface(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .border(
                1.dp,
                if (isExecutionActive) AgentCyan.copy(alpha = 0.5f) else MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f),
                RoundedCornerShape(16.dp)
            ),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        tonalElevation = 2.dp
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header Bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (isExecutionActive) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(AgentCyan.copy(alpha = pulseAlpha))
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Agent Pipeline Active",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = AgentCyan
                        )
                    } else {
                        val headerText = when (taskStatus) {
                            TaskStatus.COMPLETED -> "Pipeline Completed"
                            TaskStatus.CANCELLED -> "Pipeline Halted"
                            TaskStatus.WAITING_FOR_CONFIRMATION -> "Security Gate Active"
                            else -> "Execution Pipeline"
                        }
                        val headerColor = when (taskStatus) {
                            TaskStatus.COMPLETED -> NeonGreen
                            TaskStatus.WAITING_FOR_CONFIRMATION -> NeonAmber
                            TaskStatus.CANCELLED -> NeonRose
                            else -> MaterialTheme.colorScheme.onSurface
                        }
                        Text(
                            text = headerText,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = headerColor
                        )
                    }
                }

                if (isExecutionActive) {
                    OutlinedButton(
                        onClick = onStopClick,
                        shape = RoundedCornerShape(20.dp),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = NeonRose,
                            containerColor = NeonRose.copy(alpha = 0.1f)
                        ),
                        border = androidx.compose.foundation.BorderStroke(1.dp, NeonRose.copy(alpha = 0.5f)),
                        modifier = Modifier.height(28.dp),
                        contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 10.dp, vertical = 0.dp)
                    ) {
                        Icon(Icons.Default.Stop, contentDescription = "Stop", modifier = Modifier.size(12.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("STOP", fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            // Progress Bar & Step Counter
            if (totalCount > 0) {
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Step $completedCount of $totalCount",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.outline,
                        fontWeight = FontWeight.SemiBold
                    )
                    Text(
                        text = "${(progress * 100).toInt()}%",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (progress == 1f) NeonGreen else AgentCyan,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
                LinearProgressIndicator(
                    progress = { progress },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(4.dp)
                        .clip(RoundedCornerShape(2.dp)),
                    color = if (progress == 1f) NeonGreen else AgentCyan,
                    trackColor = MaterialTheme.colorScheme.surfaceVariant
                )
            }

            if (!currentAction.isNullOrBlank() && isExecutionActive) {
                Spacer(modifier = Modifier.height(10.dp))
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = AgentCyan.copy(alpha = 0.1f),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.ElectricBolt, contentDescription = null, tint = AgentCyan, modifier = Modifier.size(14.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = currentAction,
                            style = MaterialTheme.typography.bodySmall,
                            color = AgentCyan,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Connected Timeline Steps
            Column(modifier = Modifier.fillMaxWidth()) {
                steps.forEachIndexed { index, step ->
                    TimelineStepRow(
                        step = step,
                        isLast = index == steps.size - 1,
                        showDetail = expanded
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Expand/Collapse Details Button
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { expanded = !expanded }
                    .padding(vertical = 4.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = if (expanded) "Hide tool payloads" else "Inspect tool payloads & risk",
                    style = MaterialTheme.typography.labelSmall,
                    color = AgentCyan,
                    fontWeight = FontWeight.SemiBold
                )
                Spacer(modifier = Modifier.width(4.dp))
                Icon(
                    imageVector = if (expanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                    contentDescription = null,
                    modifier = Modifier.size(14.dp),
                    tint = AgentCyan
                )
            }
        }
    }
}

@Composable
private fun TimelineStepRow(
    step: ExecutionStep,
    isLast: Boolean,
    showDetail: Boolean
) {
    Row(
        modifier = Modifier.fillMaxWidth()
    ) {
        // Node & Vertical Line
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.width(24.dp)
        ) {
            when (step.status) {
                StepStatus.SUCCESS -> {
                    Box(
                        modifier = Modifier
                            .size(18.dp)
                            .background(NeonGreen, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Check,
                            contentDescription = "Success",
                            tint = Color.Black,
                            modifier = Modifier.size(11.dp)
                        )
                    }
                }
                StepStatus.RUNNING -> {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp,
                        color = AgentCyan
                    )
                }
                StepStatus.FAILED -> {
                    Box(
                        modifier = Modifier
                            .size(18.dp)
                            .background(NeonRose, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Failed",
                            tint = Color.White,
                            modifier = Modifier.size(11.dp)
                        )
                    }
                }
                StepStatus.PENDING, StepStatus.CANCELLED -> {
                    if (step.riskLevel == RiskLevel.HIGH) {
                        Box(
                            modifier = Modifier
                                .size(18.dp)
                                .border(1.5.dp, NeonAmber, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Security,
                                contentDescription = "Security Gate",
                                tint = NeonAmber,
                                modifier = Modifier.size(10.dp)
                            )
                        }
                    } else {
                        Box(
                            modifier = Modifier
                                .size(18.dp)
                                .border(1.5.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.4f), CircleShape)
                        )
                    }
                }
            }

            if (!isLast) {
                Box(
                    modifier = Modifier
                        .width(1.5.dp)
                        .height(if (showDetail) 48.dp else 18.dp)
                        .background(
                            if (step.status == StepStatus.SUCCESS) NeonGreen.copy(alpha = 0.4f)
                            else MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.3f)
                        )
                )
            }
        }

        Spacer(modifier = Modifier.width(10.dp))

        // Text & Detail Payload
        Column(
            modifier = Modifier
                .weight(1f)
                .padding(bottom = if (isLast) 0.dp else 6.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = step.title,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = if (step.status == StepStatus.RUNNING) FontWeight.Bold else FontWeight.Normal,
                    color = when (step.status) {
                        StepStatus.SUCCESS -> MaterialTheme.colorScheme.onSurface
                        StepStatus.RUNNING -> AgentCyan
                        StepStatus.FAILED -> NeonRose
                        else -> MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f)
                    }
                )

                if (step.riskLevel == RiskLevel.HIGH) {
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = NeonAmber.copy(alpha = 0.15f)
                    ) {
                        Text(
                            text = "GATE",
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            color = NeonAmber,
                            modifier = Modifier.padding(horizontal = 4.dp, vertical = 1.dp)
                        )
                    }
                }
            }

            AnimatedVisibility(visible = showDetail) {
                Column(modifier = Modifier.padding(top = 2.dp, bottom = 4.dp)) {
                    if (step.description.isNotBlank()) {
                        Text(
                            text = step.description,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f)
                        )
                    }
                    Text(
                        text = "tool: `${step.tool}` ${if (step.toolArgs.isNotEmpty()) "| args: ${step.toolArgs}" else ""}",
                        style = MaterialTheme.typography.labelSmall,
                        color = AgentCyan.copy(alpha = 0.8f),
                        fontFamily = FontFamily.Monospace,
                        fontSize = 10.sp
                    )
                }
            }
        }
    }
}
