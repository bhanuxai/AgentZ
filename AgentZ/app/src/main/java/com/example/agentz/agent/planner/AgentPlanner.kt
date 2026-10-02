package com.example.agentz.agent.planner

import com.example.agentz.data.models.ConfirmationDetails
import com.example.agentz.data.models.ExecutionStep
import com.example.agentz.data.models.RiskLevel
import com.example.agentz.data.models.StepStatus
import java.util.UUID

data class PlanResult(
    val intent: String,
    val entities: MutableMap<String, String>,
    val missingParameters: List<String>,
    val questionToUser: String? = null,
    val suggestedOptions: List<String> = emptyList(),
    val steps: List<ExecutionStep> = emptyList(),
    val confirmationCard: ConfirmationDetails? = null,
    val responseText: String,
    val thinkingProcess: String? = null,
    val intentCategory: String? = null,
    val latencyMs: Long = 180
)

class AgentPlanner {

    private val ongoingEntities = mutableMapOf<String, String>()
    private var currentIntent: String = ""

    fun reset() {
        ongoingEntities.clear()
        currentIntent = ""
    }

    fun plan(userMessage: String, memories: Map<String, String> = emptyMap()): PlanResult {
        val startTime = System.currentTimeMillis()

        if (currentIntent == "AGENT_CALL") {
            currentIntent = ""
        }

        // Wake word & calling AgentZ pattern
        val wakeRegex = Regex("^(?:(?:hey|hi|hello|ok|okay)?\\s*(?:call\\s+)?agent\\s*z[,:\\s]*)+", RegexOption.IGNORE_CASE)
        val isWakeCall = wakeRegex.containsMatchIn(userMessage)
        val cleanMessage = if (isWakeCall) {
            userMessage.replace(wakeRegex, "").trim()
        } else {
            userMessage.trim()
        }

        val lower = cleanMessage.lowercase()

        // Pure wake call without command
        if (isWakeCall && (lower.isEmpty() || lower in listOf("hey", "hello", "hi", "yo", "yes", "there", "are you there", "listen"))) {
            currentIntent = "AGENT_CALL"
            return PlanResult(
                intent = "AGENT_CALL",
                entities = mutableMapOf("called_by_voice" to "true"),
                missingParameters = listOf("command"),
                questionToUser = "I'm listening! What would you like me to do on your phone?",
                suggestedOptions = listOf(
                    "Book me a Rapido from my current location to LPU.",
                    "Send Rahul a message saying I'll reach in 20 minutes.",
                    "Turn on Wi-Fi."
                ),
                responseText = "Hello! I'm **AgentZ**, your autonomous on-device agent. I'm listening—tell me what you need done.",
                thinkingProcess = "• Trigger: Wake word detected [Hey AgentZ]\n• Mode: Interactive Voice Standby\n• State: Ready for device instructions",
                intentCategory = "Voice Activation",
                latencyMs = 65
            )
        }

        val effectiveMessage = if (cleanMessage.isNotEmpty()) cleanMessage else userMessage

        // 1. Detect Intent
        if (currentIntent.isEmpty()) {
            currentIntent = when {
                lower.contains("rapido") || lower.contains("ride") || lower.contains("auto") ||
                lower.contains("cab") || lower.contains("bike") || lower.contains("uber") || lower.contains("ola") -> "BOOK_RIDE"
                lower.contains("message") || lower.contains("send") || lower.contains("whatsapp") -> "SEND_MESSAGE"
                lower.contains("navigate") || lower.contains("directions") || lower.contains("maps") -> "NAVIGATE"
                lower.contains("wifi") || lower.contains("bluetooth") || lower.contains("turn on") -> "DEVICE_ACTION"
                lower.startsWith("open ") || lower.startsWith("launch ") || lower.startsWith("start ") ||
                lower.contains("open ") || lower.contains("launch ") -> "OPEN_APP"
                else -> "GENERAL_QUERY"
            }
        }

        return when (currentIntent) {
            "BOOK_RIDE" -> planRideBooking(effectiveMessage, memories)
            "SEND_MESSAGE" -> planSendMessage(effectiveMessage)
            "NAVIGATE" -> planNavigation(effectiveMessage)
            "OPEN_APP" -> planOpenApp(effectiveMessage)
            else -> planGeneralQuery(effectiveMessage)
        }
    }

