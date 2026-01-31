package io.sleepfm.wear.data.repository

import android.content.Context
import io.mockk.*
import io.mockk.impl.annotations.MockK
import com.google.android.gms.wearable.*
import com.google.android.gms.tasks.Tasks
import com.google.gson.Gson
import io.sleepfm.wear.data.model.CollectedSleepData
import io.sleepfm.wear.data.model.SensorReading
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class PhoneConnectionRepositoryTest {

    @MockK
    private lateinit var context: Context

    @MockK
    private lateinit var dataClient: DataClient

    @MockK
    private lateinit var messageClient: MessageClient

    @MockK
    private lateinit var capabilityClient: CapabilityClient

    @MockK
    private lateinit var nodeClient: NodeClient

    private lateinit var gson: Gson
    private lateinit var repository: PhoneConnectionRepository

    @Before
    fun setUp() {
        MockKAnnotations.init(this, relaxed = true)
        gson = Gson()

        // Mock Wearable.getXxxClient static calls
        mockkStatic(Wearable::class)
        every { Wearable.getDataClient(any<Context>()) } returns dataClient
        every { Wearable.getMessageClient(any<Context>()) } returns messageClient
        every { Wearable.getCapabilityClient(any<Context>()) } returns capabilityClient
        every { Wearable.getNodeClient(any<Context>()) } returns nodeClient

        repository = PhoneConnectionRepository(context, gson)
    }

    @After
    fun tearDown() {
        unmockkAll()
    }

    // ========== sendSleepData Tests ==========

    @Test
    fun `sendSleepData should put data item with correct path`() = runTest {
        // Given
        val data = CollectedSleepData(
            startTime = 1000L,
            endTime = 2000L,
            heartRateData = listOf(SensorReading(1500L, 72f)),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        val mockDataItem = mockk<DataItem>()
        every { dataClient.putDataItem(any()) } returns Tasks.forResult(mockDataItem)

        // When
        val result = repository.sendSleepData(data)

        // Then
        assertTrue(result.isSuccess)
        verify {
            dataClient.putDataItem(match { request ->
                request.uri.path == PhoneConnectionRepository.SLEEP_DATA_PATH
            })
        }
    }

    @Test
    fun `sendSleepData should return failure on exception`() = runTest {
        // Given
        val data = CollectedSleepData(
            startTime = 1000L,
            endTime = 2000L,
            heartRateData = emptyList(),
            spO2Data = emptyList(),
            accelerometerData = emptyList()
        )
        val exception = RuntimeException("Network error")
        every { dataClient.putDataItem(any()) } returns Tasks.forException(exception)

        // When
        val result = repository.sendSleepData(data)

        // Then
        assertTrue(result.isFailure)
    }

    // ========== requestSyncFromPhone Tests ==========

    @Test
    fun `requestSyncFromPhone should send message to connected node`() = runTest {
        // Given
        val mockNode = mockk<Node> {
            every { id } returns "test-node-id"
            every { isNearby } returns true
        }
        every { nodeClient.connectedNodes } returns Tasks.forResult(listOf(mockNode))
        every { messageClient.sendMessage(any(), any(), any()) } returns Tasks.forResult(1)

        // When
        val result = repository.requestSyncFromPhone()

        // Then
        assertTrue(result.isSuccess)
        verify {
            messageClient.sendMessage(
                "test-node-id",
                PhoneConnectionRepository.SYNC_REQUEST_PATH,
                any()
            )
        }
    }

    @Test
    fun `requestSyncFromPhone should return failure when no phone connected`() = runTest {
        // Given
        every { nodeClient.connectedNodes } returns Tasks.forResult(emptyList())

        // When
        val result = repository.requestSyncFromPhone()

        // Then
        assertTrue(result.isFailure)
    }

    // ========== getConnectedPhoneNode Tests ==========

    @Test
    fun `getConnectedPhoneNode should return nearby node first`() = runTest {
        // Given
        val nearbyNode = mockk<Node> {
            every { id } returns "nearby-node"
            every { isNearby } returns true
        }
        val farNode = mockk<Node> {
            every { id } returns "far-node"
            every { isNearby } returns false
        }
        val capabilityInfo = mockk<CapabilityInfo> {
            every { nodes } returns setOf(farNode, nearbyNode)
        }
        every {
            capabilityClient.getCapability(
                PhoneConnectionRepository.CAPABILITY_PHONE_APP,
                CapabilityClient.FILTER_REACHABLE
            )
        } returns Tasks.forResult(capabilityInfo)

        // When
        val result = repository.getConnectedPhoneNode()

        // Then
        assertEquals("nearby-node", result?.id)
    }

    @Test
    fun `getConnectedPhoneNode should return null when no nodes`() = runTest {
        // Given
        val capabilityInfo = mockk<CapabilityInfo> {
            every { nodes } returns emptySet()
        }
        every {
            capabilityClient.getCapability(any(), any())
        } returns Tasks.forResult(capabilityInfo)

        // When
        val result = repository.getConnectedPhoneNode()

        // Then
        assertNull(result)
    }

    // ========== isPhoneConnected Tests ==========

    @Test
    fun `isPhoneConnected should return true when node exists`() = runTest {
        // Given
        val mockNode = mockk<Node> {
            every { id } returns "test-node"
            every { isNearby } returns true
        }
        val capabilityInfo = mockk<CapabilityInfo> {
            every { nodes } returns setOf(mockNode)
        }
        every {
            capabilityClient.getCapability(any(), any())
        } returns Tasks.forResult(capabilityInfo)

        // When
        val result = repository.isPhoneConnected()

        // Then
        assertTrue(result)
    }

    @Test
    fun `isPhoneConnected should return false when no nodes`() = runTest {
        // Given
        val capabilityInfo = mockk<CapabilityInfo> {
            every { nodes } returns emptySet()
        }
        every {
            capabilityClient.getCapability(any(), any())
        } returns Tasks.forResult(capabilityInfo)

        // When
        val result = repository.isPhoneConnected()

        // Then
        assertFalse(result)
    }
}
