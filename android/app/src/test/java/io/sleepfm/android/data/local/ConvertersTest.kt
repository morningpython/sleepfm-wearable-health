package io.sleepfm.android.data.local

import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.util.Date

class ConvertersTest {

    private lateinit var converters: Converters

    @Before
    fun setup() {
        converters = Converters()
    }

    @Test
    fun `fromTimestamp converts Long to Date`() {
        // Given
        val timestamp = 1609459200000L // 2021-01-01 00:00:00 UTC

        // When
        val result = converters.fromTimestamp(timestamp)

        // Then
        assertNotNull(result)
        assertEquals(timestamp, result?.time)
    }

    @Test
    fun `fromTimestamp returns null for null input`() {
        // When
        val result = converters.fromTimestamp(null)

        // Then
        assertNull(result)
    }

    @Test
    fun `dateToTimestamp converts Date to Long`() {
        // Given
        val date = Date(1609459200000L)

        // When
        val result = converters.dateToTimestamp(date)

        // Then
        assertEquals(1609459200000L, result)
    }

    @Test
    fun `dateToTimestamp returns null for null input`() {
        // When
        val result = converters.dateToTimestamp(null)

        // Then
        assertNull(result)
    }

    @Test
    fun `round trip conversion preserves value`() {
        // Given
        val originalTimestamp = System.currentTimeMillis()

        // When
        val date = converters.fromTimestamp(originalTimestamp)
        val resultTimestamp = converters.dateToTimestamp(date)

        // Then
        assertEquals(originalTimestamp, resultTimestamp)
    }

    @Test
    fun `fromTimestamp handles epoch time`() {
        // Given - Unix epoch
        val epochTimestamp = 0L

        // When
        val result = converters.fromTimestamp(epochTimestamp)

        // Then
        assertNotNull(result)
        assertEquals(0L, result?.time)
    }

    @Test
    fun `dateToTimestamp handles current time`() {
        // Given
        val now = Date()

        // When
        val result = converters.dateToTimestamp(now)

        // Then
        assertNotNull(result)
        assertTrue(result!! > 0)
    }

    @Test
    fun `fromTimestamp handles future dates`() {
        // Given - far future timestamp (year 2100)
        val futureTimestamp = 4102444800000L

        // When
        val result = converters.fromTimestamp(futureTimestamp)

        // Then
        assertNotNull(result)
        assertEquals(futureTimestamp, result?.time)
    }
}
