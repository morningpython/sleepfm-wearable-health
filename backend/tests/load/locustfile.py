"""
Locust 부하 테스트 스크립트

API 성능 및 동시 사용자 처리 능력 테스트
실행: locust -f tests/load/locustfile.py --host=http://localhost:8000
"""

import json
import random
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner


class SleepFMUser(HttpUser):
    """SleepFM API 부하 테스트 사용자"""
    
    # 요청 간 대기 시간 (1-5초)
    wait_time = between(1, 5)
    
    # 사용자별 데이터
    access_token: str = None
    refresh_token: str = None
    user_id: int = None
    session_ids: list = []
    
    def on_start(self):
        """테스트 시작 시 실행 - 사용자 등록 및 로그인"""
        self._register_and_login()
    
    def _register_and_login(self):
        """사용자 등록 또는 로그인"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        email = f"loadtest_{timestamp}@test.com"
        password = "TestPassword123!"
        
        # 등록 시도
        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "username": f"loadtest_{timestamp[:10]}",
                "password": password,
            },
            name="/api/v1/auth/register",
        )
        
        # 로그인
        login_response = self.client.post(
            "/api/v1/auth/token",
            json={
                "email": email,
                "password": password,
            },
            name="/api/v1/auth/token",
        )
        
        if login_response.status_code == 200:
            data = login_response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            self.user_id = data.get("user", {}).get("id")
    
    def _get_auth_header(self) -> dict:
        """인증 헤더 반환"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    # ========================================
    # 인증 관련 태스크
    # ========================================
    
    @task(1)
    def refresh_token_task(self):
        """토큰 갱신"""
        if self.refresh_token:
            response = self.client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": self.refresh_token},
                name="/api/v1/auth/refresh",
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
    
    # ========================================
    # 세션 관련 태스크
    # ========================================
    
    @task(5)
    def get_sessions(self):
        """세션 목록 조회 (가장 빈번한 요청)"""
        self.client.get(
            "/api/v1/sessions",
            headers=self._get_auth_header(),
            name="/api/v1/sessions",
        )
    
    @task(2)
    def upload_session(self):
        """세션 업로드"""
        if not self.access_token:
            return
        
        # 테스트 센서 데이터 생성
        sensor_data = self._generate_sensor_data()
        
        response = self.client.post(
            "/api/v1/sessions/upload",
            json=sensor_data,
            headers=self._get_auth_header(),
            name="/api/v1/sessions/upload",
        )
        
        if response.status_code in [200, 201]:
            session_id = response.json().get("session_id")
            if session_id:
                self.session_ids.append(session_id)
    
    @task(3)
    def get_session_detail(self):
        """세션 상세 조회"""
        if self.session_ids:
            session_id = random.choice(self.session_ids)
            self.client.get(
                f"/api/v1/sessions/{session_id}",
                headers=self._get_auth_header(),
                name="/api/v1/sessions/{id}",
            )
    
    # ========================================
    # 분석 관련 태스크
    # ========================================
    
    @task(4)
    def analyze_sleep_stages(self):
        """수면 단계 분석"""
        if not self.session_ids:
            return
        
        session_id = random.choice(self.session_ids)
        self.client.post(
            "/api/v1/analysis/sleep-stages",
            json={"session_id": session_id},
            headers=self._get_auth_header(),
            name="/api/v1/analysis/sleep-stages",
        )
    
    @task(3)
    def analyze_apnea(self):
        """무호흡 분석"""
        if not self.session_ids:
            return
        
        session_id = random.choice(self.session_ids)
        self.client.post(
            "/api/v1/analysis/apnea",
            json={"session_id": session_id},
            headers=self._get_auth_header(),
            name="/api/v1/analysis/apnea",
        )
    
    @task(2)
    def analyze_disease_risk(self):
        """질병 위험 예측"""
        if not self.session_ids:
            return
        
        session_id = random.choice(self.session_ids)
        self.client.post(
            "/api/v1/analysis/disease-risk",
            json={"session_id": session_id},
            headers=self._get_auth_header(),
            name="/api/v1/analysis/disease-risk",
        )
    
    @task(2)
    def integrated_analysis(self):
        """통합 분석"""
        if not self.session_ids:
            return
        
        session_id = random.choice(self.session_ids)
        self.client.post(
            "/api/v1/analysis/integrated",
            json={"session_id": session_id},
            headers=self._get_auth_header(),
            name="/api/v1/analysis/integrated",
        )
    
    # ========================================
    # 히스토리 관련 태스크
    # ========================================
    
    @task(3)
    def get_history(self):
        """분석 히스토리 조회"""
        self.client.get(
            "/api/v1/history/results",
            headers=self._get_auth_header(),
            name="/api/v1/history/results",
        )
    
    @task(2)
    def get_session_results(self):
        """세션별 분석 결과 조회"""
        if self.session_ids:
            session_id = random.choice(self.session_ids)
            self.client.get(
                f"/api/v1/history/sessions/{session_id}/results",
                headers=self._get_auth_header(),
                name="/api/v1/history/sessions/{id}/results",
            )
    
    # ========================================
    # 헬스체크 태스크
    # ========================================
    
    @task(10)
    def health_check(self):
        """헬스체크 (가장 빈번)"""
        self.client.get("/health", name="/health")
    
    @task(1)
    def root_endpoint(self):
        """루트 엔드포인트"""
        self.client.get("/", name="/")
    
    # ========================================
    # 헬퍼 메서드
    # ========================================
    
    def _generate_sensor_data(self) -> dict:
        """테스트용 센서 데이터 생성"""
        now = datetime.utcnow()
        
        # 8시간 수면 데이터 시뮬레이션 (30초 에폭 = 960개 데이터포인트)
        epochs = 960
        
        return {
            "session_date": (now - timedelta(hours=8)).isoformat(),
            "device_type": random.choice(["apple_watch", "fitbit", "garmin"]),
            "sensor_data": {
                "heart_rate": [random.randint(50, 80) for _ in range(epochs)],
                "spo2": [random.randint(94, 99) for _ in range(epochs)],
                "movement": [random.uniform(0, 1) for _ in range(epochs)],
                "timestamps": [
                    (now - timedelta(hours=8) + timedelta(seconds=30*i)).isoformat()
                    for i in range(epochs)
                ],
            },
            "metadata": {
                "firmware_version": "1.0.0",
                "app_version": "1.0.0",
            },
        }


class HighLoadUser(SleepFMUser):
    """고부하 테스트용 사용자 (더 짧은 대기 시간)"""
    wait_time = between(0.1, 0.5)


# ========================================
# 이벤트 핸들러
# ========================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """테스트 시작 시 실행"""
    if isinstance(environment.runner, MasterRunner):
        print("마스터 노드에서 테스트 시작")
    else:
        print("테스트 시작")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """테스트 종료 시 실행"""
    print("테스트 종료")
    
    # 통계 출력
    if environment.stats.total.num_requests > 0:
        print(f"\n=== 테스트 결과 요약 ===")
        print(f"총 요청 수: {environment.stats.total.num_requests}")
        print(f"실패 수: {environment.stats.total.num_failures}")
        print(f"평균 응답 시간: {environment.stats.total.avg_response_time:.2f}ms")
        print(f"95% 응답 시간: {environment.stats.total.get_response_time_percentile(0.95):.2f}ms")
        print(f"99% 응답 시간: {environment.stats.total.get_response_time_percentile(0.99):.2f}ms")
        print(f"RPS: {environment.stats.total.current_rps:.2f}")
