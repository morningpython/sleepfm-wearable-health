//
//  SettingsView.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// 설정 화면
struct SettingsView: View {
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var healthKitManager: HealthKitManager
    @State private var showLogoutAlert = false
    @State private var notificationsEnabled = true
    @State private var sleepReminder = true
    @State private var wakeAlarm = true
    @State private var darkMode = true
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 배경
                Color.sleepBackground
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: SleepSpacing.lg) {
                        // 프로필 섹션
                        profileSection
                        
                        // 연동 섹션
                        connectionSection
                        
                        // 알림 섹션
                        notificationSection
                        
                        // 앱 섹션
                        appSection
                        
                        // 계정 섹션
                        accountSection
                        
                        // 앱 정보
                        appInfoSection
                    }
                    .padding(.horizontal, SleepSpacing.lg)
                    .padding(.bottom, SleepSpacing.xxl)
                }
            }
            .navigationTitle("설정")
            .navigationBarTitleDisplayMode(.large)
            .toolbarBackground(Color.sleepBackground, for: .navigationBar)
        }
        .alert("로그아웃", isPresented: $showLogoutAlert) {
            Button("취소", role: .cancel) {}
            Button("로그아웃", role: .destructive) {
                authManager.logout()
            }
        } message: {
            Text("정말 로그아웃하시겠습니까?")
        }
    }
    
    // MARK: - Profile Section
    
    private var profileSection: some View {
        NavigationLink {
            ProfileEditView()
        } label: {
            HStack(spacing: SleepSpacing.md) {
                // 프로필 이미지
                ZStack {
                    Circle()
                        .fill(SleepGradients.primary)
                        .frame(width: 64, height: 64)
                    
                    Text(profileInitial)
                        .font(SleepTypography.title2)
                        .foregroundColor(.white)
                }
                
                // 사용자 정보
                VStack(alignment: .leading, spacing: SleepSpacing.xxs) {
                    Text(authManager.currentUser?.fullName ?? authManager.currentUser?.username ?? "사용자")
                        .font(SleepTypography.headline)
                        .foregroundColor(.sleepTextPrimary)
                    
                    Text(authManager.currentUser?.email ?? "")
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepTextSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.sleepTextDisabled)
            }
            .sleepCard()
        }
    }
    
    private var profileInitial: String {
        let name = authManager.currentUser?.fullName ?? authManager.currentUser?.username ?? "U"
        return String(name.prefix(1)).uppercased()
    }
    
    // MARK: - Connection Section
    
    private var connectionSection: some View {
        SettingsSection(title: "연동") {
            SettingsRow(
                icon: "heart.fill",
                iconColor: .sleepDanger,
                title: "Apple Health",
                subtitle: healthKitManager.isAuthorized ? "연동됨" : "연동 안됨"
            ) {
                Toggle("", isOn: .constant(healthKitManager.isAuthorized))
                    .tint(.sleepPrimary)
                    .disabled(!healthKitManager.isAuthorized)
                    .onTapGesture {
                        if !healthKitManager.isAuthorized {
                            Task {
                                await healthKitManager.requestAuthorization()
                            }
                        }
                    }
            }
            
            SettingsRow(
                icon: "applewatch",
                iconColor: .sleepInfo,
                title: "Apple Watch",
                subtitle: "연동 안됨"
            ) {
                Image(systemName: "chevron.right")
                    .foregroundColor(.sleepTextDisabled)
            }
        }
    }
    
    // MARK: - Notification Section
    
    private var notificationSection: some View {
        SettingsSection(title: "알림") {
            SettingsRow(
                icon: "bell.fill",
                iconColor: .sleepWarning,
                title: "알림",
                subtitle: notificationsEnabled ? "켜짐" : "꺼짐"
            ) {
                Toggle("", isOn: $notificationsEnabled)
                    .tint(.sleepPrimary)
            }
            
            if notificationsEnabled {
                SettingsRow(
                    icon: "moon.fill",
                    iconColor: .sleepPrimary,
                    title: "취침 알림",
                    subtitle: "22:30"
                ) {
                    Toggle("", isOn: $sleepReminder)
                        .tint(.sleepPrimary)
                }
                
                SettingsRow(
                    icon: "alarm.fill",
                    iconColor: .sleepSecondary,
                    title: "기상 알람",
                    subtitle: "07:00"
                ) {
                    Toggle("", isOn: $wakeAlarm)
                        .tint(.sleepPrimary)
                }
            }
        }
    }
    
    // MARK: - App Section
    
    private var appSection: some View {
        SettingsSection(title: "앱") {
            SettingsRow(
                icon: "moon.circle.fill",
                iconColor: .sleepPrimary,
                title: "다크 모드",
                subtitle: nil
            ) {
                Toggle("", isOn: $darkMode)
                    .tint(.sleepPrimary)
            }
            
            NavigationLink {
                // TODO: 언어 설정
            } label: {
                SettingsRow(
                    icon: "globe",
                    iconColor: .sleepInfo,
                    title: "언어",
                    subtitle: "한국어"
                ) {
                    Image(systemName: "chevron.right")
                        .foregroundColor(.sleepTextDisabled)
                }
            }
            
            NavigationLink {
                // TODO: 단위 설정
            } label: {
                SettingsRow(
                    icon: "ruler",
                    iconColor: .sleepSuccess,
                    title: "단위",
                    subtitle: "미터법"
                ) {
                    Image(systemName: "chevron.right")
                        .foregroundColor(.sleepTextDisabled)
                }
            }
        }
    }
    
    // MARK: - Account Section
    
    private var accountSection: some View {
        SettingsSection(title: "계정") {
            NavigationLink {
                // TODO: 비밀번호 변경
            } label: {
                SettingsRow(
                    icon: "lock.fill",
                    iconColor: .sleepTextSecondary,
                    title: "비밀번호 변경",
                    subtitle: nil
                ) {
                    Image(systemName: "chevron.right")
                        .foregroundColor(.sleepTextDisabled)
                }
            }
            
            NavigationLink {
                // TODO: 데이터 내보내기
            } label: {
                SettingsRow(
                    icon: "square.and.arrow.up",
                    iconColor: .sleepInfo,
                    title: "데이터 내보내기",
                    subtitle: nil
                ) {
                    Image(systemName: "chevron.right")
                        .foregroundColor(.sleepTextDisabled)
                }
            }
            
            Button {
                showLogoutAlert = true
            } label: {
                SettingsRow(
                    icon: "rectangle.portrait.and.arrow.right",
                    iconColor: .sleepWarning,
                    title: "로그아웃",
                    subtitle: nil
                ) {
                    EmptyView()
                }
            }
            
            NavigationLink {
                // TODO: 계정 삭제
            } label: {
                SettingsRow(
                    icon: "trash.fill",
                    iconColor: .sleepDanger,
                    title: "계정 삭제",
                    subtitle: nil
                ) {
                    Image(systemName: "chevron.right")
                        .foregroundColor(.sleepTextDisabled)
                }
            }
        }
    }
    
    // MARK: - App Info Section
    
    private var appInfoSection: some View {
        SettingsSection(title: "정보") {
            NavigationLink {
                // TODO: 이용약관
            } label: {
                SettingsRow(
                    icon: "doc.text.fill",
                    iconColor: .sleepTextSecondary,
                    title: "이용약관",
                    subtitle: nil
                ) {
                    Image(systemName: "chevron.right")
                        .foregroundColor(.sleepTextDisabled)
                }
            }
            
            NavigationLink {
                // TODO: 개인정보처리방침
            } label: {
                SettingsRow(
                    icon: "hand.raised.fill",
                    iconColor: .sleepTextSecondary,
                    title: "개인정보처리방침",
                    subtitle: nil
                ) {
                    Image(systemName: "chevron.right")
                        .foregroundColor(.sleepTextDisabled)
                }
            }
            
            SettingsRow(
                icon: "info.circle.fill",
                iconColor: .sleepTextSecondary,
                title: "버전",
                subtitle: nil
            ) {
                Text("1.0.0")
                    .font(SleepTypography.subheadline)
                    .foregroundColor(.sleepTextDisabled)
            }
        }
    }
}

