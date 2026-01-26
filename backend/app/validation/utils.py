"""
유틸리티 함수

데이터 검증에 필요한 헬퍼 함수들을 제공합니다.
"""

import numpy as np
from typing import Optional, List, Tuple, Dict
from scipy import signal, stats


def calculate_missing_ratio(data: np.ndarray) -> float:
    """
    결측치 비율 계산
    
    Args:
        data: 센서 데이터 배열 (NaN = 결측치)
    
    Returns:
        결측치 비율 (0-1)
    
    Examples:
        >>> data = np.array([1, 2, np.nan, 4, 5])
        >>> calculate_missing_ratio(data)
        0.2  # 20%
    """
    if len(data) == 0:
        return 0.0
    
    missing_count = np.sum(np.isnan(data))
    total_count = len(data)
    
    return missing_count / total_count


def detect_missing_segments(
    data: np.ndarray,
    sampling_rate: float,
    min_duration: float = 60.0,
) -> List[Dict[str, float]]:
    """
    연속된 결측치 구간 탐지
    
    Args:
        data: 센서 데이터 배열
        sampling_rate: 샘플링 레이트 (Hz)
        min_duration: 최소 구간 길이 (초, 기본: 60초)
    
    Returns:
        결측치 구간 리스트, 각 딕셔너리는 다음 포함:
        - start_idx: 시작 인덱스
        - end_idx: 종료 인덱스
        - duration: 지속 시간 (초)
        - num_samples: 샘플 개수
    
    Examples:
        >>> data = np.array([1, 2, np.nan, np.nan, np.nan, 6])
        >>> detect_missing_segments(data, sampling_rate=1.0, min_duration=2.0)
        [{'start_idx': 2, 'end_idx': 4, 'duration': 3.0, 'num_samples': 3}]
    """
    is_missing = np.isnan(data)
    
    # 결측치가 없으면 빈 리스트 반환
    if not np.any(is_missing):
        return []
    
    # 연속된 결측치 구간 찾기
    segments = []
    in_segment = False
    start_idx = 0
    
    for i, missing in enumerate(is_missing):
        if missing and not in_segment:
            # 새 구간 시작
            start_idx = i
            in_segment = True
        elif not missing and in_segment:
            # 구간 종료
            end_idx = i - 1
            duration = (end_idx - start_idx + 1) / sampling_rate
            
            if duration >= min_duration:
                segments.append({
                    "start_idx": int(start_idx),
                    "end_idx": int(end_idx),
                    "duration": float(duration),
                    "num_samples": int(end_idx - start_idx + 1),
                })
            
            in_segment = False
    
    # 마지막 구간 처리
    if in_segment:
        end_idx = len(data) - 1
        duration = (end_idx - start_idx + 1) / sampling_rate
        
        if duration >= min_duration:
            segments.append({
                "start_idx": int(start_idx),
                "end_idx": int(end_idx),
                "duration": float(duration),
                "num_samples": int(end_idx - start_idx + 1),
            })
    
    return segments


