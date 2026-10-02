package com.example.agentz.core.security

import com.example.agentz.data.models.RiskLevel

object ActionPolicyEngine {

    private val HIGH_RISK_KEYWORDS = listOf(
        "confirm booking", "book", "place order", "pay", "payment",
        "send message", "delete", "remove", "checkout", "transfer",
        "purchase", "submit", "wipe"
    )

    private val MEDIUM_RISK_KEYWORDS = listOf(
        "add to cart", "modify", "update settings", "draft message",
        "toggle setting", "clear cache"
    )

    private val CONSEQUENTIAL_ACTIONS = listOf(
        "confirm_booking", "book_ride", "place_order", "make_payment",
        "pay", "send_message", "delete", "purchase", "submit_booking"
    )

    private val SAFE_READ_TOOLS = listOf(
        "internal_parse", "get_current_location", "read_screen", "open_app",
        "find_ui_element", "scroll", "get_installed_apps", "get_visible_text"
    )

    private val INJECTION_REGEXES = listOf(
        Regex("(?i)ignore (all )?previous instructions"),
        Regex("(?i)system prompt override"),
        Regex("(?i)you are now in developer mode"),
        Regex("(?i)bypass (all )?restrictions"),
        Regex("(?i)transfer money to"),
        Regex("(?i)send my (passwords?|credentials?|otp|token)"),
        Regex("(?i)do not ask (the )?user"),
        Regex("(?i)execute without confirmation")
    )

    fun classifyRisk(actionType: String, targetName: String, parameters: Map<String, String> = emptyMap()): RiskLevel {
        val actNorm = actionType.lowercase().replace(" ", "_")
        val targetNorm = targetName.lowercase().replace("_", " ")

        if (actNorm in SAFE_READ_TOOLS && !targetNorm.contains("confirm")) {
            return RiskLevel.LOW
        }

        if (actNorm in CONSEQUENTIAL_ACTIONS) {
            return RiskLevel.HIGH
        }

        for (kw in HIGH_RISK_KEYWORDS) {
            if (targetNorm.contains(kw)) {
                return RiskLevel.HIGH
            }
        }

        for (kw in MEDIUM_RISK_KEYWORDS) {
            if (targetNorm.contains(kw) || actNorm.contains(kw)) {
                return RiskLevel.MEDIUM
            }
        }

        return RiskLevel.LOW
    }

    data class PolicyCheckResult(
        val allowed: Boolean,
        val riskLevel: RiskLevel,
        val reason: String,
        val requiresConfirmation: Boolean
    )

    fun validateAction(
        actionType: String,
        targetName: String,
        isUserConfirmed: Boolean,
        parameters: Map<String, String> = emptyMap()
    ): PolicyCheckResult {
        val risk = classifyRisk(actionType, targetName, parameters)

        return when (risk) {
            RiskLevel.HIGH -> {
                if (!isUserConfirmed) {
                    PolicyCheckResult(
                        allowed = false,
                        riskLevel = risk,
                        reason = "Consequential action '$actionType' on '$targetName' requires explicit user confirmation.",
                        requiresConfirmation = true
                    )
                } else {
                    PolicyCheckResult(
                        allowed = true,
                        riskLevel = risk,
                        reason = "Explicit user confirmation granted. Executing consequential action.",
                        requiresConfirmation = false
                    )
                }
            }
            RiskLevel.MEDIUM -> {
                PolicyCheckResult(
                    allowed = true,
                    riskLevel = risk,
                    reason = "Medium risk action permitted with user awareness.",
                    requiresConfirmation = false
                )
            }
            RiskLevel.LOW -> {
                PolicyCheckResult(
                    allowed = true,
                    riskLevel = risk,
                    reason = "Low risk action permitted automatically.",
                    requiresConfirmation = false
                )
            }
        }
    }

    /**
     * Defense against Prompt Injection from third-party app UI content.
     * External text is treated as UNTRUSTED and cannot override policy rules.
     */
    fun sanitizeExternalAppText(observedText: String): Pair<String, Boolean> {
        var sanitized = observedText
        var injectionDetected = false

        for (regex in INJECTION_REGEXES) {
            if (regex.containsMatchIn(sanitized)) {
                injectionDetected = true
                sanitized = regex.replace(sanitized, "[UNTRUSTED_EXTERNAL_OVERRIDE_STRIPPED]")
            }
        }

        return Pair(sanitized, injectionDetected)
    }
}
