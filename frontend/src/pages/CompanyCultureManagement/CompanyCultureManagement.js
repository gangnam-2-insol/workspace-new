import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FiPlus, FiEdit, FiTrash2, FiEye, FiCheck, FiX } from 'react-icons/fi';

const Container = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
`;

const Button = styled.button`
  background: ${props => props.variant === 'secondary' ? 'var(--background-secondary)' : 'var(--primary-color)'};
  color: ${props => props.variant === 'secondary' ? 'var(--text-primary)' : 'white'};
  border: 1px solid ${props => props.variant === 'secondary' ? 'var(--border-color)' : 'var(--primary-color)'};
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.variant === 'secondary' ? 'var(--background-tertiary)' : 'var(--primary-dark)'};
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const Card = styled.div`
  background: ${props => props.isDefault ? 'linear-gradient(135deg, #f8fff9 0%, #e8f5e8 100%)' : 'white'};
  border-radius: 12px;
  padding: 24px;
  box-shadow: ${props => props.isDefault ? '0 4px 20px rgba(40, 167, 69, 0.15)' : '0 2px 8px rgba(0, 0, 0, 0.1)'};
  border: ${props => props.isDefault ? '2px solid #28a745' : '1px solid var(--border-color)'};
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    box-shadow: ${props => props.isDefault ? '0 6px 24px rgba(40, 167, 69, 0.2)' : '0 4px 16px rgba(0, 0, 0, 0.15)'};
    transform: translateY(-2px);
  }

  ${props => props.isDefault && `
    &::before {
      content: '⭐';
      position: absolute;
      top: -8px;
      right: -8px;
      background: #28a745;
      color: white;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    }
  `}
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const CardTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  padding: 6px;
  border-radius: 4px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }

  &.delete:hover {
    background: #fee2e2;
    color: #dc2626;
  }
`;



const Description = styled.p`
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
`;



const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const ModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-weight: 500;
  color: var(--text-primary);
  font-size: 14px;
`;

const Input = styled.input`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const Textarea = styled.textarea`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  min-height: 100px;
  resize: vertical;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const Select = styled.select`
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;



const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
`;

const EmptyStateIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
`;

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// CSS 애니메이션 스타일 추가
const spinAnimation = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// 스타일 태그 추가
const style = document.createElement('style');
style.textContent = spinAnimation;
document.head.appendChild(style);

