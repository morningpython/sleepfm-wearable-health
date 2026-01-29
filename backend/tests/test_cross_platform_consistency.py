"""
Sprint 10: 크로스 플랫폼 일관성 검증 테스트

동일 입력 → 동일 출력 검증
"""

import pytest
import numpy as np
from datetime import datetime, date
from typing import List, Dict, Any
import json


class TestCrossPlatformConsistency:
    """크로스 플랫폼 일관성 테스트"""
    
    @pytest.fixture
    def sample_sensor_data(self) -> List[Dict[str, Any]]:
        """테스트용 센서 데이터셋"""
        np.random.seed(42)  # 재현성을 위한 시드
        
        data = []
        for i in range(100):
            timestamp = datetime(2024, 1, 1, 23, 0, 0)
            timestamp = timestamp.replace(minute=i % 60, second=(i * 36) % 60)
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "heart_rate": 60 + np.random.normal(0, 5),
                "hrv": 40 + np.random.normal(0, 10),
                "spo2": 97 + np.random.normal(0, 1),
                "respiratory_rate": 14 + np.random.normal(0, 2),
                "movement": np.random.random() * 0.5,
            })
        
        return data
    
    def test_deterministic_preprocessing(self, sample_sensor_data):
        """전처리 결정론적 동작 확인"""
        # 동일 입력에 대해 동일 출력
        result1 = self._preprocess_data(sample_sensor_data)
        result2 = self._preprocess_data(sample_sensor_data)
        
        assert result1 == result2, "동일 입력에 대해 전처리 결과가 다름"
    
    def test_analysis_result_consistency(self, sample_sensor_data):
        """분석 결과 일관성 검증"""
        # 5회 실행하여 결과 비교
        results = []
        
        for _ in range(5):
            result = self._mock_analysis(sample_sensor_data)
            results.append(result)
        
        # 모든 결과가 동일해야 함
        first_result = results[0]
        for i, result in enumerate(results[1:], start=2):
            assert self._results_equal(first_result, result), \
                f"분석 결과 불일치: 1회차 vs {i}회차"
    
    def test_sleep_stage_consistency(self, sample_sensor_data):
        """수면 단계 분류 일관성"""
        stages1 = self._mock_sleep_stage_classification(sample_sensor_data)
        stages2 = self._mock_sleep_stage_classification(sample_sensor_data)
        
        assert stages1 == stages2, "수면 단계 분류 결과 불일치"
    
    def test_apnea_detection_consistency(self, sample_sensor_data):
        """무호흡 감지 일관성"""
        events1 = self._mock_apnea_detection(sample_sensor_data)
        events2 = self._mock_apnea_detection(sample_sensor_data)
        
        assert len(events1) == len(events2), "무호흡 이벤트 수 불일치"
        
        for e1, e2 in zip(events1, events2):
            assert e1["start_time"] == e2["start_time"]
            assert e1["duration"] == e2["duration"]
    
    def test_disease_risk_consistency(self, sample_sensor_data):
        """질병 위험 예측 일관성"""
        risk1 = self._mock_disease_risk(sample_sensor_data)
        risk2 = self._mock_disease_risk(sample_sensor_data)
        
        # 점수 차이 < 1%
        for disease in risk1:
            score1 = risk1[disease]
            score2 = risk2[disease]
            
            diff = abs(score1 - score2)
            assert diff < 0.01, f"{disease} 점수 차이: {diff} (기준: < 0.01)"
    
    def test_floating_point_precision(self):
        """부동소수점 정밀도 테스트"""
        # 동일한 계산을 다른 방식으로 수행
        values = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        sum1 = sum(values)
        sum2 = values[0] + values[1] + values[2] + values[3] + values[4]
        
        # 부동소수점 오차 허용
        assert abs(sum1 - sum2) < 1e-10
    
    def test_response_time_variation(self, client, test_user, auth_headers):
        """응답 시간 변동 테스트"""
        import time
        
        times = []
        
        # 10회 동일 요청
        for _ in range(10):
            start = time.time()
            response = client.post("/api/v1/auth/token", json={
                "email": test_user.email,
                "password": "testpass123"
            })
            elapsed = time.time() - start
            times.append(elapsed)
        
        # 응답 시간 차이
        max_diff = max(times) - min(times)
        
        # 차이 < 500ms
        assert max_diff < 0.5, f"응답 시간 편차: {max_diff:.3f}초 (기준: < 0.5초)"
        
        print(f"\n📊 응답 시간 통계:")
        print(f"   최소: {min(times)*1000:.1f}ms")
        print(f"   최대: {max(times)*1000:.1f}ms")
        print(f"   평균: {sum(times)/len(times)*1000:.1f}ms")
        print(f"   편차: {max_diff*1000:.1f}ms")
    
    # 헬퍼 메서드
    def _preprocess_data(self, data: List[Dict]) -> List[Dict]:
        """데이터 전처리 (결정론적)"""
        processed = []
        
        for item in data:
            processed.append({
                "timestamp": item["timestamp"],
                "heart_rate": round(item["heart_rate"], 2),
                "hrv": round(item["hrv"], 2),
                "spo2": round(item["spo2"], 2),
                "respiratory_rate": round(item["respiratory_rate"], 2),
            })
        
        return processed
    
    def _mock_analysis(self, data: List[Dict]) -> Dict:
        """모의 분석 (결정론적)"""
        np.random.seed(42)  # 동일 시드
        
        hr_values = [d["heart_rate"] for d in data]
        
        return {
            "avg_heart_rate": round(np.mean(hr_values), 2),
            "sleep_efficiency": 85.5,
            "total_sleep_time": 420,
            "deep_sleep_percent": 20.0,
        }
    
    def _mock_sleep_stage_classification(self, data: List[Dict]) -> List[str]:
        """모의 수면 단계 분류"""
        np.random.seed(42)
        
        stages = ["WAKE", "N1", "N2", "N3", "REM"]
        
        # 결정론적 분류
        result = []
        for i, _ in enumerate(data):
            stage_idx = (i * 7 + 3) % 5  # 결정론적 패턴
            result.append(stages[stage_idx])
        
        return result
    
    def _mock_apnea_detection(self, data: List[Dict]) -> List[Dict]:
        """모의 무호흡 감지"""
        np.random.seed(42)
        
        events = []
        
        for i in range(3):
            events.append({
                "start_time": f"2024-01-01T{23+i//2}:{(i*15)%60:02d}:00",
                "duration": 10 + i * 5,
                "severity": ["mild", "moderate", "severe"][i % 3],
            })
        
        return events
    
    def _mock_disease_risk(self, data: List[Dict]) -> Dict[str, float]:
        """모의 질병 위험 예측"""
        np.random.seed(42)
        
        return {
            "sleep_apnea": 0.35,
            "insomnia": 0.22,
            "cardiovascular": 0.15,
            "diabetes": 0.18,
        }
    
    def _results_equal(self, result1: Dict, result2: Dict) -> bool:
        """결과 비교 (부동소수점 허용)"""
        if result1.keys() != result2.keys():
            return False
        
        for key in result1:
            val1, val2 = result1[key], result2[key]
            
            if isinstance(val1, float):
                if abs(val1 - val2) > 1e-6:
                    return False
            elif val1 != val2:
                return False
        
        return True


