package com.example.agentz.ui.main

import androidx.activity.ComponentActivity
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import com.example.agentz.agent.engine.AgentEngine
import com.example.agentz.data.local.AgentRepository
import com.example.agentz.theme.AgentZTheme
import com.example.agentz.ui.chat.ChatScreen
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import org.junit.Before
import org.junit.Rule
import org.junit.Test

/** UI tests for [com.example.agentz.ui.chat.ChatScreen]. */
class MainScreenTest {

  @get:Rule val composeTestRule = createAndroidComposeRule<ComponentActivity>()

  @Before
  fun setup() {
    composeTestRule.setContent {
      AgentZTheme {
        val repo = AgentRepository(composeTestRule.activity)
        val engine = AgentEngine(composeTestRule.activity, repo, CoroutineScope(Dispatchers.Main))
        ChatScreen(
          repository = repo,
          engine = engine,
          onNavigateToSettings = {},
          onNavigateToPermissions = {},
          onNavigateToMemory = {},
          onNavigateToActivity = {},
          onNavigateToMockApp = {}
        )
      }
    }
  }

  @Test
  fun agentZ_title_exists() {
    composeTestRule.onNodeWithText("AgentZ").assertExists()
  }
}
