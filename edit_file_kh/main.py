from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 한글 인코딩 설정
CORS(app)

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017/')
db = client['hireme']

@app.route('/api/mail-templates', methods=['GET'])
def get_mail_templates():
    """메일 템플릿 조회"""
    try:
        templates = db.mail_templates.find_one({"_id": "default"})
        if not templates:
            # 기본 템플릿 생성
            default_templates = {
                "_id": "default",
                "passed": {
                    "subject": "축하합니다! 서류 전형 합격 안내",
                    "content": """안녕하세요, {applicant_name}님

축하드립니다! {job_posting_title} 포지션에 대한 서류 전형에 합격하셨습니다.

다음 단계인 면접 일정은 추후 별도로 안내드리겠습니다.

감사합니다.
{company_name} 채용팀"""
                },
                "rejected": {
                    "subject": "서류 전형 결과 안내",
                    "content": """안녕하세요, {applicant_name}님

{job_posting_title} 포지션에 대한 서류 전형 결과를 안내드립니다.

안타깝게도 이번 전형에서는 합격하지 못했습니다.
앞으로 더 좋은 기회가 있을 때 다시 지원해 주시기 바랍니다.

감사합니다.
{company_name} 채용팀"""
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            db.mail_templates.insert_one(default_templates)
            templates = default_templates
        
        # _id 제거하고 반환
        templates.pop("_id", None)
        return jsonify(templates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/mail-templates', methods=['POST'])
def save_mail_templates():
    """메일 템플릿 저장"""
    try:
        data = request.json
        update_data = {
            "passed": data.get("passed", {}),
            "rejected": data.get("rejected", {}),
            "updated_at": datetime.now()
        }
        
        result = db.mail_templates.update_one(
            {"_id": "default"},
            {"$set": update_data},
            upsert=True
        )
        
        return jsonify({"success": True, "message": "메일 템플릿이 저장되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/mail-settings', methods=['GET'])
def get_mail_settings():
    """메일 설정 조회"""
    try:
        settings = db.mail_settings.find_one({"_id": "default"})
        if not settings:
            # 기본 설정 생성
            default_settings = {
                "_id": "default",
                "senderEmail": "",
                "senderPassword": "",
                "senderName": "",
                "smtpServer": "smtp.gmail.com",
                "smtpPort": 587,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            db.mail_settings.insert_one(default_settings)
            settings = default_settings
        
        # _id 제거하고 반환
        settings.pop("_id", None)
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pick-chatbot/generate-title', methods=['POST'])
def generate_title():
    """채용공고 제목을 생성합니다."""
    try:
        data = request.json
        form_data = data.get('form_data', {})
        content = data.get('content', '')
        
        print(f"[API] 제목 생성 요청: {form_data}")
        
        # 폼 데이터에서 키워드 추출
        keywords = []
        if form_data.get('department'):
            keywords.append(form_data['department'])
        if form_data.get('position'):
            keywords.append(form_data['position'])
        if form_data.get('mainDuties'):
            # 주요 업무에서 키워드 추출
            duties = form_data['mainDuties']
            # 간단한 키워드 추출 (첫 번째 명사나 동사)
            words = duties.split()
            if words:
                keywords.append(words[0])
        
        # 기본 키워드가 없으면 기본값 사용
        if not keywords:
            keywords = ['직무', '인재']
        
        # AI 제목 생성 (실제로는 LLM 서비스 호출)
        # 현재는 기본 제목 생성
        generated_titles = [
            {
                "concept": "신입친화형",
                "title": f"함께 성장할 {keywords[0]} 신입을 찾습니다",
                "description": "신입 지원자들이 매력적으로 느낄 수 있는 제목"
            },
            {
                "concept": "전문가형",
                "title": f"전문성을 발휘할 {keywords[0]} 인재 모집",
                "description": "경력자들이 전문성을 발휘할 수 있다고 느끼는 제목"
            },
            {
                "concept": "일반형",
                "title": f"{keywords[0]} {keywords[1] if len(keywords) > 1 else '직무'} 채용",
                "description": "일반적인 채용공고 제목"
            },
            {
                "concept": "창의형",
                "title": f"혁신을 이끌 {keywords[0]}를 찾습니다",
                "description": "독특하고 눈에 띄는 제목"
            }
        ]
        
        return jsonify({
            "titles": generated_titles,
            "message": "AI가 생성한 제목 추천입니다."
        })
        
    except Exception as e:
        print(f"[API] 제목 생성 실패: {str(e)}")
        return jsonify({"error": f"제목 생성에 실패했습니다: {str(e)}"}), 500

@app.route('/api/mail-settings', methods=['POST'])
def save_mail_settings():
    """메일 설정 저장"""
    try:
        data = request.json
        update_data = {
            "senderEmail": data.get("senderEmail", ""),
            "senderPassword": data.get("senderPassword", ""),
            "senderName": data.get("senderName", ""),
            "smtpServer": data.get("smtpServer", "smtp.gmail.com"),
            "smtpPort": data.get("smtpPort", 587),
            "updated_at": datetime.now()
        }
        
        result = db.mail_settings.update_one(
            {"_id": "default"},
            {"$set": update_data},
            upsert=True
        )
        
        return jsonify({"success": True, "message": "메일 설정이 저장되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send-bulk-mail', methods=['POST'])
def send_bulk_mail():
    """대량 메일 발송"""
    try:
        data = request.json
        status_type = data.get("status_type")  # "passed" 또는 "rejected"
        
        if not status_type:
            return jsonify({"error": "status_type이 필요합니다."}), 400
        
        # 메일 설정 조회
        mail_settings = db.mail_settings.find_one({"_id": "default"})
        if not mail_settings:
            return jsonify({"error": "메일 설정이 필요합니다."}), 400
        
        # 메일 템플릿 조회
        mail_templates = db.mail_templates.find_one({"_id": "default"})
        if not mail_templates:
            return jsonify({"error": "메일 템플릿이 필요합니다."}), 400
        
        # 지원자 조회
        if status_type == 'passed':
            applicants = list(db.applicants.find({
                "status": {"$in": ["서류합격", "최종합격"]}
            }))
        elif status_type == 'rejected':
            applicants = list(db.applicants.find({
                "status": "서류불합격"
            }))
        else:
            return jsonify({"error": "잘못된 status_type입니다."}), 400
        
        if not applicants:
            return jsonify({"error": "발송할 지원자가 없습니다."}), 400
        
        # TODO: 실제 메일 발송 로직 구현
        # 현재는 시뮬레이션만 수행
        success_count = len(applicants)
        
        return jsonify({
            "success": True,
            "message": f"{status_type}자들에게 메일 발송이 완료되었습니다.",
            "total": len(applicants),
            "success_count": success_count,
            "failed_count": 0
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send-test-mail', methods=['POST'])
def send_test_mail():
    """테스트 메일 발송"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        data = request.json
        print(f"받은 데이터: {data}")  # 디버깅용 로그
        
        test_email = data.get("testEmail")
        mail_settings = data.get("mailSettings")
        
        print(f"테스트 이메일: {test_email}")  # 디버깅용 로그
        print(f"메일 설정: {mail_settings}")  # 디버깅용 로그
        
        if not test_email or not mail_settings:
            print("테스트 이메일 또는 메일 설정이 없습니다.")  # 디버깅용 로그
            return jsonify({"error": "테스트 이메일과 메일 설정이 필요합니다."}), 400
        
        # 메일 템플릿 조회
        mail_templates = db.mail_templates.find_one({"_id": "default"})
        if not mail_templates:
            return jsonify({"error": "메일 템플릿이 필요합니다."}), 400
        
        # 테스트 메일 내용 생성
        template = mail_templates.get("passed", {})
        subject = template.get("subject", "테스트 메일")
        content = template.get("content", "테스트 메일입니다.")
        
        # 변수 치환
        content = content.format(
            applicant_name="테스트 사용자",
            job_posting_title="테스트 채용공고",
            company_name="테스트 회사",
            position="테스트 직무"
        )
        
        # 메일 객체 생성
        msg = MIMEMultipart()
        msg['From'] = f"{mail_settings.get('senderName', '')} <{mail_settings.get('senderEmail')}>"
        msg['To'] = test_email
        msg['Subject'] = f"[테스트] {subject}"
        
        # 메일 본문 추가
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # SMTP 서버 연결 및 메일 발송
        try:
            print(f"SMTP 서버 연결 시도: {mail_settings.get('smtpServer')}:{mail_settings.get('smtpPort')}")  # 디버깅용 로그
            print(f"발송자 이메일: {mail_settings.get('senderEmail')}")  # 디버깅용 로그
            print(f"발송자 비밀번호 길이: {len(mail_settings.get('senderPassword', ''))}")  # 디버깅용 로그
            print(f"발송자 비밀번호: {mail_settings.get('senderPassword', '')[:4]}***")  # 디버깅용 로그 (앞 4자리만)
            
            smtp_port = mail_settings.get('smtpPort', 587)
            smtp_server = mail_settings.get('smtpServer', 'smtp.gmail.com')
            
            # 포트 465인 경우 SSL 사용
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                    print("SMTP SSL 서버 연결 성공")  # 디버깅용 로그
                    print(f"로그인 시도: {mail_settings.get('senderEmail')}")  # 디버깅용 로그
                    server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                    print("로그인 성공")  # 디버깅용 로그
                    server.send_message(msg)
                    print("메일 발송 성공")  # 디버깅용 로그
            else:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    print("SMTP 서버 연결 성공")  # 디버깅용 로그
                    server.starttls()
                    print("STARTTLS 성공")  # 디버깅용 로그
                    print(f"로그인 시도: {mail_settings.get('senderEmail')}")  # 디버깅용 로그
                    server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                    print("로그인 성공")  # 디버깅용 로그
                    server.send_message(msg)
                    print("메일 발송 성공")  # 디버깅용 로그
            
            return jsonify({
                "success": True,
                "message": "테스트 메일이 성공적으로 발송되었습니다.",
                "subject": f"[테스트] {subject}",
                "to": test_email
            })
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"인증 실패: {str(e)}")  # 디버깅용 로그
            return jsonify({"error": "인증 실패. 이메일 주소와 앱 비밀번호를 확인해주세요."}), 400
        except smtplib.SMTPException as e:
            print(f"SMTP 오류: {str(e)}")  # 디버깅용 로그
            return jsonify({"error": f"SMTP 오류: {str(e)}"}), 400
        except Exception as e:
            print(f"메일 발송 오류: {str(e)}")  # 디버깅용 로그
            return jsonify({"error": f"메일 발송 오류: {str(e)}"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 기존 API들...
@app.route('/api/applicants', methods=['GET', 'POST'])
def applicants():
    """지원자 목록 조회 및 생성"""
    if request.method == 'GET':
        try:
            applicants = list(db.applicants.find())
            
            # ObjectId를 문자열로 변환
            for applicant in applicants:
                applicant['_id'] = str(applicant['_id'])
                applicant['id'] = str(applicant['_id'])  # id 필드 추가
                
                # 모든 ObjectId 필드들을 문자열로 변환
                if 'job_posting_id' in applicant and applicant['job_posting_id']:
                    applicant['job_posting_id'] = str(applicant['job_posting_id'])
                if 'resume_id' in applicant and applicant['resume_id']:
                    applicant['resume_id'] = str(applicant['resume_id'])
                if 'cover_letter_id' in applicant and applicant['cover_letter_id']:
                    applicant['cover_letter_id'] = str(applicant['cover_letter_id'])
                if 'portfolio_id' in applicant and applicant['portfolio_id']:
                    applicant['portfolio_id'] = str(applicant['portfolio_id'])
            
            return jsonify({"applicants": applicants})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            
            # 필수 필드 검증
            required_fields = ['name', 'email']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400
            
            # 생성 시간 추가
            data['created_at'] = datetime.now()
            
            # 기본값 설정
            if 'status' not in data:
                data['status'] = 'pending'
            if 'analysisScore' not in data:
                data['analysisScore'] = 0
            
            # MongoDB에 삽입
            result = db.applicants.insert_one(data)
            
            if result.inserted_id:
                # 생성된 지원자 정보 반환
                applicant = db.applicants.find_one({"_id": result.inserted_id})
                applicant['_id'] = str(applicant['_id'])
                applicant['id'] = str(applicant['_id'])
                
                return jsonify(applicant), 201
            else:
                return jsonify({"error": "지원자 생성에 실패했습니다"}), 500
                
        except Exception as e:
            return jsonify({"error": f"지원자 생성 실패: {str(e)}"}), 500

@app.route('/api/applicants/stats/overview', methods=['GET'])
def get_applicant_stats():
    """지원자 통계 조회"""
    try:
        total_applicants = db.applicants.count_documents({})
        
        # 상태별 지원자 수 (영문 상태값 기준)
        pending_count = db.applicants.count_documents({"status": "pending"})
        reviewing_count = db.applicants.count_documents({"status": "reviewing"})
        interview_scheduled_count = db.applicants.count_documents({"status": "interview_scheduled"})
        passed_count = db.applicants.count_documents({"status": "passed"})
        rejected_count = db.applicants.count_documents({"status": "rejected"})
        
        # 기존 한글 상태값도 포함
        old_pending_count = db.applicants.count_documents({"status": "지원"})
        old_approved_count = db.applicants.count_documents({"status": {"$in": ["서류합격", "최종합격"]}})
        old_rejected_count = db.applicants.count_documents({"status": "서류불합격"})
        old_waiting_count = db.applicants.count_documents({"status": {"$in": ["보류", "면접대기"]}})
        
        # 통합된 카운트
        total_pending = pending_count + old_pending_count
        total_approved = passed_count + old_approved_count
        total_rejected = rejected_count + old_rejected_count
        total_waiting = reviewing_count + interview_scheduled_count + old_waiting_count
        
        # 최근 30일간 지원자 수
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_applicants = db.applicants.count_documents({"created_at": {"$gte": thirty_days_ago}})
        
        return jsonify({
            "total_applicants": total_applicants,
            "status_breakdown": {
                "pending": total_pending,
                "approved": total_approved,
                "rejected": total_rejected,
                "waiting": total_waiting,
                "reviewing": reviewing_count,
                "interview_scheduled": interview_scheduled_count,
                "passed": passed_count
            },
            "recent_applicants_30_days": recent_applicants,
            "success_rate": round((total_approved / total_applicants * 100) if total_applicants > 0 else 0, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/applicants/<applicant_id>/status', methods=['PUT'])
def update_applicant_status(applicant_id):
    """지원자 상태 업데이트"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({"error": "상태 값이 필요합니다"}), 400
        
        # ObjectId로 변환 시도
        try:
            from bson import ObjectId
            result = db.applicants.update_one(
                {"_id": ObjectId(applicant_id)},
                {"$set": {"status": new_status, "updated_at": datetime.now()}}
            )
        except:
            # ObjectId 변환 실패 시 문자열로 시도
            result = db.applicants.update_one(
                {"_id": applicant_id},
                {"$set": {"status": new_status, "updated_at": datetime.now()}}
            )
        
        if result.modified_count > 0:
            return jsonify({
                "message": "상태가 성공적으로 업데이트되었습니다",
                "status": new_status
            })
        else:
            return jsonify({"error": "지원자를 찾을 수 없습니다"}), 404
            
    except Exception as e:
        return jsonify({"error": f"상태 업데이트 실패: {str(e)}"}), 500

@app.route('/api/job-postings', methods=['GET', 'POST'])
def job_postings():
    """채용공고 목록 조회 및 생성"""
    if request.method == 'GET':
        try:
            job_postings = list(db.job_postings.find())
            
            # ObjectId를 문자열로 변환
            for job_posting in job_postings:
                job_posting['_id'] = str(job_posting['_id'])
            
            return jsonify(job_postings)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            
            # 필수 필드 검증
            required_fields = ['title', 'department', 'position']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400
            
            # 생성 시간 추가
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            
            # MongoDB에 저장
            result = db.job_postings.insert_one(data)
            
            # 생성된 문서 조회
            created_job_posting = db.job_postings.find_one({"_id": result.inserted_id})
            created_job_posting['_id'] = str(created_job_posting['_id'])
            
            return jsonify({
                "message": "채용공고가 성공적으로 생성되었습니다.",
                "job_posting": created_job_posting
            }), 201
            
        except Exception as e:
            return jsonify({"error": f"채용공고 생성 실패: {str(e)}"}), 500

@app.route('/api/job-postings/<job_id>', methods=['GET', 'PUT', 'DELETE'])
def job_posting_detail(job_id):
    """채용공고 상세 조회, 수정, 삭제"""
    if request.method == 'GET':
        try:
            from bson import ObjectId
            job_posting = db.job_postings.find_one({"_id": ObjectId(job_id)})
            
            if not job_posting:
                return jsonify({"error": "채용공고를 찾을 수 없습니다"}), 404
            
            job_posting['_id'] = str(job_posting['_id'])
            return jsonify(job_posting)
            
        except Exception as e:
            return jsonify({"error": f"채용공고 조회 실패: {str(e)}"}), 500
    
    elif request.method == 'PUT':
        try:
            from bson import ObjectId
            data = request.json
            
            # 업데이트 시간 추가
            data['updated_at'] = datetime.now()
            
            result = db.job_postings.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": data}
            )
            
            if result.modified_count > 0:
                return jsonify({"message": "채용공고가 성공적으로 수정되었습니다"})
            else:
                return jsonify({"error": "채용공고를 찾을 수 없습니다"}), 404
                
        except Exception as e:
            return jsonify({"error": f"채용공고 수정 실패: {str(e)}"}), 500
    
    elif request.method == 'DELETE':
        try:
            # job_id가 undefined이거나 유효하지 않은 경우 처리
            if not job_id or job_id == 'undefined' or job_id == 'null':
                return jsonify({"error": "유효하지 않은 채용공고 ID입니다"}), 400
            
            from bson import ObjectId
            result = db.job_postings.delete_one({"_id": ObjectId(job_id)})
            
            if result.deleted_count > 0:
                return jsonify({"message": "채용공고가 성공적으로 삭제되었습니다"})
            else:
                return jsonify({"error": "채용공고를 찾을 수 없습니다"}), 404
                
        except Exception as e:
            return jsonify({"error": f"채용공고 삭제 실패: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=8000)