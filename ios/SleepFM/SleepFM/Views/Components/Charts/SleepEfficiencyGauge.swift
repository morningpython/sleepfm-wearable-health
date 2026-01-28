//
//  SleepEfficiencyGauge.swift
//  SleepFM
//
//  수면 효율성 게이지 차트
//

import SwiftUI

/// 수면 효율성 게이지
struct SleepEfficiencyGauge: View {
    let efficiency: Double
    var size: CGFloat = 160
    var showLabel: Bool = true
    
    private var efficiencyCategory: EfficiencyCategory {
        EfficiencyCategory.fromEfficiency(efficiency)
    }
    
    var body: some View {
        ZStack {
            // 배경 아크
            Circle()
                .trim(from: 0.2, to: 0.8)
                .stroke(
                    Color.sleepTextDisabled.opacity(0.2),
                    style: StrokeStyle(lineWidth: 16, lineCap: .round)
                )
                .rotationEffect(.degrees(90))
            
            // 진행 아크
            Circle()
                .trim(from: 0.2, to: 0.2 + (efficiency / 100) * 0.6)
                .stroke(
                    efficiencyGradient,
                    style: StrokeStyle(lineWidth: 16, lineCap: .round)
                )
                .rotationEffect(.degrees(90))
                .animation(.easeInOut(duration: 1), value: efficiency)
            
            // 중앙 컨텐츠
            VStack(spacing: 4) {
                Text("\(Int(efficiency))%")
                    .font(.system(size: size * 0.22, weight: .bold))
                    .foregroundColor(.sleepTextPrimary)
                
                if showLabel {
                    Text(efficiencyCategory.label)
                        .font(.system(size: size * 0.09))
                        .foregroundColor(efficiencyCategory.color)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(efficiencyCategory.color.opacity(0.15))
                        .cornerRadius(8)
                }
            }
            
            // 최소/최대 레이블
            VStack {
                Spacer()
                HStack {
                    Text("0")
                        .font(.system(size: 10))
                        .foregroundColor(.sleepTextDisabled)
                    
                    Spacer()
                    
                    Text("100")
                        .font(.system(size: 10))
                        .foregroundColor(.sleepTextDisabled)
                }
                .padding(.horizontal, size * 0.15)
            }
        }
        .frame(width: size, height: size)
    }
    
    private var efficiencyGradient: AngularGradient {
        AngularGradient(
            colors: [.red, .orange, .yellow, .green],
            center: .center,
            startAngle: .degrees(108),
            endAngle: .degrees(252)
        )
    }
}

/// 효율성 카테고리
enum EfficiencyCategory {
    case poor
    case fair
    case good
    case excellent
    
    var label: String {
        switch self {
        case .poor: return "개선 필요"
        case .fair: return "보통"
        case .good: return "좋음"
        case .excellent: return "훌륭함"
        }
    }
    
    var color: Color {
        switch self {
        case .poor: return .red
        case .fair: return .orange
        case .good: return .green
        case .excellent: return .blue
        }
    }
    
    static func fromEfficiency(_ value: Double) -> EfficiencyCategory {
        switch value {
        case 0..<60: return .poor
        case 60..<75: return .fair
        case 75..<90: return .good
        default: return .excellent
        }
    }
}

/// 수면 점수 링
struct SleepScoreRing: View {
    let score: Double
    var size: CGFloat = 200
    var lineWidth: CGFloat = 20
    
    private var scoreCategory: ScoreCategory {
        ScoreCategory.fromScore(score)
    }
    
    var body: some View {
        ZStack {
            // 배경 링
            Circle()
                .stroke(
                    Color.sleepTextDisabled.opacity(0.15),
                    lineWidth: lineWidth
                )
            
            // 외곽 그라데이션 링
            Circle()
                .trim(from: 0, to: score / 100)
                .stroke(
                    scoreGradient,
                    style: StrokeStyle(lineWidth: lineWidth, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
                .animation(.spring(response: 0.8, dampingFraction: 0.7), value: score)
            
            // 중앙 컨텐츠
            VStack(spacing: 8) {
                Text("\(Int(score))")
                    .font(.system(size: size * 0.3, weight: .bold, design: .rounded))
                    .foregroundColor(.sleepTextPrimary)
                
                Text("수면 점수")
                    .font(.system(size: size * 0.07))
                    .foregroundColor(.sleepTextSecondary)
                
                HStack(spacing: 4) {
                    Image(systemName: scoreCategory.icon)
                        .font(.system(size: size * 0.06))
                    Text(scoreCategory.label)
                        .font(.system(size: size * 0.06, weight: .medium))
                }
                .foregroundColor(scoreCategory.color)
            }
        }
        .frame(width: size, height: size)
    }
    
    private var scoreGradient: AngularGradient {
        AngularGradient(
            gradient: Gradient(colors: [
                scoreCategory.color.opacity(0.6),
                scoreCategory.color
            ]),
            center: .center,
            startAngle: .degrees(-90),
            endAngle: .degrees(-90 + (score / 100) * 360)
        )
    }
}

/// 점수 카테고리
enum ScoreCategory {
    case poor
    case fair
    case good
    case excellent
    
    var label: String {
        switch self {
        case .poor: return "개선 필요"
        case .fair: return "보통"
        case .good: return "좋음"
        case .excellent: return "최고"
        }
    }
    
    var icon: String {
        switch self {
        case .poor: return "exclamationmark.triangle.fill"
        case .fair: return "minus.circle.fill"
        case .good: return "checkmark.circle.fill"
        case .excellent: return "star.fill"
        }
    }
    
    var color: Color {
        switch self {
        case .poor: return .red
        case .fair: return .orange
        case .good: return .green
        case .excellent: return Color.sleepPrimary
        }
    }
    
    static func fromScore(_ score: Double) -> ScoreCategory {
        switch score {
        case 0..<50: return .poor
        case 50..<70: return .fair
        case 70..<85: return .good
        default: return .excellent
        }
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 40) {
        HStack(spacing: 30) {
            SleepEfficiencyGauge(efficiency: 85)
            SleepEfficiencyGauge(efficiency: 65, size: 120)
        }
        
        HStack(spacing: 30) {
            SleepScoreRing(score: 78, size: 160)
            SleepScoreRing(score: 92, size: 120)
        }
    }
    .padding()
    .background(Color.sleepBackground)
}
