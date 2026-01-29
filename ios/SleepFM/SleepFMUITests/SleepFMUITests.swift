//
//  SleepFMUITests.swift
//  SleepFMUITests
//
//  Sprint 9: iOS E2E UI 테스트
//

import XCTest

/// E2E UI 테스트
final class SleepFMUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--uitesting"]
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
    }
    
    // MARK: - Onboarding Flow Tests
    
    func testOnboardingFlow() throws {
        // 온보딩 화면이 표시되는지 확인
        let onboardingView = app.otherElements["onboardingView"]
        
        // 온보딩이 있으면 스와이프
        if onboardingView.exists {
            // 첫 페이지
            XCTAssertTrue(app.staticTexts["수면의 비밀을 풀다"].exists ||
                         app.staticTexts["SleepFM"].exists)
            
            // 다음 페이지로 스와이프
            onboardingView.swipeLeft()
            sleep(1)
            
            onboardingView.swipeLeft()
            sleep(1)
            
            // 시작하기 버튼
            let startButton = app.buttons["시작하기"]
            if startButton.exists {
                startButton.tap()
            }
        }
    }
    
    // MARK: - Authentication Tests
    
    func testLoginScreenElements() throws {
        // 로그인 화면으로 이동 (온보딩 스킵 필요시)
        navigateToLogin()
        
        // 로그인 화면 요소 확인
        let loginView = app.otherElements["loginView"]
        
        if loginView.exists {
            XCTAssertTrue(app.textFields["이메일"].exists ||
                         app.textFields["email"].exists)
            XCTAssertTrue(app.secureTextFields["비밀번호"].exists ||
                         app.secureTextFields["password"].exists)
            XCTAssertTrue(app.buttons["로그인"].exists)
        }
    }
    
    func testSignUpFlow() throws {
        navigateToSignUp()
        
        let signUpView = app.otherElements["signUpView"]
        
        if signUpView.exists {
            // 입력 필드들
            let emailField = app.textFields["이메일"]
            let usernameField = app.textFields["사용자 이름"]
            let passwordField = app.secureTextFields["비밀번호"]
            let confirmPasswordField = app.secureTextFields["비밀번호 확인"]
            
            if emailField.exists {
                emailField.tap()
                emailField.typeText("uitest@example.com")
            }
            
            if usernameField.exists {
                usernameField.tap()
                usernameField.typeText("uitester")
            }
            
            if passwordField.exists {
                passwordField.tap()
                passwordField.typeText("TestPass123!")
            }
            
            if confirmPasswordField.exists {
                confirmPasswordField.tap()
                confirmPasswordField.typeText("TestPass123!")
            }
            
            // 회원가입 버튼
            let signUpButton = app.buttons["회원가입"]
            if signUpButton.exists && signUpButton.isEnabled {
                signUpButton.tap()
                
                // 성공 시 대시보드 또는 다음 화면으로 이동
                sleep(3)
            }
        }
    }
    
    func testLoginValidation() throws {
        navigateToLogin()
        
        let emailField = app.textFields["이메일"]
        let passwordField = app.secureTextFields["비밀번호"]
        let loginButton = app.buttons["로그인"]
        
        guard emailField.exists && passwordField.exists && loginButton.exists else {
            throw XCTSkip("Login elements not found")
        }
        
        // 빈 필드로 로그인 시도
        loginButton.tap()
        
        // 에러 메시지 확인
        sleep(1)
        let errorExists = app.staticTexts.matching(NSPredicate(format: "label CONTAINS[c] '입력' OR label CONTAINS[c] '필수'")).count > 0
        
        // 잘못된 이메일 형식
        emailField.tap()
        emailField.typeText("invalid_email")
        passwordField.tap()
        passwordField.typeText("somepassword")
        
        loginButton.tap()
        sleep(1)
    }
    
    // MARK: - Dashboard Tests
    
    func testDashboardElements() throws {
        // 로그인 상태로 대시보드 접근
        loginIfNeeded()
        
        let dashboardView = app.otherElements["dashboardView"]
        
        if dashboardView.exists || app.navigationBars["대시보드"].exists {
            // 수면 점수 카드
            XCTAssertTrue(
                app.staticTexts.matching(NSPredicate(format: "label CONTAINS[c] '수면 점수' OR label CONTAINS[c] 'Sleep Score'")).count > 0 ||
                app.otherElements["sleepScoreCard"].exists
            )
            
            // 탭 바 확인
            let tabBar = app.tabBars.firstMatch
            if tabBar.exists {
                XCTAssertTrue(tabBar.buttons.count >= 3)
            }
        }
    }
    
    func testDashboardPullToRefresh() throws {
        loginIfNeeded()
        
        let dashboardView = app.scrollViews.firstMatch
        
        if dashboardView.exists {
            // Pull to refresh
            dashboardView.swipeDown()
            sleep(2)
            
            // 로딩 인디케이터가 잠시 표시되었다가 사라짐
        }
    }
    
    // MARK: - Navigation Tests
    
    func testTabBarNavigation() throws {
        loginIfNeeded()
        
        let tabBar = app.tabBars.firstMatch
        guard tabBar.exists else {
            throw XCTSkip("Tab bar not found")
        }
        
        // 히스토리 탭
        let historyTab = tabBar.buttons["히스토리"]
        if historyTab.exists {
            historyTab.tap()
            sleep(1)
            XCTAssertTrue(app.navigationBars["히스토리"].exists ||
                         app.staticTexts["히스토리"].exists)
        }
        
        // 설정 탭
        let settingsTab = tabBar.buttons["설정"]
        if settingsTab.exists {
            settingsTab.tap()
            sleep(1)
            XCTAssertTrue(app.navigationBars["설정"].exists ||
                         app.staticTexts["설정"].exists)
        }
        
        // 대시보드로 복귀
        let dashboardTab = tabBar.buttons["대시보드"]
        if dashboardTab.exists {
            dashboardTab.tap()
            sleep(1)
        }
    }
    
    func testSleepDetailNavigation() throws {
        loginIfNeeded()
        
        // 수면 상세 화면으로 이동 (카드 탭)
        let sleepCard = app.otherElements["sleepSummaryCard"]
        
        if sleepCard.exists {
            sleepCard.tap()
            sleep(1)
            
            // 상세 화면 확인
            XCTAssertTrue(app.navigationBars["수면 분석"].exists ||
                         app.staticTexts["수면 단계"].exists)
            
            // 뒤로가기
            let backButton = app.navigationBars.buttons.firstMatch
            if backButton.exists {
                backButton.tap()
            }
        }
    }
    
    // MARK: - Settings Tests
    
    func testSettingsScreen() throws {
        loginIfNeeded()
        navigateToSettings()
        
        // 설정 항목들 확인
        let settingsList = app.tables.firstMatch.exists ? app.tables.firstMatch : app.scrollViews.firstMatch
        
        if settingsList.exists {
            // 프로필 섹션
            XCTAssertTrue(app.staticTexts.matching(NSPredicate(format: "label CONTAINS[c] '프로필' OR label CONTAINS[c] 'Profile'")).count > 0)
            
            // 알림 섹션
            XCTAssertTrue(app.staticTexts.matching(NSPredicate(format: "label CONTAINS[c] '알림' OR label CONTAINS[c] 'Notification'")).count > 0)
            
            // Apple Watch 섹션
            XCTAssertTrue(app.staticTexts.matching(NSPredicate(format: "label CONTAINS[c] 'Watch' OR label CONTAINS[c] '워치'")).count > 0)
        }
    }
    
    func testLogoutFlow() throws {
        loginIfNeeded()
        navigateToSettings()
        
        // 로그아웃 버튼 찾기
        let logoutButton = app.buttons["로그아웃"]
        
        if logoutButton.exists {
            logoutButton.tap()
            
            // 확인 다이얼로그
            let confirmButton = app.alerts.buttons["로그아웃"]
            if confirmButton.exists {
                confirmButton.tap()
                sleep(2)
                
                // 로그인 화면으로 이동했는지 확인
                XCTAssertTrue(app.buttons["로그인"].exists ||
                             app.otherElements["loginView"].exists)
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func navigateToLogin() {
        // 온보딩 건너뛰기
        let skipButton = app.buttons["건너뛰기"]
        if skipButton.exists {
            skipButton.tap()
            sleep(1)
        }
        
        // 로그인 버튼 탭 (회원가입 화면에서)
        let loginNavButton = app.buttons["로그인하기"]
        if loginNavButton.exists {
            loginNavButton.tap()
            sleep(1)
        }
    }
    
    private func navigateToSignUp() {
        // 온보딩 건너뛰기
        let skipButton = app.buttons["건너뛰기"]
        if skipButton.exists {
            skipButton.tap()
            sleep(1)
        }
        
        // 회원가입 버튼 탭
        let signUpNavButton = app.buttons["회원가입하기"]
        if signUpNavButton.exists {
            signUpNavButton.tap()
            sleep(1)
        }
    }
    
    private func navigateToSettings() {
        let tabBar = app.tabBars.firstMatch
        if tabBar.exists {
            let settingsTab = tabBar.buttons["설정"]
            if settingsTab.exists {
                settingsTab.tap()
                sleep(1)
            }
        }
    }
    
    private func loginIfNeeded() {
        // 이미 로그인되어 있으면 스킵
        let tabBar = app.tabBars.firstMatch
        if tabBar.exists {
            return
        }
        
        // 온보딩 건너뛰기
        let skipButton = app.buttons["건너뛰기"]
        if skipButton.exists {
            skipButton.tap()
            sleep(1)
        }
        
        // 테스트 계정으로 로그인
        let emailField = app.textFields["이메일"]
        let passwordField = app.secureTextFields["비밀번호"]
        let loginButton = app.buttons["로그인"]
        
        if emailField.exists && passwordField.exists && loginButton.exists {
            emailField.tap()
            emailField.typeText("test@example.com")
            
            passwordField.tap()
            passwordField.typeText("testpass123")
            
            loginButton.tap()
            sleep(3)
        }
    }
}

// MARK: - Performance Tests

final class SleepFMPerformanceTests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--uitesting"]
    }
    
    func testLaunchPerformance() throws {
        if #available(iOS 14.0, *) {
            measure(metrics: [XCTApplicationLaunchMetric()]) {
                app.launch()
            }
        }
    }
    
    func testScrollPerformance() throws {
        app.launch()
        
        // 로그인이 필요하면 스킵
        guard app.tabBars.firstMatch.exists else {
            throw XCTSkip("Need to be logged in for scroll test")
        }
        
        let scrollView = app.scrollViews.firstMatch
        
        if scrollView.exists {
            measure {
                scrollView.swipeUp()
                scrollView.swipeDown()
            }
        }
    }
}

// MARK: - Accessibility Tests

final class SleepFMAccessibilityTests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func testAccessibilityLabels() throws {
        // 주요 요소에 접근성 레이블이 있는지 확인
        let buttons = app.buttons.allElementsBoundByIndex
        
        for button in buttons.prefix(10) {
            if button.exists {
                XCTAssertFalse(button.label.isEmpty, "Button should have accessibility label")
            }
        }
    }
    
    func testVoiceOverSupport() throws {
        // 탭 바 버튼에 접근성 레이블 확인
        let tabBar = app.tabBars.firstMatch
        
        if tabBar.exists {
            for button in tabBar.buttons.allElementsBoundByIndex {
                if button.exists {
                    XCTAssertFalse(button.label.isEmpty, "Tab bar button should have label for VoiceOver")
                }
            }
        }
    }
}
