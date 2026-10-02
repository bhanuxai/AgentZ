package com.example.agentz.android.accessibility

import android.accessibilityservice.AccessibilityService
import android.os.Bundle
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class AgentAccessibilityService : AccessibilityService() {

    companion object {
        private const val TAG = "AgentAccessibility"
        var instance: AgentAccessibilityService? = null
            private set

        fun isServiceEnabled(): Boolean = instance != null
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        Log.i(TAG, "AgentAccessibilityService connected and ready")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Track window changes and UI updates
        event?.let {
            if (it.eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED ||
                it.eventType == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED
            ) {
                // Log or notify UI state changes if needed
            }
        }
    }

    override fun onInterrupt() {
        Log.w(TAG, "AgentAccessibilityService interrupted")
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        Log.i(TAG, "AgentAccessibilityService destroyed")
    }

    /**
     * Finds node semantically by text, case-insensitively.
     */
    fun findNodeByText(text: String): AccessibilityNodeInfo? {
        val root = rootInActiveWindow ?: return null
        val matchedNodes = root.findAccessibilityNodeInfosByText(text)
        if (matchedNodes.isNotEmpty()) {
            return matchedNodes[0]
        }
        return searchTreeRecursively(root) { node ->
            val nodeText = node.text?.toString() ?: ""
            val desc = node.contentDescription?.toString() ?: ""
            nodeText.contains(text, ignoreCase = true) || desc.contains(text, ignoreCase = true)
        }
    }

    /**
     * Finds node by view ID resource name.
     */
    fun findNodeByViewId(viewId: String): AccessibilityNodeInfo? {
        val root = rootInActiveWindow ?: return null
        val matchedNodes = root.findAccessibilityNodeInfosByViewId(viewId)
        return matchedNodes.firstOrNull()
    }

    /**
     * Performs click on an accessibility node or its closest clickable parent.
     */
    fun clickNode(node: AccessibilityNodeInfo): Boolean {
        var current: AccessibilityNodeInfo? = node
        while (current != null) {
            if (current.isClickable) {
                return current.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            }
            current = current.parent
        }
        // Fallback: direct click
        return node.performAction(AccessibilityNodeInfo.ACTION_CLICK)
    }

    /**
     * Enters text into an editable input field node.
     */
    fun setTextOnNode(node: AccessibilityNodeInfo, text: String): Boolean {
        val arguments = Bundle()
        arguments.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
        return node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
    }

    /**
     * Performs scroll forward or backward.
     */
    fun scrollNode(node: AccessibilityNodeInfo, forward: Boolean = true): Boolean {
        val action = if (forward) AccessibilityNodeInfo.ACTION_SCROLL_FORWARD else AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD
        return node.performAction(action)
    }

    /**
     * Extracts all visible text from current screen for observation & verification.
     */
    fun getVisibleScreenText(): List<String> {
        val root = rootInActiveWindow ?: return emptyList()
        val textList = mutableListOf<String>()
        collectTextRecursively(root, textList)
        return textList
    }

    private fun collectTextRecursively(node: AccessibilityNodeInfo, list: MutableList<String>) {
        node.text?.toString()?.takeIf { it.isNotBlank() }?.let { list.add(it) }
        node.contentDescription?.toString()?.takeIf { it.isNotBlank() }?.let { list.add(it) }
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { collectTextRecursively(it, list) }
        }
    }

    private fun searchTreeRecursively(
        node: AccessibilityNodeInfo,
        predicate: (AccessibilityNodeInfo) -> Boolean
    ): AccessibilityNodeInfo? {
        if (predicate(node)) return node
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            val found = searchTreeRecursively(child, predicate)
            if (found != null) return found
        }
        return null
    }
}
