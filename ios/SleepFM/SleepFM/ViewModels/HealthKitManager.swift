//
//  HealthKitManager.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation
import HealthKit
import Combine

/// HealthKit 데이터 관리자
@MainActor
class HealthKitManager: ObservableObject {
    // MARK: - Published Properties
    
    /// HealthKit 사용 가능 여부
    @Published var isAvailable: Bool = false
    
    /// 권한 승인 상태
    @Published var authorizationStatus: AuthorizationStatus = .notDetermined
    
    /// 최근 수면 데이터
    @Published var recentSleepData: [SleepSession] = []
    
    /// 에러 메시지
    @Published var errorMessage: String?
    
    // MARK: - Types
    
    enum AuthorizationStatus {
        case notDetermined
        case authorized
        case denied
    }
    
    // MARK: - Private Properties
    
    private let healthStore: HKHealthStore?
    
    /// 읽기 권한 요청할 데이터 타입
    private let typesToRead: Set<HKObjectType> = {
        var types = Set<HKObjectType>()
        
        // 수면 분석
        if let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) {
            types.insert(sleepType)
        }
        
        // 심박수
        if let heartRateType = HKObjectType.quantityType(forIdentifier: .heartRate) {
            types.insert(heartRateType)
        }
        
        // 호흡률
        if let respiratoryRateType = HKObjectType.quantityType(forIdentifier: .respiratoryRate) {
            types.insert(respiratoryRateType)
        }
        
