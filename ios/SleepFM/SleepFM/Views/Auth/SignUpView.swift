//
//  SignUpView.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// 회원가입 화면
struct SignUpView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var authManager: AuthManager
    
    @State private var email = ""
    @State private var username = ""
    @State private var fullName = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var agreeToTerms = false
    @State private var showAlert = false
    @State private var alertTitle = ""
    @State private var alertMessage = ""
    
    private var isFormValid: Bool {
        !email.isEmpty &&
        email.contains("@") &&
        !username.isEmpty &&
        username.count >= 3 &&
        !password.isEmpty &&
        password.count >= 8 &&
        password == confirmPassword &&
        agreeToTerms
    }
    
    private var passwordStrength: PasswordStrength {
        PasswordStrength.evaluate(password)
    }
    
    var body: some View {
        ZStack {
            // 배경
            Color.sleepBackground
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: SleepSpacing.xl) {
                    // 헤더
                    VStack(spacing: SleepSpacing.sm) {
                        Text("회원가입")
                            .font(SleepTypography.title1)
                            .foregroundColor(.sleepTextPrimary)
                        
                        Text("SleepFM과 함께 건강한 수면을 시작하세요")
                            .font(SleepTypography.subheadline)
                            .foregroundColor(.sleepTextSecondary)
                    }
                    .padding(.top, SleepSpacing.lg)
                    
                    // 입력 폼
                    VStack(spacing: SleepSpacing.lg) {
                        // 이메일
                        FormField(
                            title: "이메일",
                            placeholder: "이메일을 입력하세요",
                            text: $email,
                            keyboardType: .emailAddress,
                            textContentType: .emailAddress,
                            error: email.isEmpty || email.contains("@") ? nil : "유효한 이메일을 입력하세요"
                        )
                        
                        // 사용자명
                        FormField(
                            title: "사용자명",
                            placeholder: "사용자명을 입력하세요",
                            text: $username,
                            textContentType: .username,
                            error: username.isEmpty || username.count >= 3 ? nil : "최소 3자 이상 입력하세요"
                        )
                        
                        // 이름 (선택)
                        FormField(
                            title: "이름 (선택)",
                            placeholder: "이름을 입력하세요",
                            text: $fullName,
                            textContentType: .name
                        )
                        
                        // 비밀번호
                        VStack(alignment: .leading, spacing: SleepSpacing.xs) {
                            SecureFormField(
                                title: "비밀번호",
                                placeholder: "비밀번호를 입력하세요",
                                text: $password,
                                textContentType: .newPassword
                            )
                            
                            // 비밀번호 강도 표시
                            if !password.isEmpty {
                                HStack(spacing: SleepSpacing.xs) {
                                    ForEach(0..<4) { index in
                                        Rectangle()
                                            .fill(index < passwordStrength.level ? passwordStrength.color : Color.sleepTextDisabled.opacity(0.3))
                                            .frame(height: 4)
                                            .cornerRadius(2)
                                    }
                                }
                                
                                Text(passwordStrength.description)
                                    .font(SleepTypography.caption2)
                                    .foregroundColor(passwordStrength.color)
                            }
                        }
                        
                        // 비밀번호 확인
                        SecureFormField(
                            title: "비밀번호 확인",
                            placeholder: "비밀번호를 다시 입력하세요",
                            text: $confirmPassword,
                            textContentType: .newPassword,
                            error: confirmPassword.isEmpty || password == confirmPassword ? nil : "비밀번호가 일치하지 않습니다"
                        )
                        
                        // 이용약관 동의
                        HStack(alignment: .top, spacing: SleepSpacing.sm) {
                            Button {
                                agreeToTerms.toggle()
                            } label: {
                                Image(systemName: agreeToTerms ? "checkmark.square.fill" : "square")
                                    .font(.title3)
                                    .foregroundColor(agreeToTerms ? .sleepPrimary : .sleepTextDisabled)
                            }
                            
                            VStack(alignment: .leading, spacing: SleepSpacing.xxs) {
                                HStack(spacing: SleepSpacing.xxs) {
                                    Text("이용약관")
                                        .foregroundColor(.sleepPrimary)
                                        .underline()
                                        .onTapGesture {
                                            // TODO: 이용약관 표시
                                        }
                                    
                                    Text("및")
                                        .foregroundColor(.sleepTextSecondary)
                                    
                                    Text("개인정보처리방침")
                                        .foregroundColor(.sleepPrimary)
                                        .underline()
                                        .onTapGesture {
                                            // TODO: 개인정보처리방침 표시
                                        }
                                    
                                    Text("에 동의합니다")
                                        .foregroundColor(.sleepTextSecondary)
                                }
                                .font(SleepTypography.caption1)
                            }
                            
                            Spacer()
                        }
                    }
                    .padding(.horizontal, SleepSpacing.lg)
                    
                    // 가입 버튼
                    VStack(spacing: SleepSpacing.md) {
                        Button("회원가입") {
                            Task {
                                await signUp()
                            }
                        }
                        .buttonStyle(PrimaryButtonStyle(isEnabled: isFormValid))
                        .disabled(!isFormValid || authManager.isLoading)
                        
                        if authManager.isLoading {
                            ProgressView()
                                .tint(.sleepPrimary)
                        }
                    }
                    .padding(.horizontal, SleepSpacing.lg)
                    
                    // 로그인 링크
                    HStack(spacing: SleepSpacing.xs) {
                        Text("이미 계정이 있으신가요?")
                            .font(SleepTypography.subheadline)
                            .foregroundColor(.sleepTextSecondary)
                        
                        Button("로그인") {
                            dismiss()
                        }
                        .font(SleepTypography.subheadline.bold())
                        .foregroundColor(.sleepPrimary)
                    }
                    .padding(.top, SleepSpacing.md)
                    .padding(.bottom, SleepSpacing.xxl)
                }
            }
        }
        .navigationBarBackButtonHidden(true)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button {
                    dismiss()
                } label: {
                    Image(systemName: "chevron.left")
                        .foregroundColor(.sleepTextPrimary)
                }
            }
        }
        .alert(alertTitle, isPresented: $showAlert) {
            Button("확인", role: .cancel) {
                if alertTitle == "가입 완료" {
                    dismiss()
                }
            }
        } message: {
            Text(alertMessage)
        }
    }
    
    // MARK: - Actions
    
    private func signUp() async {
        do {
            try await authManager.signUp(
                email: email,
                username: username,
                password: password,
                fullName: fullName.isEmpty ? nil : fullName
            )
            alertTitle = "가입 완료"
            alertMessage = "회원가입이 완료되었습니다. 로그인해 주세요."
            showAlert = true
        } catch {
            alertTitle = "가입 오류"
            alertMessage = error.localizedDescription
            showAlert = true
        }
    }
}

