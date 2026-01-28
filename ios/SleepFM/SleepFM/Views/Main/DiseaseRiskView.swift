//
//  DiseaseRiskView.swift
//  SleepFM
//
//  질병 위험 분석 화면 (Story 7.3)
//

import SwiftUI
import Charts

/// 질병 위험 목록 화면
struct DiseaseRiskListView: View {
    @StateObject private var viewModel = DiseaseRiskViewModel()
    @State private var selectedDisease: DiseaseRiskItem?
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.sleepBackground
                    .ignoresSafeArea()
                
                if viewModel.isLoading {
                    loadingView
                } else {
                    contentView
                }
            }
            .navigationTitle("건강 위험 분석")
            .navigationBarTitleDisplayMode(.large)
            .toolbarBackground(Color.sleepBackground, for: .navigationBar)
            .task {
                await viewModel.loadDiseaseRisks()
            }
            .sheet(item: $selectedDisease) { disease in
                DiseaseRiskDetailView(disease: disease, viewModel: viewModel)
            }
        }
    }
    
    // MARK: - Loading View
    
    private var loadingView: some View {
        VStack(spacing: SleepSpacing.md) {
            ProgressView()
                .scaleEffect(1.5)
            Text("건강 데이터 분석 중...")
                .font(SleepTypography.body)
                .foregroundColor(.sleepTextSecondary)
        }
    }
    
    // MARK: - Content View
    
    private var contentView: some View {
        ScrollView {
            VStack(spacing: SleepSpacing.lg) {
                // 요약 카드
                summaryCard
                
                // 설명
                infoCard
                
                // 질환 목록
                diseaseListSection
            }
            .padding(.horizontal, SleepSpacing.lg)
            .padding(.bottom, SleepSpacing.xxl)
        }
    }
    
    // MARK: - Summary Card
    
    private var summaryCard: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("전체 위험도 요약")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
                
                Text("최근 분석")
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepTextSecondary)
            }
            
            // 전체 평균 점수
            HStack(spacing: SleepSpacing.xl) {
                VStack(spacing: SleepSpacing.xs) {
                    Text("\(Int(viewModel.averageRiskScore))")
                        .font(.system(size: 48, weight: .bold))
                        .foregroundColor(viewModel.overallCategory.color)
                    
                    Text("평균 위험 점수")
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepTextSecondary)
                }
                
                VStack(alignment: .leading, spacing: SleepSpacing.sm) {
                    RiskCategoryBadge(category: viewModel.overallCategory)
                    
                    Text(viewModel.overallCategory.description)
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepTextSecondary)
                        .lineLimit(2)
                }
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    // MARK: - Info Card
    
    private var infoCard: some View {
        HStack(spacing: SleepSpacing.sm) {
            Image(systemName: "info.circle.fill")
                .foregroundColor(.sleepInfo)
            
            Text("수면 데이터 기반의 위험도 예측입니다. 의학적 진단을 대체하지 않습니다.")
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
        }
        .padding(SleepSpacing.md)
        .background(Color.sleepInfo.opacity(0.1))
        .cornerRadius(SleepCornerRadius.medium)
    }
    
    // MARK: - Disease List Section
    
    private var diseaseListSection: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.md) {
            Text("질환별 위험도")
                .font(SleepTypography.headline)
                .foregroundColor(.sleepTextPrimary)
            
            ForEach(viewModel.diseases) { disease in
                DiseaseRiskCard(
                    disease: disease.disease,
                    diseaseNameKo: disease.diseaseNameKo,
                    score: disease.score,
                    category: disease.category,
                    trend: disease.trend
                ) {
                    selectedDisease = disease
                }
            }
        }
    }
}

// MARK: - Disease Risk Detail View

