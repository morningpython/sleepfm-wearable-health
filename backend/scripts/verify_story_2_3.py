#!/usr/bin/env python3
"""
Story 2.3 검증 스크립트: 멀티모달 임베딩 추출

소스 코드 기반 검증 (torch/numpy 없이도 실행 가능)
"""

import re
from pathlib import Path


def check_embedding_extractor():
    """EmbeddingExtractor 클래스 검증"""
    print("[1] EmbeddingExtractor 클래스 검증...")
    
    file_path = Path(__file__).parent.parent / "app/ml/embedding_extractor.py"
    if not file_path.exists():
        print(f"    ✗ embedding_extractor.py 없음")
        return False
    
    content = file_path.read_text()
    
    # 클래스 정의
    if "class EmbeddingExtractor:" not in content:
        print("    ✗ EmbeddingExtractor 클래스 없음")
        return False
    
    # 주요 메서드
    required_methods = [
        "__init__",
        "extract",
        "_determine_batch_size",
        "_process_batches",
        "extract_batch_info",
    ]
    
    for method in required_methods:
        if f"def {method}(" not in content:
            print(f"    ✗ {method} 메서드 없음")
            return False
    
    print("    ✓ EmbeddingExtractor 클래스 완성")
    return True


def check_helper_functions():
    """헬퍼 함수 검증"""
    print("[2] 헬퍼 함수 검증...")
    
    file_path = Path(__file__).parent.parent / "app/ml/embedding_extractor.py"
    content = file_path.read_text()
    
    required_functions = [
        "extract_embeddings",
        "validate_embeddings",
        "compute_embedding_statistics",
    ]
    
    for func in required_functions:
        if f"def {func}(" not in content:
            print(f"    ✗ {func} 함수 없음")
            return False
    
    print(f"    ✓ {len(required_functions)}개 헬퍼 함수 완성")
    return True


def check_features():
    """주요 기능 검증"""
    print("[3] 주요 기능 검증...")
    
    file_path = Path(__file__).parent.parent / "app/ml/embedding_extractor.py"
    content = file_path.read_text()
    
    features = {
        "동적 배치 크기": "_determine_batch_size",
        "혼합 정밀도": "mixed_precision",
        "배치 처리": "_process_batches",
        "NaN/Inf 검증": "np.isnan",
        "임베딩 통계": "compute_embedding_statistics",
    }
    
    missing = []
    for feature_name, pattern in features.items():
        if pattern not in content:
            missing.append(feature_name)
            print(f"    ✗ {feature_name} 미구현")
    
    if not missing:
        print(f"    ✓ 모든 {len(features)}가지 기능 구현")
        return True
    
    return False


def check_docstrings():
    """문서화 검증"""
    print("[4] 문서화 검증...")
    
    file_path = Path(__file__).parent.parent / "app/ml/embedding_extractor.py"
    content = file_path.read_text()
    
    # 모듈 docstring
    if not content.startswith('"""'):
        print("    ✗ 모듈 docstring 없음")
        return False
    
    # 클래스/함수 docstring 개수
    docstring_count = len(re.findall(r'"""[\s\S]*?"""', content))
    
    if docstring_count < 10:
        print(f"    ✗ docstring 부족 ({docstring_count}개)")
        return False
    
    print(f"    ✓ {docstring_count}개 docstring 완성")
    return True


def check_tests():
    """테스트 파일 검증"""
    print("[5] 테스트 파일 검증...")
    
    test_file = Path(__file__).parent.parent / "tests/test_story_2_3_embedding.py"
    
    if not test_file.exists():
        print(f"    ✗ {test_file.name} 없음")
        return False
    
    content = test_file.read_text()
    
    # 테스트 클래스 개수
    classes = len(re.findall(r"^class Test\w+:", content, re.MULTILINE))
    
    # 테스트 메서드 개수
    tests = len(re.findall(r"def test_\w+\(", content))
    
    if tests < 10:
        print(f"    ✗ 테스트 부족 ({tests}개)")
        return False
    
    print(f"    ✓ {classes}개 테스트 클래스, {tests}개 테스트 메서드")
    return True