    private fun planRideBooking(message: String, memories: Map<String, String>): PlanResult {
        val lower = message.lowercase()

        // Extract Pickup
        if (!ongoingEntities.containsKey("pickup")) {
            if (lower.contains("from here") || lower.contains("current location")) {
                ongoingEntities["pickup"] = "Current location"
            } else if (lower.contains("from")) {
                val match = Regex("from\\s+([A-Za-z0-9\\s]+?)\\s+to", RegexOption.IGNORE_CASE).find(message)
                ongoingEntities["pickup"] = match?.groupValues?.get(1)?.trim() ?: "Current location"
            } else {
                ongoingEntities["pickup"] = "Current location"
            }
        }

        // Extract Destination
        if (!ongoingEntities.containsKey("destination")) {
            if (lower.contains("to lpu") || lower.contains("lpu")) {
                ongoingEntities["destination"] = "Lovely Professional University (LPU)"
            } else if (lower.contains("to airport") || lower.contains("airport")) {
                ongoingEntities["destination"] = "Airport"
            } else if (lower.contains("to")) {
                val match = Regex("to\\s+([A-Za-z0-9\\s]+)", RegexOption.IGNORE_CASE).find(message)
                ongoingEntities["destination"] = match?.groupValues?.get(1)?.trim() ?: "LPU"
            }
        }

        // Extract Vehicle
        if (!ongoingEntities.containsKey("vehicle")) {
            when {
                lower.contains("auto") -> ongoingEntities["vehicle"] = "Auto"
                lower.contains("bike") -> ongoingEntities["vehicle"] = "Bike"
                lower.contains("cab") || lower.contains("car") -> ongoingEntities["vehicle"] = "Cab"
                memories.containsKey("Preferred ride") -> ongoingEntities["vehicle"] = memories["Preferred ride"]!!
            }
        }

        // Extract Payment
        if (!ongoingEntities.containsKey("payment")) {
            when {
                lower.contains("cash") -> ongoingEntities["payment"] = "Cash"
                lower.contains("upi") || lower.contains("gpay") || lower.contains("phonepe") -> ongoingEntities["payment"] = "UPI"
                memories.containsKey("Preferred payment") -> ongoingEntities["payment"] = memories["Preferred payment"]!!
            }
        }

        // Check missing parameters
        val missing = mutableListOf<String>()
        if (!ongoingEntities.containsKey("vehicle")) missing.add("vehicle")
        if (!ongoingEntities.containsKey("payment")) missing.add("payment")

        // Multi-turn questioning
        if ("vehicle" in missing) {
            return PlanResult(
                intent = "BOOK_RIDE",
                entities = ongoingEntities,
                missingParameters = missing,
                questionToUser = "I can do that. I’ll use your current location as the pickup point.\n\nWhich ride do you want?",
                suggestedOptions = listOf("Auto", "Bike", "Cab"),
                responseText = "I can do that. I’ll use your current location as the pickup point.\n\nWhich ride do you want?",
                thinkingProcess = "• Intent: BOOK_RIDE (confidence: 0.98)\n• Destination: ${ongoingEntities["destination"] ?: "LPU"}\n• Pickup: ${ongoingEntities["pickup"] ?: "Current location"}\n• Missing: Vehicle type (Auto/Bike/Cab)\n• Action: Soliciting user clarification",
                intentCategory = "Ride Automation",
                latencyMs = 120
            )
        }

        if ("payment" in missing) {
            val v = ongoingEntities["vehicle"] ?: "Auto"
            return PlanResult(
                intent = "BOOK_RIDE",
                entities = ongoingEntities,
                missingParameters = missing,
                questionToUser = "Got it. I’ll look for an $v.\n\nI also need your preferred payment method:",
                suggestedOptions = listOf("Cash", "UPI"),
                responseText = "Got it. I’ll look for an $v.\n\nI also need your preferred payment method:",
                thinkingProcess = "• Intent: BOOK_RIDE\n• Vehicle Selected: $v\n• Missing: Payment method\n• Action: Requesting payment selection before generating automation pipeline",
                intentCategory = "Ride Automation",
                latencyMs = 95
            )
        }

        // All required info gathered! Generate step sequence
        val vehicle = ongoingEntities["vehicle"] ?: "Auto"
        val dest = ongoingEntities["destination"] ?: "LPU"
        val pickup = ongoingEntities["pickup"] ?: "Current location"
        val payment = ongoingEntities["payment"] ?: "Cash"

        val fare = when (vehicle.lowercase()) {
            "auto" -> "₹183"
            "bike" -> "₹95"
            else -> "₹320"
        }

        val steps = listOf(
            ExecutionStep(
                title = "Understanding request",
                description = "Parsed user intent: Book $vehicle ride to $dest",
                tool = "internal_parse",
                status = StepStatus.PENDING,
                riskLevel = RiskLevel.LOW
            ),
            ExecutionStep(
                title = "Current location obtained",
                description = "Acquired device GPS position for pickup: $pickup",
                tool = "get_current_location",
                status = StepStatus.PENDING,
                riskLevel = RiskLevel.LOW
            ),
            ExecutionStep(
                title = "Opening Rapido",
                description = "Launching com.rapido.passenger",
                tool = "open_app",
                toolArgs = mapOf("package" to "com.rapido.passenger"),
                status = StepStatus.PENDING,
                riskLevel = RiskLevel.LOW
            ),
            ExecutionStep(
                title = "Entering pickup location",
                description = "Setting pickup point: $pickup",
                tool = "type_text",
                toolArgs = mapOf("field" to "pickup", "value" to pickup),
                status = StepStatus.PENDING,
                riskLevel = RiskLevel.LOW
            ),
            ExecutionStep(
                title = "Entering destination",
                description = "Setting destination: $dest",
                tool = "type_text",
                toolArgs = mapOf("field" to "destination", "value" to dest),
                status = StepStatus.PENDING,
                riskLevel = RiskLevel.LOW
            ),
            ExecutionStep(
                title = "Selecting $vehicle",
                description = "Selecting category '$vehicle' from available rides",
                tool = "click_ui_element",
                toolArgs = mapOf("target" to vehicle),
                status = StepStatus.PENDING,
                riskLevel = RiskLevel.LOW
            ),
            ExecutionStep(
                title = "Checking fare",
                description = "Reading route quote ($fare) and estimated travel time",
                tool = "read_screen",
                status = StepStatus.PENDING,
                riskLevel = RiskLevel.LOW
            ),
            ExecutionStep(
                title = "Confirming booking",
                description = "Consequential transaction: finalize ride request on Rapido",
                tool = "confirm_booking",
                toolArgs = mapOf("provider" to "Rapido", "vehicle" to vehicle, "payment" to payment),
                status = StepStatus.PENDING,
                riskLevel = RiskLevel.HIGH
            )
        )

        val confirmationCard = ConfirmationDetails(
            title = "Confirm booking",
            provider = "Rapido",
            vehicle = vehicle,
            pickup = pickup,
            destination = dest,
            fare = fare,
            paymentMethod = payment,
            riskLevel = RiskLevel.HIGH,
            message = "Your Rapido $vehicle is ready to book."
        )

        val thinking = buildString {
            append("• Intent: BOOK_RIDE (confidence: 0.99)\n")
            append("• Parameters: Vehicle=$vehicle | Destination=$dest | Payment=$payment\n")
            if (memories.isNotEmpty()) {
                append("• Memory Context: Injected ${memories.size} saved user preference(s)\n")
            }
            append("• Policy Engine: 7 Low-Risk preparation steps, 1 High-Risk Consequential Step\n")
            append("• Safety Protocol: Execution will gate before 'confirm_booking'")
        }

        return PlanResult(
            intent = "BOOK_RIDE",
            entities = ongoingEntities,
            missingParameters = emptyList(),
            steps = steps,
            confirmationCard = confirmationCard,
            responseText = "I've planned the ride details. Starting execution...",
            thinkingProcess = thinking,
            intentCategory = "Ride Automation",
            latencyMs = 210
        )
    }

