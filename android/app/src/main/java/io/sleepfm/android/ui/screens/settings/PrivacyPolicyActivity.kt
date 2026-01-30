package io.sleepfm.android.ui.screens.settings

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.sleepfm.android.ui.theme.SleepFMTheme

/**
 * Privacy Policy Activity for Health Connect
 * Required by Health Connect guidelines
 */
class PrivacyPolicyActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SleepFMTheme {
                PrivacyPolicyScreen(
                    onBackClick = { finish() }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun PrivacyPolicyScreen(
    onBackClick: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("개인정보 처리방침") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "뒤로가기")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            Text(
                text = "SleepFM 개인정보 처리방침",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            PolicySection(
                title = "1. 수집하는 개인정보",
                content = """
                    SleepFM은 다음과 같은 건강 정보를 수집합니다:
                    
                    • 수면 데이터: 수면 시작/종료 시간, 수면 단계
                    • 심박수 데이터: 수면 중 심박수 측정값
                    • 산소포화도 데이터: 수면 중 SpO2 측정값
                    • 걸음 수 데이터: 일일 활동량
                    
                    이 데이터는 Google Health Connect를 통해 수집됩니다.
                """.trimIndent()
            )
            
            PolicySection(
                title = "2. 개인정보의 이용 목적",
                content = """
                    수집된 정보는 다음 목적으로 사용됩니다:
                    
                    • 수면 품질 분석 및 수면 단계 예측
                    • AI 기반 건강 위험도 예측
                    • 개인화된 수면 개선 조언 제공
                    • 수면 기록 및 트렌드 분석
                """.trimIndent()
            )
            
            PolicySection(
                title = "3. 개인정보의 보관 및 보호",
                content = """
                    • 건강 데이터는 암호화되어 안전하게 저장됩니다.
                    • 데이터는 사용자의 기기와 보안된 서버에 저장됩니다.
                    • 언제든지 앱에서 데이터를 삭제할 수 있습니다.
                """.trimIndent()
            )
            
            PolicySection(
                title = "4. 개인정보의 제3자 제공",
                content = """
                    SleepFM은 사용자의 동의 없이 개인 건강 정보를 제3자에게 제공하지 않습니다.
                    
                    단, 다음의 경우는 예외로 합니다:
                    • 법령에 의해 요구되는 경우
                    • 사용자가 명시적으로 동의한 경우
                """.trimIndent()
            )
            
            PolicySection(
                title = "5. 사용자의 권리",
                content = """
                    사용자는 다음과 같은 권리를 가집니다:
                    
                    • 수집된 데이터 열람 요청
                    • 데이터 수정 또는 삭제 요청
                    • Health Connect 권한 철회
                    • 서비스 이용 중단
                """.trimIndent()
            )
            
            PolicySection(
                title = "6. 문의",
                content = """
                    개인정보 처리방침에 대한 문의사항이 있으시면 다음으로 연락해 주세요:
                    
                    이메일: privacy@sleepfm.io
                """.trimIndent()
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            Text(
                text = "최종 업데이트: 2024년 1월",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
private fun PolicySection(
    title: String,
    content: String
) {
    Column(
        modifier = Modifier.padding(vertical = 8.dp)
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = content,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f),
            lineHeight = MaterialTheme.typography.bodyMedium.lineHeight * 1.5
        )
    }
}
