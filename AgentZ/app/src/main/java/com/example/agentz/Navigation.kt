package com.example.agentz

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.ui.NavDisplay
import com.example.agentz.agent.engine.AgentEngine
import com.example.agentz.data.local.AgentRepository
import com.example.agentz.ui.activity.ActivityLogScreen
import com.example.agentz.ui.chat.ChatScreen
import com.example.agentz.ui.memory.MemoryScreen
import com.example.agentz.ui.mock_app.MockRapidoScreen
import com.example.agentz.ui.permissions.PermissionsScreen
import com.example.agentz.ui.settings.SettingsScreen

@Composable
fun MainNavigation() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val repository = remember { AgentRepository(context) }
    val engine = remember { AgentEngine(context, repository, scope) }

    val backStack = rememberNavBackStack(ChatScreenKey)

    NavDisplay(
        backStack = backStack,
        onBack = { backStack.removeLastOrNull() },
        entryProvider = entryProvider {
            entry<ChatScreenKey> {
                ChatScreen(
                    repository = repository,
                    engine = engine,
                    onNavigateToSettings = { backStack.add(SettingsScreenKey) },
                    onNavigateToPermissions = { backStack.add(PermissionsScreenKey) },
                    onNavigateToMemory = { backStack.add(MemoryScreenKey) },
                    onNavigateToActivity = { backStack.add(ActivityLogScreenKey) },
                    onNavigateToMockApp = { backStack.add(MockAppScreenKey) },
                    modifier = Modifier.fillMaxSize()
                )
            }
            entry<SettingsScreenKey> {
                SettingsScreen(
                    repository = repository,
                    onBack = { backStack.removeLastOrNull() },
                    onNavigateToPermissions = { backStack.add(PermissionsScreenKey) },
                    onNavigateToMemory = { backStack.add(MemoryScreenKey) },
                    onNavigateToActivity = { backStack.add(ActivityLogScreenKey) },
                    onNavigateToMockApp = { backStack.add(MockAppScreenKey) },
                    modifier = Modifier.fillMaxSize()
                )
            }
            entry<PermissionsScreenKey> {
                PermissionsScreen(
                    onBack = { backStack.removeLastOrNull() },
                    modifier = Modifier.fillMaxSize()
                )
            }
            entry<MemoryScreenKey> {
                MemoryScreen(
                    repository = repository,
                    onBack = { backStack.removeLastOrNull() },
                    modifier = Modifier.fillMaxSize()
                )
            }
            entry<ActivityLogScreenKey> {
                ActivityLogScreen(
                    repository = repository,
                    onBack = { backStack.removeLastOrNull() },
                    modifier = Modifier.fillMaxSize()
                )
            }
            entry<MockAppScreenKey> {
                MockRapidoScreen(
                    onBack = { backStack.removeLastOrNull() },
                    modifier = Modifier.fillMaxSize()
                )
            }
        }
    )
}
