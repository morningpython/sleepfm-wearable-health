//
//  WatchHealthManager.swift
//  SleepFM Watch App
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation
import HealthKit
import WatchKit

/// watchOS HealthKit 매니저
/// 
/// 주요 기능:
/// - HealthKit 권한 관리
/// - 실시간 심박수, 호흡률 쿼리
/// - 수면 상태 감지
/// - 가속도계 데이터 수집
@MainActor
class WatchHealthManager: NSObject, ObservableObject {
    // MARK: - Published Properties
    
    @Published var isAuthorized = false
    @Published var currentHeartRate: Int = 0
    @Published var currentRespiratoryRate: Double = 0
    @Published var lastNightSleepScore: Int = 78 // 샘플값
    @Published var isCollecting = false
    
    // MARK: - Private Properties
    
    private let healthStore = HKHealthStore()
    private var heartRateQuery: HKAnchoredObjectQuery?
    private var respiratoryQuery: HKAnchoredObjectQuery?
    private var workoutSession: HKWorkoutSession?
    private var workoutBuilder: HKLiveWorkoutBuilder?
    
    // 데이터 타입
    private let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate)!
    private let respiratoryRateType = HKQuantityType.quantityType(forIdentifier: .respiratoryRate)!
    private let oxygenSaturationType = HKQuantityType.quantityType(forIdentifier: .oxygenSaturation)!
    private let hrvType = HKQuantityType.quantityType(forIdentifier: .heartRateVariabilitySDNN)!
    private let sleepType = HKCategoryType.categoryType(forIdentifier: .sleepAnalysis)!
    
    // MARK: - Initialization
    
    override init() {
        super.init()
    }
    
    // MARK: - Authorization
    
    /// HealthKit 권한 요청
    func requestAuthorization() async {
        guard HKHealthStore.isHealthDataAvailable() else {
            print("HealthKit not available on this device")
            return
        }
        
        let typesToRead: Set<HKObjectType> = [
            heartRateType,
            respiratoryRateType,
            oxygenSaturationType,
            hrvType,
            sleepType
        ]
        
        let typesToWrite: Set<HKSampleType> = [
            HKQuantityType.workoutType()
        ]
        
        do {
            try await healthStore.requestAuthorization(toShare: typesToWrite, read: typesToRead)
            isAuthorized = true
            print("HealthKit authorization granted")
        } catch {
            print("HealthKit authorization failed: \(error.localizedDescription)")
            isAuthorized = false
        }
    }
    
    // MARK: - Workout Session (백그라운드 수집용)
    
    /// 워크아웃 세션 시작 (백그라운드 데이터 수집)
    func startWorkoutSession() async throws {
        let configuration = HKWorkoutConfiguration()
        configuration.activityType = .mindAndBody // 수면 추적용
        configuration.locationType = .indoor
        
        do {
            workoutSession = try HKWorkoutSession(healthStore: healthStore, configuration: configuration)
            workoutBuilder = workoutSession?.associatedWorkoutBuilder()
            
            workoutBuilder?.dataSource = HKLiveWorkoutDataSource(
                healthStore: healthStore,
                workoutConfiguration: configuration
            )
            
            workoutSession?.delegate = self
            workoutBuilder?.delegate = self
            
            // 세션 시작
            let startDate = Date()
            workoutSession?.startActivity(with: startDate)
            try await workoutBuilder?.beginCollection(at: startDate)
            
            isCollecting = true
            print("Workout session started for sleep tracking")
            
            // 실시간 쿼리 시작
            startRealtimeQueries()
            
        } catch {
            print("Failed to start workout session: \(error)")
            throw error
        }
    }
    
    /// 워크아웃 세션 종료
    func stopWorkoutSession() async {
        guard let session = workoutSession else { return }
        
        session.end()
        
        do {
            try await workoutBuilder?.endCollection(at: Date())
            try await workoutBuilder?.finishWorkout()
        } catch {
            print("Failed to finish workout: \(error)")
        }
        
        stopRealtimeQueries()
        isCollecting = false
        workoutSession = nil
        workoutBuilder = nil
        
        print("Workout session ended")
    }
    
    // MARK: - Realtime Queries
    
    /// 실시간 심박수 쿼리 시작
    private func startRealtimeQueries() {
        startHeartRateQuery()
        startRespiratoryRateQuery()
    }
    
    /// 실시간 쿼리 중지
    private func stopRealtimeQueries() {
        if let query = heartRateQuery {
            healthStore.stop(query)
            heartRateQuery = nil
        }
        
        if let query = respiratoryQuery {
            healthStore.stop(query)
            respiratoryQuery = nil
        }
    }
    
    /// 심박수 실시간 쿼리
    private func startHeartRateQuery() {
        let predicate = HKQuery.predicateForSamples(
            withStart: Date(),
            end: nil,
            options: .strictStartDate
        )
        
        heartRateQuery = HKAnchoredObjectQuery(
            type: heartRateType,
            predicate: predicate,
            anchor: nil,
            limit: HKObjectQueryNoLimit
        ) { [weak self] query, samples, deletedObjects, anchor, error in
            self?.processHeartRateSamples(samples)
        }
        
        heartRateQuery?.updateHandler = { [weak self] query, samples, deletedObjects, anchor, error in
            self?.processHeartRateSamples(samples)
        }
        
        if let query = heartRateQuery {
            healthStore.execute(query)
        }
    }
    
    /// 심박수 샘플 처리
    private func processHeartRateSamples(_ samples: [HKSample]?) {
        guard let quantitySamples = samples as? [HKQuantitySample],
              let lastSample = quantitySamples.last else { return }
        
        let heartRate = lastSample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
        
        Task { @MainActor in
            self.currentHeartRate = Int(heartRate)
            
            // 이상 징후 체크
            checkHeartRateAnomaly(heartRate: heartRate)
            
            // 데이터 저장
            SensorDataStore.shared.addHeartRate(heartRate, at: lastSample.startDate)
        }
    }
    
    /// 호흡률 실시간 쿼리
    private func startRespiratoryRateQuery() {
        let predicate = HKQuery.predicateForSamples(
            withStart: Date(),
            end: nil,
            options: .strictStartDate
        )
        
        respiratoryQuery = HKAnchoredObjectQuery(
            type: respiratoryRateType,
            predicate: predicate,
            anchor: nil,
            limit: HKObjectQueryNoLimit
        ) { [weak self] query, samples, deletedObjects, anchor, error in
            self?.processRespiratoryRateSamples(samples)
        }
        
        respiratoryQuery?.updateHandler = { [weak self] query, samples, deletedObjects, anchor, error in
            self?.processRespiratoryRateSamples(samples)
        }
        
        if let query = respiratoryQuery {
            healthStore.execute(query)
        }
    }
    
    /// 호흡률 샘플 처리
    private func processRespiratoryRateSamples(_ samples: [HKSample]?) {
        guard let quantitySamples = samples as? [HKQuantitySample],
              let lastSample = quantitySamples.last else { return }
        
        let respiratoryRate = lastSample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
        
        Task { @MainActor in
            self.currentRespiratoryRate = respiratoryRate
            
            // 데이터 저장
            SensorDataStore.shared.addRespiratoryRate(respiratoryRate, at: lastSample.startDate)
        }
    }
    
    // MARK: - Anomaly Detection
    
    /// 심박수 이상 징후 체크
    private func checkHeartRateAnomaly(heartRate: Double) {
        // 비정상 심박수: < 40 또는 > 120 bpm
        if heartRate < 40 || heartRate > 120 {
            NotificationService.shared.sendHealthAlert(
                title: "비정상 심박수 감지",
                body: "현재 심박수: \(Int(heartRate)) bpm",
                type: .abnormalHeartRate
            )
        }
    }
    
    // MARK: - Sleep Detection
    
    /// 수면 상태 확인
    func checkSleepStatus() async -> Bool {
        let predicate = HKQuery.predicateForSamples(
            withStart: Date().addingTimeInterval(-3600), // 최근 1시간
            end: Date(),
            options: .strictStartDate
        )
        
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)
        
        return await withCheckedContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: sleepType,
                predicate: predicate,
                limit: 1,
                sortDescriptors: [sortDescriptor]
            ) { query, samples, error in
                guard let sample = samples?.first as? HKCategorySample else {
                    continuation.resume(returning: false)
                    return
                }
                
                // 수면 중인지 확인 (inBed 또는 asleep)
                let isSleeping = sample.value == HKCategoryValueSleepAnalysis.asleepUnspecified.rawValue ||
                                 sample.value == HKCategoryValueSleepAnalysis.asleepCore.rawValue ||
                                 sample.value == HKCategoryValueSleepAnalysis.asleepDeep.rawValue ||
                                 sample.value == HKCategoryValueSleepAnalysis.asleepREM.rawValue
                
                continuation.resume(returning: isSleeping)
            }
            
            healthStore.execute(query)
        }
    }
    
    // MARK: - Historical Data
    
    /// 어젯밤 수면 데이터 가져오기
    func fetchLastNightSleepData() async {
        let calendar = Calendar.current
        let now = Date()
        
        // 어제 저녁 8시부터 오늘 오전 12시까지
        guard let yesterday = calendar.date(byAdding: .day, value: -1, to: now),
              let startOfYesterday = calendar.date(bySettingHour: 20, minute: 0, second: 0, of: yesterday),
              let endOfToday = calendar.date(bySettingHour: 12, minute: 0, second: 0, of: now) else {
            return
        }
        
        let predicate = HKQuery.predicateForSamples(
            withStart: startOfYesterday,
            end: endOfToday,
            options: .strictStartDate
        )
        
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: true)
        
        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            let query = HKSampleQuery(
                sampleType: sleepType,
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: [sortDescriptor]
            ) { [weak self] query, samples, error in
                guard let samples = samples as? [HKCategorySample], !samples.isEmpty else {
                    continuation.resume()
                    return
                }
                
                // 수면 점수 계산 (간단한 로직)
                let totalSleepMinutes = samples.reduce(0.0) { total, sample in
                    let duration = sample.endDate.timeIntervalSince(sample.startDate) / 60
                    return total + duration
                }
                
                // 7-9시간이 최적, 그에 따른 점수 계산
                let optimalMinutes = 480.0 // 8시간
                let score = min(100, Int((totalSleepMinutes / optimalMinutes) * 100))
                
                Task { @MainActor in
                    self?.lastNightSleepScore = score
                }
                
                continuation.resume()
            }
            
            healthStore.execute(query)
        }
    }
}

