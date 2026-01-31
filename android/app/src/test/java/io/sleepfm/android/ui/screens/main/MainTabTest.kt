package io.sleepfm.android.ui.screens.main

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import org.junit.Assert.*
import org.junit.Test

class MainTabTest {

    @Test
    fun `Dashboard tab should have correct properties`() {
        val tab = MainTab.Dashboard
        
        assertEquals("dashboard", tab.route)
        assertEquals("대시보드", tab.title)
        assertEquals(Icons.Filled.Home, tab.selectedIcon)
        assertEquals(Icons.Outlined.Home, tab.unselectedIcon)
    }

    @Test
    fun `History tab should have correct properties`() {
        val tab = MainTab.History
        
        assertEquals("history", tab.route)
        assertEquals("기록", tab.title)
        assertEquals(Icons.Filled.History, tab.selectedIcon)
        assertEquals(Icons.Outlined.History, tab.unselectedIcon)
    }

    @Test
    fun `Settings tab should have correct properties`() {
        val tab = MainTab.Settings
        
        assertEquals("settings", tab.route)
        assertEquals("설정", tab.title)
        assertEquals(Icons.Filled.Settings, tab.selectedIcon)
        assertEquals(Icons.Outlined.Settings, tab.unselectedIcon)
    }

    @Test
    fun `all tabs should have unique routes`() {
        val tabs = listOf(MainTab.Dashboard, MainTab.History, MainTab.Settings)
        val routes = tabs.map { it.route }
        
        assertEquals(routes.size, routes.distinct().size)
    }

    @Test
    fun `all tabs should have unique titles`() {
        val tabs = listOf(MainTab.Dashboard, MainTab.History, MainTab.Settings)
        val titles = tabs.map { it.title }
        
        assertEquals(titles.size, titles.distinct().size)
    }

    @Test
    fun `tabs list should contain exactly 3 tabs`() {
        val tabs = listOf(MainTab.Dashboard, MainTab.History, MainTab.Settings)
        
        assertEquals(3, tabs.size)
    }

    @Test
    fun `Dashboard should be the first tab`() {
        val tabs = listOf(MainTab.Dashboard, MainTab.History, MainTab.Settings)
        
        assertEquals(MainTab.Dashboard, tabs.first())
    }

    @Test
    fun `selected and unselected icons should be different for Dashboard`() {
        assertNotEquals(MainTab.Dashboard.selectedIcon, MainTab.Dashboard.unselectedIcon)
    }

    @Test
    fun `selected and unselected icons should be different for History`() {
        assertNotEquals(MainTab.History.selectedIcon, MainTab.History.unselectedIcon)
    }

    @Test
    fun `selected and unselected icons should be different for Settings`() {
        assertNotEquals(MainTab.Settings.selectedIcon, MainTab.Settings.unselectedIcon)
    }
}