def estimate_heart_rate(
    ecg_signal: np.ndarray,
    sampling_rate: float,
    method: str = "peaks",
) -> float:
    """
    ECG 신호에서 심박수 추정
    
    Args:
        ecg_signal: ECG 신호 배열
        sampling_rate: 샘플링 레이트 (Hz)
        method: 추정 방법 ("peaks" 또는 "fft")
    
    Returns:
        추정 심박수 (BPM)
    
    Raises:
        ValueError: 신호가 너무 짧거나 피크를 찾을 수 없는 경우
    
    Examples:
        >>> # 60 BPM 모의 ECG 신호
        >>> t = np.linspace(0, 10, 1000)  # 10초
        >>> ecg = np.sin(2 * np.pi * 1.0 * t)  # 1 Hz = 60 BPM
        >>> estimate_heart_rate(ecg, sampling_rate=100)
        60.0
    """
    if len(ecg_signal) < sampling_rate * 2:
        raise ValueError("Signal too short for heart rate estimation (need >= 2 seconds)")
    
    # NaN 제거
    valid_data = ecg_signal[~np.isnan(ecg_signal)]
    if len(valid_data) < sampling_rate * 2:
        raise ValueError("Too many missing values for heart rate estimation")
    
    if method == "peaks":
        # 피크 기반 추정
        # R-피크 탐지 (높은 값, 최소 간격 0.4초 = 150 BPM)
        min_distance = int(sampling_rate * 0.4)
        
        # 신호 정규화
        normalized = (valid_data - np.mean(valid_data)) / (np.std(valid_data) + 1e-8)
        
        # 피크 찾기 (높이 > 평균 + 1 std)
        peaks, _ = signal.find_peaks(
            normalized,
            distance=min_distance,
            height=0.5,  # 정규화 후 임계값
        )
        
        if len(peaks) < 2:
            raise ValueError("Could not detect sufficient peaks for heart rate estimation")
        
        # RR 간격 (초)
        rr_intervals = np.diff(peaks) / sampling_rate
        
        # 평균 RR 간격 → 심박수
        mean_rr = np.mean(rr_intervals)
        heart_rate = 60.0 / mean_rr
        
        return float(heart_rate)
    
    elif method == "fft":
        # FFT 기반 추정
        # 신호 길이 맞추기 (power of 2)
        n = len(valid_data)
        nfft = 2 ** int(np.ceil(np.log2(n)))
        
        # FFT 계산
        fft_result = np.fft.rfft(valid_data, n=nfft)
        freqs = np.fft.rfftfreq(nfft, d=1/sampling_rate)
        
        # 파워 스펙트럼
        power = np.abs(fft_result) ** 2
        
        # 심박수 범위 (0.5-3.5 Hz = 30-210 BPM)
        valid_range = (freqs >= 0.5) & (freqs <= 3.5)
        
        if not np.any(valid_range):
            raise ValueError("No valid frequency range for heart rate estimation")
        
        # 최대 파워 주파수 찾기
        dominant_freq = freqs[valid_range][np.argmax(power[valid_range])]
        
        # 주파수 → 심박수
        heart_rate = dominant_freq * 60.0
        
        return float(heart_rate)
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'peaks' or 'fft'")


def estimate_respiration_rate(
    accel_signal: np.ndarray,
    sampling_rate: float,
    axis: int = 2,  # Z축 (가슴 움직임)
) -> float:
    """
    가속도계 신호에서 호흡률 추정
    
    Args:
        accel_signal: 가속도계 신호 (1D 또는 3D)
        sampling_rate: 샘플링 레이트 (Hz)
        axis: 3D인 경우 사용할 축 (기본: 2 = Z축)
    
    Returns:
        추정 호흡률 (breaths/min)
    
    Raises:
        ValueError: 신호가 너무 짧은 경우
    
    Examples:
        >>> # 12 breaths/min 모의 호흡 신호
        >>> t = np.linspace(0, 60, 6000)  # 60초 @ 100Hz
        >>> resp = np.sin(2 * np.pi * 0.2 * t)  # 0.2 Hz = 12 breaths/min
        >>> estimate_respiration_rate(resp, sampling_rate=100)
        12.0
    """
    if len(accel_signal) < sampling_rate * 10:
        raise ValueError("Signal too short for respiration rate estimation (need >= 10 seconds)")
    
    # 3D 신호인 경우 특정 축 선택
    if accel_signal.ndim == 2:
        if axis >= accel_signal.shape[1]:
            raise ValueError(f"Invalid axis {axis} for signal with shape {accel_signal.shape}")
        signal_1d = accel_signal[:, axis]
    else:
        signal_1d = accel_signal
    
    # NaN 제거
    valid_data = signal_1d[~np.isnan(signal_1d)]
    if len(valid_data) < sampling_rate * 10:
        raise ValueError("Too many missing values for respiration rate estimation")
    
    # 대역통과 필터 (0.1-0.7 Hz = 6-42 breaths/min)
    sos = signal.butter(
        N=4,
        Wn=[0.1, 0.7],
        btype='bandpass',
        fs=sampling_rate,
        output='sos',
    )
    filtered = signal.sosfilt(sos, valid_data)
    
    # 피크 탐지 (최소 간격 1.5초 = 40 breaths/min)
    min_distance = int(sampling_rate * 1.5)
    
    peaks, _ = signal.find_peaks(
        filtered,
        distance=min_distance,
    )
    
    if len(peaks) < 2:
        raise ValueError("Could not detect sufficient peaks for respiration rate estimation")
    
    # 호흡 간격 (초)
    breath_intervals = np.diff(peaks) / sampling_rate
    
    # 평균 호흡 간격 → 호흡률
    mean_interval = np.mean(breath_intervals)
    respiration_rate = 60.0 / mean_interval
    
    return float(respiration_rate)


