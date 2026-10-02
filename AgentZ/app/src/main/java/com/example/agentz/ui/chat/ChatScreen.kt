package com.example.agentz.ui.chat

import android.app.Activity
import android.content.Intent
import android.speech.RecognizerIntent
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.AttachFile
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material.icons.filled.PhoneAndroid
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.outlined.DirectionsCar
import androidx.compose.material.icons.outlined.History
import androidx.compose.material.icons.outlined.Message
import androidx.compose.material.icons.outlined.Psychology
import androidx.compose.material.icons.outlined.Security
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.agentz.agent.engine.AgentEngine
import com.example.agentz.data.local.AgentRepository
import com.example.agentz.data.models.AgentMode
import com.example.agentz.data.models.ChatMessage
import com.example.agentz.data.models.TaskStatus
import com.example.agentz.theme.AgentCyan
import com.example.agentz.theme.AgentVioletLight
import com.example.agentz.theme.NeonAmber
import com.example.agentz.theme.NeonGreen
import com.example.agentz.theme.NeonRose
import com.example.agentz.ui.components.AgentCoreOrb
import com.example.agentz.ui.components.AgentReasoningView
import com.example.agentz.ui.components.ConfirmationCardView
import com.example.agentz.ui.components.ExecutionCard
import com.example.agentz.ui.components.RichMarkdownText
import com.example.agentz.ui.components.VoiceListeningDialog

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    repository: AgentRepository,
    engine: AgentEngine,
    onNavigateToSettings: () -> Unit,
    onNavigateToPermissions: () -> Unit,
    onNavigateToMemory: () -> Unit,
    onNavigateToActivity: () -> Unit,
    onNavigateToMockApp: () -> Unit,
    modifier: Modifier = Modifier
) {
    val messages by repository.messages.collectAsState()
    val agentMode by repository.agentMode.collectAsState()
    val taskStatus by engine.taskStatus.collectAsState()

    var inputText by remember { mutableStateOf("") }
    var menuExpanded by remember { mutableStateOf(false) }
    var modeMenuExpanded by remember { mutableStateOf(false) }
    var showVoiceDialog by remember { mutableStateOf(false) }
    val listState = rememberLazyListState()

    val context = LocalContext.current
    val speechRecognizerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val spokenText = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull()
            if (!spokenText.isNullOrBlank()) {
                inputText = spokenText
                engine.handleUserMessage(spokenText)
            }
        }
    }

    val launchVoiceInput = {
        try {
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_PROMPT, "Say 'Hey AgentZ' or speak your request...")
            }
            speechRecognizerLauncher.launch(intent)
        } catch (e: Exception) {
            // If system recognizer not found, display in-app voice dialog
            showVoiceDialog = true
        }
    }

    // Auto-scroll on new messages
    LaunchedEffect(messages.size, messages.lastOrNull()?.steps?.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    if (showVoiceDialog) {
        VoiceListeningDialog(
            onDismiss = { showVoiceDialog = false },
            onManualInput = { cmd -> engine.handleUserMessage(cmd) }
        )
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        AgentCoreOrb(
                            size = 28.dp,
                            taskStatus = taskStatus,
                            isThinking = taskStatus == TaskStatus.UNDERSTANDING || taskStatus == TaskStatus.PLANNING
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(
                                text = "AgentZ",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                            Text(
                                text = "AI Device Agent",
                                style = MaterialTheme.typography.labelSmall,
                                color = AgentCyan,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                        Spacer(modifier = Modifier.width(10.dp))
                        
                        // Mode Switcher Pill
                        Box {
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f),
                                border = androidx.compose.foundation.BorderStroke(1.dp, AgentCyan.copy(alpha = 0.3f)),
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .clickable { modeMenuExpanded = true }
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 7.dp, vertical = 3.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(6.dp)
                                            .background(
                                                when (agentMode) {
                                                    AgentMode.MOCK_MODE -> NeonGreen
                                                    AgentMode.DEVICE_MODE -> AgentCyan
                                                    AgentMode.DEMO_MODE -> AgentVioletLight
                                                },
                                                CircleShape
                                            )
                                    )
                                    Spacer(modifier = Modifier.width(5.dp))
                                    Text(
                                        text = when (agentMode) {
                                            AgentMode.MOCK_MODE -> "SANDBOX"
                                            AgentMode.DEVICE_MODE -> "DEVICE"
                                            AgentMode.DEMO_MODE -> "DEMO"
                                        },
                                        style = MaterialTheme.typography.labelSmall,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 9.5.sp,
                                        color = MaterialTheme.colorScheme.onSurface
                                    )
                                }
                            }

                            DropdownMenu(
                                expanded = modeMenuExpanded,
                                onDismissRequest = { modeMenuExpanded = false }
                            ) {
                                DropdownMenuItem(
                                    text = { Text("MOCK_MODE (Sandbox)") },
                                    onClick = {
                                        repository.setAgentMode(AgentMode.MOCK_MODE)
                                        modeMenuExpanded = false
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text("DEVICE_MODE (Live Android)") },
                                    onClick = {
                                        repository.setAgentMode(AgentMode.DEVICE_MODE)
                                        modeMenuExpanded = false
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text("DEMO_MODE (Fast Presentation)") },
                                    onClick = {
                                        repository.setAgentMode(AgentMode.DEMO_MODE)
                                        modeMenuExpanded = false
                                    }
                                )
                            }
                        }
                    }
                },
                actions = {
                    IconButton(onClick = { engine.resetConversation() }) {
                        Icon(Icons.Default.Add, contentDescription = "New Conversation", tint = MaterialTheme.colorScheme.onSurface)
                    }
                    Box {
                        IconButton(onClick = { menuExpanded = true }) {
                            Icon(Icons.Default.MoreVert, contentDescription = "Menu", tint = MaterialTheme.colorScheme.onSurface)
                        }
                        DropdownMenu(
                            expanded = menuExpanded,
                            onDismissRequest = { menuExpanded = false }
                        ) {
                            DropdownMenuItem(
                                text = { Text("Permissions Center") },
                                onClick = {
                                    menuExpanded = false
                                    onNavigateToPermissions()
                                },
                                leadingIcon = { Icon(Icons.Outlined.Security, contentDescription = null, tint = AgentCyan) }
                            )
                            DropdownMenuItem(
                                text = { Text("Memory & Preferences") },
                                onClick = {
                                    menuExpanded = false
                                    onNavigateToMemory()
                                },
                                leadingIcon = { Icon(Icons.Outlined.Psychology, contentDescription = null, tint = AgentCyan) }
                            )
                            DropdownMenuItem(
                                text = { Text("Activity Log") },
                                onClick = {
                                    menuExpanded = false
                                    onNavigateToActivity()
                                },
                                leadingIcon = { Icon(Icons.Outlined.History, contentDescription = null, tint = AgentCyan) }
                            )
                            DropdownMenuItem(
                                text = { Text("Interactive Sandbox (Rapido)") },
                                onClick = {
                                    menuExpanded = false
                                    onNavigateToMockApp()
                                },
                                leadingIcon = { Icon(Icons.Outlined.DirectionsCar, contentDescription = null, tint = AgentCyan) }
                            )
                            DropdownMenuItem(
                                text = { Text("Settings") },
                                onClick = {
                                    menuExpanded = false
                                    onNavigateToSettings()
                                },
                                leadingIcon = { Icon(Icons.Outlined.Settings, contentDescription = null, tint = AgentCyan) }
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        },
        bottomBar = {
            // Composer Box
            ComposerArea(
                text = inputText,
                onTextChange = { inputText = it },
                onSend = {
                    if (inputText.isNotBlank()) {
                        val toSend = inputText
                        inputText = ""
                        engine.handleUserMessage(toSend)
                    }
                },
                isExecuting = taskStatus == TaskStatus.EXECUTING,
                onStop = { engine.stopExecution() },
                onMicClick = launchVoiceInput
            )
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            if (messages.isEmpty()) {
                // Home Screen Empty State / AI Dashboard
                HomeEmptyState(
                    onSelectSuggestion = { suggestion ->
                        inputText = suggestion
                        engine.handleUserMessage(suggestion)
                    },
                    onVoiceClick = launchVoiceInput,
                    agentMode = agentMode
                )
            } else {
                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(messages, key = { it.id }) { message ->
                        MessageItem(
                            message = message,
                            onOptionClick = { option ->
                                engine.handleUserMessage(option)
                            },
                            onConfirmBooking = {
                                engine.confirmConsequentialAction(true)
                            },
                            onCancelBooking = {
                                engine.confirmConsequentialAction(false)
                            },
                            onStopClick = {
                                engine.stopExecution()
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun MessageItem(
    message: ChatMessage,
    onOptionClick: (String) -> Unit,
    onConfirmBooking: () -> Unit,
    onCancelBooking: () -> Unit,
    onStopClick: () -> Unit
) {
    if (message.isUser) {
        // User message bubble (Right aligned)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.End
        ) {
            Surface(
                shape = RoundedCornerShape(20.dp, 20.dp, 4.dp, 20.dp),
                color = MaterialTheme.colorScheme.primaryContainer,
                border = androidx.compose.foundation.BorderStroke(1.dp, AgentCyan.copy(alpha = 0.3f)),
                modifier = Modifier.widthIn(max = 290.dp)
            ) {
                Text(
                    text = message.text,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                    modifier = Modifier.padding(14.dp)
                )
            }
        }
    } else {
        // Agent message bubble (Left aligned)
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.Start
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                AgentCoreOrb(
                    size = 24.dp,
                    taskStatus = message.taskStatus,
                    isThinking = message.isExecutionActive
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "AgentZ",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                if (message.intentCategory != null) {
                    Spacer(modifier = Modifier.width(8.dp))
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = MaterialTheme.colorScheme.surfaceVariant
                    ) {
                        Text(
                            text = message.intentCategory,
                            fontSize = 9.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = MaterialTheme.colorScheme.outline,
                            modifier = Modifier.padding(horizontal = 5.dp, vertical = 1.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            Surface(
                shape = RoundedCornerShape(4.dp, 20.dp, 20.dp, 20.dp),
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.45f),
                border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    // Agent Reasoning Thought Chain
                    if (!message.thinkingProcess.isNullOrBlank()) {
                        AgentReasoningView(
                            thinkingText = message.thinkingProcess,
                            intentCategory = message.intentCategory,
                            latencyMs = message.latencyMs
                        )
                        Spacer(modifier = Modifier.height(10.dp))
                    }

                    // Main response text with rich markdown formatting
                    RichMarkdownText(
                        text = message.text,
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurface
                    )

                    // Suggested Reply Options (e.g. [ Auto ] [ Bike ] [ Cab ])
                    if (message.suggestedReplies.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(14.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            message.suggestedReplies.forEach { option ->
                                Surface(
                                    shape = RoundedCornerShape(20.dp),
                                    color = AgentCyan.copy(alpha = 0.12f),
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(20.dp))
                                        .clickable { onOptionClick(option) }
                                        .border(1.dp, AgentCyan.copy(alpha = 0.5f), RoundedCornerShape(20.dp))
                                ) {
                                    Text(
                                        text = option,
                                        style = MaterialTheme.typography.labelLarge,
                                        fontWeight = FontWeight.Bold,
                                        color = AgentCyan,
                                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                                    )
                                }
                            }
                        }
                    }

                    // Live Execution Pipeline Card
                    if (message.steps.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(14.dp))
                        ExecutionCard(
                            steps = message.steps,
                            taskStatus = message.taskStatus,
                            currentAction = message.currentActionDescription,
                            isExecutionActive = message.isExecutionActive,
                            onStopClick = onStopClick
                        )
                    }

                    // High-Risk Security Confirmation Card
                    if (message.confirmationCard != null) {
                        Spacer(modifier = Modifier.height(14.dp))
                        ConfirmationCardView(
                            details = message.confirmationCard,
                            onConfirm = onConfirmBooking,
                            onCancel = onCancelBooking
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ComposerArea(
    text: String,
    onTextChange: (String) -> Unit,
    onSend: () -> Unit,
    isExecuting: Boolean,
    onStop: () -> Unit,
    onMicClick: () -> Unit = {}
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .imePadding(),
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 6.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 10.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(28.dp))
                    .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.65f))
                    .border(1.dp, AgentCyan.copy(alpha = 0.25f), RoundedCornerShape(28.dp))
                    .padding(horizontal = 10.dp, vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = { /* File attachment feature */ }, modifier = Modifier.size(36.dp)) {
                    Icon(
                        imageVector = Icons.Default.AttachFile,
                        contentDescription = "Attachment",
                        tint = MaterialTheme.colorScheme.outline
                    )
                }

                OutlinedTextField(
                    value = text,
                    onValueChange = onTextChange,
                    placeholder = {
                        Text(
                            "Message AgentZ...",
                            style = MaterialTheme.typography.bodyLarge,
                            color = MaterialTheme.colorScheme.outline
                        )
                    },
                    modifier = Modifier.weight(1f),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = Color.Transparent,
                        unfocusedBorderColor = Color.Transparent,
                        focusedContainerColor = Color.Transparent,
                        unfocusedContainerColor = Color.Transparent
                    ),
                    maxLines = 4
                )

                if (text.isBlank() && !isExecuting) {
                    IconButton(
                        onClick = onMicClick,
                        modifier = Modifier.size(36.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Mic,
                            contentDescription = "Voice Input",
                            tint = AgentCyan
                        )
                    }
                } else if (isExecuting) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .background(NeonRose, CircleShape)
                            .clip(CircleShape)
                            .clickable { onStop() },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Stop,
                            contentDescription = "Stop",
                            tint = Color.White,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                } else {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .background(AgentCyan, CircleShape)
                            .clip(CircleShape)
                            .clickable { onSend() },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.ArrowUpward,
                            contentDescription = "Send",
                            tint = Color.Black,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun HomeEmptyState(
    onSelectSuggestion: (String) -> Unit,
    onVoiceClick: () -> Unit = {},
    agentMode: AgentMode = AgentMode.MOCK_MODE
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp, vertical = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Living AI Breathing Core
        AgentCoreOrb(size = 72.dp)

        Spacer(modifier = Modifier.height(14.dp))
        Text(
            text = "AgentZ",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Black,
            color = MaterialTheme.colorScheme.onSurface
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = "Autonomous AI Device Agent",
            style = MaterialTheme.typography.bodyMedium,
            color = AgentCyan,
            fontWeight = FontWeight.SemiBold
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = "“Tell me what you want done on your phone.”",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.outline
        )

        Spacer(modifier = Modifier.height(14.dp))

        // System Health / Capability Badges
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            StatusPill(label = "Accessibility", active = true)
            StatusPill(label = "Location", active = true)
            StatusPill(label = "Policy Engine", active = true)
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Quick Action Suggestions
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            SuggestionChipCard(
                title = "Voice Command",
                subtitle = "Tap to speak: 'Hey AgentZ, book me a Rapido' or any request",
                icon = Icons.Default.Mic,
                badge = "VOICE",
                onClick = onVoiceClick
            )
            SuggestionChipCard(
                title = "Book a Ride",
                subtitle = "Book me a Rapido from my current location to LPU",
                icon = Icons.Outlined.DirectionsCar,
                badge = "AUTOMATION",
                onClick = { onSelectSuggestion("Book me a Rapido from my current location to LPU.") }
            )
            SuggestionChipCard(
                title = "Send a Message",
                subtitle = "Send Rahul a message saying I'll reach in 20 minutes",
                icon = Icons.Outlined.Message,
                badge = "COMMUNICATION",
                onClick = { onSelectSuggestion("Send Rahul a message saying I'll reach in 20 minutes.") }
            )
            SuggestionChipCard(
                title = "Turn-by-turn Navigation",
                subtitle = "Navigate me to Vijayawada airport",
                icon = Icons.Default.Navigation,
                badge = "MAPS",
                onClick = { onSelectSuggestion("Navigate me to Vijayawada airport.") }
            )
            SuggestionChipCard(
                title = "Device Controls",
                subtitle = "Turn on Wi-Fi and open device settings",
                icon = Icons.Default.PhoneAndroid,
                badge = "DEVICE",
                onClick = { onSelectSuggestion("Turn on Wi-Fi.") }
            )
        }
    }
}

@Composable
private fun StatusPill(label: String, active: Boolean) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f))
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(5.dp)
                    .background(if (active) NeonGreen else NeonRose, CircleShape)
            )
            Spacer(modifier = Modifier.width(5.dp))
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                fontSize = 9.5.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun SuggestionChipCard(
    title: String,
    subtitle: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    badge: String,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .clickable { onClick() }
            .border(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f), RoundedCornerShape(14.dp)),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.35f)
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .background(AgentCyan.copy(alpha = 0.12f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(icon, contentDescription = null, tint = AgentCyan, modifier = Modifier.size(20.dp))
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = AgentCyan.copy(alpha = 0.12f)
                    ) {
                        Text(
                            text = badge,
                            fontSize = 8.5.sp,
                            fontWeight = FontWeight.Bold,
                            color = AgentCyan,
                            modifier = Modifier.padding(horizontal = 4.dp, vertical = 1.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    lineHeight = 16.sp
                )
            }
        }
    }
}
