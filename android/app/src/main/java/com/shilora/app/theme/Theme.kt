package com.shilora.app.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// STRICT 60 : 30 : 10 BRAND COLOR DISTRIBUTION
private val ShiloraColorScheme = lightColorScheme(
    primary = SageGreen,
    onPrimary = NeutralWhite,
    primaryContainer = SageGreenSurface,
    onPrimaryContainer = NeutralBlack,

    secondary = ConcreteGrey,
    onSecondary = NeutralBlack,
    secondaryContainer = StoneCardSurface,
    onSecondaryContainer = NeutralDarkGrey,

    tertiary = BurntAmber,
    onTertiary = NeutralWhite,
    tertiaryContainer = BurntAmberGlow,
    onTertiaryContainer = BurntAmberDark,

    background = SageGreenSurface,
    onBackground = NeutralBlack,

    surface = NeutralWhite,
    onSurface = NeutralBlack,
    surfaceVariant = StoneCardSurface,
    onSurfaceVariant = NeutralDarkGrey,

    outline = StoneBorder
)

@Composable
fun ShiloraTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = SageGreenDark.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = ShiloraColorScheme,
        typography = ShiloraTypography,
        content = content
    )
}