def check_signal_quality(
    signal_data: np.ndarray,
    sampling_rate: float,
    window_duration: float = 5.0,
) -> Dict[str, float]:
    """
    신호 품질 메트릭 계산
    
    Args:
        signal_data: 신호 배열
        sampling_rate: 샘플링 레이트 (Hz)
        window_duration: 윈도우 길이 (초)
    
    Returns:
        품질 메트릭 딕셔너리:
        - snr: Signal-to-Noise Ratio (dB)
        - std: 표준편차
        - range: Peak-to-Peak 범위
        - skewness: 왜도
        - kurtosis: 첨도
    
    Examples:
        >>> data = np.random.randn(1000)
        >>> metrics = check_signal_quality(data, sampling_rate=100)
        >>> 'snr' in metrics
        True
    """
    # NaN 제거
    valid_data = signal_data[~np.isnan(signal_data)]
    
    if len(valid_data) == 0:
        return {
            "snr": 0.0,
            "std": 0.0,
            "range": 0.0,
            "skewness": 0.0,
            "kurtosis": 0.0,
        }
    
    # SNR 추정 (단순 방법: 신호 파워 / 노이즈 파워)
    # 신호: 저주파 성분, 노이즈: 고주파 성분
    window_size = int(window_duration * sampling_rate)
    if len(valid_data) >= window_size:
        # 이동 평균으로 신호 추정
        smoothed = np.convolve(valid_data, np.ones(window_size)/window_size, mode='valid')
        noise = valid_data[:len(smoothed)] - smoothed
        
        signal_power = np.mean(smoothed ** 2)
        noise_power = np.mean(noise ** 2)
        
        # 최소 노이즈 파워 보장 (너무 작으면 신호 파워의 1%)
        min_noise_power = signal_power * 0.01
        noise_power = max(noise_power, min_noise_power)
        
        if noise_power > 0 and signal_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = 100.0  # 노이즈가 없으면 매우 높은 SNR
    else:
        snr = 0.0
    
    # 기본 통계
    std = float(np.std(valid_data))
    signal_range = float(np.ptp(valid_data))  # peak-to-peak
    
    # 분포 특성
    skewness = float(stats.skew(valid_data))
    kurtosis = float(stats.kurtosis(valid_data))
    
    return {
        "snr": float(snr),
        "std": std,
        "range": signal_range,
        "skewness": skewness,
        "kurtosis": kurtosis,
    }


def interpolate_missing_data(
    data: np.ndarray,
    method: str = "linear",
    limit: Optional[int] = None,
) -> np.ndarray:
    """
    결측치 보간
    
    Args:
        data: 센서 데이터 배열 (NaN = 결측치)
        method: 보간 방법 ("linear", "cubic", "nearest")
        limit: 최대 연속 보간 개수 (None = 무제한)
    
    Returns:
        보간된 데이터 배열
    
    Examples:
        >>> data = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
        >>> interpolate_missing_data(data, method="linear")
        array([1., 2., 3., 4., 5.])
    """
    if not np.any(np.isnan(data)):
        return data.copy()
    
    # 인덱스 배열
    x = np.arange(len(data))
    
    # 유효 데이터 마스크
    valid_mask = ~np.isnan(data)
    
    if not np.any(valid_mask):
        # 모든 데이터가 NaN이면 0으로 채움
        return np.zeros_like(data)
    
    # 유효 데이터로 보간
    if method == "linear":
        interpolated = np.interp(x, x[valid_mask], data[valid_mask])
    elif method == "nearest":
        from scipy.interpolate import interp1d
        f = interp1d(x[valid_mask], data[valid_mask], kind='nearest', fill_value="extrapolate")
        interpolated = f(x)
    elif method == "cubic":
        if np.sum(valid_mask) < 4:
            # cubic은 최소 4개 포인트 필요
            interpolated = np.interp(x, x[valid_mask], data[valid_mask])
        else:
            from scipy.interpolate import interp1d
            f = interp1d(x[valid_mask], data[valid_mask], kind='cubic', fill_value="extrapolate")
            interpolated = f(x)
    else:
        raise ValueError(f"Unknown interpolation method: {method}")
    
    # limit 적용
    if limit is not None:
        result = data.copy()
        consecutive_count = 0
        
        for i in range(len(data)):
            if np.isnan(data[i]):
                consecutive_count += 1
                if consecutive_count <= limit:
                    result[i] = interpolated[i]
            else:
                consecutive_count = 0
        
        return result
    
    return interpolated
