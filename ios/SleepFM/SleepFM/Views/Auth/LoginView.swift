//
//  LoginView.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// 로그인 화면
struct LoginView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var email = ""
    @State private var password = ""
    @State private var showSignUp = false
    @State private var showAlert = false
    @State private var alertMessage = ""
    
    private var isFormValid: Bool {
        !email.isEmpty && !password.isEmpty && email.contains("@")
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 배경
                Color.sleepBackground
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: SleepSpacing.xl) {
                        // 로고 및 타이틀
                        VStack(spacing: SleepSpacing.md) {
                            // 앱 로고
                            ZStack {
                                Circle()
                                    .fill(SleepGradients.primary)
                                    .frame(width: 100, height: 100)
                                    .blur(radius: 30)
                                    .opacity(0.5)
                                
                                Image(systemName: "moon.zzz.fill")
                                    .font(.system(size: 50))
                                    .foregroundStyle(SleepGradients.primary)
                            }
                            
                            Text("SleepFM")
                                .font(SleepTypography.largeTitle)
                                .foregroundColor(.sleepTextPrimary)
                            
                            Text("수면 건강의 새로운 기준")
                                .font(SleepTypography.subheadline)
                                .foregroundColor(.sleepTextSecondary)
                        }
                        .padding(.top, SleepSpacing.xxl)
                        
                        // 로그인 폼
                        VStack(spacing: SleepSpacing.lg) {
                            // 이메일 입력
                            VStack(alignment: .leading, spacing: SleepSpacing.xs) {
                                Text("이메일")
                                    .font(SleepTypography.caption1)
                                    .foregroundColor(.sleepTextSecondary)
                                
                                TextField("", text: $email)
                                    .placeholder(when: email.isEmpty) {
                                        Text("이메일을 입력하세요")
                                            .foregroundColor(.sleepTextDisabled)
                                    }
                                    .keyboardType(.emailAddress)
                                    .textContentType(.emailAddress)
                                    .autocapitalization(.none)
                                    .foregroundColor(.sleepTextPrimary)
                                    .padding()
                                    .background(Color.sleepSurface)
                                    .cornerRadius(SleepCornerRadius.medium)
                            }
                            
                            // 비밀번호 입력
                            VStack(alignment: .leading, spacing: SleepSpacing.xs) {
                                Text("비밀번호")
                                    .font(SleepTypography.caption1)
                                    .foregroundColor(.sleepTextSecondary)
                                
                                SecureField("", text: $password)
                                    .placeholder(when: password.isEmpty) {
                                        Text("비밀번호를 입력하세요")
                                            .foregroundColor(.sleepTextDisabled)
                                    }
                                    .textContentType(.password)
                                    .foregroundColor(.sleepTextPrimary)
                                    .padding()
                                    .background(Color.sleepSurface)
                                    .cornerRadius(SleepCornerRadius.medium)
                            }
                            
                            // 비밀번호 찾기
                            HStack {
                                Spacer()
                                Button("비밀번호를 잊으셨나요?") {
                                    // TODO: 비밀번호 재설정
                                }
                                .font(SleepTypography.caption1)
                                .foregroundColor(.sleepPrimary)
                            }
                        }
                        .padding(.horizontal, SleepSpacing.lg)
                        
                        // 로그인 버튼
                        VStack(spacing: SleepSpacing.md) {
                            Button("로그인") {
                                Task {
                                    await login()
                                }
                            }
                            .buttonStyle(PrimaryButtonStyle(isEnabled: isFormValid))
                            .disabled(!isFormValid || authManager.isLoading)
                            
                            // 로딩 인디케이터
                            if authManager.isLoading {
                                ProgressView()
                                    .tint(.sleepPrimary)
                            }
                        }
                        .padding(.horizontal, SleepSpacing.lg)
                        
                        // 소셜 로그인 (향후 구현)
                        VStack(spacing: SleepSpacing.md) {
                            HStack {
                                Rectangle()
                                    .fill(Color.sleepTextDisabled.opacity(0.3))
                                    .frame(height: 1)
                                
                                Text("또는")
                                    .font(SleepTypography.caption1)
                                    .foregroundColor(.sleepTextDisabled)
                                
                                Rectangle()
                                    .fill(Color.sleepTextDisabled.opacity(0.3))
                                    .frame(height: 1)
                            }
                            
                            // Apple 로그인 버튼 (향후 구현)
                            Button {
                                // TODO: Sign in with Apple
                            } label: {
                                HStack(spacing: SleepSpacing.sm) {
                                    Image(systemName: "apple.logo")
                                    Text("Apple로 계속하기")
                                }
                                .font(SleepTypography.headline)
                                .foregroundColor(.sleepTextPrimary)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, SleepSpacing.md)
                                .background(Color.sleepSurface)
                                .cornerRadius(SleepCornerRadius.medium)
                            }
                        }
                        .padding(.horizontal, SleepSpacing.lg)
                        .padding(.top, SleepSpacing.md)
                        
                        // 회원가입 링크
                        HStack(spacing: SleepSpacing.xs) {
                            Text("계정이 없으신가요?")
                                .font(SleepTypography.subheadline)
                                .foregroundColor(.sleepTextSecondary)
                            
                            Button("회원가입") {
                                showSignUp = true
                            }
                            .font(SleepTypography.subheadline.bold())
                            .foregroundColor(.sleepPrimary)
                        }
                        .padding(.top, SleepSpacing.lg)
                        .padding(.bottom, SleepSpacing.xxl)
                    }
                }
            }
            .navigationDestination(isPresented: $showSignUp) {
                SignUpView()
            }
            .alert("로그인 오류", isPresented: $showAlert) {
                Button("확인", role: .cancel) {}
            } message: {
                Text(alertMessage)
            }
        }
    }
    
    // MARK: - Actions
    
    private func login() async {
        do {
            try await authManager.login(email: email, password: password)
        } catch {
            alertMessage = error.localizedDescription
            showAlert = true
        }
    }
}

// MARK: - Placeholder Extension

extension View {
    func placeholder<Content: View>(
        when shouldShow: Bool,
        alignment: Alignment = .leading,
        @ViewBuilder placeholder: () -> Content
    ) -> some View {
        ZStack(alignment: alignment) {
            placeholder().opacity(shouldShow ? 1 : 0)
            self
        }
    }
}

// MARK: - Preview

#Preview {
    LoginView()
        .environmentObject(AuthManager())
}
