#!/usr/bin/env python3
"""
스크립트: SleepFM 모델 가중치 초기화

용도:
- 모델 가중치 다운로드
- 로컬 환경에서 모델 검증
- 서버 시작 전 모델 준비

사용법:
    python scripts/init_sleepfm_model.py [--device cpu|cuda] [--no-download]
"""

import sys
import argparse
import logging
from pathlib import Path

# 백엔드 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.sleepfm_encoder import (
    load_sleepfm_model,
    validate_model_io,
    download_model_weights,
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main(args):
    """메인 함수"""
    logger.info("=" * 60)
    logger.info("SleepFM Model Initialization")
    logger.info("=" * 60)
    
    # 1. 모델 가중치 다운로드
    if not args.no_download:
        logger.info("\n[Step 1] Downloading model weights...")
        try:
            model_path = download_model_weights()
            logger.info(f"✓ Model weights ready at: {model_path}")
        except Exception as e:
            logger.error(f"✗ Download failed: {e}")
            if args.device == "cuda":
                logger.warning("Falling back to CPU for testing...")
                args.device = "cpu"
    
    # 2. 모델 로드
    logger.info(f"\n[Step 2] Loading model on {args.device}...")
    try:
        model, device = load_sleepfm_model(
            device=args.device,
            download_if_missing=False,
        )
        logger.info(f"✓ Model loaded successfully on {device}")
    except Exception as e:
        logger.error(f"✗ Failed to load model: {e}")
        return 1
    
    # 3. 모델 IO 검증
    logger.info("\n[Step 3] Validating model input/output shapes...")
    try:
        validate_model_io(model, device)
        logger.info("✓ Model validation passed")
    except Exception as e:
        logger.error(f"✗ Model validation failed: {e}")
        return 1
    
    # 4. 모델 정보 출력
    logger.info("\n[Step 4] Model Information")
    logger.info("-" * 60)
    logger.info(f"Model Name: SleepFM Encoder")
    logger.info(f"Input Shape: (batch, 3, 640)")
    logger.info(f"  - batch: 배치 크기 (동적)")
    logger.info(f"  - 3: 채널 수 (ECG, PPG, Accelerometer)")
    logger.info(f"  - 640: 시간 스텝 (5초 @ 128Hz)")
    logger.info(f"Output Shape: (batch, 512)")
    logger.info(f"  - 512: 임베딩 벡터 차원")
    logger.info(f"Device: {device}")
    logger.info(f"Precision: FP32 (float32)")
    logger.info("-" * 60)
    
    # 5. 테스트 추론 실행
    logger.info("\n[Step 5] Running test inference...")
    try:
        import torch
        
        test_input = torch.randn(2, 3, 640, device=device)
        with torch.no_grad():
            test_output = model(test_input)
        
        logger.info(f"✓ Test inference completed")
        logger.info(f"  Input: {test_input.shape}")
        logger.info(f"  Output: {test_output.shape}")
        logger.info(f"  Output range: [{test_output.min():.4f}, {test_output.max():.4f}]")
    except Exception as e:
        logger.error(f"✗ Test inference failed: {e}")
        return 1
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ Model initialization completed successfully!")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SleepFM Model 초기화 및 검증 스크립트"
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default=None,
        help="실행 디바이스 (기본값: GPU 사용 가능하면 cuda, 아니면 cpu)",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="모델 가중치 다운로드 스킵 (이미 로컬에 있을 때)",
    )
    
    args = parser.parse_args()
    
    sys.exit(main(args))