// MARK: - Supporting Views

struct SettingsSection<Content: View>: View {
    let title: String
    @ViewBuilder let content: Content
    
    var body: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.sm) {
            Text(title)
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
                .textCase(.uppercase)
            
            VStack(spacing: 1) {
                content
            }
            .background(Color.sleepCardBackground)
            .cornerRadius(SleepCornerRadius.medium)
        }
    }
}

struct SettingsRow<Content: View>: View {
    let icon: String
    let iconColor: Color
    let title: String
    let subtitle: String?
    @ViewBuilder let accessory: Content
    
    var body: some View {
        HStack(spacing: SleepSpacing.md) {
            // 아이콘
            ZStack {
                RoundedRectangle(cornerRadius: 8)
                    .fill(iconColor.opacity(0.2))
                    .frame(width: 32, height: 32)
                
                Image(systemName: icon)
                    .font(.system(size: 14))
                    .foregroundColor(iconColor)
            }
            
            // 텍스트
            VStack(alignment: .leading, spacing: SleepSpacing.xxs) {
                Text(title)
                    .font(SleepTypography.body)
                    .foregroundColor(.sleepTextPrimary)
                
                if let subtitle = subtitle {
                    Text(subtitle)
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepTextSecondary)
                }
            }
            
            Spacer()
            
            // 액세서리
            accessory
        }
        .padding(SleepSpacing.md)
        .background(Color.sleepCardBackground)
    }
}

