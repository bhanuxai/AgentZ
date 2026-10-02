package com.example.agentz.ui.components

import androidx.compose.foundation.text.BasicText
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.sp
import com.example.agentz.theme.AgentCyan
import com.example.agentz.theme.NeonGreen

@Composable
fun RichMarkdownText(
    text: String,
    modifier: Modifier = Modifier,
    style: TextStyle = MaterialTheme.typography.bodyLarge,
    color: Color = MaterialTheme.colorScheme.onSurface
) {
    val annotatedString = parseMarkdown(
        text = text,
        baseColor = color,
        primaryHighlight = MaterialTheme.colorScheme.primary,
        boldColor = color
    )

    BasicText(
        text = annotatedString,
        modifier = modifier,
        style = style
    )
}

/**
 * Parses bold (**text**), inline code (`code`), bullet points, and pricing highlights
 */
fun parseMarkdown(
    text: String,
    baseColor: Color,
    primaryHighlight: Color,
    boldColor: Color
): AnnotatedString {
    return buildAnnotatedString {
        val parts = text.split("(?<=\n)|(?=\n)")
        
        for (line in parts) {
            var currentIndex = 0
            val boldRegex = Regex("\\*\\*(.*?)\\*\\*")
            val matches = boldRegex.findAll(line)
            
            var lastIndex = 0
            for (match in matches) {
                if (match.range.first > lastIndex) {
                    val normalText = line.substring(lastIndex, match.range.first)
                    appendStyledText(normalText, baseColor, primaryHighlight)
                }
                
                val boldContent = match.groupValues[1]
                withStyle(SpanStyle(fontWeight = FontWeight.Bold, color = boldColor)) {
                    append(boldContent)
                }
                lastIndex = match.range.last + 1
            }
            
            if (lastIndex < line.length) {
                val remainingText = line.substring(lastIndex)
                appendStyledText(remainingText, baseColor, primaryHighlight)
            }
        }
    }
}

private fun AnnotatedString.Builder.appendStyledText(
    text: String,
    baseColor: Color,
    primaryHighlight: Color
) {
    // Check for inline backticks `tool_call`
    val codeRegex = Regex("`(.*?)`")
    val codeMatches = codeRegex.findAll(text)
    
    if (codeMatches.none()) {
        withStyle(SpanStyle(color = baseColor)) {
            append(text)
        }
        return
    }
    
    var lastIdx = 0
    for (m in codeMatches) {
        if (m.range.first > lastIdx) {
            withStyle(SpanStyle(color = baseColor)) {
                append(text.substring(lastIdx, m.range.first))
            }
        }
        
        val codeText = m.groupValues[1]
        withStyle(
            SpanStyle(
                color = primaryHighlight,
                fontFamily = FontFamily.Monospace,
                fontWeight = FontWeight.SemiBold,
                fontSize = 13.sp
            )
        ) {
            append(codeText)
        }
        lastIdx = m.range.last + 1
    }
    
    if (lastIdx < text.length) {
        withStyle(SpanStyle(color = baseColor)) {
            append(text.substring(lastIdx))
        }
    }
}
