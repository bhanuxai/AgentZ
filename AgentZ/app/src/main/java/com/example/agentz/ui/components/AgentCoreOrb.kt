package com.example.agentz.ui.components

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.agentz.data.models.TaskStatus
import com.example.agentz.theme.AgentCyan
import com.example.agentz.theme.AgentViolet
import com.example.agentz.theme.NeonAmber
import com.example.agentz.theme.NeonGreen
import com.example.agentz.theme.NeonRose

@Composable
fun AgentCoreOrb(
    size: Dp = 48.dp,
    taskStatus: TaskStatus = TaskStatus.IDLE,
    isThinking: Boolean = false,
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "AgentOrbTransition")

    // Pulse animation
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.08f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = if (isThinking || taskStatus == TaskStatus.EXECUTING) 800 else 1800, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "OrbPulse"
    )

    // Halo scale
    val haloScale by infiniteTransition.animateFloat(
        initialValue = 1.0f,
        targetValue = 1.35f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = if (isThinking || taskStatus == TaskStatus.EXECUTING) 1000 else 2200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "HaloPulse"
    )

    // Subtle rotation for active states
    val rotationAngle by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 6000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "OrbRotation"
    )

    val coreGradient = when {
        taskStatus == TaskStatus.WAITING_FOR_CONFIRMATION -> Brush.sweepGradient(
            listOf(NeonAmber, Color(0xFFFFB300), NeonAmber)
        )
        taskStatus == TaskStatus.COMPLETED -> Brush.sweepGradient(
            listOf(NeonGreen, Color(0xFF00E676), NeonGreen)
        )
        taskStatus == TaskStatus.EXECUTION_FAILED || taskStatus == TaskStatus.CANCELLED -> Brush.sweepGradient(
            listOf(NeonRose, Color(0xFFFF1744), NeonRose)
        )
        isThinking || taskStatus == TaskStatus.EXECUTING || taskStatus == TaskStatus.PLANNING -> Brush.sweepGradient(
            listOf(AgentCyan, AgentViolet, Color(0xFF00E5FF), AgentViolet)
        )
        else -> Brush.sweepGradient(
            listOf(AgentCyan, AgentViolet, AgentCyan)
        )
    }

    val glowColor = when {
        taskStatus == TaskStatus.WAITING_FOR_CONFIRMATION -> NeonAmber
        taskStatus == TaskStatus.COMPLETED -> NeonGreen
        taskStatus == TaskStatus.EXECUTION_FAILED || taskStatus == TaskStatus.CANCELLED -> NeonRose
        else -> AgentCyan
    }

    Box(
        modifier = modifier.size(size),
        contentAlignment = Alignment.Center
    ) {
        // Outer ambient glow ring
        Box(
            modifier = Modifier
                .size(size * 1.15f)
                .scale(haloScale)
                .background(
                    Brush.radialGradient(
                        colors = listOf(glowColor.copy(alpha = 0.35f), Color.Transparent)
                    ),
                    shape = CircleShape
                )
        )

        // Mid pulsing orbital boundary
        Box(
            modifier = Modifier
                .size(size)
                .scale(pulseScale)
                .rotate(rotationAngle)
                .border(
                    width = if (size > 40.dp) 2.dp else 1.dp,
                    brush = coreGradient,
                    shape = CircleShape
                )
        )

        // Core Center Orb
        Box(
            modifier = Modifier
                .size(size * 0.82f)
                .clip(CircleShape)
                .background(coreGradient),
            contentAlignment = Alignment.Center
        ) {
            val fontSize = (size.value * 0.45f).sp
            Text(
                text = "Z",
                fontSize = fontSize,
                fontWeight = FontWeight.Black,
                color = Color.White
            )
        }
    }
}