// MARK: - HKWorkoutSessionDelegate

extension WatchHealthManager: HKWorkoutSessionDelegate {
    nonisolated func workoutSession(
        _ workoutSession: HKWorkoutSession,
        didChangeTo toState: HKWorkoutSessionState,
        from fromState: HKWorkoutSessionState,
        date: Date
    ) {
        print("Workout state changed: \(fromState.rawValue) -> \(toState.rawValue)")
        
        Task { @MainActor in
            switch toState {
            case .running:
                self.isCollecting = true
            case .ended, .stopped:
                self.isCollecting = false
            default:
                break
            }
        }
    }
    
    nonisolated func workoutSession(
        _ workoutSession: HKWorkoutSession,
        didFailWithError error: Error
    ) {
        print("Workout session failed: \(error.localizedDescription)")
        
        Task { @MainActor in
            self.isCollecting = false
        }
    }
}

// MARK: - HKLiveWorkoutBuilderDelegate

extension WatchHealthManager: HKLiveWorkoutBuilderDelegate {
    nonisolated func workoutBuilder(
        _ workoutBuilder: HKLiveWorkoutBuilder,
        didCollectDataOf collectedTypes: Set<HKSampleType>
    ) {
        // 수집된 데이터 타입 로깅
        for type in collectedTypes {
            print("Collected data of type: \(type.identifier)")
        }
    }
    
    nonisolated func workoutBuilderDidCollectEvent(_ workoutBuilder: HKLiveWorkoutBuilder) {
        // 이벤트 수집됨
    }
}
