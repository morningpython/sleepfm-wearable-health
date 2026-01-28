//
//  HistoryCalendarView.swift
//  SleepFM
//
//  캘린더 기반 수면 기록 화면 (Story 7.4 강화)
//

import SwiftUI

/// 캘린더 기반 히스토리 화면
struct HistoryCalendarView: View {
    @StateObject private var viewModel = HistoryViewModel()
    @State private var viewMode: ViewMode = .calendar
    @State private var selectedDate: Date = Date()
    @State private var showingDetail = false
    
    enum ViewMode: String, CaseIterable {
        case calendar = "달력"
        case list = "목록"
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.sleepBackground
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // 뷰 모드 토글
                    viewModeToggle
                    
                    // 선택한 날짜 요약
                    if let data = viewModel.getSleepData(for: selectedDate) {
                        selectedDateSummary(data: data)
                    }
                    
                    // 메인 컨텐츠
                    if viewMode == .calendar {
                        calendarContent
                    } else {
                        listContent
                    }
                }
            }
            .navigationTitle("수면 기록")
            .navigationBarTitleDisplayMode(.large)
            .toolbarBackground(Color.sleepBackground, for: .navigationBar)
            .task {
                await viewModel.loadHistoryData()
            }
            .sheet(isPresented: $showingDetail) {
                NavigationStack {
                    SleepDetailView(sessionId: nil, date: selectedDate)
                }
            }
        }
    }
    
    // MARK: - View Mode Toggle
    
    private var viewModeToggle: some View {
        HStack {
            Picker("보기 모드", selection: $viewMode) {
                ForEach(ViewMode.allCases, id: \.self) { mode in
                    Text(mode.rawValue).tag(mode)
                }
            }
            .pickerStyle(.segmented)
            .frame(width: 160)
        }
        .padding(.horizontal, SleepSpacing.lg)
        .padding(.vertical, SleepSpacing.sm)
    }
    
    // MARK: - Selected Date Summary
    
    private func selectedDateSummary(data: CalendarDaySleepData) -> some View {
        Button {
            showingDetail = true
        } label: {
            HStack(spacing: SleepSpacing.md) {
                // 점수
                VStack(spacing: 2) {
                    Text("\(Int(data.score ?? 0))")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(data.scoreCategory?.color ?? .sleepTextDisabled)
                    
                    Text("점")
                        .font(SleepTypography.caption2)
                        .foregroundColor(.sleepTextSecondary)
                }
                .frame(width: 60)
                
                VStack(alignment: .leading, spacing: SleepSpacing.xxs) {
                    Text(formattedSelectedDate)
                        .font(SleepTypography.headline)
                        .foregroundColor(.sleepTextPrimary)
                    
                    if let score = data.score {
                        Text(ScoreCategory.fromScore(score).label)
                            .font(SleepTypography.caption1)
                            .foregroundColor(data.scoreCategory?.color ?? .sleepTextSecondary)
                    }
                }
                
                Spacer()
                
                Text("상세보기")
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepPrimary)
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12))
                    .foregroundColor(.sleepPrimary)
            }
            .padding(SleepSpacing.md)
            .background(Color.sleepCardBackground)
            .cornerRadius(SleepCornerRadius.medium)
            .padding(.horizontal, SleepSpacing.lg)
        }
        .buttonStyle(.plain)
    }
    
    private var formattedSelectedDate: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ko_KR")
        formatter.dateFormat = "M월 d일 (E)"
        return formatter.string(from: selectedDate)
    }
    
    // MARK: - Calendar Content
    
    private var calendarContent: some View {
        ScrollView {
            VStack(spacing: SleepSpacing.lg) {
                // 주간 요약
                weekSummaryCard
                
                // 캘린더
                SleepCalendarView(
                    selectedDate: $selectedDate,
                    sleepData: viewModel.calendarData
                ) { date in
                    if viewModel.getSleepData(for: date)?.hasData == true {
                        showingDetail = true
                    }
                }
                .padding(SleepSpacing.md)
                .background(Color.sleepCardBackground)
                .cornerRadius(SleepCornerRadius.large)
                
                // 월간 통계
                monthlyStatsCard
                
                // 범례
                legendCard
            }
            .padding(.horizontal, SleepSpacing.lg)
            .padding(.bottom, SleepSpacing.xxl)
        }
    }
    
    // MARK: - Week Summary Card
    
    private var weekSummaryCard: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("이번 주")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            WeeklyCalendarView(
                selectedDate: $selectedDate,
                sleepData: viewModel.calendarData
            ) { date in
                selectedDate = date
                if viewModel.getSleepData(for: date)?.hasData == true {
                    showingDetail = true
                }
            }
            
            HStack(spacing: SleepSpacing.lg) {
                WeekStatItem(
                    title: "평균 점수",
                    value: "\(Int(viewModel.weeklyAverageScore))점",
                    icon: "chart.bar.fill",
                    color: ScoreCategory.fromScore(viewModel.weeklyAverageScore).color
                )
                
                WeekStatItem(
                    title: "평균 수면",
                    value: viewModel.formattedWeeklyAverageDuration,
                    icon: "bed.double.fill",
                    color: .sleepPrimary
                )
                
                WeekStatItem(
                    title: "기록일",
                    value: "\(viewModel.weeklyRecordedDays)일",
                    icon: "calendar",
                    color: .sleepSecondary
                )
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    // MARK: - Monthly Stats Card
    
    private var monthlyStatsCard: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("월간 통계")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            HStack(spacing: SleepSpacing.md) {
                MonthlyStatCard(
                    title: "최고 점수",
                    value: "\(Int(viewModel.monthlyHighScore))",
                    subtitle: "점",
                    color: .sleepSuccess
                )
                
                MonthlyStatCard(
                    title: "최저 점수",
                    value: "\(Int(viewModel.monthlyLowScore))",
                    subtitle: "점",
                    color: .sleepWarning
                )
                
                MonthlyStatCard(
                    title: "연속 기록",
                    value: "\(viewModel.streakDays)",
                    subtitle: "일",
                    color: .sleepPrimary
                )
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    // MARK: - Legend Card
    
    private var legendCard: some View {
        VStack(spacing: SleepSpacing.sm) {
            HStack {
                Text("점수 범례")
                    .font(SleepTypography.subheadline)
                    .foregroundColor(.sleepTextSecondary)
                
                Spacer()
            }
            
            HStack(spacing: SleepSpacing.lg) {
                LegendItem(color: .sleepPrimary, label: "85+ 최고")
                LegendItem(color: .green, label: "70-84 좋음")
                LegendItem(color: .orange, label: "50-69 보통")
                LegendItem(color: .red, label: "50↓ 개선필요")
            }
        }
        .padding(SleepSpacing.md)
        .background(Color.sleepCardBackground.opacity(0.5))
        .cornerRadius(SleepCornerRadius.medium)
    }
    
    // MARK: - List Content
    
    private var listContent: some View {
        ScrollView {
            LazyVStack(spacing: SleepSpacing.sm) {
                ForEach(viewModel.sortedSessions) { session in
                    SessionListRow(session: session) {
                        selectedDate = session.date
                        showingDetail = true
                    }
                }
            }
            .padding(.horizontal, SleepSpacing.lg)
            .padding(.bottom, SleepSpacing.xxl)
        }
    }
}

// MARK: - Supporting Views

struct WeekStatItem: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: SleepSpacing.xs) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundColor(color)
            
            Text(value)
                .font(SleepTypography.headline)
                .foregroundColor(.sleepTextPrimary)
            
            Text(title)
                .font(SleepTypography.caption2)
                .foregroundColor(.sleepTextSecondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct MonthlyStatCard: View {
    let title: String
    let value: String
    let subtitle: String
    let color: Color
    
    var body: some View {
        VStack(spacing: SleepSpacing.xs) {
            Text(title)
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
            
            HStack(alignment: .bottom, spacing: 2) {
                Text(value)
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(color)
                
                Text(subtitle)
                    .font(SleepTypography.caption2)
                    .foregroundColor(.sleepTextSecondary)
                    .padding(.bottom, 4)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, SleepSpacing.md)
        .background(color.opacity(0.1))
        .cornerRadius(SleepCornerRadius.medium)
    }
}

struct LegendItem: View {
    let color: Color
    let label: String
    
    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            
            Text(label)
                .font(.system(size: 10))
                .foregroundColor(.sleepTextSecondary)
        }
    }
}

struct SessionListRow: View {
    let session: SleepHistorySession
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: SleepSpacing.md) {
                // 날짜
                VStack(alignment: .leading, spacing: 2) {
                    Text(session.dayString)
                        .font(SleepTypography.headline)
                        .foregroundColor(.sleepTextPrimary)
                    
                    Text(session.dateString)
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepTextSecondary)
                }
                .frame(width: 60, alignment: .leading)
                
                // 점수 바
                GeometryReader { geometry in
                    ZStack(alignment: .leading) {
                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color.sleepTextDisabled.opacity(0.2))
                        
                        RoundedRectangle(cornerRadius: 4)
                            .fill(session.scoreCategory.color)
                            .frame(width: geometry.size.width * (session.score / 100))
                    }
                }
                .frame(height: 20)
                
                // 점수
                Text("\(Int(session.score))")
                    .font(SleepTypography.headline)
                    .foregroundColor(session.scoreCategory.color)
                    .frame(width: 35, alignment: .trailing)
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12))
                    .foregroundColor(.sleepTextDisabled)
            }
            .padding(SleepSpacing.md)
            .background(Color.sleepCardBackground)
            .cornerRadius(SleepCornerRadius.medium)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Preview

#Preview {
    HistoryCalendarView()
}
