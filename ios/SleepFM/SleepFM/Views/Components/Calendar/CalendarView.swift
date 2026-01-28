//
//  CalendarView.swift
//  SleepFM
//
//  수면 기록 캘린더 뷰
//

import SwiftUI

/// 캘린더 날짜별 수면 데이터
struct CalendarDaySleepData: Identifiable {
    let id = UUID()
    let date: Date
    let score: Double?
    let hasData: Bool
    
    var scoreCategory: ScoreCategory? {
        guard let score = score else { return nil }
        return ScoreCategory.fromScore(score)
    }
}

/// 수면 캘린더 뷰
struct SleepCalendarView: View {
    @Binding var selectedDate: Date
    let sleepData: [Date: CalendarDaySleepData]
    var onDateSelected: ((Date) -> Void)?
    
    @State private var currentMonth: Date = Date()
    
    private let calendar = Calendar.current
    private let columns = Array(repeating: GridItem(.flexible()), count: 7)
    private let weekdaySymbols = ["일", "월", "화", "수", "목", "금", "토"]
    
    var body: some View {
        VStack(spacing: SleepSpacing.md) {
            // 월 네비게이션
            monthNavigation
            
            // 요일 헤더
            weekdayHeader
            
            // 캘린더 그리드
            calendarGrid
        }
    }
    
    // MARK: - Month Navigation
    
    private var monthNavigation: some View {
        HStack {
            Button {
                withAnimation {
                    currentMonth = calendar.date(byAdding: .month, value: -1, to: currentMonth) ?? currentMonth
                }
            } label: {
                Image(systemName: "chevron.left")
                    .foregroundColor(.sleepTextPrimary)
                    .padding(SleepSpacing.sm)
            }
            
            Spacer()
            
            Text(monthYearString)
                .font(SleepTypography.headline)
                .foregroundColor(.sleepTextPrimary)
            
            Spacer()
            
            Button {
                withAnimation {
                    let nextMonth = calendar.date(byAdding: .month, value: 1, to: currentMonth) ?? currentMonth
                    // 미래로 가지 않도록
                    if nextMonth <= Date() {
                        currentMonth = nextMonth
                    }
                }
            } label: {
                Image(systemName: "chevron.right")
                    .foregroundColor(canGoForward ? .sleepTextPrimary : .sleepTextDisabled)
                    .padding(SleepSpacing.sm)
            }
            .disabled(!canGoForward)
        }
    }
    
    private var monthYearString: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ko_KR")
        formatter.dateFormat = "yyyy년 M월"
        return formatter.string(from: currentMonth)
    }
    
    private var canGoForward: Bool {
        let nextMonth = calendar.date(byAdding: .month, value: 1, to: currentMonth) ?? currentMonth
        return nextMonth <= Date()
    }
    
    // MARK: - Weekday Header
    
    private var weekdayHeader: some View {
        HStack {
            ForEach(weekdaySymbols, id: \.self) { symbol in
                Text(symbol)
                    .font(SleepTypography.caption1)
                    .foregroundColor(symbol == "일" ? .red.opacity(0.7) : (symbol == "토" ? .blue.opacity(0.7) : .sleepTextSecondary))
                    .frame(maxWidth: .infinity)
            }
        }
    }
    
    // MARK: - Calendar Grid
    
    private var calendarGrid: some View {
        let days = daysInMonth()
        
        return LazyVGrid(columns: columns, spacing: SleepSpacing.sm) {
            ForEach(days, id: \.self) { date in
                if let date = date {
                    DayCell(
                        date: date,
                        sleepData: sleepData[normalizedDate(date)],
                        isSelected: calendar.isDate(date, inSameDayAs: selectedDate),
                        isToday: calendar.isDateInToday(date),
                        isFuture: date > Date()
                    ) {
                        selectedDate = date
                        onDateSelected?(date)
                    }
                } else {
                    Color.clear
                        .frame(height: 44)
                }
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func daysInMonth() -> [Date?] {
        guard let monthInterval = calendar.dateInterval(of: .month, for: currentMonth),
              let monthFirstWeek = calendar.dateInterval(of: .weekOfMonth, for: monthInterval.start) else {
            return []
        }
        
        var days: [Date?] = []
        var currentDate = monthFirstWeek.start
        
        // 이전 달 빈 칸
        while currentDate < monthInterval.start {
            days.append(nil)
            currentDate = calendar.date(byAdding: .day, value: 1, to: currentDate) ?? currentDate
        }
        
        // 현재 달
        while currentDate < monthInterval.end {
            days.append(currentDate)
            currentDate = calendar.date(byAdding: .day, value: 1, to: currentDate) ?? currentDate
        }
        
        // 다음 달 빈 칸 (6주까지)
        while days.count < 42 {
            days.append(nil)
        }
        
        return days
    }
    
    private func normalizedDate(_ date: Date) -> Date {
        calendar.startOfDay(for: date)
    }
}

/// 날짜 셀
struct DayCell: View {
    let date: Date
    let sleepData: CalendarDaySleepData?
    let isSelected: Bool
    let isToday: Bool
    let isFuture: Bool
    let action: () -> Void
    
    private let calendar = Calendar.current
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 2) {
                // 날짜
                Text("\(calendar.component(.day, from: date))")
                    .font(SleepTypography.subheadline)
                    .fontWeight(isToday ? .bold : .regular)
                    .foregroundColor(textColor)
                
                // 점수 인디케이터
                if let data = sleepData, data.hasData {
                    Circle()
                        .fill(data.scoreCategory?.color ?? .gray)
                        .frame(width: 6, height: 6)
                } else {
                    Circle()
                        .fill(Color.clear)
                        .frame(width: 6, height: 6)
                }
            }
            .frame(width: 40, height: 44)
            .background(
                RoundedRectangle(cornerRadius: SleepCornerRadius.small)
                    .fill(backgroundColor)
            )
            .overlay(
                RoundedRectangle(cornerRadius: SleepCornerRadius.small)
                    .stroke(isToday ? Color.sleepPrimary : Color.clear, lineWidth: 2)
            )
        }
        .disabled(isFuture)
    }
    
    private var textColor: Color {
        if isFuture {
            return .sleepTextDisabled
        } else if isSelected {
            return .white
        } else {
            return .sleepTextPrimary
        }
    }
    
    private var backgroundColor: Color {
        if isSelected {
            return .sleepPrimary
        } else if sleepData?.hasData == true {
            return sleepData?.scoreCategory?.color.opacity(0.15) ?? Color.clear
        } else {
            return Color.clear
        }
    }
}

