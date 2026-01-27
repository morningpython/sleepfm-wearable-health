//
//  APIService.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation

/// API 에러 타입
enum APIError: Error, LocalizedError {
    case invalidURL
    case networkError(Error)
    case serverError(statusCode: Int, message: String?)
    case decodingError(Error)
    case unauthorized
    case notFound
    case validationError(String)
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "잘못된 URL입니다."
        case .networkError(let error):
            return "네트워크 오류: \(error.localizedDescription)"
        case .serverError(let statusCode, let message):
            return message ?? "서버 오류 (\(statusCode))"
        case .decodingError:
            return "데이터 처리 오류가 발생했습니다."
        case .unauthorized:
            return "인증이 필요합니다."
        case .notFound:
            return "요청한 리소스를 찾을 수 없습니다."
        case .validationError(let message):
            return message
        case .unknown:
            return "알 수 없는 오류가 발생했습니다."
        }
    }
}

/// API 서비스
actor APIService {
    // MARK: - Singleton
    
    static let shared = APIService()
    
    // MARK: - Properties
    
    private let baseURL: String
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    
    // MARK: - Initialization
    
    private init() {
        // TODO: 환경별 설정
        #if DEBUG
        self.baseURL = "http://localhost:8000/api/v1"
        #else
        self.baseURL = "https://api.sleepfm.com/api/v1"
        #endif
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
        
        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)
            
            // ISO8601 with fractional seconds
            let formatter = ISO8601DateFormatter()
            formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            if let date = formatter.date(from: dateString) {
                return date
            }
            
            // ISO8601 without fractional seconds
            formatter.formatOptions = [.withInternetDateTime]
            if let date = formatter.date(from: dateString) {
                return date
            }
            
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Cannot decode date: \(dateString)"
            )
        }
        
        self.encoder = JSONEncoder()
        self.encoder.dateEncodingStrategy = .iso8601
    }
    
    // MARK: - Auth Endpoints
    
    /// 회원가입
    func signUp(email: String, username: String, password: String, fullName: String?) async throws -> AuthResponse {
        let body: [String: Any] = [
            "email": email,
            "username": username,
            "password": password,
            "full_name": fullName ?? NSNull()
        ]
        
        return try await post(endpoint: "/auth/register", body: body)
    }
    
    /// 로그인
    func login(email: String, password: String) async throws -> AuthResponse {
        let body = [
            "email": email,
            "password": password
        ]
        
        return try await post(endpoint: "/auth/login", body: body)
    }
    
    /// 토큰 갱신
    func refreshToken(refreshToken: String) async throws -> TokenResponse {
        let body = ["refresh_token": refreshToken]
        return try await post(endpoint: "/auth/refresh", body: body)
    }
    
    /// 현재 사용자 정보
    func getCurrentUser() async throws -> User {
        return try await get(endpoint: "/auth/me", authenticated: true)
    }
    
    // MARK: - Sleep Session Endpoints
    
    /// 세션 목록 조회
    func getSessions(
        userId: Int,
        limit: Int = 10,
        offset: Int = 0,
        startDate: Date? = nil,
        endDate: Date? = nil
    ) async throws -> SessionListResponse {
        var queryItems = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]
        
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        
        if let startDate = startDate {
            queryItems.append(URLQueryItem(name: "start_date", value: dateFormatter.string(from: startDate)))
        }
        
        if let endDate = endDate {
            queryItems.append(URLQueryItem(name: "end_date", value: dateFormatter.string(from: endDate)))
        }
        
        return try await get(
            endpoint: "/users/\(userId)/sessions",
            queryItems: queryItems,
            authenticated: true
        )
    }
    
    /// 세션 결과 조회
    func getSessionResults(sessionId: Int) async throws -> SessionResultsResponse {
        return try await get(endpoint: "/sessions/\(sessionId)/results", authenticated: true)
    }
    
    // MARK: - Analysis Endpoints
    
    /// 통합 분석 요청
    func requestAnalysis(sessionId: Int) async throws -> IntegratedAnalysisResponse {
        let body = ["session_id": sessionId]
        return try await post(endpoint: "/analyze", body: body, authenticated: true)
    }
    
    /// 질병 위험 분석
    func analyzeDiseaseRisk(sessionId: Int) async throws -> DiseaseRiskResponse {
        let body = ["session_id": sessionId]
        return try await post(endpoint: "/analyze/disease-risk", body: body, authenticated: true)
    }
    
    // MARK: - Private Methods
    
    private func get<T: Decodable>(
        endpoint: String,
        queryItems: [URLQueryItem] = [],
        authenticated: Bool = false
    ) async throws -> T {
        guard var components = URLComponents(string: baseURL + endpoint) else {
            throw APIError.invalidURL
        }
        
        if !queryItems.isEmpty {
            components.queryItems = queryItems
        }
        
        guard let url = components.url else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if authenticated {
            guard let token = KeychainService.shared.getAccessToken() else {
                throw APIError.unauthorized
            }
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        return try await performRequest(request)
    }
    
    private func post<T: Decodable>(
        endpoint: String,
        body: [String: Any],
        authenticated: Bool = false
    ) async throws -> T {
        guard let url = URL(string: baseURL + endpoint) else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        if authenticated {
            guard let token = KeychainService.shared.getAccessToken() else {
                throw APIError.unauthorized
            }
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        return try await performRequest(request)
    }
    
    private func performRequest<T: Decodable>(_ request: URLRequest) async throws -> T {
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.unknown
        }
        
        switch httpResponse.statusCode {
        case 200...299:
            do {
                return try decoder.decode(T.self, from: data)
            } catch {
                throw APIError.decodingError(error)
            }
            
        case 401:
            throw APIError.unauthorized
            
        case 404:
            throw APIError.notFound
            
        case 422:
            // Validation error
            if let errorResponse = try? decoder.decode(ValidationErrorResponse.self, from: data) {
                throw APIError.validationError(errorResponse.detail.first?.msg ?? "검증 오류")
            }
            throw APIError.validationError("입력값이 올바르지 않습니다.")
            
        default:
            let message = String(data: data, encoding: .utf8)
            throw APIError.serverError(statusCode: httpResponse.statusCode, message: message)
        }
    }
}

