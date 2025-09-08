# -*- coding: utf-8 -*-

import numpy as np
import torch

def set_seed(seed=42):
    """랜덤 시드 설정"""
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)

def normalize_features(features):
    """특성 정규화"""
    return (features - np.mean(features)) / (np.std(features) + 1e-8)

def create_padding_mask(sequences, max_length):
    """패딩 마스크 생성"""
    masks = []
    for seq in sequences:
        mask = [1] * len(seq) + [0] * (max_length - len(seq))
        masks.append(mask)
    return np.array(masks)

def calculate_accuracy(predictions, targets):
    """정확도 계산"""
    correct = np.sum(predictions == targets)
    total = len(predictions)
    return correct / total if total > 0 else 0.0

def format_diagnosis_result(cdi_score, rcmas_score, bdi_score):
    """진단 결과 포맷팅"""
    result = {
        'cdi_score': cdi_score,
        'rcmas_score': rcmas_score,
        'bdi_score': bdi_score,
        'interpretation': {
            'cdi': _interpret_cdi_score(cdi_score),
            'rcmas': _interpret_rcmas_score(rcmas_score),
            'bdi': _interpret_bdi_score(bdi_score)
        }
    }
    return result

def _interpret_cdi_score(score):
    """CDI 점수 해석"""
    if score is None:
        return "평가되지 않음"
    elif score <= 1:
        return "정상 범위"
    elif score <= 2:
        return "경미한 우울 증상"
    else:
        return "우울 증상 주의 필요"

def _interpret_rcmas_score(score):
    """RCMAS 점수 해석"""
    if score is None:
        return "평가되지 않음"
    elif score <= 1:
        return "정상 범위"
    elif score <= 2:
        return "경미한 불안 증상"
    else:
        return "불안 증상 주의 필요"

def _interpret_bdi_score(score):
    """BDI 점수 해석"""
    if score is None:
        return "평가되지 않음"
    elif score <= 1:
        return "정상 범위"
    elif score <= 2:
        return "경미한 우울 증상"
    else:
        return "우울 증상 주의 필요"

