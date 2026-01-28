//
//  SleepSessionUploader.swift
//  SleepFM
//
//  Watch에서 수신한 센서 데이터를 서버로 업로드하는 서비스
//

import Foundation
import Combine

/// 수면 세션 업로드 서비스
@MainActor
final class SleepSessionUploader: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = SleepSessionUploader()
    
    // MARK: - Published Properties
    
    /// 업로드 진행률 (0.0 ~ 1.0)
    @Published private(set) var uploadProgress: Double = 0
    
    /// 업로드 상태
    @Published private(set) var uploadStatus: UploadStatus = .idle
    
    /// 마지막 업로드 시간
    @Published private(set) var lastUploadDate: Date?
    
    /// 대기 중인 세션 수
    @Published private(set) var pendingSessionCount: Int = 0
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    private let connectivityManager: PhoneConnectivityManager
    private var cancellables = Set<AnyCancellable>()
    private var pendingSessions: [PendingSleepSession] = []
    
    // MARK: - Initialization
    
    private init(
        apiService: APIService = .shared,
        connectivityManager: PhoneConnectivityManager = .shared
    ) {
        self.apiService = apiService
        self.connectivityManager = connectivityManager
        
        setupNotifications()
        loadPendingSessions()
    }
    
    // MARK: - Setup
    
    private func setupNotifications() {
        // Watch에서 수면 종료 시 자동 업로드
        NotificationCenter.default.publisher(for: .watchSleepEnded)
            .sink { [weak self] _ in
                Task {
                    await self?.processSleepEndedFromWatch()
                }
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Public Methods
    
    /// Watch에서 받은 데이터로 세션 생성 및 업로드
    func createAndUploadSession() async throws {
        uploadStatus = .preparing
        
        // Watch에서 대기 중인 데이터 가져오기
        let sensorData = connectivityManager.fetchPendingSensorData()
        
        guard !sensorData.isEmpty else {
            uploadStatus = .idle
            throw UploadError.noData
        }
        
        // 세션 데이터 구성
        let session = createSessionFromSensorData(sensorData)
        
        // 업로드
        try await uploadSession(session)
    }
    
    /// 특정 세션 업로드
    func uploadSession(_ session: PendingSleepSession) async throws {
        uploadStatus = .uploading
        uploadProgress = 0
        
        do {
            // 1단계: 세션 생성
            uploadProgress = 0.2
            let sessionResponse = try await createServerSession(session)
            
            // 2단계: 센서 데이터 업로드 (청크 단위)
            uploadProgress = 0.4
            try await uploadSensorData(sessionId: sessionResponse.sessionId, data: session.sensorData)
            
            // 3단계: 분석 요청
            uploadProgress = 0.8
            let _ = try await apiService.requestAnalysis(sessionId: sessionResponse.sessionId)
            
            // 완료
            uploadProgress = 1.0
            uploadStatus = .completed
            lastUploadDate = Date()
            
            // 대기 목록에서 제거
            removePendingSession(session.id)
            
        } catch {
            uploadStatus = .failed(error.localizedDescription)
            throw error
        }
    }
    
    /// 대기 중인 모든 세션 업로드
    func uploadAllPendingSessions() async {
        guard !pendingSessions.isEmpty else { return }
        
        for session in pendingSessions {
            do {
                try await uploadSession(session)
            } catch {
                print("❌ Failed to upload session \(session.id): \(error)")
                // 계속 진행
            }
        }
    }
    
    /// 대기 세션 추가
    func addPendingSession(_ session: PendingSleepSession) {
        pendingSessions.append(session)
        pendingSessionCount = pendingSessions.count
        savePendingSessions()
    }
    
    /// 재시도
    func retryUpload() async {
        guard case .failed = uploadStatus else { return }
        uploadStatus = .idle
        await uploadAllPendingSessions()
    }
    
    // MARK: - Private Methods
    
    private func processSleepEndedFromWatch() async {
        do {
            try await createAndUploadSession()
        } catch {
            print("❌ Failed to process watch sleep data: \(error)")
        }
    }
    
    private func createSessionFromSensorData(_ packets: [SensorDataPacket]) -> PendingSleepSession {
        guard let firstPacket = packets.first, let lastPacket = packets.last else {
            return PendingSleepSession(
                id: UUID(),
                startTime: Date(),
                endTime: Date(),
                sensorData: []
            )
        }
        
        // 센서 타입별로 그룹화
        let groupedData = Dictionary(grouping: packets, by: { $0.type })
        
        // 센서 데이터 변환
        var sensorDataItems: [SensorDataItem] = []
        
        for (type, samples) in groupedData {
            for sample in samples {
                sensorDataItems.append(SensorDataItem(
                    type: type.rawValue,
                    timestamp: sample.timestamp,
                    value: sample.value,
                    metadata: sample.metadata
                ))
            }
        }
        
        return PendingSleepSession(
            id: UUID(),
            startTime: firstPacket.timestamp,
            endTime: lastPacket.timestamp,
            sensorData: sensorDataItems
        )
    }
    
    private func createServerSession(_ session: PendingSleepSession) async throws -> CreateSessionResponse {
        // API를 통해 새 세션 생성
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        
        let body: [String: Any] = [
            "session_date": dateFormatter.string(from: session.startTime),
            "start_time": ISO8601DateFormatter().string(from: session.startTime),
            "end_time": ISO8601DateFormatter().string(from: session.endTime),
            "source": "apple_watch"
        ]
        
        // TODO: 실제 API 호출 구현
        // 현재는 더미 응답 반환
        return CreateSessionResponse(sessionId: Int.random(in: 1000...9999), status: "created")
    }
    
    private func uploadSensorData(sessionId: Int, data: [SensorDataItem]) async throws {
        // 청크 단위로 업로드 (500개씩)
        let chunkSize = 500
        let chunks = stride(from: 0, to: data.count, by: chunkSize).map {
            Array(data[$0..<min($0 + chunkSize, data.count)])
        }
        
        for (index, chunk) in chunks.enumerated() {
            // TODO: 실제 API 호출
            // try await apiService.uploadSensorChunk(sessionId: sessionId, data: chunk)
            
            // 진행률 업데이트
            let baseProgress = 0.4
            let uploadRange = 0.4 // 0.4 ~ 0.8
            let chunkProgress = Double(index + 1) / Double(chunks.count)
            uploadProgress = baseProgress + (uploadRange * chunkProgress)
            
            // 시뮬레이션 딜레이
            try await Task.sleep(nanoseconds: 100_000_000)
        }
    }
    
    private func loadPendingSessions() {
        // UserDefaults에서 대기 세션 로드
        if let data = UserDefaults.standard.data(forKey: "pendingSessions"),
           let sessions = try? JSONDecoder().decode([PendingSleepSession].self, from: data) {
            pendingSessions = sessions
            pendingSessionCount = sessions.count
        }
    }
    
    private func savePendingSessions() {
        if let data = try? JSONEncoder().encode(pendingSessions) {
            UserDefaults.standard.set(data, forKey: "pendingSessions")
        }
    }
    
    private func removePendingSession(_ id: UUID) {
        pendingSessions.removeAll { $0.id == id }
        pendingSessionCount = pendingSessions.count
        savePendingSessions()
    }
}

// MARK: - Supporting Types

/// 업로드 상태
enum UploadStatus: Equatable {
    case idle
    case preparing
    case uploading
    case completed
    case failed(String)
    
    var displayText: String {
        switch self {
        case .idle: return "대기 중"
        case .preparing: return "준비 중..."
        case .uploading: return "업로드 중..."
        case .completed: return "완료"
        case .failed(let error): return "실패: \(error)"
        }
    }
    
    var isInProgress: Bool {
        switch self {
        case .preparing, .uploading: return true
        default: return false
        }
    }
}

/// 업로드 에러
enum UploadError: LocalizedError {
    case noData
    case networkError(Error)
    case serverError(String)
    case unauthorized
    
    var errorDescription: String? {
        switch self {
        case .noData: return "업로드할 데이터가 없습니다."
        case .networkError(let error): return "네트워크 오류: \(error.localizedDescription)"
        case .serverError(let message): return "서버 오류: \(message)"
        case .unauthorized: return "로그인이 필요합니다."
        }
    }
}

/// 대기 중인 수면 세션
struct PendingSleepSession: Codable, Identifiable {
    let id: UUID
    let startTime: Date
    let endTime: Date
    let sensorData: [SensorDataItem]
    
    var durationMinutes: Int {
        Int(endTime.timeIntervalSince(startTime) / 60)
    }
}

/// 센서 데이터 아이템
struct SensorDataItem: Codable {
    let type: String
    let timestamp: Date
    let value: Double
    let metadata: [String: AnyCodableValue]?
    
    init(type: String, timestamp: Date, value: Double, metadata: [String: Any]?) {
        self.type = type
        self.timestamp = timestamp
        self.value = value
        self.metadata = metadata?.mapValues { AnyCodableValue($0) }
    }
}

/// Codable을 위한 Any 래퍼
struct AnyCodableValue: Codable {
    let value: Any
    
    init(_ value: Any) {
        self.value = value
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if let string = try? container.decode(String.self) {
            value = string
        } else {
            value = NSNull()
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch value {
        case let bool as Bool: try container.encode(bool)
        case let int as Int: try container.encode(int)
        case let double as Double: try container.encode(double)
        case let string as String: try container.encode(string)
        default: try container.encodeNil()
        }
    }
}

/// 세션 생성 응답
struct CreateSessionResponse: Codable {
    let sessionId: Int
    let status: String
    
    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case status
    }
}