        // 심박 변이도
        if let hrvType = HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN) {
            types.insert(hrvType)
        }
        
        // 산소 포화도
        if let oxygenType = HKObjectType.quantityType(forIdentifier: .oxygenSaturation) {
            types.insert(oxygenType)
        }
        
        return types
    }()
    
    // MARK: - Initialization
    
    init() {
        if HKHealthStore.isHealthDataAvailable() {
            self.healthStore = HKHealthStore()
            self.isAvailable = true
        } else {
            self.healthStore = nil
            self.isAvailable = false
        }
    }
    
    // MARK: - Public Methods
    
    /// HealthKit 권한 요청
    func requestAuthorization() async -> Bool {
        guard let healthStore = healthStore else {
            errorMessage = "이 기기에서는 HealthKit을 사용할 수 없습니다."
            return false
        }
        
        do {
            try await healthStore.requestAuthorization(toShare: [], read: typesToRead)
            authorizationStatus = .authorized
            return true
        } catch {
            errorMessage = "HealthKit 권한 요청에 실패했습니다: \(error.localizedDescription)"
            authorizationStatus = .denied
            return false
        }
    }
    
    /// 최근 수면 데이터 조회
    func fetchRecentSleepData(days: Int = 7) async {
        guard let healthStore = healthStore else { return }
        guard let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else { return }
        
        let calendar = Calendar.current
        let endDate = Date()
        guard let startDate = calendar.date(byAdding: .day, value: -days, to: endDate) else { return }
        
        let predicate = HKQuery.predicateForSamples(
            withStart: startDate,
            end: endDate,
            options: .strictStartDate
        )
        
        let sortDescriptor = NSSortDescriptor(
            key: HKSampleSortIdentifierStartDate,
            ascending: false
        )
        
        do {
            let samples = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<[HKCategorySample], Error>) in
                let query = HKSampleQuery(
                    sampleType: sleepType,
                    predicate: predicate,
                    limit: HKObjectQueryNoLimit,
                    sortDescriptors: [sortDescriptor]
                ) { _, samples, error in
                    if let error = error {
                        continuation.resume(throwing: error)
                        return
                    }
                    
                    let categorySamples = samples as? [HKCategorySample] ?? []
                    continuation.resume(returning: categorySamples)
                }
                
                healthStore.execute(query)
            }
            
            // 수면 세션으로 변환
            recentSleepData = processSleepSamples(samples)
            
        } catch {
            errorMessage = "수면 데이터를 가져오는데 실패했습니다: \(error.localizedDescription)"
        }
    }
    
    /// 특정 기간의 심박수 데이터 조회
    func fetchHeartRateData(from startDate: Date, to endDate: Date) async -> [HeartRateSample] {
        guard let healthStore = healthStore else { return [] }
        guard let heartRateType = HKObjectType.quantityType(forIdentifier: .heartRate) else { return [] }
        
        let predicate = HKQuery.predicateForSamples(
            withStart: startDate,
            end: endDate,
            options: .strictStartDate
        )
        
        let sortDescriptor = NSSortDescriptor(
            key: HKSampleSortIdentifierStartDate,
            ascending: true
        )
        
        do {
            let samples = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<[HKQuantitySample], Error>) in
                let query = HKSampleQuery(
                    sampleType: heartRateType,
                    predicate: predicate,
                    limit: HKObjectQueryNoLimit,
                    sortDescriptors: [sortDescriptor]
                ) { _, samples, error in
                    if let error = error {
                        continuation.resume(throwing: error)
                        return
                    }
                    
                    let quantitySamples = samples as? [HKQuantitySample] ?? []
                    continuation.resume(returning: quantitySamples)
                }
                
                healthStore.execute(query)
            }
            
            // 심박수 샘플로 변환
            return samples.map { sample in
                HeartRateSample(
                    timestamp: sample.startDate,
                    bpm: sample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
                )
            }
            
        } catch {
            errorMessage = "심박수 데이터를 가져오는데 실패했습니다."
            return []
        }
    }
    
    /// 특정 기간의 호흡률 데이터 조회
    func fetchRespiratoryRateData(from startDate: Date, to endDate: Date) async -> [RespiratoryRateSample] {
        guard let healthStore = healthStore else { return [] }
        guard let respiratoryType = HKObjectType.quantityType(forIdentifier: .respiratoryRate) else { return [] }
        
        let predicate = HKQuery.predicateForSamples(
            withStart: startDate,
            end: endDate,
            options: .strictStartDate
        )
        
        let sortDescriptor = NSSortDescriptor(
            key: HKSampleSortIdentifierStartDate,
            ascending: true
        )
        
        do {
            let samples = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<[HKQuantitySample], Error>) in
                let query = HKSampleQuery(
                    sampleType: respiratoryType,
                    predicate: predicate,
                    limit: HKObjectQueryNoLimit,
                    sortDescriptors: [sortDescriptor]
                ) { _, samples, error in
                    if let error = error {
                        continuation.resume(throwing: error)
                        return
                    }
                    
                    let quantitySamples = samples as? [HKQuantitySample] ?? []
                    continuation.resume(returning: quantitySamples)
                }
                
                healthStore.execute(query)
            }
            
            return samples.map { sample in
                RespiratoryRateSample(
                    timestamp: sample.startDate,
                    breathsPerMinute: sample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
                )
            }
            
        } catch {
            errorMessage = "호흡률 데이터를 가져오는데 실패했습니다."
            return []
        }
    }
    
    // MARK: - Private Methods
    
    /// 수면 샘플을 세션으로 변환
    private func processSleepSamples(_ samples: [HKCategorySample]) -> [SleepSession] {
        // inBed 샘플들을 그룹화하여 세션 생성
        var sessions: [SleepSession] = []
        
        // 날짜별로 그룹화
        let groupedByDate = Dictionary(grouping: samples) { sample in
            Calendar.current.startOfDay(for: sample.startDate)
        }
        
        for (date, daySamples) in groupedByDate {
            guard let firstSample = daySamples.min(by: { $0.startDate < $1.startDate }),
                  let lastSample = daySamples.max(by: { $0.endDate < $1.endDate }) else {
                continue
            }
            
            let duration = lastSample.endDate.timeIntervalSince(firstSample.startDate) / 3600.0
            
            // 30분 이상의 수면만 포함
            if duration >= 0.5 {
                sessions.append(SleepSession(
                    id: UUID().uuidString,
                    date: date,
                    startTime: firstSample.startDate,
                    endTime: lastSample.endDate,
                    durationHours: duration
                ))
            }
        }
        
        return sessions.sorted { $0.date > $1.date }
    }
}

// MARK: - Supporting Types

/// 심박수 샘플
struct HeartRateSample {
    let timestamp: Date
    let bpm: Double
}

/// 호흡률 샘플
struct RespiratoryRateSample {
    let timestamp: Date
    let breathsPerMinute: Double
}
