#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from pymongo import MongoClient
from pathlib import Path

def connect_mongodb():
    """MongoDB 연결"""
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client.hireme
        print("✅ MongoDB 연결 성공")
        return db
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        return None

def load_resume_data(resume_id):
    """이력서 ID로 첨부파일에서 데이터 로드"""
    try:
        # PDF OCR 결과 디렉토리
        results_dir = Path("pdf_ocr_data/results")
        
        # 모든 JSON 파일 검색
        for json_file in results_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # MongoDB ID가 일치하는지 확인
                if data.get('mongo_id') == resume_id:
                    print(f"✅ 이력서 데이터 찾음: {json_file.name}")
                    return data
                    
            except Exception as e:
                print(f"⚠️ 파일 읽기 오류 {json_file}: {e}")
                continue
                
        print(f"⚠️ 이력서 ID {resume_id}에 해당하는 첨부파일을 찾을 수 없음")
        return None
        
    except Exception as e:
        print(f"❌ 이력서 데이터 로드 오류: {e}")
        return None

def extract_resume_info(resume_data):
    """이력서 데이터에서 필요한 정보 추출"""
    if not resume_data:
        return None
        
    try:
        # 기본 정보 추출
        fields = resume_data.get('fields', {})
        summary = resume_data.get('summary', '')
        
        resume_info = {
            'name': fields.get('names', [''])[0] if fields.get('names') else '',
            'email': fields.get('emails', [''])[0] if fields.get('emails') else '',
            'phone': fields.get('phones', [''])[0] if fields.get('phones') else '',
            'position': fields.get('positions', [''])[0] if fields.get('positions') else '',
            'skills': ', '.join(fields.get('skills', [])) if fields.get('skills') else '',
            'education': ', '.join(fields.get('education', [])) if fields.get('education') else '',
            'companies': ', '.join(fields.get('companies', [])) if fields.get('companies') else '',
            'addresses': ', '.join(fields.get('addresses', [])) if fields.get('addresses') else '',
            'summary': summary,
            'keywords': resume_data.get('keywords', [])
        }
        
        return resume_info
        
    except Exception as e:
        print(f"❌ 이력서 정보 추출 오류: {e}")
        return None

def update_applicant_resume(db, applicant, resume_info):
    """지원자의 이력서 정보 업데이트"""
    try:
        applicant_id = applicant.get('_id')
        
        if not applicant_id:
            print(f"⚠️ 지원자 ID가 없음: {applicant.get('name', '이름 없음')}")
            return False
            
        # 업데이트할 데이터 준비
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        # 이력서 정보가 있으면 업데이트
        if resume_info:
            update_data.update({
                'name': resume_info.get('name') or applicant.get('name'),
                'email': resume_info.get('email') or applicant.get('email'),
                'phone': resume_info.get('phone') or applicant.get('phone'),
                'position': resume_info.get('position') or applicant.get('position'),
                'skills': resume_info.get('skills') or applicant.get('skills'),
                'department': resume_info.get('position', '').split()[0] if resume_info.get('position') else applicant.get('department'),
                'growthBackground': resume_info.get('summary', ''),
                'motivation': f"{resume_info.get('name', '지원자')}의 이력서를 통해 지원자의 역량과 경험을 확인했습니다.",
                'careerHistory': resume_info.get('summary', ''),
                'analysisScore': 75,  # 기본 점수
                'analysisResult': resume_info.get('summary', '')
            })
        
        # MongoDB 업데이트
        result = db.applicants.update_one(
            {'_id': applicant_id},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            print(f"✅ {applicant.get('name', '이름 없음')} 이력서 정보 업데이트 완료")
            return True
        else:
            print(f"⚠️ {applicant.get('name', '이름 없음')} 업데이트할 내용 없음")
            return False
            
    except Exception as e:
        print(f"❌ 지원자 업데이트 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 지원자 이력서 정보 자동 업데이트 시작")
    
    # MongoDB 연결
    db = connect_mongodb()
    if db is None:
        return
    
    try:
        # 모든 지원자 조회
        applicants = list(db.applicants.find({}))
        print(f"📊 총 지원자 수: {len(applicants)}")
        
        updated_count = 0
        
        for applicant in applicants:
            applicant_name = applicant.get('name', '이름 없음')
            resume_id = applicant.get('resume_id')
            
            print(f"\n--- {applicant_name} 처리 중 ---")
            
            if resume_id:
                # 이력서 데이터 로드
                resume_data = load_resume_data(resume_id)
                
                # 이력서 정보 추출
                resume_info = extract_resume_info(resume_data)
                
                # 지원자 정보 업데이트
                if update_applicant_resume(db, applicant, resume_info):
                    updated_count += 1
            else:
                print(f"⚠️ {applicant_name}: 이력서 ID가 없음")
        
        print(f"\n🎉 업데이트 완료! 총 {updated_count}명의 지원자 정보가 업데이트되었습니다.")
        
    except Exception as e:
        print(f"❌ 메인 프로세스 오류: {e}")
    
    finally:
        if db:
            db.client.close()
            print("🔌 MongoDB 연결 종료")

if __name__ == "__main__":
    main()