// MARK: - Profile Edit View

struct ProfileEditView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var authManager: AuthManager
    @State private var fullName = ""
    @State private var username = ""
    @State private var isSaving = false
    
    var body: some View {
        ZStack {
            Color.sleepBackground
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: SleepSpacing.lg) {
                    // 프로필 이미지
                    ZStack {
                        Circle()
                            .fill(SleepGradients.primary)
                            .frame(width: 100, height: 100)
                        
                        Text(String(fullName.prefix(1)).uppercased())
                            .font(SleepTypography.largeTitle)
                            .foregroundColor(.white)
                        
                        // 편집 버튼
                        Circle()
                            .fill(Color.sleepPrimary)
                            .frame(width: 32, height: 32)
                            .overlay(
                                Image(systemName: "camera.fill")
                                    .font(.system(size: 14))
                                    .foregroundColor(.white)
                            )
                            .offset(x: 35, y: 35)
                    }
                    .padding(.top, SleepSpacing.xl)
                    
                    // 입력 폼
                    VStack(spacing: SleepSpacing.md) {
                        FormField(
                            title: "이름",
                            placeholder: "이름을 입력하세요",
                            text: $fullName
                        )
                        
                        FormField(
                            title: "사용자명",
                            placeholder: "사용자명을 입력하세요",
                            text: $username
                        )
                        
                        // 이메일 (읽기 전용)
                        VStack(alignment: .leading, spacing: SleepSpacing.xs) {
                            Text("이메일")
                                .font(SleepTypography.caption1)
                                .foregroundColor(.sleepTextSecondary)
                            
                            Text(authManager.currentUser?.email ?? "")
                                .font(SleepTypography.body)
                                .foregroundColor(.sleepTextDisabled)
                                .padding()
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.sleepSurface.opacity(0.5))
                                .cornerRadius(SleepCornerRadius.medium)
                        }
                    }
                    .padding(.horizontal, SleepSpacing.lg)
                    
                    // 저장 버튼
                    Button("저장") {
                        saveProfile()
                    }
                    .buttonStyle(PrimaryButtonStyle(isEnabled: !fullName.isEmpty))
                    .disabled(fullName.isEmpty || isSaving)
                    .padding(.horizontal, SleepSpacing.lg)
                    .padding(.top, SleepSpacing.lg)
                }
            }
        }
        .navigationTitle("프로필 편집")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            fullName = authManager.currentUser?.fullName ?? ""
            username = authManager.currentUser?.username ?? ""
        }
    }
    
    private func saveProfile() {
        isSaving = true
        // TODO: API 호출
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            isSaving = false
            dismiss()
        }
    }
}

// MARK: - Preview

#Preview {
    SettingsView()
        .environmentObject(AuthManager())
        .environmentObject(HealthKitManager())
}
