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
fun TrackingScreen(
    onStopTracking: () -> Unit,
    viewModel: TrackingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        timeText = { TimeText() }
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(SleepBackground)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Status indicator
            Text(
                text = "●",
                color = StatusTracking,
                style = MaterialTheme.typography.display3
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "수면 추적 중",
                style = MaterialTheme.typography.title2,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Elapsed time
            Text(
                text = uiState.elapsedTime,
                style = MaterialTheme.typography.display2,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Current metrics
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                MetricChip(
                    label = "심박수",
                    value = "${uiState.currentHeartRate}",
                    unit = "bpm"
                )
                MetricChip(
                    label = "SpO2",
                    value = "${uiState.currentSpO2}",
                    unit = "%"
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Stop button
            Button(
                onClick = {
                    viewModel.stopTracking()
                    onStopTracking()
                },
                colors = ButtonDefaults.buttonColors(
                    backgroundColor = SleepError
                ),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("중지")
            }
        }
    }
}

@Composable
private fun MetricChip(
    label: String,
    value: String,
    unit: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.caption3,
            color = SleepOnSurfaceVariant
        )
        Row(
            verticalAlignment = Alignment.Bottom
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.body1
            )
            Text(
                text = unit,
                style = MaterialTheme.typography.caption3,
                modifier = Modifier.padding(start = 2.dp)
            )
        }
    }
}
