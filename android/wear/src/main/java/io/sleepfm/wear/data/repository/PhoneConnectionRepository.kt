package io.sleepfm.wear.data.repository

import android.content.Context
import com.google.android.gms.wearable.*
import com.google.gson.Gson
import dagger.hilt.android.qualifiers.ApplicationContext
import io.sleepfm.wear.data.model.CollectedSleepData
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PhoneConnectionRepository @Inject constructor(
    @ApplicationContext private val context: Context,
    private val gson: Gson
) {
    companion object {
        const val SLEEP_DATA_PATH = "/sleep_data"
        const val SYNC_REQUEST_PATH = "/sync_request"
        const val CAPABILITY_PHONE_APP = "sleepfm_phone_app"
    }
    
    private val dataClient: DataClient by lazy { Wearable.getDataClient(context) }
    private val messageClient: MessageClient by lazy { Wearable.getMessageClient(context) }
    private val capabilityClient: CapabilityClient by lazy { Wearable.getCapabilityClient(context) }
    private val nodeClient: NodeClient by lazy { Wearable.getNodeClient(context) }
    
    val connectionStatus: Flow<ConnectionStatus> = callbackFlow {
        val listener = CapabilityClient.OnCapabilityChangedListener { capabilityInfo ->
            val isConnected = capabilityInfo.nodes.isNotEmpty()
            val nodeId = capabilityInfo.nodes.firstOrNull()?.id
            trySend(ConnectionStatus(isConnected = isConnected, connectedNodeId = nodeId))
        }
        
        capabilityClient.addListener(listener, CAPABILITY_PHONE_APP)
        
        // Check initial state
        try {
            val info = capabilityClient.getCapability(
                CAPABILITY_PHONE_APP,
                CapabilityClient.FILTER_REACHABLE
            ).await()
            val isConnected = info.nodes.isNotEmpty()
            val nodeId = info.nodes.firstOrNull()?.id
            trySend(ConnectionStatus(isConnected = isConnected, connectedNodeId = nodeId))
        } catch (e: Exception) {
            trySend(ConnectionStatus(isConnected = false, error = e.message))
        }
        
        awaitClose {
            capabilityClient.removeListener(listener)
        }
    }
    
    suspend fun sendSleepData(data: CollectedSleepData): Result<Unit> {
        return try {
            val dataJson = gson.toJson(data)
            val putDataRequest = PutDataMapRequest.create(SLEEP_DATA_PATH).apply {
                dataMap.putString("data", dataJson)
                dataMap.putLong("timestamp", System.currentTimeMillis())
            }.asPutDataRequest().setUrgent()
            
            dataClient.putDataItem(putDataRequest).await()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun requestSyncFromPhone(): Result<Unit> {
        return try {
            val connectedNodes = nodeClient.connectedNodes.await()
            val phoneNode = connectedNodes.firstOrNull { it.isNearby }
            
            if (phoneNode != null) {
                messageClient.sendMessage(
                    phoneNode.id,
                    SYNC_REQUEST_PATH,
                    ByteArray(0)
                ).await()
                Result.success(Unit)
            } else {
                Result.failure(Exception("Phone not connected"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getConnectedPhoneNode(): Node? {
        return try {
            val info = capabilityClient.getCapability(
                CAPABILITY_PHONE_APP,
                CapabilityClient.FILTER_REACHABLE
            ).await()
            
            info.nodes.firstOrNull { it.isNearby } ?: info.nodes.firstOrNull()
        } catch (e: Exception) {
            null
        }
    }
    
    suspend fun isPhoneConnected(): Boolean {
        return getConnectedPhoneNode() != null
    }
    
    data class ConnectionStatus(
        val isConnected: Boolean = false,
        val connectedNodeId: String? = null,
        val error: String? = null
    )
}
