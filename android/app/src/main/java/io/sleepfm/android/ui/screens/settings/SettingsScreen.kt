package io.sleepfm.android.ui.screens.settings

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onLogout: () -> Unit,
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var showLogoutDialog by remember { mutableStateOf(false) }
    
    LaunchedEffect(uiState.isLoggedOut) {
        if (uiState.isLoggedOut) {
            onLogout()
        }
    }
    
    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            title = { Text("로그아웃") },
            text = { Text("정말 로그아웃 하시겠습니까?") },
            confirmButton = {
                TextButton(
                    onClick = {
                        showLogoutDialog = false
                        viewModel.logout()
                    }
                ) {
                    Text("로그아웃")
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutDialog = false }) {
                    Text("취소")
                }
            }
        )
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("설정") }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
        ) {
            // User Profile Section
            uiState.user?.let { user ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.AccountCircle,
                            contentDescription = null,
                            modifier = Modifier.size(56.dp),
                            tint = MaterialTheme.colorScheme.primary
                        )
                        
                        Spacer(modifier = Modifier.width(16.dp))
                        
                        Column {
                            Text(
                                text = user.username,
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = user.email,
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                            )
                        }
                    }
                }
            }
            
            // Settings Sections
            SettingsSection(title = "앱 설정") {
                SettingsItem(
                    icon = Icons.Outlined.Notifications,
                    title = "알림 설정",
                    subtitle = "수면 알림 및 리마인더",
                    onClick = { /* Navigate to notification settings */ }
                )
                
                SettingsItem(
                    icon = Icons.Outlined.DarkMode,
                    title = "다크 모드",
                    subtitle = if (uiState.isDarkMode) "활성화됨" else "비활성화됨",
                    trailing = {
                        Switch(
                            checked = uiState.isDarkMode,
                            onCheckedChange = { viewModel.setDarkMode(it) }
                        )
                    },
                    onClick = { viewModel.setDarkMode(!uiState.isDarkMode) }
                )
            }
            
            SettingsSection(title = "Health Connect") {
                SettingsItem(
                    icon = Icons.Outlined.HealthAndSafety,
                    title = "Health Connect 연동",
                    subtitle = if (uiState.isHealthConnectConnected) "연동됨" else "연동 안됨",
                    onClick = { /* Open Health Connect settings */ }
                )
                
                SettingsItem(
                    icon = Icons.Outlined.Sync,
                    title = "데이터 동기화",
                    subtitle = "마지막 동기화: ${uiState.lastSyncTime}",
                    onClick = { viewModel.syncData() }
                )
            }
            
            SettingsSection(title = "계정") {
                SettingsItem(
                    icon = Icons.Outlined.Security,
                    title = "개인정보 처리방침",
                    onClick = { /* Open privacy policy */ }
                )
                
                SettingsItem(
                    icon = Icons.Outlined.Description,
                    title = "이용약관",
                    onClick = { /* Open terms of service */ }
                )
                
                SettingsItem(
                    icon = Icons.Outlined.Logout,
                    title = "로그아웃",
                    titleColor = MaterialTheme.colorScheme.error,
                    onClick = { showLogoutDialog = true }
                )
            }
            
            SettingsSection(title = "앱 정보") {
                SettingsItem(
                    icon = Icons.Outlined.Info,
                    title = "버전",
                    subtitle = "1.0.0",
                    onClick = { }
                )
            }
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
private fun SettingsSection(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Column(
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleSmall,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
        )
        content()
    }
}

@Composable
private fun SettingsItem(
    icon: ImageVector,
    title: String,
    subtitle: String? = null,
    titleColor: androidx.compose.ui.graphics.Color = MaterialTheme.colorScheme.onSurface,
    trailing: @Composable (() -> Unit)? = null,
    onClick: () -> Unit
) {
    ListItem(
        headlineContent = { 
            Text(
                text = title,
                color = titleColor
            ) 
        },
        supportingContent = subtitle?.let { 
            { 
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                ) 
            } 
        },
        leadingContent = {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = if (titleColor == MaterialTheme.colorScheme.error) 
                    titleColor 
                else 
                    MaterialTheme.colorScheme.onSurfaceVariant
            )
        },
        trailingContent = trailing ?: {
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        },
        modifier = Modifier.clickable(onClick = onClick)
    )
}
