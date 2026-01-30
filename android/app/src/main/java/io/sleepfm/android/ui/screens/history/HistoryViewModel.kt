package io.sleepfm.android.ui.screens.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.sleepfm.android.data.repository.SleepRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

data class HistorySession(
    val id: Int,
    val dateString: String,
    val bedTime: String,
    val wakeTime: String,
    val durationString: String,
    val efficiency: Int,
    val quality: String // "excellent", "good", "fair", "poor"
)

data class HistoryUiState(
    val isLoading: Boolean = false,
    val sessions: List<HistorySession> = emptyList(),
    val error: String? = null
)

@HiltViewModel
class HistoryViewModel @Inject constructor(
    private val sleepRepository: SleepRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(HistoryUiState())
    val uiState: StateFlow<HistoryUiState> = _uiState.asStateFlow()
    
    private val dateFormat = SimpleDateFormat("M월 d일 (E)", Locale.KOREAN)
    private val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())
    
    init {
        loadHistory()
    }
    
    fun refresh() {
        loadHistory()
    }
    
    private fun loadHistory() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            // First, try to load from remote
            val result = sleepRepository.getHistory()
            
            result.fold(
                onSuccess = { sessions ->
                    val historySessions = sessions.map { session ->
                        val startDate = parseDate(session.startTime)
                        val endDate = session.endTime?.let { parseDate(it) }
                        val durationMinutes = session.durationMinutes ?: 0
                        
                        HistorySession(
                            id = session.id,
                            dateString = dateFormat.format(startDate),
                            bedTime = timeFormat.format(startDate),
                            wakeTime = endDate?.let { timeFormat.format(it) } ?: "--:--",
                            durationString = formatDuration(durationMinutes),
                            efficiency = ((session.efficiency ?: 0f) * 100).toInt(),
                            quality = getQualityFromScore(session.sleepQuality ?: 0f)
                        )
                    }
                    _uiState.update { 
                        it.copy(
                            isLoading = false, 
                            sessions = historySessions,
                            error = null
                        ) 
                    }
                },
                onFailure = { exception ->
                    // Fall back to local data
                    loadLocalHistory()
                    _uiState.update { 
                        it.copy(error = exception.message)
                    }
                }
            )
        }
    }
    
    private fun loadLocalHistory() {
        viewModelScope.launch {
            sleepRepository.allSessions.collect { localSessions ->
                val historySessions = localSessions.map { entity ->
                    val durationMinutes = entity.durationMinutes ?: 0
                    
                    HistorySession(
                        id = entity.id,
                        dateString = dateFormat.format(entity.startTime),
                        bedTime = timeFormat.format(entity.startTime),
                        wakeTime = entity.endTime?.let { timeFormat.format(it) } ?: "--:--",
                        durationString = formatDuration(durationMinutes),
                        efficiency = ((entity.efficiency ?: 0f) * 100).toInt(),
                        quality = getQualityFromScore(entity.sleepQuality ?: 0f)
                    )
                }
                _uiState.update { 
                    it.copy(
                        isLoading = false,
                        sessions = historySessions
                    ) 
                }
            }
        }
    }
    
    private fun parseDate(dateString: String): Date {
        return try {
            SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                .parse(dateString) ?: Date()
        } catch (e: Exception) {
            Date()
        }
    }
    
    private fun formatDuration(minutes: Int): String {
        val hours = minutes / 60
        val mins = minutes % 60
        return if (hours > 0) {
            "${hours}시간 ${mins}분"
        } else {
            "${mins}분"
        }
    }
    
    private fun getQualityFromScore(score: Float): String {
        return when {
            score >= 0.85f -> "excellent"
            score >= 0.70f -> "good"
            score >= 0.50f -> "fair"
            else -> "poor"
        }
    }
}
