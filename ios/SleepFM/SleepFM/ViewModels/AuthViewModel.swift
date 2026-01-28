//
//  AuthViewModel.swift
//  SleepFM
//
//  인증 상태 관리 ViewModel
//

import Foundation
import Combine

/// 인증 뷰모델
@MainActor
final class AuthViewModel: ObservableObject {
    
    // MARK: - Singleton
    
    static let shared = AuthViewModel()
    
    // MARK: - Published Properties
    
    /// 현재 사용자
    @Published private(set) var currentUser: User?
    
    /// 로그인 상태
    @Published private(set) var isLoggedIn = false
    
    /// 로딩 상태
    @Published var isLoading = false
    
    /// 에러 메시지
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    private let keychainService: KeychainService
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    private init(
        apiService: APIService = .shared,
        keychainService: KeychainService = .shared
    ) {
        self.apiService = apiService
        self.keychainService = keychainService
        
        // 저장된 토큰으로 자동 로그인 시도
        Task {
            await checkAuthStatus()
        }
    }
    
    // MARK: - Public Methods
    
    /// 회원가입
    func signUp(email: String, username: String, password: String, fullName: String?) async -> Bool {
        isLoading = true
        errorMessage = nil
        
        do {
            let response = try await apiService.signUp(
                email: email,
                username: username,
                password: password,
                fullName: fullName
            )
            
            // 토큰 저장
            saveTokens(response.token)
            
            // 사용자 정보 설정
            currentUser = response.user
            isLoggedIn = true
            
            // Watch에 로그인 상태 전송
            updateWatchLoginStatus()
            
            isLoading = false
            return true
            
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
    
    /// 로그인
    func login(email: String, password: String) async -> Bool {
        isLoading = true
        errorMessage = nil
        
        do {
            let response = try await apiService.login(email: email, password: password)
            
            // 토큰 저장
            saveTokens(response.token)
            
            // 사용자 정보 설정
            currentUser = response.user
            isLoggedIn = true
            
            // Watch에 로그인 상태 전송
            updateWatchLoginStatus()
            
            isLoading = false
            return true
            
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }
    
    /// 로그아웃
    func logout() {
        keychainService.deleteTokens()
        currentUser = nil
        isLoggedIn = false
        
        // Watch에 로그아웃 상태 전송
        updateWatchLoginStatus()
    }
    
    /// 토큰 갱신
    func refreshTokenIfNeeded() async -> Bool {
        guard let refreshToken = keychainService.getRefreshToken() else {
            return false
        }
        
        do {
            let response = try await apiService.refreshToken(refreshToken: refreshToken)
            saveTokens(response)
            return true
        } catch {
            // 갱신 실패 시 로그아웃
            logout()
            return false
        }
    }
    
    /// 인증 상태 확인
    func checkAuthStatus() async {
        guard keychainService.getAccessToken() != nil else {
            isLoggedIn = false
            return
        }
        
        do {
            currentUser = try await apiService.getCurrentUser()
            isLoggedIn = true
            updateWatchLoginStatus()
        } catch {
            // 토큰 갱신 시도
            if await refreshTokenIfNeeded() {
                do {
                    currentUser = try await apiService.getCurrentUser()
                    isLoggedIn = true
                    updateWatchLoginStatus()
                } catch {
                    logout()
                }
            } else {
                logout()
            }
        }
    }
    
    // MARK: - Private Methods
    
    private func saveTokens(_ tokenResponse: TokenResponse) {
        keychainService.saveAccessToken(tokenResponse.accessToken)
        keychainService.saveRefreshToken(tokenResponse.refreshToken)
    }
    
    private func updateWatchLoginStatus() {
        PhoneConnectivityManager.shared.updatePhoneStatus(
            isLoggedIn: isLoggedIn,
            userName: currentUser?.username
        )
    }
}

// MARK: - Response Types (if not defined elsewhere)

/// 인증 응답
struct AuthResponse: Codable {
    let user: User
    let token: TokenResponse
}

/// 토큰 응답
struct TokenResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    let expiresIn: Int
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case tokenType = "token_type"
        case expiresIn = "expires_in"
    }
}

/// 사용자 모델
struct User: Codable, Identifiable {
    let id: Int
    let email: String
    let username: String
    let fullName: String?
    let profileImage: String?
    let createdAt: String
    let isActive: Bool
    
    enum CodingKeys: String, CodingKey {
        case id
        case email
        case username
        case fullName = "full_name"
        case profileImage = "profile_image"
        case createdAt = "created_at"
        case isActive = "is_active"
    }
}
