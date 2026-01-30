package io.sleepfm.android.ui.screens.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.sleepfm.android.data.repository.SleepRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DashboardRisk(
    val disease: String,
    val level: String,
    val score: Float
)

data class DashboardUiState(
    val isLoading: Boolean = false,
    val sleepScore: Int = 0,
    val scoreMessage: String = "수면 데이터를 불러오는 중...",
    val hasLastNightData: Boolean = false,
    val totalSleepHours: String = "0시간 0분",
    val sleepEfficiency: Int = 0,
    val bedTime: String = "--:--",
    val wakeTime: String = "--:--",
    val wakeMinutes: Int = 0,
    val lightMinutes: Int = 0,
    val deepMinutes: Int = 0,
    val remMinutes: Int = 0,
    val diseaseRisks: List<DashboardRisk> = emptyList(),
    val isHealthConnectAvailable: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val sleepRepository: SleepRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(DashboardUiState())
    val uiState: StateFlow<DashboardUiState> = _uiState.asStateFlow()
    
    init {
        loadDashboardData()
    }
    
    fun syncData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            val result = sleepRepository.getHistory()
            
            result.fold(
                onSuccess = { sessions ->
                    if (sessions.isNotEmpty()) {
                        val latestSession = sessions.first()
                        loadSessionDetails(latestSession.id)
                    } else {
                        _uiState.update { 
                            it.copy(
                                isLoading = false,
                                hasLastNightData = false,
                                sleepScore = 0,
                                scoreMessage = "수면 데이터가 없습니다"
                            ) 
                        }
                    }
                },
                onFailure = { exception ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false, 
                            error = exception.message
                        ) 
                    }
                }
            )
        }
    }
    
    private fun loadDashboardData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            // Load latest session from local database
            sleepRepository.latestSession.collect { session ->
                if (session != null) {
                    val hours = (session.durationMinutes ?: 0) / 60
                    val minutes = (session.durationMinutes ?: 0) % 60
                    
                    val score = calculateSleepScore(
                        session.sleepQuality ?: 0f,
                        session.efficiency ?: 0f
                    )
                    
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            hasLastNightData = true,
                            sleepScore = score,
                            scoreMessage = getScoreMessage(score),
                            totalSleepHours = "${hours}시간 ${minutes}분",
                            sleepEfficiency = ((session.efficiency ?: 0f) * 100).toInt(),
                            bedTime = formatTime(session.startTime),
                            wakeTime = session.endTime?.let { formatTime(it) } ?: "--:--"
                        )
                    }
                    
                    // Load analysis if available
                    loadSessionDetails(session.id)
                } else {
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            hasLastNightData = false,
                            sleepScore = 0,
                            scoreMessage = "수면 데이터가 없습니다"
                        ) 
                    }
                }
            }
        }
    }
    
    private suspend fun loadSessionDetails(sessionId: Int) {
        // Load analysis
        val analysisResult = sleepRepository.analyzeSession(sessionId)
        analysisResult.onSuccess { analysis ->
            _uiState.update { 
                it.copy(
                    wakeMinutes = analysis.summary.wakeMinutes,
                    lightMinutes = analysis.summary.lightMinutes,
                    deepMinutes = analysis.summary.deepMinutes,
                    remMinutes = analysis.summary.remMinutes
                ) 
            }
        }
        
        // Load disease risks
        val riskResult = sleepRepository.predictDiseaseRisk(sessionId)
        riskResult.onSuccess { riskResponse ->
            val risks = riskResponse.predictions.map { prediction ->
                DashboardRisk(
                    disease = translateDisease(prediction.disease),
                    level = prediction.riskLevel,
                    score = prediction.riskScore
                )
            }
            _uiState.update { it.copy(diseaseRisks = risks) }
        }
        
        _uiState.update { it.copy(isLoading = false) }
    }
    
    private fun calculateSleepScore(quality: Float, efficiency: Float): Int {
        return ((quality * 50 + efficiency * 50) * 100).toInt().coerceIn(0, 100)
    }
    
    private fun getScoreMessage(score: Int): String {
        return when {
            score >= 90 -> "훌륭한 수면이었습니다! 🌟"
            score >= 80 -> "좋은 수면입니다 😊"
            score >= 70 -> "괜찮은 수면이었습니다"
            score >= 60 -> "개선이 필요합니다"
            else -> "수면 패턴을 점검해 보세요"
        }
    }
    
    private fun formatTime(date: java.util.Date): String {
        val format = java.text.SimpleDateFormat("HH:mm", java.util.Locale.getDefault())
        return format.format(date)
    }
    
    private fun translateDisease(disease: String): String {
        return when (disease.lowercase()) {
            "sleep_apnea" -> "수면무호흡증"
            "insomnia" -> "불면증"
            "restless_leg" -> "하지불안증후군"
            "narcolepsy" -> "기면증"
            else -> disease
        }
    }
}
