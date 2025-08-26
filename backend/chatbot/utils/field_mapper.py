"""
필드 매핑 유틸리티
"""

from typing import Dict, Any, Optional

class FieldMapper:
    """필드 매핑 유틸리티 클래스"""
    
    # 백엔드 필드명과 프론트엔드 필드명 매핑
    FIELD_MAPPING = {
        # 기본 정보
        'title': 'title',
        'department': 'department',
        'experience': 'experience',
        'salary': 'salary',
        'location': 'locationCity',
        'headcount': 'headcount',
        
        # 상세 정보
        'description': 'description',
        'requirements': 'requirements',
        'benefits': 'benefits',
        'work_type': 'workType',
        'education': 'education',
        
        # 회사 정보
        'company_name': 'companyName',
        'company_size': 'companySize',
        'industry': 'industry',
        
        # 기타
        'deadline': 'deadline',
        'contact': 'contact',
        'website': 'website'
    }
    
    # 역방향 매핑 (프론트엔드 -> 백엔드)
    REVERSE_FIELD_MAPPING = {v: k for k, v in FIELD_MAPPING.items()}
    
    @classmethod
    def map_backend_to_frontend(cls, backend_fields: Dict[str, Any]) -> Dict[str, Any]:
        """백엔드 필드명을 프론트엔드 필드명으로 변환"""
        frontend_fields = {}
        
        for backend_field, value in backend_fields.items():
            if backend_field in cls.FIELD_MAPPING:
                frontend_field = cls.FIELD_MAPPING[backend_field]
                frontend_fields[frontend_field] = value
            else:
                # 매핑이 없는 경우 그대로 사용
                frontend_fields[backend_field] = value
        
        return frontend_fields
    
    @classmethod
    def map_frontend_to_backend(cls, frontend_fields: Dict[str, Any]) -> Dict[str, Any]:
        """프론트엔드 필드명을 백엔드 필드명으로 변환"""
        backend_fields = {}
        
        for frontend_field, value in frontend_fields.items():
            if frontend_field in cls.REVERSE_FIELD_MAPPING:
                backend_field = cls.REVERSE_FIELD_MAPPING[frontend_field]
                backend_fields[backend_field] = value
            else:
                # 매핑이 없는 경우 그대로 사용
                backend_fields[frontend_field] = value
        
        return backend_fields
    
    @classmethod
    def get_frontend_field_name(cls, backend_field: str) -> str:
        """백엔드 필드명에 해당하는 프론트엔드 필드명 반환"""
        return cls.FIELD_MAPPING.get(backend_field, backend_field)
    
    @classmethod
    def get_backend_field_name(cls, frontend_field: str) -> str:
        """프론트엔드 필드명에 해당하는 백엔드 필드명 반환"""
        return cls.REVERSE_FIELD_MAPPING.get(frontend_field, frontend_field)
    
    @classmethod
    def validate_field_mapping(cls, field_name: str, direction: str = "backend_to_frontend") -> bool:
        """필드 매핑 유효성 검사"""
        if direction == "backend_to_frontend":
            return field_name in cls.FIELD_MAPPING
        elif direction == "frontend_to_backend":
            return field_name in cls.REVERSE_FIELD_MAPPING
        else:
            return False
    
    @classmethod
    def get_all_mapped_fields(cls) -> Dict[str, str]:
        """모든 매핑된 필드 반환"""
        return cls.FIELD_MAPPING.copy()
    
    @classmethod
    def get_all_reverse_mapped_fields(cls) -> Dict[str, str]:
        """모든 역방향 매핑된 필드 반환"""
        return cls.REVERSE_FIELD_MAPPING.copy()

