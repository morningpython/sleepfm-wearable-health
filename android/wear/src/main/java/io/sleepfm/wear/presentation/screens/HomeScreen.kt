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
import io.sleepfm.wear.presentation.theme.SleepBackground
import io.sleepfm.wear.presentation.theme.StatusTracking

@Composable
fun HomeScreen(
    onStartTracking: () -> Unit,
    onViewSummary: () -> Unit,
    onOpenSettings: () -> Unit,
    viewModel: HomeViewModel = hiltViewModel()
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
                    text = "🌙 SleepFM",
                    style = MaterialTheme.typography.title2,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
            
            // Status indicator
            item {
                if (uiState.isTracking) {
                    Chip(
                        onClick = { },
                        colors = ChipDefaults.chipColors(
                            backgroundColor = StatusTracking.copy(alpha = 0.2f)
                        ),
                        label = {
                            Text(
                                text = "추적 중",
                                color = StatusTracking
                            )
                        },
                        icon = {
                            Text("●", color = StatusTracking)
                        }
                    )
                }
            }
            
            // Start/Stop Tracking Button
            item {
                Button(
                    onClick = {
                        if (uiState.isTracking) {
                            viewModel.stopTracking()
                        } else {
                            viewModel.startTracking()
                            onStartTracking()
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    Text(
                        text = if (uiState.isTracking) "추적 중지" else "수면 추적 시작",
                        textAlign = TextAlign.Center
                    )
                }
            }
            
            // Last night summary
            if (uiState.lastSleepDuration != null) {
                item {
                    Chip(
                        onClick = onViewSummary,
                        modifier = Modifier.fillMaxWidth(),
                        label = {
                            Column {
                                Text(
                                    text = "어젯밤 수면",
                                    style = MaterialTheme.typography.caption2
                                )
                                Text(
                                    text = uiState.lastSleepDuration!!,
                                    style = MaterialTheme.typography.body1
                                )
                            }
                        },
                        icon = {
                            Text("😴")
                        }
                    )
                }
            }
            
            // Settings
            item {
                Chip(
                    onClick = onOpenSettings,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("설정") },
                    icon = { Text("⚙️") }
                )
            }
            
            // Phone sync status
            item {
                Text(
                    text = if (uiState.isPhoneConnected) "📱 연결됨" else "📱 연결 안됨",
                    style = MaterialTheme.typography.caption3,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
        }
    }
}