struct DiseaseRiskDetailView: View {
    let disease: DiseaseRiskItem
    @ObservedObject var viewModel: DiseaseRiskViewModel
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.sleepBackground
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: SleepSpacing.lg) {
                        // 헤더
                        headerSection
                        
                        // 현재 상태
                        currentStatusSection
                        
                        // 트렌드 차트
                        trendSection
                        
                        // 상세 정보
                        detailInfoSection
                        
                        // 권장사항
                        recommendationsSection
                    }
                    .padding(.horizontal, SleepSpacing.lg)
                    .padding(.bottom, SleepSpacing.xxl)
                }
            }
            .navigationTitle(disease.diseaseNameKo)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("닫기") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        VStack(spacing: SleepSpacing.md) {
            // 게이지 차트
            DiseaseRiskGaugeChart(
                score: disease.score,
                category: disease.category,
                size: 160
            )
            
            // 카테고리 배지
            RiskCategoryBadge(category: disease.category, size: .large)
        }
        .padding(.top, SleepSpacing.lg)
    }
    
    // MARK: - Current Status Section
    
    private var currentStatusSection: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("현재 상태")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
                
                TrendBadge(direction: disease.trend, value: trendValueText)
            }
            
            HStack(spacing: SleepSpacing.lg) {
                StatusInfoItem(
                    title: "위험 점수",
                    value: "\(Int(disease.score))점",
                    color: disease.category.color
                )
                
                StatusInfoItem(
                    title: "위험 등급",
                    value: disease.category.label,
                    color: disease.category.color
                )
                
                StatusInfoItem(
                    title: "분석 기준일",
                    value: "오늘",
                    color: .sleepTextSecondary
                )
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    private var trendValueText: String {
        switch disease.trend {
        case .up: return "+5"
        case .down: return "-3"
        case .stable: return "0"
        }
    }
    
    // MARK: - Trend Section
    
    private var trendSection: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("주간 트렌드")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
                
                Picker("기간", selection: .constant(0)) {
                    Text("주간").tag(0)
                    Text("월간").tag(1)
                }
                .pickerStyle(.segmented)
                .frame(width: 120)
            }
            
            // 트렌드 차트
            let trendData = viewModel.getTrendData(for: disease.disease)
            DiseaseRiskTrendChart(data: trendData, disease: disease.disease, height: 180)
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    // MARK: - Detail Info Section
    
    private var detailInfoSection: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("상세 정보")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            VStack(alignment: .leading, spacing: SleepSpacing.sm) {
                DetailInfoRow(
                    label: "질환명",
                    value: disease.diseaseNameKo
                )
                
                DetailInfoRow(
                    label: "영문명",
                    value: disease.disease.replacingOccurrences(of: "_", with: " ").capitalized
                )
                
                DetailInfoRow(
                    label: "분석 근거",
                    value: "수면 단계, 심박 변이, 호흡 패턴"
                )
                
                DetailInfoRow(
                    label: "신뢰도",
                    value: "85%"
                )
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    // MARK: - Recommendations Section
    
    private var recommendationsSection: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Image(systemName: "heart.text.square.fill")
                    .foregroundColor(.sleepDanger)
                
                Text("건강 관리 권장사항")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            VStack(alignment: .leading, spacing: SleepSpacing.sm) {
                ForEach(recommendationsForDisease, id: \.self) { recommendation in
                    RecommendationRow(text: recommendation)
                }
            }
            
            // 경고 메시지 (고위험일 경우)
            if disease.category == .high || disease.category == .veryHigh {
                warningMessage
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    private var recommendationsForDisease: [String] {
        switch disease.disease {
        case "parkinsons":
            return [
                "규칙적인 유산소 운동을 주 3회 이상 해보세요.",
                "충분한 수면 시간을 확보하세요 (7-8시간).",
                "스트레스 관리와 명상을 시도해보세요."
            ]
        case "dementia":
            return [
                "두뇌 활동을 자극하는 활동을 꾸준히 하세요.",
                "사회적 활동을 유지하세요.",
                "건강한 식습관을 유지하세요."
            ]
        case "myocardial_infarction":
            return [
                "심혈관 건강을 위해 저염식을 실천하세요.",
                "정기적인 심장 검진을 받으세요.",
                "금연과 절주를 실천하세요."
            ]
        case "heart_failure":
            return [
                "적절한 체중 관리가 중요합니다.",
                "나트륨 섭취를 제한하세요.",
                "규칙적인 운동을 하되 무리하지 마세요."
            ]
        case "stroke":
            return [
                "혈압 관리를 철저히 하세요.",
                "당뇨 관리에 신경 쓰세요.",
                "정기적인 건강검진을 받으세요."
            ]
        default:
            return [
                "규칙적인 수면 습관을 유지하세요.",
                "건강한 생활 습관을 유지하세요."
            ]
        }
    }
    
    private var warningMessage: some View {
        HStack(spacing: SleepSpacing.sm) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.sleepWarning)
            
            VStack(alignment: .leading, spacing: 2) {
                Text("주의가 필요합니다")
                    .font(SleepTypography.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.sleepWarning)
                
                Text("위험도가 높으니 전문의 상담을 권장합니다.")
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepTextSecondary)
            }
            
            Spacer()
        }
        .padding(SleepSpacing.md)
        .background(Color.sleepWarning.opacity(0.1))
        .cornerRadius(SleepCornerRadius.medium)
    }
}

// MARK: - Supporting Views

struct RiskCategoryBadge: View {
    let category: RiskCategory
    var size: BadgeSize = .regular
    
    enum BadgeSize {
        case regular
        case large
        
        var fontSize: CGFloat {
            switch self {
            case .regular: return 12
            case .large: return 14
            }
        }
        
        var padding: CGFloat {
            switch self {
            case .regular: return 8
            case .large: return 12
            }
        }
    }
    
    var body: some View {
        Text(category.label)
            .font(.system(size: size.fontSize, weight: .semibold))
            .foregroundColor(category.color)
            .padding(.horizontal, size.padding)
            .padding(.vertical, size.padding / 2)
            .background(category.color.opacity(0.15))
            .cornerRadius(8)
    }
}

struct StatusInfoItem: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: SleepSpacing.xxs) {
            Text(title)
                .font(SleepTypography.caption2)
                .foregroundColor(.sleepTextSecondary)
            
            Text(value)
                .font(SleepTypography.headline)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
    }
}

struct DetailInfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(SleepTypography.body)
                .foregroundColor(.sleepTextSecondary)
            
            Spacer()
            
            Text(value)
                .font(SleepTypography.body)
                .foregroundColor(.sleepTextPrimary)
        }
        .padding(.vertical, SleepSpacing.xxs)
    }
}

// MARK: - Risk Category Extension

extension RiskCategory {
    var description: String {
        switch self {
        case .low:
            return "현재 건강 상태가 양호합니다. 현재 생활 습관을 유지하세요."
        case .moderate:
            return "주의가 필요한 수준입니다. 생활 습관 개선을 권장합니다."
        case .high:
            return "위험 수준이 높습니다. 전문의 상담을 권장합니다."
        case .veryHigh:
            return "매우 높은 위험 수준입니다. 즉시 전문의 상담이 필요합니다."
        }
    }
}

// MARK: - Preview

#Preview {
    DiseaseRiskListView()
}
