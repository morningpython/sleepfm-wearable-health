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
fun SummaryScreen(
    viewModel: SummaryViewModel = hiltViewModel()
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
                    text = "어젯밤 수면",
                    style = MaterialTheme.typography.title2,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
            
            // Sleep score
            item {
                CircularProgressIndicator(
                    progress = uiState.sleepScore / 100f,
                    modifier = Modifier.size(80.dp),
                    indicatorColor = SleepPrimary,
                    trackColor = SleepSurfaceVariant,
                    strokeWidth = 8.dp
                )
            }
            
            item {
                Text(
                    text = "${uiState.sleepScore}점",
                    style = MaterialTheme.typography.display3,
                    textAlign = TextAlign.Center
                )
            }
            
            // Sleep duration
            item {
                Chip(
                    onClick = { },
                    modifier = Modifier.fillMaxWidth(),
                    label = {
                        Column {
                            Text("수면 시간", style = MaterialTheme.typography.caption2)
                            Text(uiState.sleepDuration, style = MaterialTheme.typography.body1)
                        }
                    },
                    icon = { Text("⏱️") },
                    colors = ChipDefaults.chipColors(
                        backgroundColor = SleepSurface
                    )
                )
            }
            
            // Sleep time
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("취침", style = MaterialTheme.typography.caption3, color = SleepOnSurfaceVariant)
                        Text(uiState.bedTime, style = MaterialTheme.typography.body2)
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("기상", style = MaterialTheme.typography.caption3, color = SleepOnSurfaceVariant)
                        Text(uiState.wakeTime, style = MaterialTheme.typography.body2)
                    }
                }
            }
            
            // Sleep stages
            item {
                Text(
                    text = "수면 단계",
                    style = MaterialTheme.typography.caption1,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
            
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    SleepStageItem(
                        label = "깊은",
                        minutes = uiState.deepMinutes,
                        color = StageDeep
                    )
                    SleepStageItem(
                        label = "얕은",
                        minutes = uiState.lightMinutes,
                        color = StageLight
                    )
                    SleepStageItem(
                        label = "REM",
                        minutes = uiState.remMinutes,
                        color = StageREM
                    )
                }
            }
            
            // Heart rate
            item {
                Chip(
                    onClick = { },
                    modifier = Modifier.fillMaxWidth(),
                    label = {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("평균 심박수")
                            Text("${uiState.avgHeartRate} bpm")
                        }
                    },
                    icon = { Text("❤️") },
                    colors = ChipDefaults.chipColors(
                        backgroundColor = SleepSurface
                    )
                )
            }
            
            // SpO2
            item {
                Chip(
                    onClick = { },
                    modifier = Modifier.fillMaxWidth(),
                    label = {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("평균 SpO2")
                            Text("${uiState.avgSpO2}%")
                        }
                    },
                    icon = { Text("🫁") },
                    colors = ChipDefaults.chipColors(
                        backgroundColor = SleepSurface
                    )
                )
            }
        }
    }
}

@Composable
private fun SleepStageItem(
    label: String,
    minutes: Int,
    color: androidx.compose.ui.graphics.Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "●",
            color = color,
            style = MaterialTheme.typography.body2
        )
        Text(
            text = label,
            style = MaterialTheme.typography.caption3,
            color = SleepOnSurfaceVariant
        )
        Text(
            text = "${minutes}분",
            style = MaterialTheme.typography.caption2
        )
    }
}
