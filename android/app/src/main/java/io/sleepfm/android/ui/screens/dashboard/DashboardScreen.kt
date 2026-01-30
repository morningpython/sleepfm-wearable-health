package io.sleepfm.android.ui.screens.dashboard

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import io.sleepfm.android.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("수면 대시보드") },
                actions = {
                    IconButton(onClick = { viewModel.syncData() }) {
                        Icon(Icons.Default.Sync, contentDescription = "동기화")
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (uiState.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            } else {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(16.dp)
                ) {
                    // Sleep Score Card
                    SleepScoreCard(
                        score = uiState.sleepScore,
                        message = uiState.scoreMessage
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Last Night Summary
                    if (uiState.hasLastNightData) {
                        LastNightSummaryCard(
                            totalSleep = uiState.totalSleepHours,
                            efficiency = uiState.sleepEfficiency,
                            bedTime = uiState.bedTime,
                            wakeTime = uiState.wakeTime
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        // Sleep Stages
                        SleepStagesCard(
                            wakeMinutes = uiState.wakeMinutes,
                            lightMinutes = uiState.lightMinutes,
                            deepMinutes = uiState.deepMinutes,
                            remMinutes = uiState.remMinutes
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        // Health Risk Card
                        if (uiState.diseaseRisks.isNotEmpty()) {
                            HealthRiskCard(risks = uiState.diseaseRisks)
                        }
                    } else {
                        // No Data Card
                        NoDataCard()
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Quick Actions
                    QuickActionsCard(
                        onSyncClick = { viewModel.syncData() },
                        isHealthConnectAvailable = uiState.isHealthConnectAvailable
                    )
                    
                    Spacer(modifier = Modifier.height(32.dp))
                }
            }
        }
    }
}

@Composable
private fun SleepScoreCard(
    score: Int,
    message: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "오늘의 수면 점수",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primary),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "$score",
                    style = MaterialTheme.typography.displayLarge,
                    color = MaterialTheme.colorScheme.onPrimary,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = message,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
        }
    }
}

@Composable
private fun LastNightSummaryCard(
    totalSleep: String,
    efficiency: Int,
    bedTime: String,
    wakeTime: String
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "어젯밤 수면",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                SummaryItem(
                    icon = Icons.Default.Bedtime,
                    label = "취침",
                    value = bedTime
                )
                SummaryItem(
                    icon = Icons.Default.WbSunny,
                    label = "기상",
                    value = wakeTime
                )
                SummaryItem(
                    icon = Icons.Default.Timer,
                    label = "수면시간",
                    value = totalSleep
                )
                SummaryItem(
                    icon = Icons.Default.TrendingUp,
                    label = "효율",
                    value = "$efficiency%"
                )
            }
        }
    }
}

@Composable
private fun SummaryItem(
    icon: ImageVector,
    label: String,
    value: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun SleepStagesCard(
    wakeMinutes: Int,
    lightMinutes: Int,
    deepMinutes: Int,
    remMinutes: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "수면 단계",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Stage bars
            val total = wakeMinutes + lightMinutes + deepMinutes + remMinutes
            
            StageBar(
                label = "깨어있음",
                minutes = wakeMinutes,
                total = total,
                color = SleepStageWake
            )
            StageBar(
                label = "얕은 수면",
                minutes = lightMinutes,
                total = total,
                color = SleepStageLight
            )
            StageBar(
                label = "깊은 수면",
                minutes = deepMinutes,
                total = total,
                color = SleepStageDeep
            )
            StageBar(
                label = "REM 수면",
                minutes = remMinutes,
                total = total,
                color = SleepStageREM
            )
        }
    }
}

@Composable
private fun StageBar(
    label: String,
    minutes: Int,
    total: Int,
    color: Color
) {
    val percentage = if (total > 0) minutes.toFloat() / total else 0f
    
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.width(80.dp)
        )
        
        Box(
            modifier = Modifier
                .weight(1f)
                .height(24.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(percentage)
                    .clip(RoundedCornerShape(4.dp))
                    .background(color)
            )
        }
        
        Text(
            text = "${minutes}분",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.width(50.dp),
            textAlign = androidx.compose.ui.text.style.TextAlign.End
        )
    }
}

@Composable
private fun HealthRiskCard(
    risks: List<DashboardRisk>
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "건강 위험도",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            risks.forEach { risk ->
                RiskItem(risk = risk)
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
private fun RiskItem(risk: DashboardRisk) {
    val color = when (risk.level) {
        "low" -> RiskLow
        "moderate" -> RiskModerate
        else -> RiskHigh
    }
    
    val levelText = when (risk.level) {
        "low" -> "낮음"
        "moderate" -> "보통"
        else -> "높음"
    }
    
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(12.dp)
                .clip(CircleShape)
                .background(color)
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = risk.disease,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.weight(1f)
        )
        Text(
            text = levelText,
            style = MaterialTheme.typography.bodyMedium,
            color = color,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun NoDataCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Bedtime,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "수면 데이터가 없습니다",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "Wear OS 앱을 착용하고 수면을 시작하세요",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
            )
        }
    }
}

@Composable
private fun QuickActionsCard(
    onSyncClick: () -> Unit,
    isHealthConnectAvailable: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "빠른 작업",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                ActionButton(
                    icon = Icons.Default.Sync,
                    label = "데이터 동기화",
                    onClick = onSyncClick
                )
                
                ActionButton(
                    icon = Icons.Default.HealthAndSafety,
                    label = "Health Connect",
                    onClick = { /* Open Health Connect settings */ },
                    enabled = isHealthConnectAvailable
                )
            }
        }
    }
}

@Composable
private fun ActionButton(
    icon: ImageVector,
    label: String,
    onClick: () -> Unit,
    enabled: Boolean = true
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        FilledTonalIconButton(
            onClick = onClick,
            enabled = enabled,
            modifier = Modifier.size(56.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(24.dp)
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = if (enabled) 
                MaterialTheme.colorScheme.onSurface 
            else 
                MaterialTheme.colorScheme.onSurface.copy(alpha = 0.38f)
        )
    }
}
