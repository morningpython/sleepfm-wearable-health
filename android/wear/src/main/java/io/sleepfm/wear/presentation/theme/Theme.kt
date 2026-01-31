package io.sleepfm.wear.presentation.theme

import androidx.compose.runtime.Composable
import androidx.wear.compose.material.MaterialTheme
import androidx.wear.compose.material.Colors

private val wearColorPalette = Colors(
    primary = SleepPrimary,
    primaryVariant = SleepPrimaryDark,
    secondary = SleepSecondary,
    secondaryVariant = SleepSecondaryDark,
    error = SleepError,
    onPrimary = SleepOnPrimary,
    onSecondary = SleepOnSecondary,
    onError = SleepOnError,
    background = SleepBackground,
    onBackground = SleepOnBackground,
    surface = SleepSurface,
    onSurface = SleepOnSurface
)

@Composable
fun SleepFMWearTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colors = wearColorPalette,
        content = content
    )
}
