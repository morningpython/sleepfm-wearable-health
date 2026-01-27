//
//  DesignSystem.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

// MARK: - Color Palette

/// SleepFM 앱 컬러 팔레트
extension Color {
    // MARK: - Primary Colors
    
    /// 메인 브랜드 색상 - 수면을 상징하는 Deep Indigo
    static let sleepPrimary = Color(hex: "4A00E0")
    
    /// 보조 브랜드 색상 - 편안함을 상징하는 Soft Purple
    static let sleepSecondary = Color(hex: "8E2DE2")
    
    /// 그라디언트 시작 색상
    static let gradientStart = Color(hex: "667eea")
    
    /// 그라디언트 끝 색상
    static let gradientEnd = Color(hex: "764ba2")
    
    // MARK: - Background Colors
    
    /// 앱 배경색 (다크 모드)
    static let sleepBackground = Color(hex: "0F0F23")
    
    /// 카드 배경색
    static let sleepCardBackground = Color(hex: "1A1A2E")
    
    /// 서피스 색상
    static let sleepSurface = Color(hex: "16213E")
    
    // MARK: - Text Colors
    
    /// 주요 텍스트
    static let sleepTextPrimary = Color.white
    
    /// 보조 텍스트
    static let sleepTextSecondary = Color(hex: "B8B8D1")
    
    /// 비활성 텍스트
    static let sleepTextDisabled = Color(hex: "6C6C80")
    
    // MARK: - Semantic Colors
    
    /// 성공 색상
    static let sleepSuccess = Color(hex: "00D26A")
    
    /// 경고 색상
    static let sleepWarning = Color(hex: "FFB800")
    
    /// 위험 색상
    static let sleepDanger = Color(hex: "FF4757")
    
    /// 정보 색상
    static let sleepInfo = Color(hex: "54A0FF")
    
    // MARK: - Sleep Stage Colors
    
    /// Wake 단계
    static let stageWake = Color(hex: "FF6B6B")
    
    /// N1 (Light Sleep 1) 단계
    static let stageN1 = Color(hex: "FFA06B")
    
    /// N2 (Light Sleep 2) 단계
    static let stageN2 = Color(hex: "FFE66B")
    
    /// N3 (Deep Sleep) 단계
    static let stageN3 = Color(hex: "4ECDC4")
    
    /// REM 단계
    static let stageREM = Color(hex: "A06BFF")
    
    // MARK: - Initializer
    
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Typography

/// 타이포그래피 스타일
struct SleepTypography {
    // MARK: - Large Title
    
    static let largeTitle = Font.system(size: 34, weight: .bold, design: .rounded)
    
    // MARK: - Title
    
    static let title1 = Font.system(size: 28, weight: .bold, design: .rounded)
    static let title2 = Font.system(size: 22, weight: .bold, design: .rounded)
    static let title3 = Font.system(size: 20, weight: .semibold, design: .rounded)
    
    // MARK: - Headline
    
    static let headline = Font.system(size: 17, weight: .semibold, design: .rounded)
    
    // MARK: - Body
    
    static let body = Font.system(size: 17, weight: .regular, design: .rounded)
    static let bodyBold = Font.system(size: 17, weight: .semibold, design: .rounded)
    
    // MARK: - Callout
    
    static let callout = Font.system(size: 16, weight: .regular, design: .rounded)
    
    // MARK: - Subheadline
    
    static let subheadline = Font.system(size: 15, weight: .regular, design: .rounded)
    
    // MARK: - Footnote
    
    static let footnote = Font.system(size: 13, weight: .regular, design: .rounded)
    
    // MARK: - Caption
    
    static let caption1 = Font.system(size: 12, weight: .regular, design: .rounded)
    static let caption2 = Font.system(size: 11, weight: .regular, design: .rounded)
    
    // MARK: - Numbers
    