const CompanyCultureManagement = () => {
  const [cultures, setCultures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [editingCulture, setEditingCulture] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [aiGeneratedCultures, setAiGeneratedCultures] = useState([]);
  const [selectedAICultures, setSelectedAICultures] = useState([]);
  const [showKeywordModal, setShowKeywordModal] = useState(false);
  const [userKeywords, setUserKeywords] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    loadCultures();
  }, []);

  const loadCultures = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/company-culture/`);

      if (response.ok) {
        const data = await response.json();
        setCultures(data);
      } else {
        console.error('인재상 로딩 실패:', response.status);
      }
    } catch (error) {
      console.error('인재상 로딩 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const submitData = {
        ...formData
      };

      const url = editingCulture
        ? `${API_BASE_URL}/api/company-culture/${editingCulture.id}`
        : `${API_BASE_URL}/api/company-culture/`;

      const method = editingCulture ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });

      if (response.ok) {
        const result = await response.json();
        setShowModal(false);
        setEditingCulture(null);
        resetForm();
        loadCultures();

        // 성공 메시지 표시
        if (editingCulture) {
          alert('인재상이 성공적으로 수정되었습니다.');
        } else {
          alert('인재상이 성공적으로 등록되었습니다.');
        }
      } else {
        const error = await response.json();
        alert(`저장 실패: ${error.detail}`);
      }
    } catch (error) {
      console.error('저장 오류:', error);
      alert('저장 중 오류가 발생했습니다.');
    }
  };

  const handleEdit = (culture) => {
    setEditingCulture(culture);
    setFormData({
      name: culture.name,
      description: culture.description
    });
    setShowModal(true);
  };

  const handleDelete = async (cultureId) => {
    // 기본 인재상인지 확인
    const culture = cultures.find(c => c.id === cultureId);
    if (culture && culture.is_default) {
      alert('기본 인재상은 삭제할 수 없습니다. 다른 인재상을 기본으로 설정한 후 삭제해주세요.');
      return;
    }

    if (!window.confirm('정말로 이 인재상을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/${cultureId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        loadCultures();
        alert('인재상이 삭제되었습니다.');
      } else {
        const errorData = await response.json();
        alert(`삭제 실패: ${errorData.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('삭제 오류:', error);
      alert('삭제 중 오류가 발생했습니다.');
    }
  };

  const handleSetDefault = async (cultureId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/company-culture/${cultureId}/set-default`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        loadCultures();
        alert('기본 인재상이 설정되었습니다.');
      } else {
        alert('기본 인재상 설정 실패');
      }
    } catch (error) {
      console.error('기본 인재상 설정 오류:', error);
      alert('기본 인재상 설정 중 오류가 발생했습니다.');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: ''
    });
  };

    const handleAIGenerate = async () => {
    // 키워드 입력 모달 표시
    setShowKeywordModal(true);
  };

  const handleKeywordSubmit = async () => {
    // 키워드가 없어도 기본 인재상 추천 가능하도록 수정
    let keywords = [];
    if (userKeywords.trim()) {
      keywords = userKeywords
        .split(',')
        .map(keyword => keyword.trim())
        .filter(keyword => keyword.length > 0);
    }

    try {
      setIsGenerating(true);

      // AI 인재상 생성 API 호출 (키워드 기반)
      const response = await fetch(`${API_BASE_URL}/api/company-culture/ai-generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keywords: keywords,
          job: selectedJob,
          department: selectedDepartment,
          use_trends: true
        }),
      });

      if (response.ok) {
        const generatedCultures = await response.json();
        setAiGeneratedCultures(generatedCultures);
        setSelectedAICultures([]);
        setShowKeywordModal(false);
        setShowAIModal(true);
      } else {
        alert('AI 인재상 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('AI 인재상 생성 오류:', error);
      alert('AI 인재상 생성 중 오류가 발생했습니다. 수동으로 입력해주세요.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAICultureSelect = (culture, isSelected) => {
    if (isSelected) {
      setSelectedAICultures(prev => [...prev, culture]);
    } else {
      setSelectedAICultures(prev => prev.filter(c => c.name !== culture.name));
    }
  };

  const handleAICultureSave = async () => {
    try {
      setLoading(true);

      // 선택된 인재상들을 저장
      for (const culture of selectedAICultures) {
        const response = await fetch(`${API_BASE_URL}/api/company-culture/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(culture),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`인재상 저장 실패: ${culture.name} - ${errorData.detail}`);
        }

        const result = await response.json();
      }

      setShowAIModal(false);
      setSelectedAICultures([]);
      setAiGeneratedCultures([]);
      loadCultures();
      alert(`${selectedAICultures.length}개의 인재상이 성공적으로 저장되었습니다.`);
    } catch (error) {
      console.error('AI 인재상 저장 오류:', error);
      alert('인재상 저장 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '24px', marginBottom: '20px' }}>🔄 로딩 중...</div>


        </div>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>회사 인재상 관리</Title>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Button onClick={() => setShowModal(true)}>
            <FiPlus size={16} />
            인재상 추가
          </Button>
                    <Button
            variant="secondary"
            onClick={() => handleAIGenerate()}
            disabled={loading}
          >
            <FiPlus size={16} />
            AI 인재상 추천
          </Button>
        </div>
      </Header>

      {cultures.length === 0 ? (
        <EmptyState>
          <EmptyStateIcon>🏢</EmptyStateIcon>
          <h3>등록된 인재상이 없습니다</h3>
          <p>회사의 핵심 가치와 인재상을 정의해보세요.</p>



          <Button onClick={() => setShowModal(true)} style={{ marginTop: '16px' }}>
            <FiPlus size={16} />
            첫 번째 인재상 추가
          </Button>
        </EmptyState>
      ) : (
        <>


          <Grid>
            {cultures && cultures.length > 0 ? (
              cultures.map((culture, index) => {

                return (
                  <Card key={culture.id || `culture-${index}`} isDefault={culture.is_default}>
                    <CardHeader>
                      <CardTitle>
                        {culture.name || '이름 없음'}
                        {culture.is_default && (
                          <span style={{
                            fontSize: '12px',
                            color: '#28a745',
                            marginLeft: '10px',
                            fontWeight: 'bold',
                            backgroundColor: '#d4edda',
                            padding: '2px 8px',
                            borderRadius: '4px'
                          }}>
                            ⭐ 기본 인재상
                          </span>
                        )}
                        <span style={{ fontSize: '12px', color: '#666', marginLeft: '10px' }}>
                          (ID: {culture.id || 'ID 없음'})
                        </span>
                      </CardTitle>
                      <CardActions>
                        <ActionButton onClick={() => handleEdit(culture)}>
                          <FiEdit size={16} />
                        </ActionButton>
                        <ActionButton
                          className="delete"
                          onClick={() => handleDelete(culture.id)}
                          disabled={culture.is_default}
                          style={{
                            opacity: culture.is_default ? 0.5 : 1,
                            cursor: culture.is_default ? 'not-allowed' : 'pointer'
                          }}
                          title={culture.is_default ? '기본 인재상은 삭제할 수 없습니다' : '삭제'}
                        >
                          <FiTrash2 size={16} />
                        </ActionButton>
                        {!culture.is_default && (
                          <ActionButton
                            onClick={() => handleSetDefault(culture.id)}
                            disabled={loading}
                            style={{
                              color: '#28a745',
                              backgroundColor: '#f8fff9',
                              border: '1px solid #28a745',
                              borderRadius: '6px',
                              padding: '6px 10px'
                            }}
                          >
                            <FiCheck size={16} />
                            기본으로 설정
                          </ActionButton>
                        )}
                        {culture.is_default && (
                          <ActionButton
                            disabled
                            style={{
                              color: '#28a745',
                              fontWeight: 'bold',
                              backgroundColor: '#d4edda',
                              border: '1px solid #28a745',
                              borderRadius: '6px',
                              padding: '6px 10px'
                            }}
                          >
                            <FiCheck size={16} />
                            ⭐ 기본 인재상
                          </ActionButton>
                        )}
                      </CardActions>
                    </CardHeader>

                    <Description>
                      {culture.description || '설명 없음'}
                    </Description>


                  </Card>
                );
              })
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '40px',
                color: '#666'
              }}>
                <p>인재상 데이터를 불러오는 중...</p>
              </div>
            )}
          </Grid>
        </>
      )}

      {showModal && (
        <Modal onClick={() => setShowModal(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <ModalHeader>
              <ModalTitle>
                {editingCulture ? '인재상 수정' : '인재상 추가'}
              </ModalTitle>
              <ActionButton onClick={() => setShowModal(false)}>
                <FiX size={20} />
              </ActionButton>
            </ModalHeader>

            <Form onSubmit={handleSubmit}>
              <FormGroup>
                <Label>인재상 이름 *</Label>
                <Input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="예: 혁신적 사고"
                  required
                />
              </FormGroup>

              <FormGroup>
                <Label>설명 *</Label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="인재상에 대한 상세한 설명을 입력하세요."
                  required
                />
              </FormGroup>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowModal(false)}
                >
                  취소
                </Button>
                <Button type="submit">
                  <FiCheck size={16} />
                  {editingCulture ? '수정' : '추가'}
                </Button>
              </div>
            </Form>
          </ModalContent>
        </Modal>
      )}

      {/* AI 인재상 선택 모달 */}
      {showAIModal && (
        <Modal onClick={() => setShowAIModal(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <ModalHeader>
              <ModalTitle>AI 생성 인재상 선택</ModalTitle>
              <ActionButton onClick={() => setShowAIModal(false)}>
                <FiX size={20} />
              </ActionButton>
            </ModalHeader>

            <div style={{ marginBottom: '20px' }}>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
                AI가 생성한 인재상 중 원하는 항목을 선택하세요.
              </p>

              <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setSelectedAICultures(aiGeneratedCultures);
                  }}
                  disabled={selectedAICultures.length === aiGeneratedCultures.length}
                >
                  전체 선택
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => setSelectedAICultures([])}
                  disabled={selectedAICultures.length === 0}
                >
                  전체 해제
                </Button>
              </div>
            </div>

            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {aiGeneratedCultures.map((culture, index) => {
                const isSelected = selectedAICultures.some(c => c.name === culture.name);
                return (
                  <div
                    key={index}
                    style={{
                      border: `2px solid ${isSelected ? 'var(--primary-color)' : 'var(--border-color)'}`,
                      borderRadius: '8px',
                      padding: '16px',
                      marginBottom: '12px',
                      cursor: 'pointer',
                      backgroundColor: isSelected ? 'var(--primary-light)' : 'white',
                      transition: 'all 0.2s ease'
                    }}
                    onClick={() => handleAICultureSelect(culture, !isSelected)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleAICultureSelect(culture, !isSelected)}
                        style={{ width: '18px', height: '18px' }}
                      />
                      <div style={{ flex: 1 }}>
                        <h4 style={{ margin: '0 0 8px 0', color: 'var(--text-primary)' }}>
                          {culture.name}
                        </h4>
                        <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '14px' }}>
                          {culture.description}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <Button
                variant="secondary"
                onClick={() => setShowAIModal(false)}
              >
                취소
              </Button>
              <Button
                onClick={handleAICultureSave}
                disabled={selectedAICultures.length === 0 || loading}
              >
                <FiCheck size={16} />
                선택한 인재상 저장 ({selectedAICultures.length}개)
              </Button>
            </div>
          </ModalContent>
        </Modal>
      )}

      {/* 키워드 입력 모달 */}
      {showKeywordModal && (
        <Modal onClick={() => setShowKeywordModal(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <ModalHeader>
              <ModalTitle>AI 인재상 추천 설정</ModalTitle>
              <ActionButton onClick={() => setShowKeywordModal(false)}>
                <FiX size={20} />
              </ActionButton>
            </ModalHeader>

            <div style={{ marginBottom: '20px' }}>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
                키워드와 직무 정보를 입력하면 AI가 맞춤형 인재상을 추천해드립니다.
              </p>
            </div>

            <Form onSubmit={(e) => { e.preventDefault(); handleKeywordSubmit(); }}>
              <FormGroup>
                <Label>키워드 입력</Label>
                <Textarea
                  value={userKeywords}
                  onChange={(e) => setUserKeywords(e.target.value)}
                  placeholder="예: 책임감, 협업, 문제해결, 혁신적 사고, 고객 중심"
                  style={{ minHeight: '80px' }}
                />
                <small style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
                  쉼표(,)로 구분하여 여러 키워드를 입력하세요. (선택사항)
                </small>
              </FormGroup>

              <FormGroup>
                <Label>직무 선택</Label>
                <Select
                  value={selectedJob}
                  onChange={(e) => setSelectedJob(e.target.value)}
                >
                  <option value="">직무 선택 (선택사항)</option>
                  <option value="개발자">개발자</option>
                  <option value="디자이너">디자이너</option>
                  <option value="기획자">기획자</option>
                  <option value="마케터">마케터</option>
                  <option value="영업">영업</option>
                  <option value="인사">인사</option>
                  <option value="재무">재무</option>
                  <option value="운영">운영</option>
                </Select>
              </FormGroup>

              <FormGroup>
                <Label>부서 선택</Label>
                <Select
                  value={selectedDepartment}
                  onChange={(e) => setSelectedDepartment(e.target.value)}
                >
                  <option value="">부서 선택 (선택사항)</option>
                  <option value="개발팀">개발팀</option>
                  <option value="AI팀">AI팀</option>
                  <option value="디자인팀">디자인팀</option>
                  <option value="기획팀">기획팀</option>
                  <option value="마케팅팀">마케팅팀</option>
                  <option value="영업팀">영업팀</option>
                  <option value="인사팀">인사팀</option>
                  <option value="재무팀">재무팀</option>
                  <option value="운영팀">운영팀</option>
                </Select>
              </FormGroup>

              <div style={{
                background: 'var(--background-secondary)',
                padding: '12px',
                borderRadius: '8px',
                marginBottom: '20px'
              }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: 'var(--text-primary)' }}>
                  🤖 AI 추천 기능
                </h4>
                <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  <li>입력한 키워드를 기반으로 맞춤형 인재상 추천</li>
                  <li>최신 채용 트렌드 데이터 분석</li>
                  <li>직무/부서별 특화된 인재상 생성</li>
                </ul>
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowKeywordModal(false)}
                >
                  취소
                </Button>
                <Button
                  type="submit"
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <div style={{
                        width: '16px',
                        height: '16px',
                        border: '2px solid transparent',
                        borderTop: '2px solid white',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                        marginRight: '8px'
                      }} />
                      AI 추천 생성 중...
                    </>
                  ) : (
                    <>
                      <FiPlus size={16} />
                      AI 인재상 추천
                    </>
                  )}
                </Button>
              </div>
            </Form>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
};

export default CompanyCultureManagement;
