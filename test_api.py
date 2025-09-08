#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_api():
    """API 테스트 스크립트"""
    base_url = "http://localhost:5001"
    
    print("🚀 API 테스트 시작")
    print("=" * 50)
    
    # 1. 세션 시작
    print("1. 세션 시작...")
    response = requests.post(f"{base_url}/api/start_session")
    if response.status_code == 200:
        data = response.json()
        session_id = data['session_id']
        print(f"✅ 세션 시작 성공: {session_id}")
        print(f"   환영 메시지: {data['welcome_message']}")
    else:
        print(f"❌ 세션 시작 실패: {response.status_code}")
        return
    
    print("\n" + "=" * 50)
    
    # 2. 대화 테스트
    test_messages = [
        "안녕",
        "좋아",
        "공부가 잘 안돼. 힘들어",
        "외로워",
        "잠이 안와"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"{i}. 사용자: {message}")
        
        response = requests.post(
            f"{base_url}/api/message",
            json={
                "session_id": session_id,
                "message": message
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   의도: {data['intent']}")
            print(f"   시스템: {data['response']}")
            print(f"   완료 여부: {data['is_complete']}")
            
            if data['is_complete']:
                print(f"   진단 결과: {data['diagnosis_result']}")
                break
        else:
            print(f"   ❌ 오류: {response.status_code}")
        
        print()
        time.sleep(1)
    
    print("=" * 50)
    
    # 3. 최종 상태 확인
    print("3. 최종 상태 확인...")
    response = requests.get(f"{base_url}/api/status?session_id={session_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 진단 완료: {data['is_diagnosis_complete']}")
        print(f"   현재 점수: {data['current_scores']}")
    
    # 4. 세션 히스토리 확인
    print("\n4. 세션 히스토리...")
    response = requests.get(f"{base_url}/api/session_history?session_id={session_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"   대화 수: {len(data['conversation_history'])}")
        for i, conv in enumerate(data['conversation_history'], 1):
            print(f"   {i}. [{conv['intent']}] 사용자: {conv['user']}")
            print(f"      시스템: {conv['system']}")
    
    print("\n🎉 API 테스트 완료!")

if __name__ == "__main__":
    test_api()
