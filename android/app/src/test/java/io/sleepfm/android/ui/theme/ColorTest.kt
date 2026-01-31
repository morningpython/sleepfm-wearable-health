package io.sleepfm.android.ui.theme

import org.junit.Assert.*
import org.junit.Test

class ColorTest {

    // ==========================================
    // Primary Colors Tests
    // ==========================================

    @Test
    fun `Purple80 is defined`() {
        assertNotNull(Purple80)
    }

    @Test
    fun `PurpleGrey80 is defined`() {
        assertNotNull(PurpleGrey80)
    }

    @Test
    fun `Pink80 is defined`() {
        assertNotNull(Pink80)
    }

    @Test
    fun `Purple40 is defined`() {
        assertNotNull(Purple40)
    }

    @Test
    fun `PurpleGrey40 is defined`() {
        assertNotNull(PurpleGrey40)
    }

    @Test
    fun `Pink40 is defined`() {
        assertNotNull(Pink40)
    }

    // ==========================================
    // Sleep Stage Colors Tests
    // ==========================================

    @Test
    fun `SleepWake is red color`() {
        val color = SleepWake
        // Extract red component (should be high)
        assertTrue(color.red > 0.5f)
    }

    @Test
    fun `SleepLight is teal color`() {
        val color = SleepLight
        // Teal has high green and blue
        assertTrue(color.green > 0.5f || color.blue > 0.5f)
    }

    @Test
    fun `SleepDeep is blue color`() {
        val color = SleepDeep
        // Blue should be prominent
        assertTrue(color.blue > 0.5f)
    }

    @Test
    fun `SleepREM is green color`() {
        val color = SleepREM
        // Green should be prominent
        assertTrue(color.green > 0.5f)
    }

    @Test
    fun `all sleep stage colors are distinct`() {
        val colors = listOf(SleepWake, SleepLight, SleepDeep, SleepREM)
        val uniqueColors = colors.toSet()
        
        assertEquals(4, uniqueColors.size)
    }

    // ==========================================
    // Risk Level Colors Tests
    // ==========================================

    @Test
    fun `RiskLow is green`() {
        val color = RiskLow
        assertTrue(color.green > color.red && color.green > color.blue)
    }

    @Test
    fun `RiskModerate is orange`() {
        val color = RiskModerate
        // Orange has high red and moderate green
        assertTrue(color.red > 0.8f)
        assertTrue(color.green > 0.4f)
    }

    @Test
    fun `RiskHigh is red`() {
        val color = RiskHigh
        assertTrue(color.red > color.green && color.red > color.blue)
    }

    @Test
    fun `risk colors are distinct from each other`() {
        assertNotEquals(RiskLow, RiskModerate)
        assertNotEquals(RiskModerate, RiskHigh)
        assertNotEquals(RiskLow, RiskHigh)
    }

    // ==========================================
    // Chart Colors Tests
    // ==========================================

    @Test
    fun `ChartPrimary is defined`() {
        assertNotNull(ChartPrimary)
    }

    @Test
    fun `ChartSecondary is defined`() {
        assertNotNull(ChartSecondary)
    }

    @Test
    fun `ChartBackground is light color`() {
        val color = ChartBackground
        // Should be a light gray
        assertTrue(color.red > 0.9f && color.green > 0.9f && color.blue > 0.9f)
    }

    @Test
    fun `chart colors are distinct`() {
        assertNotEquals(ChartPrimary, ChartSecondary)
        assertNotEquals(ChartPrimary, ChartBackground)
    }

    // ==========================================
    // Background Colors Tests
    // ==========================================

    @Test
    fun `BackgroundLight is very light`() {
        val color = BackgroundLight
        // Should be close to white
        assertTrue(color.red > 0.95f && color.green > 0.95f && color.blue > 0.95f)
    }

    @Test
    fun `BackgroundDark is very dark`() {
        val color = BackgroundDark
        // Should be close to black
        assertTrue(color.red < 0.1f && color.green < 0.1f && color.blue < 0.1f)
    }

    @Test
    fun `SurfaceLight is white`() {
        val color = SurfaceLight
        assertEquals(1f, color.red, 0.001f)
        assertEquals(1f, color.green, 0.001f)
        assertEquals(1f, color.blue, 0.001f)
    }

    @Test
    fun `SurfaceDark is dark gray`() {
        val color = SurfaceDark
        assertTrue(color.red < 0.2f && color.green < 0.2f && color.blue < 0.2f)
    }

    // ==========================================
    // Text Colors Tests
    // ==========================================

    @Test
    fun `TextPrimaryLight is dark`() {
        val color = TextPrimaryLight
        assertTrue(color.red < 0.2f && color.green < 0.2f && color.blue < 0.2f)
    }

    @Test
    fun `TextSecondaryLight is gray`() {
        val color = TextSecondaryLight
        // Should be medium gray
        assertTrue(color.red > 0.3f && color.red < 0.7f)
    }

    @Test
    fun `TextPrimaryDark is light`() {
        val color = TextPrimaryDark
        assertTrue(color.red > 0.8f && color.green > 0.8f && color.blue > 0.8f)
    }

    @Test
    fun `TextSecondaryDark is light gray`() {
        val color = TextSecondaryDark
        assertTrue(color.red > 0.6f && color.green > 0.6f && color.blue > 0.6f)
    }

    // ==========================================
    // Color Consistency Tests
    // ==========================================

    @Test
    fun `light and dark text colors contrast properly`() {
        // Primary light should be darker than primary dark
        assertTrue(TextPrimaryLight.red < TextPrimaryDark.red)
    }

    @Test
    fun `all colors have full alpha`() {
        val allColors = listOf(
            Purple80, PurpleGrey80, Pink80,
            Purple40, PurpleGrey40, Pink40,
            SleepWake, SleepLight, SleepDeep, SleepREM,
            RiskLow, RiskModerate, RiskHigh,
            ChartPrimary, ChartSecondary, ChartBackground,
            BackgroundLight, BackgroundDark,
            SurfaceLight, SurfaceDark,
            TextPrimaryLight, TextSecondaryLight,
            TextPrimaryDark, TextSecondaryDark
        )
        
        for (color in allColors) {
            assertEquals("Color should have full alpha", 1f, color.alpha, 0.001f)
        }
    }
}