    static let numberLarge = Font.system(size: 48, weight: .bold, design: .rounded)
    static let numberMedium = Font.system(size: 32, weight: .bold, design: .rounded)
    static let numberSmall = Font.system(size: 24, weight: .semibold, design: .rounded)
}

// MARK: - Spacing

/// 간격 시스템
struct SleepSpacing {
    static let xxxs: CGFloat = 2
    static let xxs: CGFloat = 4
    static let xs: CGFloat = 8
    static let sm: CGFloat = 12
    static let md: CGFloat = 16
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
    static let xxl: CGFloat = 48
    static let xxxl: CGFloat = 64
}

// MARK: - Corner Radius

/// 모서리 둥글기
struct SleepCornerRadius {
    static let small: CGFloat = 8
    static let medium: CGFloat = 12
    static let large: CGFloat = 16
    static let extraLarge: CGFloat = 24
    static let full: CGFloat = 9999
}

// MARK: - Shadow

/// 그림자 스타일
struct SleepShadow {
    static let small = Shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: 2)
    static let medium = Shadow(color: Color.black.opacity(0.15), radius: 8, x: 0, y: 4)
    static let large = Shadow(color: Color.black.opacity(0.2), radius: 16, x: 0, y: 8)
}

struct Shadow {
    let color: Color
    let radius: CGFloat
    let x: CGFloat
    let y: CGFloat
}

// MARK: - Gradients

/// 그라디언트 스타일
struct SleepGradients {
    /// 메인 브랜드 그라디언트
    static let primary = LinearGradient(
        colors: [.sleepPrimary, .sleepSecondary],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// 배경 그라디언트
    static let background = LinearGradient(
        colors: [.sleepBackground, .sleepSurface],
        startPoint: .top,
        endPoint: .bottom
    )
    
    /// 카드 그라디언트
    static let card = LinearGradient(
        colors: [.sleepCardBackground, .sleepSurface.opacity(0.8)],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// 수면 점수 그라디언트
    static func sleepScore(score: Double) -> LinearGradient {
        let colors: [Color]
        switch score {
        case 0..<40:
            colors = [.sleepDanger, .sleepDanger.opacity(0.7)]
        case 40..<60:
            colors = [.sleepWarning, .sleepWarning.opacity(0.7)]
        case 60..<80:
            colors = [.sleepInfo, .sleepInfo.opacity(0.7)]
        default:
            colors = [.sleepSuccess, .sleepSuccess.opacity(0.7)]
        }
        return LinearGradient(
            colors: colors,
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
}

// MARK: - View Modifiers

/// 카드 스타일 적용
struct CardStyle: ViewModifier {
    var padding: CGFloat = SleepSpacing.md
    
    func body(content: Content) -> some View {
        content
            .padding(padding)
            .background(Color.sleepCardBackground)
            .cornerRadius(SleepCornerRadius.large)
    }
}

/// 그라디언트 카드 스타일
struct GradientCardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(SleepSpacing.md)
            .background(SleepGradients.card)
            .cornerRadius(SleepCornerRadius.large)
            .overlay(
                RoundedRectangle(cornerRadius: SleepCornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
}

/// 기본 버튼 스타일
struct PrimaryButtonStyle: ButtonStyle {
    var isEnabled: Bool = true
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(SleepTypography.headline)
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, SleepSpacing.md)
            .background(
                isEnabled ? SleepGradients.primary : LinearGradient(
                    colors: [.sleepTextDisabled],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(SleepCornerRadius.medium)
            .opacity(configuration.isPressed ? 0.8 : 1.0)
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .animation(.easeInOut(duration: 0.15), value: configuration.isPressed)
    }
}

/// 보조 버튼 스타일
struct SecondaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(SleepTypography.headline)
            .foregroundColor(.sleepPrimary)
            .frame(maxWidth: .infinity)
            .padding(.vertical, SleepSpacing.md)
            .background(Color.sleepPrimary.opacity(0.1))
            .cornerRadius(SleepCornerRadius.medium)
            .overlay(
                RoundedRectangle(cornerRadius: SleepCornerRadius.medium)
                    .stroke(Color.sleepPrimary, lineWidth: 2)
            )
            .opacity(configuration.isPressed ? 0.8 : 1.0)
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .animation(.easeInOut(duration: 0.15), value: configuration.isPressed)
    }
}

// MARK: - View Extensions

extension View {
    /// 카드 스타일 적용
    func sleepCard(padding: CGFloat = SleepSpacing.md) -> some View {
        modifier(CardStyle(padding: padding))
    }
    
    /// 그라디언트 카드 스타일 적용
    func sleepGradientCard() -> some View {
        modifier(GradientCardStyle())
    }
    
    /// 그림자 적용
    func sleepShadow(_ shadow: Shadow) -> some View {
        self.shadow(color: shadow.color, radius: shadow.radius, x: shadow.x, y: shadow.y)
    }
}