    private fun planSendMessage(message: String): PlanResult {
        val destMatch = Regex("to\\s+([A-Za-z0-9]+)", RegexOption.IGNORE_CASE).find(message)
        val recipient = destMatch?.groupValues?.get(1) ?: "Rahul"
        val msgMatch = Regex("saying\\s+(.+)$", RegexOption.IGNORE_CASE).find(message)
        val content = msgMatch?.groupValues?.get(1) ?: "I'll reach in 20 minutes"

        val steps = listOf(
            ExecutionStep(title = "Locating contact", description = "Searching for $recipient in contacts", tool = "search_contacts", riskLevel = RiskLevel.LOW),
            ExecutionStep(title = "Opening WhatsApp", description = "Launching com.whatsapp", tool = "open_app", riskLevel = RiskLevel.LOW),
            ExecutionStep(title = "Drafting message", description = "Typing \"$content\"", tool = "type_text", riskLevel = RiskLevel.MEDIUM),
            ExecutionStep(title = "Sending message", description = "Consequential action: dispatch message to $recipient", tool = "send_message", riskLevel = RiskLevel.HIGH)
        )

        val confirmationCard = ConfirmationDetails(
            title = "Confirm Send Message",
            provider = "WhatsApp",
            vehicle = "Message",
            pickup = "To: $recipient",
            destination = content,
            fare = "Free",
            paymentMethod = "N/A",
            message = "Confirm sending message to $recipient?"
        )

        return PlanResult(
            intent = "SEND_MESSAGE",
            entities = mutableMapOf("recipient" to recipient, "content" to content),
            missingParameters = emptyList(),
            steps = steps,
            confirmationCard = confirmationCard,
            responseText = "I've drafted your message. Please review and confirm before I send it.",
            thinkingProcess = "• Intent: SEND_MESSAGE\n• Target App: WhatsApp (com.whatsapp)\n• Recipient: $recipient\n• Content: \"$content\"\n• Policy Gate: High-Risk consequential messaging gate enabled",
            intentCategory = "Smart Messaging",
            latencyMs = 150
        )
    }

