//
//  AuthManager.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation
import Combine

/// 인증 상태 관리자
@MainActor
class AuthManager: ObservableObject {
    // MARK: - Published Properties
    
    /// 인증 여부
    @Published var isAuthenticated: Bool = false
    
    /// 현재 사용자
    @Published var currentUser: User?
    
    /// 온보딩 완료 여부
    @Published var hasSeenOnboarding: Bool = false
    
    /// 로딩 상태
    @Published var isLoading: Bool = false
    
    /// 에러 메시지
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    private let keychainService: KeychainService
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Constants
    
    private let onboardingKey = "hasSeenOnboarding"
    
    // MARK: - Initialization
    
    init(
        apiService: APIService = APIService.shared,
        keychainService: KeychainService = KeychainService.shared
    ) {
        self.apiService = apiService
        self.keychainService = keychainService
        
        // 저장된 상태 복원
        self.hasSeenOnboarding = UserDefaults.standard.bool(forKey: onboardingKey)
        
        // 토큰 존재 시 자동 로그인 시도
        if keychainService.getAccessToken() != nil {
            Task {
                await refreshAuthentication()
            }
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
            keychainService.saveAccessToken(response.accessToken)
            keychainService.saveRefreshToken(response.refreshToken)
            
            // 사용자 정보 저장
            currentUser = response.user
            isAuthenticated = true
            isLoading = false
            
            return true
        } catch let error as APIError {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        } catch {
            errorMessage = "회원가입에 실패했습니다."
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
            keychainService.saveAccessToken(response.accessToken)
            keychainService.saveRefreshToken(response.refreshToken)
            
            // 사용자 정보 저장
            currentUser = response.user
            isAuthenticated = true
            isLoading = false
            
            return true
        } catch let error as APIError {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        } catch {
            errorMessage = "로그인에 실패했습니다."
            isLoading = false
            return false
        }
    }
    
    /// 로그아웃
    func logout() {
        keychainService.clearTokens()
        currentUser = nil
        isAuthenticated = false
    }
    
    /// 온보딩 완료 표시
    func completeOnboarding() {
        hasSeenOnboarding = true
        UserDefaults.standard.set(true, forKey: onboardingKey)
    }
    
    /// 인증 상태 새로고침
    func refreshAuthentication() async {
        guard let refreshToken = keychainService.getRefreshToken() else {
            isAuthenticated = false
            return
        }
        
        do {
            let response = try await apiService.refreshToken(refreshToken: refreshToken)
            keychainService.saveAccessToken(response.accessToken)
            keychainService.saveRefreshToken(response.refreshToken)
            
            // 현재 사용자 정보 가져오기
            let user = try await apiService.getCurrentUser()
            currentUser = user
            isAuthenticated = true
        } catch {
            // 토큰 만료 - 로그아웃 처리
            logout()
        }
    }
}
