package io.sleepfm.wear.presentation.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import io.sleepfm.wear.data.repository.SleepTrackingRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SummaryUiState(
    val sleepScore: Int = 0,
    val sleepDuration: String = "0시간 0분",
    val bedTime: String = "--:--",
    val wakeTime: String = "--:--",
    val deepMinutes: Int = 0,
    val lightMinutes: Int = 0,
    val remMinutes: Int = 0,
    val wakeMinutes: Int = 0,
    val avgHeartRate: Int = 0,
    val avgSpO2: Int = 0
)

@HiltViewModel
class SummaryViewModel @Inject constructor(
    private val sleepTrackingRepository: SleepTrackingRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(SummaryUiState())
    val uiState: StateFlow<SummaryUiState> = _uiState.asStateFlow()
    
    init {
        loadLastSleepSummary()
    }
    
    private fun loadLastSleepSummary() {
        viewModelScope.launch {
            val session = sleepTrackingRepository.getLastSession() ?: return@launch
            
            val hours = session.durationMinutes / 60
            val minutes = session.durationMinutes % 60
            
            _uiState.update { 
                it.copy(
                    sleepScore = session.sleepScore,
                    sleepDuration = "${hours}시간 ${minutes}분",
                    bedTime = session.bedTime,
                    wakeTime = session.wakeTime,
                    deepMinutes = session.deepMinutes,
                    lightMinutes = session.lightMinutes,
                    remMinutes = session.remMinutes,
                    wakeMinutes = session.wakeMinutes,
                    avgHeartRate = session.avgHeartRate,
                    avgSpO2 = session.avgSpO2
                )
            }
        }
    }
}
