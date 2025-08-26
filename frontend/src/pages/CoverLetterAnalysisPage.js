import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import CoverLetterAnalysis from '../components/CoverLetterAnalysis';

const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
`;

const ContentWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const Header = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  text-align: center;
`;

const HeaderTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
`;

const HeaderSubtitle = styled.p`
  font-size: 18px;
  opacity: 0.9;
  line-height: 1.6;
`;

const Content = styled.div`
  padding: 40px;
`;

const SelectionSection = styled.div`
  margin-bottom: 32px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
`;

const SelectionTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
`;

const CoverLetterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const CoverLetterCard = styled.div`
  background: white;
  border: 2px solid ${props => props.selected ? '#3b82f6' : '#e9ecef'};
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    border-color: #3b82f6;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  }

  ${props => props.selected && `
    background: #f0f7ff;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  `}
`;

const CoverLetterName = styled.div`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
`;

const CoverLetterPosition = styled.div`
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
`;

const CoverLetterDate = styled.div`
  font-size: 12px;
  color: #999;
`;

const SelectedBadge = styled.div`
  position: absolute;
  top: 8px;
  right: 8px;
  background: #3b82f6;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
`;

const AnalyzeButton = styled.button`
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 16px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }

  &:disabled {
    background: #6c757d;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 16px;
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  padding: 12px;
  margin: 16px 0;
  font-size: 14px;
`;

const CoverLetterAnalysisPage = () => {
  const [coverLetters, setCoverLetters] = useState([]);
  const [selectedCoverLetter, setSelectedCoverLetter] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  // 샘플 자소서 데이터 로드
  useEffect(() => {
    loadSampleCoverLetters();
  }, []);

  const loadSampleCoverLetters = async () => {
    try {
      setIsLoading(true);
      setError(null);

            // 샘플 자소서 데이터 가져오기
      try {
        const response = await fetch('http://localhost:8000/api/sample/cover-letters');

        if (response.ok) {
          const data = await response.json();
          setCoverLetters(data.cover_letters || []);
        } else {
          // API가 없으면 기본 샘플 데이터 사용
          console.log('API 응답 실패, 기본 샘플 데이터 사용');
          throw new Error('API 응답 실패');
        }
      } catch (error) {
        console.log('API 호출 실패, 기본 샘플 데이터 사용:', error);
        // 기본 샘플 데이터 사용
        setCoverLetters([
          {
            id: 1,
            name: '김철수',
            position: '프론트엔드 개발자',
            submittedDate: '2024-01-15',
            content: `안녕하세요. 저는 소프트웨어 개발자로서 3년간의 경험을 쌓아온 김철수입니다.

기술적 역량
저는 Java, Spring Framework, React, Node.js 등 다양한 기술 스택을 보유하고 있습니다. 특히 마이크로서비스 아키텍처 설계와 클라우드 환경에서의 애플리케이션 배포에 대한 경험이 풍부합니다. 최근에는 AWS와 Docker를 활용한 CI/CD 파이프라인 구축 프로젝트를 성공적으로 완료했습니다.

직무 이해도
귀사의 혁신적인 기술 문화와 사용자 중심의 제품 개발 철학에 깊이 공감합니다. 특히 AI와 빅데이터를 활용한 새로운 서비스 개발에 대한 귀사의 비전이 저의 전문 분야와 일치한다고 생각합니다. 저는 이러한 기술을 활용하여 사용자에게 더 나은 가치를 제공하는 서비스를 개발하고 싶습니다.

성장 가능성
저는 지속적인 학습과 새로운 기술 습득에 대한 열정이 있습니다. 최근에는 머신러닝과 데이터 엔지니어링 분야에 관심을 가지고 관련 온라인 강의를 수강하고 있습니다. 또한 오픈소스 프로젝트에 기여하며 커뮤니티와 함께 성장하고 있습니다.

팀워크 및 커뮤니케이션
이전 회사에서는 5명의 개발팀에서 프로젝트 리더를 맡아 팀원들과의 원활한 소통을 통해 프로젝트를 성공적으로 완료했습니다. 다양한 배경을 가진 팀원들과의 협업을 통해 문제 해결 능력과 갈등 조정 능력을 향상시켰습니다.

지원 동기
귀사의 혁신적인 제품과 서비스가 사용자들의 삶을 어떻게 변화시키는지 지켜보며, 저도 이러한 가치 있는 일에 기여하고 싶다는 생각을 하게 되었습니다. 특히 귀사의 사용자 중심 설계 철학과 지속적인 혁신 추구가 저의 가치관과 일치합니다.

앞으로 귀사에서 더 많은 경험을 쌓으며 성장하고, 팀과 함께 사용자에게 가치 있는 서비스를 제공하는 개발자가 되고 싶습니다. 감사합니다.`
          },
          {
            id: 2,
            name: '이영희',
            position: '백엔드 개발자',
            submittedDate: '2024-01-14',
            content: `안녕하세요. 백엔드 개발자 이영희입니다.

저는 4년간의 백엔드 개발 경험을 통해 Java, Spring Boot, MySQL, Redis 등의 기술 스택을 활용하여 다양한 웹 서비스를 개발해왔습니다. 특히 대용량 트래픽 처리와 데이터베이스 최적화에 대한 깊은 이해를 가지고 있습니다.

최근에는 마이크로서비스 아키텍처로의 전환 프로젝트를 주도하여 시스템의 확장성과 유지보수성을 크게 향상시켰습니다. 이 과정에서 Docker, Kubernetes를 활용한 컨테이너화와 CI/CD 파이프라인 구축 경험도 쌓았습니다.

귀사의 데이터 중심 의사결정과 고성능 시스템 구축에 대한 접근 방식에 깊이 공감합니다. 저의 기술적 경험과 문제 해결 능력을 바탕으로 귀사의 서비스 발전에 기여하고 싶습니다.`
          },
          {
            id: 3,
            name: '박민수',
            position: 'UI/UX 디자이너',
            submittedDate: '2024-01-13',
            content: `안녕하세요. UI/UX 디자이너 박민수입니다.

저는 사용자 중심의 디자인 철학을 바탕으로 3년간 다양한 디지털 제품의 사용자 경험을 설계해왔습니다. Figma, Sketch, Adobe Creative Suite를 활용하여 웹과 모바일 애플리케이션의 인터페이스를 디자인하고, 사용자 테스트를 통해 지속적으로 개선해왔습니다.

특히 접근성과 사용성을 고려한 디자인 시스템 구축에 대한 경험이 풍부하며, 개발팀과의 원활한 협업을 통해 아이디어를 실제 제품으로 구현하는 과정을 즐깁니다.

귀사의 혁신적인 제품과 사용자 중심의 디자인 철학에 깊이 공감하며, 저의 창의성과 기술적 이해를 바탕으로 더 나은 사용자 경험을 만들어가고 싶습니다.`
          }
        ]);
      }
    } catch (error) {
      console.error('자소서 데이터 로드 오류:', error);
      setError('자소서 데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCoverLetterSelect = (coverLetter) => {
    setSelectedCoverLetter(coverLetter);
    setAnalysisResult(null); // 이전 분석 결과 초기화
  };

  const handleAnalysisComplete = (result) => {
    setAnalysisResult(result);
    console.log('자소서 분석 완료:', result);
  };

  const handleAnalyze = async () => {
    if (!selectedCoverLetter) {
      setError('분석할 자소서를 선택해주세요.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // 선택된 자소서의 내용을 텍스트 파일로 변환하여 분석
      const content = selectedCoverLetter.content;

      // 텍스트를 Blob으로 변환
      const blob = new Blob([content], { type: 'text/plain' });
      const file = new File([blob], `${selectedCoverLetter.name}_자소서.txt`, { type: 'text/plain' });

      // 자소서 분석 API 호출
      const formData = new FormData();
      formData.append('file', file);
      formData.append('job_description', `${selectedCoverLetter.position} 직무`);
      formData.append('analysis_type', 'comprehensive');

      const response = await fetch('http://localhost:8000/api/cover-letter/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message || '자소서 분석에 실패했습니다.');
      }

      setAnalysisResult(result.data);
    } catch (error) {
      console.error('자소서 분석 오류:', error);
      setError(error.message || '자소서 분석 중 오류가 발생했습니다.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (isLoading) {
    return (
      <PageContainer>
        <ContentWrapper>
          <Header>
            <HeaderTitle>자소서 AI 분석</HeaderTitle>
            <HeaderSubtitle>
              업로드한 자소서를 AI가 분석하여 기술적합성, 직무이해도, 성장 가능성 등을<br/>
              종합적으로 평가해드립니다.
            </HeaderSubtitle>
          </Header>
          <Content>
            <LoadingMessage>자소서 데이터를 불러오는 중...</LoadingMessage>
          </Content>
        </ContentWrapper>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <ContentWrapper>
        <Header>
          <HeaderTitle>자소서 AI 분석</HeaderTitle>
          <HeaderSubtitle>
            샘플 자소서를 선택하여 AI가 분석한 결과를 확인해보세요.<br/>
            기술적합성, 직무이해도, 성장 가능성 등을 종합적으로 평가해드립니다.
          </HeaderSubtitle>
        </Header>

        <Content>
          {/* 자소서 선택 섹션 */}
          <SelectionSection>
            <SelectionTitle>분석할 자소서 선택</SelectionTitle>
            <CoverLetterGrid>
              {coverLetters.map((coverLetter) => (
                <CoverLetterCard
                  key={coverLetter.id}
                  selected={selectedCoverLetter?.id === coverLetter.id}
                  onClick={() => handleCoverLetterSelect(coverLetter)}
                >
                  {selectedCoverLetter?.id === coverLetter.id && (
                    <SelectedBadge>선택됨</SelectedBadge>
                  )}
                  <CoverLetterName>{coverLetter.name}</CoverLetterName>
                  <CoverLetterPosition>{coverLetter.position}</CoverLetterPosition>
                  <CoverLetterDate>제출일: {coverLetter.submittedDate}</CoverLetterDate>
                </CoverLetterCard>
              ))}
            </CoverLetterGrid>

            <AnalyzeButton
              onClick={handleAnalyze}
              disabled={!selectedCoverLetter || isAnalyzing}
            >
              {isAnalyzing ? '분석 중...' : '선택한 자소서 분석하기'}
            </AnalyzeButton>

            {error && (
              <ErrorMessage>
                {error}
              </ErrorMessage>
            )}
          </SelectionSection>

          {/* 분석 결과 표시 */}
          {analysisResult && (
            <CoverLetterAnalysis
              analysisData={analysisResult}
              onAnalysisComplete={handleAnalysisComplete}
            />
          )}
        </Content>
      </ContentWrapper>
    </PageContainer>
  );
};

export default CoverLetterAnalysisPage;
