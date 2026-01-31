package io.sleepfm.wear.service

import android.content.Intent
import com.google.android.gms.wearable.*
import dagger.hilt.android.AndroidEntryPoint
import io.sleepfm.wear.data.local.SleepDataStore
import io.sleepfm.wear.data.repository.PhoneConnectionRepository
import kotlinx.coroutines.*
import timber.log.Timber
import javax.inject.Inject

/**
 * Service for syncing data with the phone app via Wearable Data Layer API
 */
@AndroidEntryPoint
class DataSyncService : WearableListenerService() {
    
    @Inject
    lateinit var sleepDataStore: SleepDataStore
    
    @Inject
    lateinit var phoneConnectionRepository: PhoneConnectionRepository
    
    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    
    companion object {
        const val SLEEP_DATA_PATH = "/sleep_data"
        const val SYNC_REQUEST_PATH = "/sync_request"
        const val SYNC_RESPONSE_PATH = "/sync_response"
    }
    
    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }
    
    override fun onDataChanged(dataEvents: DataEventBuffer) {
        Timber.d("Data changed: ${dataEvents.count} events")
        
        dataEvents.forEach { event ->
            when (event.type) {
                DataEvent.TYPE_CHANGED -> {
                    val dataItem = event.dataItem
                    handleDataChange(dataItem)
                }
                DataEvent.TYPE_DELETED -> {
                    Timber.d("Data deleted: ${event.dataItem.uri}")
                }
            }
        }
    }
    
    override fun onMessageReceived(messageEvent: MessageEvent) {
        Timber.d("Message received: ${messageEvent.path}")
        
        when (messageEvent.path) {
            SYNC_REQUEST_PATH -> {
                serviceScope.launch {
                    handleSyncRequest(messageEvent)
                }
            }
        }
    }
    
    override fun onCapabilityChanged(capabilityInfo: CapabilityInfo) {
        Timber.d("Capability changed: ${capabilityInfo.name}, nodes: ${capabilityInfo.nodes.size}")
        // Connection status is automatically updated via PhoneConnectionRepository.connectionStatus flow
    }
    
    private fun handleDataChange(dataItem: DataItem) {
        val uri = dataItem.uri
        Timber.d("Handling data change: $uri")
        
        when (uri.path) {
            SYNC_RESPONSE_PATH -> {
                serviceScope.launch {
                    // Phone acknowledged sync
                    sleepDataStore.setLastSyncTime(System.currentTimeMillis())
                }
            }
        }
    }
    
    private suspend fun handleSyncRequest(messageEvent: MessageEvent) {
        try {
            // Get all collected sleep data
            val sleepData = sleepDataStore.getCollectedSleepData()
            
            // Send data to phone
            phoneConnectionRepository.sendSleepData(sleepData)
            
            Timber.d("Sleep data sent to phone")
        } catch (e: Exception) {
            Timber.e(e, "Error handling sync request")
        }
    }
}