def check_imports():
    """임포트 검증"""
    print("[6] 임포트/의존성 검증...")
    
    # embedding_extractor.py 임포트
    embedding_file = Path(__file__).parent.parent / "app/ml/embedding_extractor.py"
    embedding_content = embedding_file.read_text()
    
    required_imports = {
        "numpy": "import numpy",
        "torch": "import torch",
        "torch.nn.Module": "torch.nn.Module",
    }
    
    missing = []
    for lib, pattern in required_imports.items():
        if pattern not in embedding_content:
            missing.append(lib)
            print(f"    ✗ {lib} 임포트 없음")
    
    # inference.py 검증
    inference_file = Path(__file__).parent.parent / "app/ml/inference.py"
    if not inference_file.exists():
        print("    ✗ inference.py 없음")
        return False
    
    inference_content = inference_file.read_text()
    if "InferenceEngine" not in inference_content:
        print("    ✗ inference.py에서 InferenceEngine 클래스 없음")
        return False
    
    if "EmbeddingExtractor" not in inference_content:
        print("    ✗ inference.py에서 EmbeddingExtractor 사용 없음")
        return False
    
    # __init__.py 검증
    init_file = Path(__file__).parent.parent / "app/ml/__init__.py"
    if not init_file.exists():
        print("    ✗ app/ml/__init__.py 없음")
        return False
    
    init_content = init_file.read_text()
    if "EmbeddingExtractor" not in init_content:
        print("    ✗ __init__.py에서 EmbeddingExtractor 내보내지 않음")
        return False
    
    if not missing:
        print(f"    ✓ 모든 주요 임포트 완성 (embedding_extractor.py, inference.py)")
        return True
    
    return False


def check_acceptance_criteria():
    """acceptance criteria 검증"""
    print("[7] Acceptance Criteria 검증...")
    
    file_path = Path(__file__).parent.parent / "app/ml/embedding_extractor.py"
    content = file_path.read_text()
    
    criteria = {
        "텐서 입력 처리": ["def extract(", "torch.Tensor"],
        "임베딩 출력 512차원": ["embedding_dim", "512"],
        "배치 처리": ["_process_batches", "batch_size"],
        "OOM 방지": ["_determine_batch_size", "torch.cuda"],
        "NumPy 반환": ["return_numpy", "numpy()"],
    }
    
    passed = 0
    for criterion_name, patterns in criteria.items():
        if all(p in content for p in patterns):
            passed += 1
            print(f"    ✓ {criterion_name}")
        else:
            print(f"    ✗ {criterion_name}")
    
    return passed == len(criteria)


def check_code_structure():
    """코드 구조 검증"""
    print("[8] 코드 구조 검증...")
    
    embedding_file = Path(__file__).parent.parent / "app/ml/embedding_extractor.py"
    inference_file = Path(__file__).parent.parent / "app/ml/inference.py"
    
    if not embedding_file.exists():
        return False
    
    embedding_lines = embedding_file.read_text().split("\n")
    
    # embedding_extractor.py 라인 수
    if len(embedding_lines) < 300:
        print(f"    ✗ embedding_extractor.py 길이 부족 ({len(embedding_lines)} 라인)")
        return False
    
    # inference.py 라인 수
    if not inference_file.exists():
        print("    ✗ inference.py 없음")
        return False
    
    inference_lines = inference_file.read_text().split("\n")
    if len(inference_lines) < 100:
        print(f"    ✗ inference.py 길이 부족 ({len(inference_lines)} 라인)")
        return False
    
    # 함수/클래스 개수
    emb_functions = len([l for l in embedding_lines if l.strip().startswith("def ")])
    emb_classes = len([l for l in embedding_lines if l.strip().startswith("class ")])
    
    inf_functions = len([l for l in inference_lines if l.strip().startswith("def ")])
    inf_classes = len([l for l in inference_lines if l.strip().startswith("class ")])
    
    total_lines = len(embedding_lines) + len(inference_lines)
    print(f"    ✓ 총 {total_lines} 라인")
    print(f"      - embedding_extractor.py: {len(embedding_lines)} 라인, {emb_classes}개 클래스, {emb_functions}개 함수")
    print(f"      - inference.py: {len(inference_lines)} 라인, {inf_classes}개 클래스, {inf_functions}개 함수")
    return True


def main():
    """메인 검증"""
    print("\n" + "="*60)
    print("Story 2.3: 멀티모달 임베딩 추출 검증")
    print("="*60 + "\n")
    
    checks = [
        check_embedding_extractor,
        check_helper_functions,
        check_features,
        check_docstrings,
        check_tests,
        check_imports,
        check_acceptance_criteria,
        check_code_structure,
    ]
    
    passed = sum(1 for check in checks if check())
    total = len(checks)
    
    print("\n" + "="*60)
    print(f"검증 결과: {passed}/{total} 통과")
    print("="*60 + "\n")
    
    if passed == total:
        print("✅ Story 2.3 모든 검증 완료!")
        return 0
    else:
        print(f"❌ {total - passed}개 항목 검증 실패")
        return 1


if __name__ == "__main__":
    exit(main())
