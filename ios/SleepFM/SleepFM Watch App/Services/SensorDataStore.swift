//
//  SensorDataStore.swift
//  SleepFM Watch App
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation

/// 센서 데이터 임시 저장소
///
/// 수면 중 수집된 센서 데이터를 메모리에 저장합니다.
/// iPhone으로 전송 완료 후 데이터를 삭제합니다.
///
/// 참고: 실제 프로덕션에서는 SQLite나 Core Data 사용 권장
actor SensorDataStore {
    // MARK: - Singleton
    
    static let shared = SensorDataStore()
    
    // MARK: - Storage
    
    private var heartRateSamples: [SensorSample] = []
    private var respiratoryRateSamples: [SensorSample] = []
    private var accelerometerSamples: [AccelerometerSample] = []
    
    // MARK: - Limits
    
    /// 최대 샘플 수 (메모리 제한)
    /// 8시간 x 60분 x 60초 = 28,800 샘플 (1Hz 기준)
    private let maxSamples = 30000
    
    // MARK: - Initialization
    
    private init() {}
    
    // MARK: - Add Data
    
    /// 심박수 데이터 추가
    func addHeartRate(_ value: Double, at timestamp: Date) {
        let sample = SensorSample(timestamp: timestamp, value: value)
        heartRateSamples.append(sample)
        
        // 메모리 제한 관리
        if heartRateSamples.count > maxSamples {
            heartRateSamples.removeFirst(1000)
        }
    }
    
    /// 호흡률 데이터 추가
    func addRespiratoryRate(_ value: Double, at timestamp: Date) {
        let sample = SensorSample(timestamp: timestamp, value: value)
        respiratoryRateSamples.append(sample)
        
        if respiratoryRateSamples.count > maxSamples {
            respiratoryRateSamples.removeFirst(1000)
        }
    }
    
    /// 가속도계 데이터 추가
    func addAccelerometer(x: Double, y: Double, z: Double, at timestamp: Date) {
        let sample = AccelerometerSample(timestamp: timestamp, x: x, y: y, z: z)
        accelerometerSamples.append(sample)
        
        if accelerometerSamples.count > maxSamples {
            accelerometerSamples.removeFirst(1000)
        }
    }
    
    // MARK: - Retrieve Data
    
    /// 전체 샘플 수
    var totalSampleCount: Int {
        heartRateSamples.count + respiratoryRateSamples.count + accelerometerSamples.count
    }
    
    /// 모든 데이터 가져오기
    func getAllData() -> [String: Any] {
        return [
            "heartRate": heartRateSamples,
            "respiratoryRate": respiratoryRateSamples,
            "accelerometer": accelerometerSamples
        ]
    }
    
    /// 데이터 패키지 생성
    func getDataPackage(sessionId: String, startTime: Date, endTime: Date) -> SensorDataPackage {
        return SensorDataPackage(
            sessionId: sessionId,
            startTime: startTime,
            endTime: endTime,
            heartRateSamples: heartRateSamples,
            respiratoryRateSamples: respiratoryRateSamples,
            accelerometerSamples: accelerometerSamples
        )
    }
    
    /// 특정 시간 범위의 심박수 가져오기
    func getHeartRateSamples(from startDate: Date, to endDate: Date) -> [SensorSample] {
        return heartRateSamples.filter { $0.timestamp >= startDate && $0.timestamp <= endDate }
    }
    
    /// 특정 시간 범위의 호흡률 가져오기
    func getRespiratoryRateSamples(from startDate: Date, to endDate: Date) -> [SensorSample] {
        return respiratoryRateSamples.filter { $0.timestamp >= startDate && $0.timestamp <= endDate }
    }
    
    /// 특정 시간 범위의 가속도 가져오기
    func getAccelerometerSamples(from startDate: Date, to endDate: Date) -> [AccelerometerSample] {
        return accelerometerSamples.filter { $0.timestamp >= startDate && $0.timestamp <= endDate }
    }
    
    // MARK: - Statistics
    
    /// 심박수 통계
    func getHeartRateStatistics() -> (min: Double, max: Double, avg: Double)? {
        guard !heartRateSamples.isEmpty else { return nil }
        
        let values = heartRateSamples.map { $0.value }
        let min = values.min() ?? 0
        let max = values.max() ?? 0
        let avg = values.reduce(0, +) / Double(values.count)
        
        return (min, max, avg)
    }
    
    /// 호흡률 통계
    func getRespiratoryRateStatistics() -> (min: Double, max: Double, avg: Double)? {
        guard !respiratoryRateSamples.isEmpty else { return nil }
        
        let values = respiratoryRateSamples.map { $0.value }
        let min = values.min() ?? 0
        let max = values.max() ?? 0
        let avg = values.reduce(0, +) / Double(values.count)
        
        return (min, max, avg)
    }
    
    /// 움직임 통계 (가속도 벡터 크기)
    func getMovementStatistics() -> (total: Double, avg: Double)? {
        guard !accelerometerSamples.isEmpty else { return nil }
        
        let magnitudes = accelerometerSamples.map { sample in
            sqrt(sample.x * sample.x + sample.y * sample.y + sample.z * sample.z)
        }
        
        let total = magnitudes.reduce(0, +)
        let avg = total / Double(magnitudes.count)
        
        return (total, avg)
    }
    
    // MARK: - Clear Data
    
    /// 모든 데이터 초기화
    func reset() {
        heartRateSamples.removeAll()
        respiratoryRateSamples.removeAll()
        accelerometerSamples.removeAll()
    }
    
    /// 특정 시간 이전 데이터 삭제
    func removeData(before date: Date) {
        heartRateSamples.removeAll { $0.timestamp < date }
        respiratoryRateSamples.removeAll { $0.timestamp < date }
        accelerometerSamples.removeAll { $0.timestamp < date }
    }
}

// MARK: - Codable Extensions

extension SensorSample: Codable {}
extension AccelerometerSample: Codable {}

// MARK: - Data Export

extension SensorDataStore {
    /// JSON으로 내보내기
    func exportToJSON() -> Data? {
        let export: [String: Any] = [
            "exportTime": Date().timeIntervalSince1970,
            "heartRateSamples": heartRateSamples.map { ["t": $0.timestamp.timeIntervalSince1970, "v": $0.value] },
            "respiratoryRateSamples": respiratoryRateSamples.map { ["t": $0.timestamp.timeIntervalSince1970, "v": $0.value] },
            "accelerometerSamples": accelerometerSamples.map { ["t": $0.timestamp.timeIntervalSince1970, "x": $0.x, "y": $0.y, "z": $0.z] }
        ]
        
        return try? JSONSerialization.data(withJSONObject: export, options: .prettyPrinted)
    }
}