    private fun planNavigation(message: String): PlanResult {
        val destMatch = Regex("to\\s+([A-Za-z0-9\\s]+)", RegexOption.IGNORE_CASE).find(message)
        val dest = destMatch?.groupValues?.get(1)?.trim() ?: "Vijayawada Airport"

        val steps = listOf(
            ExecutionStep(title = "Acquiring GPS location", description = "Resolving current position", tool = "get_current_location", riskLevel = RiskLevel.LOW),
            ExecutionStep(title = "Opening Google Maps", description = "Launching com.google.android.apps.maps", tool = "open_app", riskLevel = RiskLevel.LOW),
            ExecutionStep(title = "Setting destination", description = "Setting destination to $dest", tool = "type_text", riskLevel = RiskLevel.LOW),
            ExecutionStep(title = "Starting turn-by-turn navigation", description = "Calculating quickest route", tool = "click_ui_element", riskLevel = RiskLevel.LOW)
        )

        return PlanResult(
            intent = "NAVIGATE",
            entities = mutableMapOf("destination" to dest),
            missingParameters = emptyList(),
            steps = steps,
            responseText = "Navigating you to **$dest** via Google Maps.",
            thinkingProcess = "• Intent: NAVIGATE\n• Target Location: $dest\n• Provider: Google Maps (com.google.android.apps.maps)\n• Risk Assessment: LOW (safe routing action)",
            intentCategory = "Navigation",
            latencyMs = 130
        )
    }

    private fun planOpenApp(message: String): PlanResult {
        val appMatch = Regex("(?:open|launch|start)\\s+(?:up\\s+)?(?:the\\s+)?([A-Za-z0-9\\s_\\-\\.]+)", RegexOption.IGNORE_CASE).find(message)
        val appName = appMatch?.groupValues?.get(1)?.trim() ?: "app"
        val cleanName = appName.replace(Regex("\\b(app|application|program)\\b", RegexOption.IGNORE_CASE), "").trim()
        val pkg = when (cleanName.lowercase()) {
            "rapido" -> "com.rapido.passenger"
            "uber" -> "com.ubercab"
            "ola" -> "com.olacabs"
            "whatsapp" -> "com.whatsapp"
            "youtube" -> "com.google.android.youtube"
            "maps", "google maps" -> "com.google.android.apps.maps"
            "chrome" -> "com.android.chrome"
            "settings" -> "com.android.settings"
            "camera" -> "com.android.camera"
            else -> "com.android.$cleanName"
        }

        val steps = listOf(
            ExecutionStep(
                title = "Locating $cleanName",
                description = "Resolving package identifier $pkg",
                tool = "resolve_package",
                riskLevel = RiskLevel.LOW
            ),
            ExecutionStep(
                title = "Launching $cleanName",
                description = "Opening $pkg on your device",
                tool = "open_app",
                riskLevel = RiskLevel.LOW
            )
        )

        return PlanResult(
            intent = "OPEN_APP",
            entities = mutableMapOf("app_name" to cleanName, "package_name" to pkg),
            missingParameters = emptyList(),
            steps = steps,
            responseText = "Opening **$cleanName** on your device.",
            thinkingProcess = "• Intent: OPEN_APP\n• Target: $cleanName ($pkg)\n• Method: AccessibilityService / AppRegistry launch\n• Risk: LOW",
            intentCategory = "App Launcher",
            latencyMs = 110
        )
    }

    private fun planGeneralQuery(message: String): PlanResult {
        return PlanResult(
            intent = "GENERAL_QUERY",
            entities = mutableMapOf(),
            missingParameters = emptyList(),
            responseText = "I received: \"$message\". AgentZ executes instructions directly on your device. You can say:\n• **Open <app>** (e.g. *Open YouTube*)\n• **Book me a Rapido** from my current location to LPU\n• **Send Rahul a message** saying I'll reach in 20 minutes\n• **Navigate me** to Vijayawada airport",
            thinkingProcess = "• Intent: GENERAL_QUERY\n• Evaluation: No direct device automation match\n• Strategy: Displaying contextual voice/action shortcuts",
            intentCategory = "General Query",
            latencyMs = 85
        )
    }
}
