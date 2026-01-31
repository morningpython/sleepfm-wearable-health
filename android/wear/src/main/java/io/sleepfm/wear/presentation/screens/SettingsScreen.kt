package io.sleepfm.wear.presentation.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.wear.compose.material.*
import io.sleepfm.wear.presentation.theme.*

@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val listState = rememberScalingLazyListState()
    
    Scaffold(
        timeText = { TimeText() },
        vignette = { Vignette(vignettePosition = VignettePosition.TopAndBottom) },
        positionIndicator = { PositionIndicator(scalingLazyListState = listState) }
    ) {
        ScalingLazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .background(SleepBackground),
            state = listState,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Title
            item {
                Text(
                    text = "설정",
                    style = MaterialTheme.typography.title2,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
            
            // Phone connection
            item {
                Chip(
                    onClick = { viewModel.syncWithPhone() },
                    modifier = Modifier.fillMaxWidth(),
                    label = {
                        Column {
                            Text("휴대폰 연결")
                            Text(
                                text = if (uiState.isPhoneConnected) "연결됨" else "연결 안됨",
                                style = MaterialTheme.typography.caption2,
                                color = if (uiState.isPhoneConnected) StatusTracking else SleepOnSurfaceVariant
                            )
                        }
                    },
                    icon = { Text("📱") },
                    colors = ChipDefaults.chipColors(backgroundColor = SleepSurface)
                )
            }
            
            // Auto tracking toggle
            item {
                ToggleChip(
                    checked = uiState.autoTrackingEnabled,
                    onCheckedChange = { viewModel.setAutoTracking(it) },
                    modifier = Modifier.fillMaxWidth(),
                    label = {
                        Column {
                            Text("자동 수면 감지")
                            Text(
                                text = "움직임 기반 자동 시작",
                                style = MaterialTheme.typography.caption2,
                                color = SleepOnSurfaceVariant
                            )
                        }
                    },
                    toggleControl = {
                        Switch(
                            checked = uiState.autoTrackingEnabled,
                            onCheckedChange = null
                        )
                    },
                    colors = ToggleChipDefaults.toggleChipColors(
                        checkedStartBackgroundColor = SleepPrimary.copy(alpha = 0.3f),
                        checkedEndBackgroundColor = SleepPrimary.copy(alpha = 0.3f)
                    )
                )
            }
            
            // Haptic feedback toggle
            item {
                ToggleChip(
                    checked = uiState.hapticFeedbackEnabled,
                    onCheckedChange = { viewModel.setHapticFeedback(it) },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("진동 피드백") },
                    toggleControl = {
                        Switch(
                            checked = uiState.hapticFeedbackEnabled,
                            onCheckedChange = null
                        )
                    },
                    colors = ToggleChipDefaults.toggleChipColors(
                        checkedStartBackgroundColor = SleepPrimary.copy(alpha = 0.3f),
                        checkedEndBackgroundColor = SleepPrimary.copy(alpha = 0.3f)
                    )
                )
            }
            
            // Data sync
            item {
                Chip(
                    onClick = { viewModel.syncWithPhone() },
                    modifier = Modifier.fillMaxWidth(),
                    label = {
                        Column {
                            Text("데이터 동기화")
                            Text(
                                text = "마지막: ${uiState.lastSyncTime}",
                                style = MaterialTheme.typography.caption2,
                                color = SleepOnSurfaceVariant
                            )
                        }
                    },
                    icon = { Text("🔄") },
                    colors = ChipDefaults.chipColors(backgroundColor = SleepSurface)
                )
            }
            
            // Battery optimization info
            item {
                Chip(
                    onClick = { },
                    modifier = Modifier.fillMaxWidth(),
                    label = {
                        Column {
                            Text("배터리 최적화")
                            Text(
                                text = "정확한 추적을 위해 비활성화 권장",
                                style = MaterialTheme.typography.caption2,
                                color = SleepOnSurfaceVariant
                            )
                        }
                    },
                    icon = { Text("🔋") },
                    colors = ChipDefaults.chipColors(backgroundColor = SleepSurface)
                )
            }
            
            // Version info
            item {
                Text(
                    text = "버전 1.0.0",
                    style = MaterialTheme.typography.caption3,
                    color = SleepOnSurfaceVariant,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(top = 16.dp)
                )
            }
        }
    }
}
