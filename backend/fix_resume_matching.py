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

def load_all_resume_data():
    """모든 첨부파일에서 이력서 데이터 로드"""
    try:
        results_dir = Path("pdf_ocr_data/results")
        resume_data = {}
        
        for json_file in results_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 이름으로 데이터 그룹화
                name = data.get('fields', {}).get('names', [''])[0]
                if name:
                    if name not in resume_data:
                        resume_data[name] = []
                    resume_data[name].append(data)
                    
            except Exception as e:
                print(f"⚠️ 파일 읽기 오류 {json_file}: {e}")
                continue
                
        print(f"✅ 총 {len(resume_data)}명의 지원자 이력서 데이터 로드 완료")
        return resume_data
        
    except Exception as e:
        print(f"❌ 이력서 데이터 로드 오류: {e}")
        return {}

def extract_resume_info(resume_data):
    """이력서 데이터에서 필요한 정보 추출"""
    if not resume_data:
        return None
        
    try:
        # 가장 최신 데이터 사용 (여러 파일이 있을 경우)
        latest_data = resume_data[0] if isinstance(resume_data, list) else resume_data
        
        fields = latest_data.get('fields', {})
        summary = latest_data.get('summary', '')
        
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
            'keywords': latest_data.get('keywords', [])
        }
        
        return resume_info
        
    except Exception as e:
        print(f"❌ 이력서 정보 추출 오류: {e}")
        return None

def update_applicant_with_resume(db, applicant, resume_info):
    """지원자의 이력서 정보로 업데이트"""
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
            # 기본 정보 업데이트
            if resume_info.get('name'):
                update_data['name'] = resume_info['name']
            if resume_info.get('email'):
                update_data['email'] = resume_info['email']
            if resume_info.get('phone'):
                update_data['phone'] = resume_info['phone']
            if resume_info.get('position'):
                update_data['position'] = resume_info['position']
                # 부서는 직무의 첫 번째 단어로 설정
                update_data['department'] = resume_info['position'].split()[0] if resume_info['position'] else applicant.get('department')
            
            # 기술 스택 및 기타 정보
            if resume_info.get('skills'):
                update_data['skills'] = resume_info['skills']
            
            # 이력서 내용을 성장 배경과 경력 사항에 설정
            if resume_info.get('summary'):
                update_data['growthBackground'] = resume_info['summary']
                update_data['careerHistory'] = resume_info['summary']
                update_data['analysisResult'] = resume_info['summary']
            
            # 기본 분석 점수 설정
            update_data['analysisScore'] = 75
            
            # 동기 부여 메시지
            name = resume_info.get('name', applicant.get('name', '지원자'))
            update_data['motivation'] = f"{name}의 이력서를 통해 지원자의 역량과 경험을 확인했습니다."
        
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
    print("🚀 지원자 이력서 정보 자동 매칭 및 업데이트 시작")
    
    # MongoDB 연결
    db = connect_mongodb()
    if db is None:
        return
    
    try:
        # 모든 첨부파일에서 이력서 데이터 로드
        resume_data = load_all_resume_data()
        
        if not resume_data:
            print("❌ 첨부파일에서 이력서 데이터를 찾을 수 없습니다.")
            return
        
        # 모든 지원자 조회
        applicants = list(db.applicants.find({}))
        print(f"📊 총 지원자 수: {len(applicants)}")
        
        updated_count = 0
        
        for applicant in applicants:
            applicant_name = applicant.get('name', '이름 없음')
            print(f"\n--- {applicant_name} 처리 중 ---")
            
            # 이름으로 이력서 데이터 찾기
            if applicant_name in resume_data:
                print(f"✅ {applicant_name}의 이력서 데이터 발견")
                
                # 이력서 정보 추출
                resume_info = extract_resume_info(resume_data[applicant_name])
                
                # 지원자 정보 업데이트
                if update_applicant_with_resume(db, applicant, resume_info):
                    updated_count += 1
            else:
                print(f"⚠️ {applicant_name}: 해당하는 이력서 데이터 없음")
        
        print(f"\n🎉 업데이트 완료! 총 {updated_count}명의 지원자 정보가 업데이트되었습니다.")
        
        # 업데이트된 지원자 정보 확인
        print("\n📋 업데이트된 지원자 목록:")
        updated_applicants = list(db.applicants.find({'updated_at': {'$exists': True}}, {'name': 1, 'position': 1, 'skills': 1}))
        for app in updated_applicants[:5]:  # 처음 5명만 표시
            print(f"- {app.get('name', '이름 없음')}: {app.get('position', '직무 없음')} | {app.get('skills', '기술 없음')[:50]}...")
        
    except Exception as e:
        print(f"❌ 메인 프로세스 오류: {e}")
    
    finally:
        if db:
            db.client.close()
            print("🔌 MongoDB 연결 종료")

if __name__ == "__main__":
    main()
