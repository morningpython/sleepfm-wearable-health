//
//  KeychainService.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation
import Security

/// Keychain 서비스 - 보안 토큰 저장
final class KeychainService {
    // MARK: - Singleton
    
    static let shared = KeychainService()
    
    // MARK: - Keys
    
    private enum Keys {
        static let accessToken = "com.sleepfm.accessToken"
        static let refreshToken = "com.sleepfm.refreshToken"
        static let userId = "com.sleepfm.userId"
    }
    
    // MARK: - Initialization
    
    private init() {}
    
    // MARK: - Access Token
    
    /// Access Token 저장
    func saveAccessToken(_ token: String) {
        save(key: Keys.accessToken, value: token)
    }
    
    /// Access Token 가져오기
    func getAccessToken() -> String? {
        return get(key: Keys.accessToken)
    }
    
    /// Access Token 삭제
    func deleteAccessToken() {
        delete(key: Keys.accessToken)
    }
    
    // MARK: - Refresh Token
    
    /// Refresh Token 저장
    func saveRefreshToken(_ token: String) {
        save(key: Keys.refreshToken, value: token)
    }
    
    /// Refresh Token 가져오기
    func getRefreshToken() -> String? {
        return get(key: Keys.refreshToken)
    }
    
    /// Refresh Token 삭제
    func deleteRefreshToken() {
        delete(key: Keys.refreshToken)
    }
    
    // MARK: - User ID
    
    /// User ID 저장
    func saveUserId(_ userId: Int) {
        save(key: Keys.userId, value: String(userId))
    }
    
    /// User ID 가져오기
    func getUserId() -> Int? {
        guard let value = get(key: Keys.userId) else { return nil }
        return Int(value)
    }
    
    /// User ID 삭제
    func deleteUserId() {
        delete(key: Keys.userId)
    }
    
    // MARK: - Clear All
    
    /// 모든 인증 정보 삭제
    func clearAll() {
        deleteAccessToken()
        deleteRefreshToken()
        deleteUserId()
    }
    
    // MARK: - Private Methods
    
    private func save(key: String, value: String) {
        guard let data = value.data(using: .utf8) else { return }
        
        // 기존 항목 삭제
        delete(key: key)
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]
        
        let status = SecItemAdd(query as CFDictionary, nil)
        
        if status != errSecSuccess {
            print("Keychain save error: \(status)")
        }
    }
    
    private func get(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess,
              let data = result as? Data,
              let value = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return value
    }
    
    private func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}
