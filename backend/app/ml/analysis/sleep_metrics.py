"""
수면 분석 관련 유틸리티 함수

수면 효율성 계산, 단계별 지속 시간 등
"""

from typing import List, Dict


def calculate_sleep_efficiency(stages: List[int]) -> float:
    """
    수면 효율성 계산
    
    수면 효율성 = (총 수면 시간 / 총 침대 시간) × 100
    Wake (0) 제외한 모든 단계를 수면으로 간주
    
    Args:
        stages: 수면 단계 배열 (0=Wake, 1=N1, 2=N2, 3=N3, 4=REM)
    
    Returns:
        수면 효율성 (0-100%)
    
    Examples:
        >>> stages = [0, 0, 2, 2, 2, 3, 3, 4, 4, 0]
        >>> calculate_sleep_efficiency(stages)
        70.0  # 7/10 = 70%
    """
    if not stages:
        return 0.0
    
    total_epochs = len(stages)
    sleep_epochs = sum(1 for stage in stages if stage != 0)  # Wake가 아닌 것
    
    efficiency = (sleep_epochs / total_epochs) * 100.0
    
    return efficiency


def calculate_stage_durations(
    stages: List[int],
    epoch_length_seconds: int = 30
) -> Dict[str, float]:
    """
    각 수면 단계별 지속 시간 계산 (분 단위)
    
    Args:
        stages: 수면 단계 배열
        epoch_length_seconds: 에포크 길이 (초, 기본 30초)
    
    Returns:
        각 단계별 지속 시간 (분)
    
    Examples:
        >>> stages = [0, 0, 2, 2, 3, 3, 4]
        >>> calculate_stage_durations(stages, epoch_length_seconds=30)
        {'Wake': 1.0, 'N1': 0.0, 'N2': 1.0, 'N3': 1.0, 'REM': 0.5}
    """
    stage_names = ["Wake", "N1", "N2", "N3", "REM"]
    
    # 각 단계별 에포크 수 계산
    stage_counts = {name: 0 for name in stage_names}
    
    for stage in stages:
        if 0 <= stage <= 4:
            stage_counts[stage_names[stage]] += 1
    
    # 에포크 수 → 분 단위 변환
    epoch_length_minutes = epoch_length_seconds / 60.0
    
    durations = {
        name: count * epoch_length_minutes
        for name, count in stage_counts.items()
    }
    
    return durations
