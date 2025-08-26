#!/usr/bin/env python3
"""
지원자들에게 자동 메일 발송 스크립트
"""

import pymongo
from bson import ObjectId
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from typing import List, Dict, Any

class MailSender:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['hireme']
        
        # 메일 설정 (실제 환경에서는 환경변수로 관리)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('MAIL_SENDER_EMAIL', 'your-email@gmail.com')
        self.sender_password = os.getenv('MAIL_SENDER_PASSWORD', 'your-app-password')
        
    def get_mail_templates(self) -> Dict[str, Any]:
        """메일 템플릿 조회 (실제로는 데이터베이스에서 가져옴)"""
        # 기본 템플릿
        default_templates = {
            'passed': {
                'subject': '축하합니다! 서류 전형 합격 안내',
                'content': '''안녕하세요, {applicant_name}님

축하드립니다! {job_posting_title} 포지션에 대한 서류 전형에 합격하셨습니다.

다음 단계인 면접 일정은 추후 별도로 안내드리겠습니다.

감사합니다.
{company_name} 채용팀'''
            },
            'rejected': {
                'subject': '서류 전형 결과 안내',
                'content': '''안녕하세요, {applicant_name}님

{job_posting_title} 포지션에 대한 서류 전형 결과를 안내드립니다.

안타깝게도 이번 전형에서는 합격하지 못했습니다.
앞으로 더 좋은 기회가 있을 때 다시 지원해 주시기 바랍니다.

감사합니다.
{company_name} 채용팀'''
            }
        }
        
        # TODO: 데이터베이스에서 저장된 템플릿 가져오기
        return default_templates
    
    def get_applicants_by_status(self, status_type: str) -> List[Dict[str, Any]]:
        """상태별 지원자 조회"""
        try:
            if status_type == 'passed':
                # 합격자 (서류합격, 최종합격)
                applicants = list(self.db.applicants.find({
                    "status": {"$in": ["서류합격", "최종합격"]}
                }))
            elif status_type == 'rejected':
                # 불합격자 (서류불합격)
                applicants = list(self.db.applicants.find({
                    "status": "서류불합격"
                }))
            else:
                return []
            
            # ObjectId를 문자열로 변환
            for applicant in applicants:
                applicant["_id"] = str(applicant["_id"])
                
            return applicants
        except Exception as e:
            print(f"❌ 지원자 조회 실패: {e}")
            return []
    
    def get_job_posting_info(self, job_posting_id: str) -> Dict[str, Any]:
        """채용공고 정보 조회"""
        try:
            job_posting = self.db.job_postings.find_one({"_id": ObjectId(job_posting_id)})
            if job_posting:
                job_posting["_id"] = str(job_posting["_id"])
            return job_posting or {}
        except Exception as e:
            print(f"❌ 채용공고 정보 조회 실패: {e}")
            return {}
    
    def format_mail_content(self, template: str, applicant: Dict[str, Any], job_posting: Dict[str, Any]) -> str:
        """메일 내용 포맷팅"""
        try:
            # 변수 치환
            formatted_content = template.format(
                applicant_name=applicant.get('name', '지원자'),
                job_posting_title=job_posting.get('title', '채용공고'),
                company_name=job_posting.get('company', '회사명'),
                position=applicant.get('position', '지원 직무')
            )
            return formatted_content
        except Exception as e:
            print(f"❌ 메일 내용 포맷팅 실패: {e}")
            return template
    
    def send_mail(self, to_email: str, subject: str, content: str) -> bool:
        """개별 메일 발송"""
        try:
            # 메일 객체 생성
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 메일 본문 추가
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # SMTP 서버 연결 및 메일 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"❌ 메일 발송 실패 ({to_email}): {e}")
            return False
    
    def send_bulk_mail(self, status_type: str) -> Dict[str, Any]:
        """대량 메일 발송"""
        print(f"📧 {status_type}자들에게 메일 발송 시작...")
        
        # 지원자 조회
        applicants = self.get_applicants_by_status(status_type)
        if not applicants:
            print("⚠️ 발송할 지원자가 없습니다.")
            return {"success": False, "message": "발송할 지원자가 없습니다."}
        
        # 메일 템플릿 조회
        templates = self.get_mail_templates()
        template = templates.get(status_type)
        if not template:
            print("❌ 메일 템플릿을 찾을 수 없습니다.")
            return {"success": False, "message": "메일 템플릿을 찾을 수 없습니다."}
        
        success_count = 0
        failed_count = 0
        failed_emails = []
        
        for applicant in applicants:
            # 지원자 이메일 확인
            email = applicant.get('email')
            if not email:
                print(f"⚠️ {applicant.get('name', 'Unknown')}의 이메일이 없습니다.")
                failed_count += 1
                continue
            
            # 채용공고 정보 조회
            job_posting_id = applicant.get('job_posting_id')
            job_posting = self.get_job_posting_info(job_posting_id) if job_posting_id else {}
            
            # 메일 내용 포맷팅
            formatted_content = self.format_mail_content(
                template['content'], 
                applicant, 
                job_posting
            )
            
            # 메일 발송
            if self.send_mail(email, template['subject'], formatted_content):
                success_count += 1
                print(f"✅ {applicant.get('name', 'Unknown')} ({email}) - 메일 발송 성공")
            else:
                failed_count += 1
                failed_emails.append(email)
                print(f"❌ {applicant.get('name', 'Unknown')} ({email}) - 메일 발송 실패")
        
        # 결과 요약
        result = {
            "success": True,
            "total": len(applicants),
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_emails": failed_emails,
            "message": f"메일 발송 완료: {success_count}건 성공, {failed_count}건 실패"
        }
        
        print(f"\n📊 메일 발송 결과:")
        print(f"  - 총 대상: {len(applicants)}명")
        print(f"  - 성공: {success_count}건")
        print(f"  - 실패: {failed_count}건")
        
        if failed_emails:
            print(f"  - 실패한 이메일: {', '.join(failed_emails)}")
        
        return result

def main():
    """메인 함수"""
    sender = MailSender()
    
    # 사용 예시
    print("🚀 메일 발송 시스템")
    print("1. 합격자 메일 발송")
    print("2. 불합격자 메일 발송")
    
    choice = input("선택하세요 (1 또는 2): ").strip()
    
    if choice == "1":
        result = sender.send_bulk_mail("passed")
    elif choice == "2":
        result = sender.send_bulk_mail("rejected")
    else:
        print("❌ 잘못된 선택입니다.")
        return
    
    print(f"\n🎉 {result['message']}")

if __name__ == "__main__":
    main()
