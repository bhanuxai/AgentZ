package com.example.agentz.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme = darkColorScheme(
    primary = AgentCyan,
    onPrimary = Color(0xFF00363F),
    primaryContainer = Color(0xFF004F5D),
    onPrimaryContainer = Color(0xFF9CF0FF),
    
    secondary = AgentVioletLight,
    onSecondary = Color(0xFF381E72),
    secondaryContainer = Color(0xFF4F378B),
    onSecondaryContainer = Color(0xFFEADDFF),
    
    tertiary = NeonGreenLight,
    onTertiary = Color(0xFF003920),
    tertiaryContainer = Color(0xFF005230),
    onTertiaryContainer = Color(0xFF6CF8A7),
    
    background = AgentDarkBackground,
    onBackground = TextPrimaryDark,
    surface = AgentDarkSurface,
    onSurface = TextPrimaryDark,
    surfaceVariant = AgentDarkSurfaceVariant,
    onSurfaceVariant = TextSecondaryDark,
    surfaceContainer = AgentDarkSurfaceElevated,
    
    error = NeonRose,
    onError = Color.White,
    errorContainer = Color(0xFF93000A),
    onErrorContainer = Color(0xFFFFDAD6),
    
    outline = TextMutedDark,
    outlineVariant = AgentDarkCardBorder
)

private val LightColorScheme = lightColorScheme(
    primary = AgentCyanDark,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFBCEBFF),
    onPrimaryContainer = Color(0xFF001F28),
    
    secondary = AgentIndigo,
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFE0E0FF),
    onSecondaryContainer = Color(0xFF190065),
    
    tertiary = NeonGreen,
    onTertiary = Color.White,
    tertiaryContainer = Color(0xFFB9F6CA),
    onTertiaryContainer = Color(0xFF002110),
    
    background = AgentLightBackground,
    onBackground = TextPrimaryLight,
    surface = AgentLightSurface,
    onSurface = TextPrimaryLight,
    surfaceVariant = AgentLightSurfaceVariant,
    onSurfaceVariant = TextSecondaryLight,
    
    error = NeonRoseDark,
    onError = Color.White,
    errorContainer = Color(0xFFFFDAD6),
    onErrorContainer = Color(0xFF410002),
    
    outline = TextMutedLight,
    outlineVariant = AgentLightCardBorder
)

@Composable
fun AgentZTheme(
    darkTheme: Boolean = true, // Default to dark for high-tech AI agent aesthetic
    dynamicColor: Boolean = false, // Use our handcrafted AI cyber palette
    content: @Composable () -> Unit,
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
