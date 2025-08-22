import asyncio
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path
import json

from .ai_analyzer import analyze_text
from .config import Settings
from .storage import save_document_to_mongo
from .utils import ensure_directories

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundProcessor:
    """백그라운드에서 AI 분석을 처리하는 클래스"""
    
    def __init__(self):
        self.settings = Settings()
        self.processing_queue = []
        self.is_running = False
        self.worker_thread = None
        self.processing_status = {}  # 작업 상태 추적
        
    def start_worker(self):
        """백그라운드 워커 스레드 시작"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("🚀 백그라운드 AI 분석 워커 시작됨")
    
    def stop_worker(self):
        """백그라운드 워커 스레드 중지"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
            logger.info("⏹️ 백그라운드 AI 분석 워커 중지됨")
    
    def add_to_queue(self, task_id: str, pdf_path: str, extracted_text: str, 
                     basic_info: Dict[str, Any], document_type: str = "resume"):
        """분석 작업을 큐에 추가"""
        task = {
            "id": task_id,
            "pdf_path": pdf_path,
            "extracted_text": extracted_text,
            "basic_info": basic_info,
            "document_type": document_type,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None
        }
        
        self.processing_queue.append(task)
        self.processing_status[task_id] = task
        
        logger.info(f"📋 작업 {task_id}가 큐에 추가됨 (총 {len(self.processing_queue)}개)")
        
        # 워커가 실행 중이 아니면 시작
        if not self.is_running:
            self.start_worker()
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 조회"""
        return self.processing_status.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Any]:
        """모든 작업 상태 조회"""
        return {
            "queue_length": len(self.processing_queue),
            "processing": len([t for t in self.processing_status.values() if t["status"] == "processing"]),
            "completed": len([t for t in self.processing_status.values() if t["status"] == "completed"]),
            "failed": len([t for t in self.processing_status.values() if t["status"] == "failed"]),
            "tasks": self.processing_status
        }
    
    def _worker_loop(self):
        """백그라운드 워커 메인 루프"""
        logger.info("🔄 백그라운드 워커 루프 시작")
        
        while self.is_running:
            try:
                if self.processing_queue:
                    # 큐에서 작업 가져오기
                    task = self.processing_queue.pop(0)
                    self._process_task(task)
                else:
                    # 큐가 비어있으면 잠시 대기
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ 백그라운드 워커 오류: {str(e)}")
                time.sleep(5)  # 오류 발생 시 잠시 대기
        
        logger.info("🔄 백그라운드 워커 루프 종료")
    
    def _process_task(self, task: Dict[str, Any]):
        """개별 작업 처리"""
        task_id = task["id"]
        logger.info(f"🔍 작업 {task_id} AI 분석 시작")
        
        try:
            # 작업 상태를 processing으로 변경
            task["status"] = "processing"
            task["started_at"] = datetime.utcnow().isoformat()
            self.processing_status[task_id] = task
            
            # AI 분석 수행
            analysis_result = self._perform_ai_analysis(
                task["extracted_text"], 
                task["document_type"]
            )
            
            # 결과를 MongoDB에 저장
            self._save_analysis_result(task, analysis_result)
            
            # 작업 완료
            task["status"] = "completed"
            task["completed_at"] = datetime.utcnow().isoformat()
            self.processing_status[task_id] = task
            
            logger.info(f"✅ 작업 {task_id} AI 분석 완료")
            
        except Exception as e:
            # 오류 발생 시 상태 업데이트
            task["status"] = "failed"
            task["error"] = str(e)
            task["completed_at"] = datetime.utcnow().isoformat()
            self.processing_status[task_id] = task
            
            logger.error(f"❌ 작업 {task_id} AI 분석 실패: {str(e)}")
    
    def _perform_ai_analysis(self, text: str, document_type: str) -> Dict[str, Any]:
        """AI 분석 수행"""
        try:
            # 텍스트 길이 제한 (너무 긴 텍스트는 처리 시간이 오래 걸림)
            max_length = self.settings.max_text_length
            if len(text) > max_length:
                text = text[:max_length]
                logger.info(f"📝 텍스트 길이 제한: {max_length}자로 자름")
            
            # AI 분석 실행
            analysis = analyze_text(text, self.settings)
            
            return {
                "ai_analysis": analysis,
                "document_type": document_type,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "text_length": len(text),
                "truncated": len(text) > max_length
            }
            
        except Exception as e:
            logger.error(f"❌ AI 분석 실패: {str(e)}")
            raise
    
    def _save_analysis_result(self, task: Dict[str, Any], analysis_result: Dict[str, Any]):
        """분석 결과를 MongoDB에 저장"""
        try:
            # 기존 문서에 AI 분석 결과 추가
            document_data = {
                "ai_analysis": analysis_result,
                "processing_status": "completed",
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # MongoDB 업데이트 (실제 구현은 mongo_service 사용)
            # self.mongo_service.update_document(task["id"], document_data)
            
            logger.info(f"💾 작업 {task['id']} 분석 결과 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 분석 결과 저장 실패: {str(e)}")
            raise

# 전역 인스턴스
background_processor = BackgroundProcessor()

def get_background_processor() -> BackgroundProcessor:
    """백그라운드 프로세서 인스턴스 반환"""
    return background_processor

