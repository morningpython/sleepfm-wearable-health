//
//  OnboardingView.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// 온보딩 페이지 데이터
struct OnboardingPage: Identifiable {
    let id = UUID()
    let image: String
    let title: String
    let description: String
}

/// 온보딩 화면
struct OnboardingView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var currentPage = 0
    
    private let pages: [OnboardingPage] = [
        OnboardingPage(
            image: "moon.stars.fill",
            title: "수면의 질을 분석합니다",
            description: "AI 기반의 정밀한 수면 분석으로\n당신의 수면 패턴을 파악하세요"
        ),
        OnboardingPage(
            image: "heart.text.square.fill",
            title: "건강 위험을 예측합니다",
            description: "수면 무호흡증, 심장 질환 등\n잠재적 건강 위험을 미리 감지합니다"
        ),
        OnboardingPage(
            image: "chart.line.uptrend.xyaxis",
            title: "맞춤형 인사이트를 제공합니다",
            description: "개인화된 수면 개선 권장 사항으로\n더 나은 수면을 경험하세요"
        )
    ]
    
    var body: some View {
        ZStack {
            // 배경
            Color.sleepBackground
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // 페이지 인디케이터
                HStack(spacing: SleepSpacing.xs) {
                    ForEach(0..<pages.count, id: \.self) { index in
                        Circle()
                            .fill(currentPage == index ? Color.sleepPrimary : Color.sleepTextDisabled)
                            .frame(width: 8, height: 8)
                            .animation(.easeInOut(duration: 0.3), value: currentPage)
                    }
                }
                .padding(.top, SleepSpacing.xl)
                
                // 페이지 콘텐츠
                TabView(selection: $currentPage) {
                    ForEach(Array(pages.enumerated()), id: \.element.id) { index, page in
                        OnboardingPageView(page: page)
                            .tag(index)
                    }
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                
                // 버튼 영역
                VStack(spacing: SleepSpacing.md) {
                    if currentPage == pages.count - 1 {
                        // 마지막 페이지 - 시작하기 버튼
                        Button("시작하기") {
                            authManager.completeOnboarding()
                        }
                        .buttonStyle(PrimaryButtonStyle())
                    } else {
                        // 다음 버튼
                        Button("다음") {
                            withAnimation {
                                currentPage += 1
                            }
                        }
                        .buttonStyle(PrimaryButtonStyle())
                    }
                    
                    // 건너뛰기 버튼
                    if currentPage < pages.count - 1 {
                        Button("건너뛰기") {
                            authManager.completeOnboarding()
                        }
                        .font(SleepTypography.subheadline)
                        .foregroundColor(.sleepTextSecondary)
                    }
                }
                .padding(.horizontal, SleepSpacing.lg)
                .padding(.bottom, SleepSpacing.xxl)
            }
        }
    }
}

/// 온보딩 페이지 뷰
struct OnboardingPageView: View {
    let page: OnboardingPage
    
    var body: some View {
        VStack(spacing: SleepSpacing.xl) {
            Spacer()
            
            // 아이콘
            ZStack {
                Circle()
                    .fill(SleepGradients.primary)
                    .frame(width: 160, height: 160)
                    .blur(radius: 40)
                    .opacity(0.5)
                
                Image(systemName: page.image)
                    .font(.system(size: 80))
                    .foregroundStyle(SleepGradients.primary)
            }
            
            VStack(spacing: SleepSpacing.md) {
                // 제목
                Text(page.title)
                    .font(SleepTypography.title1)
                    .foregroundColor(.sleepTextPrimary)
                    .multilineTextAlignment(.center)
                
                // 설명
                Text(page.description)
                    .font(SleepTypography.body)
                    .foregroundColor(.sleepTextSecondary)
                    .multilineTextAlignment(.center)
                    .lineSpacing(4)
            }
            .padding(.horizontal, SleepSpacing.lg)
            
            Spacer()
            Spacer()
        }
    }
}

// MARK: - Preview

#Preview {
    OnboardingView()
        .environmentObject(AuthManager())
}
