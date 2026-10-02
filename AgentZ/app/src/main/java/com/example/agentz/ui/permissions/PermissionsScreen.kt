package com.example.agentz.ui.permissions

import android.content.Context
import android.content.Intent
import android.provider.Settings
import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material.icons.outlined.Security
import androidx.compose.material.icons.outlined.Visibility
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.agentz.android.accessibility.AgentAccessibilityService
import com.example.agentz.android.location.AgentLocationProvider
import com.example.agentz.theme.AgentCyan
import com.example.agentz.theme.NeonAmber
import com.example.agentz.theme.NeonGreen
import com.example.agentz.theme.NeonRose

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PermissionsScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val locationProvider = AgentLocationProvider(context)
    val hasLocation = locationProvider.hasLocationPermission()
    val hasAccessibility = AgentAccessibilityService.isServiceEnabled()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Permissions & Security Center", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.surface)
            )
        }
    ) { innerPadding ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Guardrail Guarantee Banner
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.45f),
                border = androidx.compose.foundation.BorderStroke(1.dp, AgentCyan.copy(alpha = 0.3f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .background(AgentCyan.copy(alpha = 0.12f), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.Shield, contentDescription = null, tint = AgentCyan, modifier = Modifier.size(24.dp))
                    }
                    Spacer(modifier = Modifier.width(14.dp))
                    Column {
                        Text(
                            text = "Zero-Surveillance Architecture",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = "AgentZ never records background audio, uploads personal screen captures to the cloud, or accesses banking credentials without explicit confirmation.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            lineHeight = 16.sp
                        )
                    }
                }
            }

            Text(
                text = "SYSTEM PERMISSIONS & DRIVERS",
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
                color = AgentCyan,
                letterSpacing = 0.8.sp
            )

            // Accessibility Service Card
            PermissionItemCard(
                title = "Accessibility Automation Service",
                enabled = hasAccessibility,
                icon = Icons.Outlined.Visibility,
                badge = "CORE DRIVER",
                whyNeeded = "Required to inspect UI nodes, click buttons, and enter text on third-party apps like Rapido on your command.",
                whatAgentCanDo = "• Reads visible form fields to enter pickup/drop\n• Clicks ride selection & category buttons\n• Enforces ActionPolicyEngine confirmation on financial actions",
                onConfigure = {
                    val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                    context.startActivity(intent)
                }
            )

            // Location Permission Card
            PermissionItemCard(
                title = "Device GPS Location",
                enabled = hasLocation,
                icon = Icons.Outlined.LocationOn,
                badge = "NAVIGATION",
                whyNeeded = "Identifies your current location to automatically set pickup points and calculate ride routes.",
                whatAgentCanDo = "• Reads device coordinates when you request a ride\n• Reverse-geocodes to landmark addresses (e.g. LPU gate)\n• Never tracks background location when app is closed",
                onConfigure = {
                    val intent = Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS)
                    context.startActivity(intent)
                }
            )

            // Microphone Permission Card
            PermissionItemCard(
                title = "Microphone & Speech",
                enabled = true,
                icon = Icons.Outlined.Mic,
                badge = "VOICE INPUT",
                whyNeeded = "Transcribes voice instructions when you tap the microphone button or use 'Hey AgentZ'.",
                whatAgentCanDo = "• Transcribes audio on-device when microphone is triggered\n• Zero background listening or passive surveillance",
                onConfigure = {
                    val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                    intent.data = android.net.Uri.parse("package:${context.packageName}")
                    context.startActivity(intent)
                }
            )

            // Notifications Card
            PermissionItemCard(
                title = "System Notifications",
                enabled = true,
                icon = Icons.Outlined.Notifications,
                badge = "ALERTS",
                whyNeeded = "Alerts you when an automated task completes or when an ongoing ride status changes.",
                whatAgentCanDo = "• Posts high-priority task completion notifications\n• Delivers ride arrival & confirmation alerts",
                onConfigure = {
                    val intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                    intent.putExtra(Settings.EXTRA_APP_PACKAGE, context.packageName)
                    context.startActivity(intent)
                }
            )

            Spacer(modifier = Modifier.height(10.dp))

            // Safety Policy Matrix
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.35f),
                border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "SECURITY CAPABILITY BOUNDARIES",
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Bold,
                        color = AgentCyan
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    SecurityMatrixRow(allowed = true, label = "Read on-screen UI buttons for authorized app control")
                    SecurityMatrixRow(allowed = true, label = "Fill pickup & destination addresses automatically")
                    SecurityMatrixRow(allowed = true, label = "Check fare prices before booking")
                    SecurityMatrixRow(allowed = false, label = "Autonomously pay or transfer money without confirmation")
                    SecurityMatrixRow(allowed = false, label = "Store banking passwords, PINs, or financial OTPs")
                    SecurityMatrixRow(allowed = false, label = "Transmit screen recordings to third-party ad networks")
                }
            }
        }
    }
}

@Composable
private fun SecurityMatrixRow(allowed: Boolean, label: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = if (allowed) Icons.Default.Check else Icons.Default.Close,
            contentDescription = null,
            tint = if (allowed) NeonGreen else NeonRose,
            modifier = Modifier.size(16.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = if (allowed) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun PermissionItemCard(
    title: String,
    enabled: Boolean,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    badge: String,
    whyNeeded: String,
    whatAgentCanDo: String,
    onConfigure: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        border = androidx.compose.foundation.BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .background(AgentCyan.copy(alpha = 0.12f), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(icon, contentDescription = null, tint = AgentCyan, modifier = Modifier.size(20.dp))
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = AgentCyan.copy(alpha = 0.1f)
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
                }

                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = if (enabled) NeonGreen.copy(alpha = 0.15f) else NeonRose.copy(alpha = 0.15f)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .background(if (enabled) NeonGreen else NeonRose, CircleShape)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = if (enabled) "ACTIVE" else "DISABLED",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = if (enabled) NeonGreen else NeonRose
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "Purpose:",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.outline,
                fontWeight = FontWeight.Bold
            )
            Text(whyNeeded, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)

            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Autonomous Capabilities:",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.outline,
                fontWeight = FontWeight.Bold
            )
            Text(whatAgentCanDo, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, lineHeight = 18.sp)

            Spacer(modifier = Modifier.height(14.dp))
            OutlinedButton(
                onClick = onConfigure,
                shape = RoundedCornerShape(10.dp),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = AgentCyan),
                border = androidx.compose.foundation.BorderStroke(1.dp, AgentCyan.copy(alpha = 0.5f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(if (enabled) "Configure System Permission" else "Enable Permission in Settings", fontWeight = FontWeight.SemiBold)
            }
        }
    }
}
