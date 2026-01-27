//
//  User.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation

/// 사용자 모델
struct User: Codable, Identifiable, Equatable {
    let id: Int
    let email: String
    let username: String
    let fullName: String?
    let isActive: Bool
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case email
        case username
        case fullName = "full_name"
        case isActive = "is_active"
        case createdAt = "created_at"
    }
}

/// 인증 응답
struct AuthResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    let user: User
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case tokenType = "token_type"
        case user
    }
}

/// 토큰 응답
struct TokenResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case tokenType = "token_type"
    }
}
