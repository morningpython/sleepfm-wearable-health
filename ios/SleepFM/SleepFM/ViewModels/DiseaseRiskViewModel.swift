//
//  DiseaseRiskViewModel.swift
//  SleepFM
//
//  질병 위험 분석 ViewModel
//

import Foundation

/// 질병 위험 뷰모델
@MainActor
final class DiseaseRiskViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var diseases: [DiseaseRiskItem] = []
    @Published var trendData: [String: [RiskTrendDataPoint]] = [:]
    
    // MARK: - Computed Properties
    
    var averageRiskScore: Double {
        guard !diseases.isEmpty else { return 0 }
        return diseases.map(\.score).reduce(0, +) / Double(diseases.count)
    }
    
    var overallCategory: RiskCategory {
        RiskCategory.fromScore(averageRiskScore)
    }
    
    // MARK: - Public Methods
    
    func loadDiseaseRisks() async {
        isLoading = true
        errorMessage = nil
        
        do {
            // TODO: 실제 API 호출
            try await Task.sleep(nanoseconds: 600_000_000)
            
            // 더미 데이터
            diseases = [
                DiseaseRiskItem(
                    disease: "parkinsons",
                    diseaseNameKo: "파킨슨병",
                    score: Double.random(in: 20...45),
                    category: .moderate,
                    trend: .down
                ),
                DiseaseRiskItem(
                    disease: "dementia",
                    diseaseNameKo: "치매",
                    score: Double.random(in: 15...35),
                    category: .low,
                    trend: .stable
                ),
                DiseaseRiskItem(
                    disease: "myocardial_infarction",
                    diseaseNameKo: "심근경색",
                    score: Double.random(in: 25...55),
                    category: .moderate,
                    trend: .up
                ),
                DiseaseRiskItem(
                    disease: "heart_failure",
                    diseaseNameKo: "심부전",
                    score: Double.random(in: 18...42),
                    category: .low,
                    trend: .down
                ),
                DiseaseRiskItem(
                    disease: "stroke",
                    diseaseNameKo: "뇌졸중",
                    score: Double.random(in: 30...58),
                    category: .moderate,
                    trend: .stable
                )
            ]
            
            // 카테고리 재계산
            diseases = diseases.map { disease in
                var updated = disease
                // score에 따라 category 재설정
                let newCategory = RiskCategory.fromScore(disease.score)
                return DiseaseRiskItem(
                    disease: disease.disease,
                    diseaseNameKo: disease.diseaseNameKo,
                    score: disease.score,
                    category: newCategory,
                    trend: disease.trend
                )
            }
            
            // 트렌드 데이터 생성
            generateTrendData()
            
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    func getTrendData(for disease: String) -> [RiskTrendDataPoint] {
        return trendData[disease] ?? []
    }
    
    // MARK: - Private Methods
    
    private func generateTrendData() {
        for disease in diseases {
            var points: [RiskTrendDataPoint] = []
            let baseScore = disease.score
            
            for i in 0..<7 {
                if let date = Calendar.current.date(byAdding: .day, value: -6 + i, to: Date()) {
                    // 트렌드에 따라 점수 변동
                    let variation: Double
                    switch disease.trend {
                    case .up:
                        variation = Double(i) * 1.5 + Double.random(in: -5...5)
                    case .down:
                        variation = -Double(i) * 1.2 + Double.random(in: -5...5)
                    case .stable:
                        variation = Double.random(in: -8...8)
                    }
                    
                    let score = max(0, min(100, baseScore - variation))
                    points.append(RiskTrendDataPoint(date: date, score: score))
                }
            }
            
            trendData[disease.disease] = points
        }
    }
}