// MARK: - Password Strength

enum PasswordStrength {
    case weak
    case fair
    case good
    case strong
    
    var level: Int {
        switch self {
        case .weak: return 1
        case .fair: return 2
        case .good: return 3
        case .strong: return 4
        }
    }
    
    var description: String {
        switch self {
        case .weak: return "약함"
        case .fair: return "보통"
        case .good: return "좋음"
        case .strong: return "강함"
        }
    }
    
    var color: Color {
        switch self {
        case .weak: return .sleepDanger
        case .fair: return .sleepWarning
        case .good: return .sleepInfo
        case .strong: return .sleepSuccess
        }
    }
    
    static func evaluate(_ password: String) -> PasswordStrength {
        var score = 0
        
        // 길이 점수
        if password.count >= 8 { score += 1 }
        if password.count >= 12 { score += 1 }
        
        // 복잡성 점수
        let hasUppercase = password.range(of: "[A-Z]", options: .regularExpression) != nil
        let hasLowercase = password.range(of: "[a-z]", options: .regularExpression) != nil
        let hasNumber = password.range(of: "[0-9]", options: .regularExpression) != nil
        let hasSpecial = password.range(of: "[!@#$%^&*(),.?\":{}|<>]", options: .regularExpression) != nil
        
        if hasUppercase && hasLowercase { score += 1 }
        if hasNumber { score += 1 }
        if hasSpecial { score += 1 }
        
        switch score {
        case 0...1: return .weak
        case 2: return .fair
        case 3: return .good
        default: return .strong
        }
    }
}

// MARK: - Form Field Components

struct FormField: View {
    let title: String
    let placeholder: String
    @Binding var text: String
    var keyboardType: UIKeyboardType = .default
    var textContentType: UITextContentType? = nil
    var error: String? = nil
    
    var body: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.xs) {
            Text(title)
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
            
            TextField("", text: $text)
                .placeholder(when: text.isEmpty) {
                    Text(placeholder)
                        .foregroundColor(.sleepTextDisabled)
                }
                .keyboardType(keyboardType)
                .textContentType(textContentType)
                .autocapitalization(.none)
                .foregroundColor(.sleepTextPrimary)
                .padding()
                .background(Color.sleepSurface)
                .cornerRadius(SleepCornerRadius.medium)
                .overlay(
                    RoundedRectangle(cornerRadius: SleepCornerRadius.medium)
                        .stroke(error != nil ? Color.sleepDanger : Color.clear, lineWidth: 1)
                )
            
            if let error = error {
                Text(error)
                    .font(SleepTypography.caption2)
                    .foregroundColor(.sleepDanger)
            }
        }
    }
}

struct SecureFormField: View {
    let title: String
    let placeholder: String
    @Binding var text: String
    var textContentType: UITextContentType? = nil
    var error: String? = nil
    
    @State private var isSecure = true
    
    var body: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.xs) {
            Text(title)
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
            
            HStack {
                Group {
                    if isSecure {
                        SecureField("", text: $text)
                            .placeholder(when: text.isEmpty) {
                                Text(placeholder)
                                    .foregroundColor(.sleepTextDisabled)
                            }
                    } else {
                        TextField("", text: $text)
                            .placeholder(when: text.isEmpty) {
                                Text(placeholder)
                                    .foregroundColor(.sleepTextDisabled)
                            }
                    }
                }
                .textContentType(textContentType)
                .autocapitalization(.none)
                .foregroundColor(.sleepTextPrimary)
                
                Button {
                    isSecure.toggle()
                } label: {
                    Image(systemName: isSecure ? "eye.slash" : "eye")
                        .foregroundColor(.sleepTextDisabled)
                }
            }
            .padding()
            .background(Color.sleepSurface)
            .cornerRadius(SleepCornerRadius.medium)
            .overlay(
                RoundedRectangle(cornerRadius: SleepCornerRadius.medium)
                    .stroke(error != nil ? Color.sleepDanger : Color.clear, lineWidth: 1)
            )
            
            if let error = error {
                Text(error)
                    .font(SleepTypography.caption2)
                    .foregroundColor(.sleepDanger)
            }
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        SignUpView()
            .environmentObject(AuthManager())
    }
}
