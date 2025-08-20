import React from 'react';

const PortfolioSummaryPanel = ({ portfolio }) => {
  if (!portfolio) {
    return null;
  }

  return (
    <>
      <h3 style={{ fontSize: 18, fontWeight: 700, margin: '16px 0 12px 0' }}>프로젝트</h3>
      {(portfolio.projects || []).map((project, index) => (
        <div key={index} style={{ border: '1px solid var(--border-color)', borderRadius: 12, padding: 16, marginBottom: 12 }}>
          <div style={{ fontWeight: 700, marginBottom: 6 }}>{project.title}</div>
          <div style={{ color: 'var(--text-secondary)', marginBottom: 8 }}>{project.description}</div>
          <div><strong>기술스택:</strong> {(project.technologies || []).join(', ')}</div>
          <div style={{ marginTop: 6 }}><strong>주요 기능:</strong></div>
          <ul style={{ margin: '6px 0 0 18px' }}>
            {(project.features || []).map((feature, idx) => (
              <li key={idx}>{feature}</li>
            ))}
          </ul>
          <div style={{ marginTop: 6 }}>
            <strong>GitHub:</strong> {project.github ? (<a href={project.github} target="_blank" rel="noopener noreferrer">{project.github}</a>) : 'N/A'}
          </div>
          <div style={{ marginTop: 4 }}>
            <strong>Demo:</strong> {project.demo ? (<a href={project.demo} target="_blank" rel="noopener noreferrer">{project.demo}</a>) : 'N/A'}
          </div>
        </div>
      ))}

      <h3 style={{ fontSize: 18, fontWeight: 700, margin: '16px 0 12px 0' }}>성과 및 수상</h3>
      <ul style={{ margin: 0, paddingLeft: 18 }}>
        {(portfolio.achievements || []).map((achievement, index) => (
          <li key={index}>{achievement}</li>
        ))}
      </ul>
    </>
  );
};

export default PortfolioSummaryPanel;


