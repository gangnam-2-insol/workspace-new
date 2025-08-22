import React from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const RadarChart = ({ analysisData, onSectionClick }) => {
  if (!analysisData) return null;

  // 차트 데이터 구성 - 사용자가 요청한 8개 항목
  const chartData = {
    labels: [
      '직무 적합성 (Job Fit)',
      '기술 스택 일치 여부',
      '경험한 프로젝트 관련성',
      '핵심 기술 역량 (Tech Competency)',
      '경력 및 성과 (Experience & Impact)',
      '문제 해결 능력 (Problem-Solving)',
      '커뮤니케이션/협업 (Collaboration)',
      '성장 가능성/학습 능력 (Growth Potential)',
      '자소서 표현력/논리성 (Clarity & Grammar)'
    ],
    datasets: [
      {
        label: '분석 점수',
        data: [
          // 1. 직무 적합성 (Job Fit) - JD와 이력서의 직무 매칭도
          analysisData.stage2?.직무_적합성 || analysisData.stage1?.job_fit_score || 70,
          
          // 2. 기술 스택 일치 여부 - JD 기술과 이력서 기술 스택 비교
          analysisData.stage2?.핵심_기술_역량 || 
          (analysisData.stage1?.skill_scores ? 
            Math.min(100, Object.values(analysisData.stage1.skill_scores).reduce((a, b) => a + b, 0) / Object.keys(analysisData.stage1.skill_scores).length) : 70),
          
          // 3. 경험한 프로젝트 관련성 - 직무와의 연관성
          analysisData.stage2?.경력_및_성과 || analysisData.stage1?.job_fit_score || 70,
          
          // 4. 핵심 기술 역량 (Tech Competency) - 기술 스택의 깊이와 넓이
          analysisData.stage2?.핵심_기술_역량 || 
          (analysisData.stage1?.skill_scores ? 
            Math.min(100, Object.values(analysisData.stage1.skill_scores).reduce((a, b) => a + b, 0) / Object.keys(analysisData.stage1.skill_scores).length) : 70),
          
          // 5. 경력 및 성과 (Experience & Impact) - 주도적 역할과 수치화된 성과
          analysisData.stage2?.경력_및_성과 || analysisData.stage1?.text_quality_score || 70,
          
          // 6. 문제 해결 능력 (Problem-Solving) - 구체적 사례와 구조화
          analysisData.stage2?.문제_해결_능력 || analysisData.stage1?.text_quality_score || 70,
          
          // 7. 커뮤니케이션/협업 (Collaboration) - 팀워크와 협업 도구 경험
          analysisData.stage2?.협업 || analysisData.stage1?.text_quality_score || 70,
          
          // 8. 성장 가능성/학습 능력 (Growth Potential) - 새로운 기술 학습과 적응력
          analysisData.stage2?.성장_가능성 || analysisData.stage1?.text_quality_score || 70,
          
          // 9. 자소서 표현력/논리성 (Clarity & Grammar) - 글의 품질과 문법
          analysisData.stage2?.표현력 || analysisData.stage1?.grammar_score || 70
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.15)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 3,
        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
        pointRadius: 5,
        pointHoverRadius: 8,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        min: 0,
        ticks: {
          stepSize: 20,
          color: '#666',
          font: {
            size: 12,
          },
          callback: function(value) {
            return value + '점';
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        angleLines: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        pointLabels: {
          color: '#333',
          font: {
            size: 11,
            weight: 'bold',
          },
          callback: function(value, index) {
            // 긴 라벨을 줄바꿈으로 처리
            const words = value.split(' ');
            if (words.length > 4) {
              return words.slice(0, 3).join(' ') + '\n' + words.slice(3).join(' ');
            } else if (words.length > 2) {
              const mid = Math.ceil(words.length / 2);
              return words.slice(0, mid).join(' ') + '\n' + words.slice(mid).join(' ');
            }
            return value;
          }
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          title: function(context) {
            return context[0].label;
          },
          label: function(context) {
            return `점수: ${context.parsed.r}점`;
          },
          afterLabel: function(context) {
            const index = context.dataIndex;
            const descriptions = [
              '지원 직무와의 연관성 및 적합성',
              'JD에 명시된 기술과 이력서 기술 스택 일치도',
              '경험한 프로젝트가 지원 포지션과의 관련성',
              '프로그래밍 언어, 프레임워크, DB 등 기술 역량',
              '단순 참여 vs 주도적 역할, 수치화된 성과',
              '문제 상황 → 해결 과정 → 성과 구조',
              '팀 프로젝트 경험, 협업 도구 사용 경험',
              '새로운 기술 학습/적용, 꾸준한 학습 습관',
              '글의 흐름, 논리적 전개, 맞춤법/문법'
            ];
            return descriptions[index] || '';
          }
        }
      },
    },
    onClick: (event, elements) => {
      if (elements.length > 0) {
        const index = elements[0].index;
        onSectionClick(index);
      }
    },
    onHover: (event, elements) => {
      event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
    },
    interaction: {
      mode: 'nearest',
      axis: 'r',
      intersect: false
    },
  };

  return (
    <div className="radar-chart-container">
      <h3>📊 종합 분석 레이더 차트</h3>
      <p className="chart-description">
        차트의 각 항목을 클릭하면 해당 상세 분석으로 이동합니다
      </p>
      <div className="chart-wrapper">
        <Radar data={chartData} options={options} />
      </div>
      
      {/* 차트 하단 설명 */}
      <div className="chart-explanations">
        <h4>📋 평가 항목 상세 설명</h4>
        <div className="explanation-grid">
          <div className="explanation-item">
            <span className="explanation-number">1</span>
            <div className="explanation-content">
              <strong>직무 적합성 (Job Fit)</strong>
              <p>지원 직무와의 연관성 및 적합성, JD 요구사항과의 매칭도</p>
            </div>
          </div>
          
          <div className="explanation-item">
            <span className="explanation-number">2</span>
            <div className="explanation-content">
              <strong>기술 스택 일치 여부</strong>
              <p>JD에 명시된 기술(Python/React 등)과 이력서 기술 스택의 일치도</p>
            </div>
          </div>
          
          <div className="explanation-item">
            <span className="explanation-number">3</span>
            <div className="explanation-content">
              <strong>경험한 프로젝트 관련성</strong>
              <p>경험한 프로젝트가 지원 포지션과 얼마나 관련 있는지</p>
            </div>
          </div>
          
          <div className="explanation-item">
            <span className="explanation-number">4</span>
            <div className="explanation-content">
              <strong>핵심 기술 역량 (Tech Competency)</strong>
              <p>프로그래밍 언어, 프레임워크, DB, 클라우드, 협업 툴 등</p>
            </div>
          </div>
          
          <div className="explanation-item">
            <span className="explanation-number">5</span>
            <div className="explanation-content">
              <strong>경력 및 성과 (Experience & Impact)</strong>
              <p>단순 참여 vs 주도적 역할, 수치화된 성과 제시 여부</p>
            </div>
          </div>
          
          <div className="explanation-item">
            <span className="explanation-number">6</span>
            <div className="explanation-content">
              <strong>문제 해결 능력 (Problem-Solving)</strong>
              <p>문제 상황 → 해결 과정 → 성과 구조의 구체적 사례</p>
            </div>
          </div>
          
          <div className="explanation-item">
            <span className="explanation-number">7</span>
            <div className="explanation-content">
              <strong>커뮤니케이션/협업 (Collaboration)</strong>
              <p>팀 프로젝트 경험, Git/Jira/Slack 등 협업 툴 사용 경험</p>
            </div>
          </div>
          
          <div className="explanation-item">
            <span className="explanation-number">8</span>
            <div className="explanation-content">
              <strong>성장 가능성/학습 능력 (Growth Potential)</strong>
              <p>새로운 기술 학습/적용 경험, 꾸준한 학습 습관</p>
            </div>
          </div>
          
          <div className="explanation-item">
            <span className="explanation-number">9</span>
            <div className="explanation-content">
              <strong>자소서 표현력/논리성 (Clarity & Grammar)</strong>
              <p>글의 흐름, 논리적 전개, 맞춤법/문법 오류 여부</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: 'rgba(54, 162, 235, 1)' }}></span>
          <span>분석 점수 (0-100점)</span>
        </div>
      </div>
    </div>
  );
};

export default RadarChart;