// MARK: - Response Types

struct SessionListResponse: Codable {
    let sessions: [SessionSummary]
    let total: Int
    let limit: Int
    let offset: Int
}

struct SessionSummary: Codable, Identifiable {
    let id: Int
    let sessionDate: String
    let durationHours: Double?
    let analysisStatus: String
    let hasResults: Bool
    
    enum CodingKeys: String, CodingKey {
        case id
        case sessionDate = "session_date"
        case durationHours = "duration_hours"
        case analysisStatus = "analysis_status"
        case hasResults = "has_results"
    }
}

struct SessionResultsResponse: Codable {
    let sessionId: Int
    let sessionDate: String
    let durationHours: Double?
    let analysisStatus: String
    let analyses: [AnalysisItem]
    
    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case sessionDate = "session_date"
        case durationHours = "duration_hours"
        case analysisStatus = "analysis_status"
        case analyses
    }
}

struct AnalysisItem: Codable, Identifiable {
    let id: Int
    let type: String
    let result: [String: AnyCodable]
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case type
        case result
        case createdAt = "created_at"
    }
}

struct IntegratedAnalysisResponse: Codable {
    let sessionId: Int
    let analysisStatus: String
    let createdAt: String
    let sleepSummary: SleepSummary?
    let sleepStages: SleepStagesResult?
    let apnea: ApneaResult?
    let diseaseRisk: DiseaseRiskResult?
    
    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case analysisStatus = "analysis_status"
        case createdAt = "created_at"
        case sleepSummary = "sleep_summary"
        case sleepStages = "sleep_stages"
        case apnea
        case diseaseRisk = "disease_risk"
    }
}

struct SleepSummary: Codable {
    let totalTimeMinutes: Double
    let totalSleepTimeMinutes: Double
    let sleepEfficiency: Double
    let sleepOnsetLatency: Double
    let wakeAfterSleepOnset: Double
    
    enum CodingKeys: String, CodingKey {
        case totalTimeMinutes = "total_time_minutes"
        case totalSleepTimeMinutes = "total_sleep_time_minutes"
        case sleepEfficiency = "sleep_efficiency"
        case sleepOnsetLatency = "sleep_onset_latency"
        case wakeAfterSleepOnset = "wake_after_sleep_onset"
    }
}

struct SleepStagesResult: Codable {
    let stageDurations: [String: Double]
    
    enum CodingKeys: String, CodingKey {
        case stageDurations = "stage_durations"
    }
}

struct ApneaResult: Codable {
    let ahi: Double
    let severity: String
    let eventCount: Int
    let recommendations: [String]
    
    enum CodingKeys: String, CodingKey {
        case ahi
        case severity
        case eventCount = "event_count"
        case recommendations
    }
}

struct DiseaseRiskResult: Codable {
    let predictions: [DiseasePrediction]
}

struct DiseaseRiskResponse: Codable {
    let analysisId: Int
    let sessionId: Int
    let predictions: [DiseasePrediction]
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case analysisId = "analysis_id"
        case sessionId = "session_id"
        case predictions
        case createdAt = "created_at"
    }
}

struct ValidationErrorResponse: Codable {
    let detail: [ValidationErrorDetail]
}

struct ValidationErrorDetail: Codable {
    let loc: [String]
    let msg: String
    let type: String
}

// MARK: - AnyCodable Helper

struct AnyCodable: Codable {
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
        } else if let array = try? container.decode([AnyCodable].self) {
            value = array.map { $0.value }
        } else if let dict = try? container.decode([String: AnyCodable].self) {
            value = dict.mapValues { $0.value }
        } else {
            value = NSNull()
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch value {
        case let bool as Bool:
            try container.encode(bool)
        case let int as Int:
            try container.encode(int)
        case let double as Double:
            try container.encode(double)
        case let string as String:
            try container.encode(string)
        case let array as [Any]:
            try container.encode(array.map { AnyCodable($0) })
        case let dict as [String: Any]:
            try container.encode(dict.mapValues { AnyCodable($0) })
        default:
            try container.encodeNil()
        }
    }
}