/// 주간 뷰
struct WeeklyCalendarView: View {
    @Binding var selectedDate: Date
    let sleepData: [Date: CalendarDaySleepData]
    var onDateSelected: ((Date) -> Void)?
    
    private let calendar = Calendar.current
    
    var body: some View {
        HStack(spacing: SleepSpacing.xs) {
            ForEach(weekDates, id: \.self) { date in
                WeekDayCell(
                    date: date,
                    sleepData: sleepData[calendar.startOfDay(for: date)],
                    isSelected: calendar.isDate(date, inSameDayAs: selectedDate),
                    isToday: calendar.isDateInToday(date)
                ) {
                    selectedDate = date
                    onDateSelected?(date)
                }
            }
        }
    }
    
    private var weekDates: [Date] {
        let startOfWeek = calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: selectedDate))!
        return (0..<7).compactMap { calendar.date(byAdding: .day, value: $0, to: startOfWeek) }
    }
}

/// 주간 뷰 날짜 셀
struct WeekDayCell: View {
    let date: Date
    let sleepData: CalendarDaySleepData?
    let isSelected: Bool
    let isToday: Bool
    let action: () -> Void
    
    private let calendar = Calendar.current
    
    private var weekdayString: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ko_KR")
        formatter.dateFormat = "E"
        return formatter.string(from: date)
    }
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                // 요일
                Text(weekdayString)
                    .font(.system(size: 11))
                    .foregroundColor(.sleepTextSecondary)
                
                // 날짜
                Text("\(calendar.component(.day, from: date))")
                    .font(SleepTypography.headline)
                    .foregroundColor(isSelected ? .white : .sleepTextPrimary)
                
                // 점수 (있으면)
                if let data = sleepData, let score = data.score {
                    Text("\(Int(score))")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundColor(isSelected ? .white.opacity(0.8) : data.scoreCategory?.color ?? .sleepTextSecondary)
                } else {
                    Text("-")
                        .font(.system(size: 10))
                        .foregroundColor(.sleepTextDisabled)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, SleepSpacing.sm)
            .background(
                RoundedRectangle(cornerRadius: SleepCornerRadius.medium)
                    .fill(isSelected ? Color.sleepPrimary : Color.sleepCardBackground)
            )
            .overlay(
                RoundedRectangle(cornerRadius: SleepCornerRadius.medium)
                    .stroke(isToday ? Color.sleepPrimary : Color.clear, lineWidth: 2)
            )
        }
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 20) {
        // 샘플 데이터
        let calendar = Calendar.current
        var sampleData: [Date: CalendarDaySleepData] = [:]
        for i in 0..<30 {
            if let date = calendar.date(byAdding: .day, value: -i, to: Date()) {
                let normalizedDate = calendar.startOfDay(for: date)
                sampleData[normalizedDate] = CalendarDaySleepData(
                    date: normalizedDate,
                    score: Double.random(in: 40...95),
                    hasData: Bool.random()
                )
            }
        }
        
        SleepCalendarView(
            selectedDate: .constant(Date()),
            sleepData: sampleData
        )
        .padding()
        .background(Color.sleepCardBackground)
        .cornerRadius(16)
        
        WeeklyCalendarView(
            selectedDate: .constant(Date()),
            sleepData: sampleData
        )
        .padding()
    }
    .padding()
    .background(Color.sleepBackground)
}
