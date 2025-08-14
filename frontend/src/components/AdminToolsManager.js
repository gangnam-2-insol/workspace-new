import React, { useEffect, useState } from 'react';
import styled from 'styled-components';

const Backdrop = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Panel = styled.div`
  width: 900px;
  max-width: 95vw;
  max-height: 90vh;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
`;

const Title = styled.h3`
  margin: 0;
  font-size: 16px;
`;

const Body = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px;
  overflow: auto;
`;

const Section = styled.div`
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 12px;
`;

const SectionTitle = styled.h4`
  margin: 0 0 10px 0;
  font-size: 14px;
`;

const List = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Row = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px;
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 8px;
`;

const Button = styled.button`
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  background: ${props => props.variant === 'danger' ? '#ff5252' : props.variant === 'ghost' ? 'transparent' : '#667eea'};
  color: ${props => props.variant === 'ghost' ? '#333' : '#fff'};
  border: ${props => props.variant === 'ghost' ? '1px solid #ddd' : 'none'};
`;

const Field = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
`;

const Input = styled.input`
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
`;

const TextArea = styled.textarea`
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  min-height: 160px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
`;

const Footer = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #eee;
`;

const AdminToolsManager = ({ sessionId, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState([]);
  const [dynamicTools, setDynamicTools] = useState([]);
  const [guide, setGuide] = useState('');
  const [ack, setAck] = useState(false);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [code, setCode] = useState('def run(query, context):\n    """query: str, context: dict -> str"""\n    return str(query)\n');
  const [trusted, setTrusted] = useState(false);

  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editCode, setEditCode] = useState('');

  const fetchList = async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/langgraph-agent/admin/tools?session_id=${encodeURIComponent(sessionId)}`);
      const data = await res.json();
      setRegistered(data.registered || []);
      setDynamicTools(data.dynamic || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchList();
    // 가이드 로드
    (async () => {
      try {
        // 정책 파일 경로에 정의된 guide_file을 우선 시도
        let txt = '';
        try {
          const pol = await fetch('/admin/backend/admin_guide/policy.json');
          const polJson = await pol.json();
          const path = polJson.guide_file || '/admin/backend/admin_guide/README.md';
          const res = await fetch(`/${path}`.replace(/\/+/g,'/'));
          txt = await res.text();
        } catch (_) {
          const res = await fetch('/admin/backend/admin_guide/README.md');
          txt = await res.text();
        }
        setGuide(txt);
      } catch (e) {
        setGuide('# 관리자 가이드 로드를 실패했습니다.');
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const createTool = async () => {
    if (!ack) {
      alert('가이드를 확인하고 동의해주세요.');
      return;
    }
    if (!sessionId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/langgraph-agent/admin/tools?session_id=${encodeURIComponent(sessionId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, code, trusted })
      });
      if (!res.ok) throw new Error('create failed');
      setName(''); setDescription('');
      await fetchList();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadToolToEdit = async (toolName) => {
    setEditName(toolName);
    // 간단히 dynamicTools에서 description만 로드, 코드는 파일 조회 API 없으므로 빈 템플릿 유지
    const item = (dynamicTools || []).find(t => t.name === toolName);
    setEditDescription(item?.description || '');
    setEditCode('# 현재 저장된 코드는 서버에서 직접 조회 API가 없어 편집 시 새 코드로 대체됩니다.\n' + code);
  };

  const updateTool = async () => {
    if (!sessionId || !editName) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/langgraph-agent/admin/tools/${encodeURIComponent(editName)}?session_id=${encodeURIComponent(sessionId)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editName, description: editDescription, code: editCode, trusted })
      });
      if (!res.ok) throw new Error('update failed');
      await fetchList();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const deleteTool = async (toolName) => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/langgraph-agent/admin/tools/${encodeURIComponent(toolName)}?session_id=${encodeURIComponent(sessionId)}`, {
        method: 'DELETE'
      });
      if (!res.ok) throw new Error('delete failed');
      await fetchList();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Backdrop onClick={onClose}>
      <Panel onClick={(e) => e.stopPropagation()}>
        <Header>
          <Title>관리자 툴 관리 패널 {loading ? '(로딩...)' : ''}</Title>
          <Button variant="ghost" onClick={onClose}>닫기</Button>
        </Header>
        <Body>
          <Section style={{gridColumn:'1 / -1'}}>
            <SectionTitle>관리자 가이드</SectionTitle>
            <div style={{whiteSpace:'pre-wrap', fontSize:12, color:'#333', background:'#fafafa', padding:12, borderRadius:8, maxHeight:200, overflow:'auto'}}>{guide}</div>
            <div style={{marginTop:8, display:'flex', alignItems:'center', gap:8}}>
              <input type="checkbox" id="ack" checked={ack} onChange={(e)=>setAck(e.target.checked)} />
              <label htmlFor="ack">가이드를 확인했습니다.</label>
            </div>
          </Section>
          <Section>
            <SectionTitle>등록된 툴 목록</SectionTitle>
            <List>
              {registered.map((name) => (
                <Row key={name}>
                  <div>{name}</div>
                  {dynamicTools.find(d => d.name === name) && (
                    <Button variant="danger" onClick={() => deleteTool(name)}>삭제</Button>
                  )}
                </Row>
              ))}
            </List>
          </Section>

          <Section>
            <SectionTitle>동적 툴 메타</SectionTitle>
            <List>
              {(dynamicTools || []).map((t) => (
                <Row key={t.name}>
                  <div style={{display:'flex',flexDirection:'column'}}>
                    <strong>{t.name}</strong>
                    <span style={{color:'#666'}}>{t.description}</span>
                  </div>
                  <div style={{display:'flex',gap:8}}>
                    <Button variant="ghost" onClick={() => loadToolToEdit(t.name)}>편집</Button>
                    <Button variant="danger" onClick={() => deleteTool(t.name)}>삭제</Button>
                  </div>
                </Row>
              ))}
            </List>
          </Section>

          <Section>
            <SectionTitle>새 툴 생성</SectionTitle>
            <Field>
              <label>이름</label>
              <Input value={name} onChange={(e)=>setName(e.target.value)} placeholder="echo_clean" />
            </Field>
            <Field>
              <label>설명</label>
              <Input value={description} onChange={(e)=>setDescription(e.target.value)} placeholder="특수문자 제거 에코" />
            </Field>
            <Field>
              <label>코드 (run(query, context) 필수)</label>
              <TextArea value={code} onChange={(e)=>setCode(e.target.value)} />
            </Field>
            <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:10}}>
              <input type="checkbox" id="trusted" checked={trusted} onChange={(e)=>setTrusted(e.target.checked)} />
              <label htmlFor="trusted">신뢰(승인)된 툴로 등록</label>
            </div>
            <Button onClick={createTool}>생성</Button>
          </Section>

          <Section>
            <SectionTitle>툴 수정</SectionTitle>
            <Field>
              <label>이름</label>
              <Input value={editName} onChange={(e)=>setEditName(e.target.value)} placeholder="수정할 툴 이름" />
            </Field>
            <Field>
              <label>설명</label>
              <Input value={editDescription} onChange={(e)=>setEditDescription(e.target.value)} placeholder="설명" />
            </Field>
            <Field>
              <label>코드</label>
              <TextArea value={editCode} onChange={(e)=>setEditCode(e.target.value)} />
            </Field>
            <Button onClick={updateTool}>업데이트</Button>
          </Section>
        </Body>
        <Footer>
          <Button variant="ghost" onClick={fetchList}>새로고침</Button>
          <Button onClick={onClose}>닫기</Button>
        </Footer>
      </Panel>
    </Backdrop>
  );
};

export default AdminToolsManager;