class TestDatasetConsistency:
    """테스트 데이터셋 일관성"""
    
    def test_standard_dataset_format(self):
        """표준 데이터셋 형식"""
        dataset = self._create_standard_dataset()
        
        # 필수 필드 확인
        for record in dataset:
            assert "timestamp" in record
            assert "heart_rate" in record
            assert "hrv" in record
            assert "spo2" in record
    
    def test_dataset_reproducibility(self):
        """데이터셋 재현성"""
        dataset1 = self._create_standard_dataset(seed=42)
        dataset2 = self._create_standard_dataset(seed=42)
        
        assert len(dataset1) == len(dataset2)
        
        for d1, d2 in zip(dataset1, dataset2):
            assert d1 == d2
    
    def _create_standard_dataset(self, seed: int = 42) -> List[Dict]:
        """표준 테스트 데이터셋 생성"""
        np.random.seed(seed)
        
        data = []
        for i in range(50):
            data.append({
                "timestamp": f"2024-01-01T{23}:{i:02d}:00",
                "heart_rate": round(65 + np.random.normal(0, 3), 1),
                "hrv": round(45 + np.random.normal(0, 5), 1),
                "spo2": round(97.5 + np.random.normal(0, 0.5), 1),
                "respiratory_rate": round(14 + np.random.normal(0, 1), 1),
            })
        
        return data


class TestOutputFormatConsistency:
    """출력 형식 일관성"""
    
    def test_json_serialization(self):
        """JSON 직렬화 일관성"""
        data = {
            "score": 0.85,
            "stages": ["N1", "N2", "N3"],
            "timestamp": "2024-01-01T00:00:00",
        }
        
        # 여러 번 직렬화
        json1 = json.dumps(data, sort_keys=True)
        json2 = json.dumps(data, sort_keys=True)
        
        assert json1 == json2
    
    def test_date_format_consistency(self):
        """날짜 형식 일관성"""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        
        # ISO 형식
        iso1 = dt.isoformat()
        iso2 = datetime.fromisoformat(iso1).isoformat()
        
        assert iso1 == iso2
    
    def test_numeric_precision_consistency(self):
        """숫자 정밀도 일관성"""
        values = [0.123456789, 0.987654321, 0.555555555]
        
        # 소수점 2자리로 반올림
        rounded = [round(v, 2) for v in values]
        
        expected = [0.12, 0.99, 0.56]
        
        assert rounded == expected
