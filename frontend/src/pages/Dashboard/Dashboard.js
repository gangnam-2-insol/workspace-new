import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiUsers, 
  FiFileText, 
  FiVideo, 
  FiCheckCircle, 
  FiTrendingUp,
  FiClock,
  FiAlertCircle,
  FiStar
} from 'react-icons/fi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const DashboardContainer = styled.div`
  padding: 24px 0;
`;

const HeroSection = styled(motion.div)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--border-radius);
  padding: 48px;
  color: white;
  margin-bottom: 32px;
  text-align: center;
`;

const HeroTitle = styled.h1`
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  
  @media (max-width: 768px) {
    font-size: 32px;
  }
`;

const HeroSubtitle = styled.p`
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 32px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const StatCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-medium);
  }
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const StatIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
`;

const StatChange = styled.div`
  font-size: 12px;
  color: ${props => props.isPositive ? '#00c851' : '#ff6b35'};
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--text-primary);
`;

const ChartGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
`;

const RecentActivity = styled.div`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
  
  &:last-child {
    border-bottom: none;
  }
`;

const ActivityIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityTitle = styled.div`
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ActivityTime = styled.div`
  font-size: 12px;
  color: var(--text-light);
`;

// 샘플 데이터
const chartData = [
  { name: '1월', 지원자: 120, 합격: 15 },
  { name: '2월', 지원자: 150, 합격: 20 },
  { name: '3월', 지원자: 180, 합격: 25 },
  { name: '4월', 지원자: 200, 합격: 30 },
  { name: '5월', 지원자: 220, 합격: 35 },
  { name: '6월', 지원자: 250, 합격: 40 },
];

const pieData = [
  { name: '서류 접수', value: 45, color: '#00c851' },
  { name: '면접 진행', value: 30, color: '#007bff' },
  { name: '최종 합격', value: 15, color: '#ff6b35' },
  { name: '불합격', value: 10, color: '#6c757d' },
];

const stats = [
  {
    title: '총 지원자',
    value: '1,247',
    change: '+12%',
    isPositive: true,
    icon: FiUsers,
    color: '#00c851'
  },
  {
    title: '서류 접수',
    value: '892',
    change: '+8%',
    isPositive: true,
    icon: FiFileText,
    color: '#007bff'
  },
  {
    title: '면접 진행',
    value: '156',
    change: '+15%',
    isPositive: true,
    icon: FiVideo,
    color: '#ff6b35'
  },
  {
    title: '최종 합격',
    value: '89',
    change: '+23%',
    isPositive: true,
    icon: FiCheckCircle,
    color: '#28a745'
  }
];

const activities = [
  {
    title: '새로운 지원자가 등록되었습니다',
    time: '5분 전',
    icon: FiUsers,
    color: '#00c851'
  },
  {
    title: 'AI 면접 분석이 완료되었습니다',
    time: '15분 전',
    icon: FiVideo,
    color: '#007bff'
  },
  {
    title: '포트폴리오 분석 결과가 업데이트되었습니다',
    time: '1시간 전',
    icon: FiStar,
    color: '#ff6b35'
  },
  {
    title: '자소서 검증이 완료되었습니다',
    time: '2시간 전',
    icon: FiFileText,
    color: '#28a745'
  }
];

const Dashboard = () => {
  return (
    <DashboardContainer>
      <HeroSection
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <HeroTitle>AI 채용 관리 시스템</HeroTitle>
        <HeroSubtitle>
          인공지능이 지원하는 스마트한 채용 프로세스로 
          최고의 인재를 찾아보세요
        </HeroSubtitle>
      </HeroSection>

      <StatsGrid>
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <StatCard
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <StatHeader>
                <div>
                  <StatValue>{stat.value}</StatValue>
                  <StatLabel>{stat.title}</StatLabel>
                </div>
                <StatIcon style={{ background: stat.color }}>
                  <Icon size={24} />
                </StatIcon>
              </StatHeader>
              <StatChange isPositive={stat.isPositive}>
                <FiTrendingUp size={12} />
                {stat.change} 지난 달 대비
              </StatChange>
            </StatCard>
          );
        })}
      </StatsGrid>

      <ChartGrid>
        <ChartCard>
          <SectionTitle>지원자 추이</SectionTitle>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="지원자" stroke="#00c851" strokeWidth={3} />
              <Line type="monotone" dataKey="합격" stroke="#007bff" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <SectionTitle>채용 현황</SectionTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </ChartGrid>

      <Section>
        <SectionTitle>최근 활동</SectionTitle>
        <RecentActivity>
          {activities.map((activity, index) => {
            const Icon = activity.icon;
            return (
              <ActivityItem key={index}>
                <ActivityIcon style={{ background: activity.color }}>
                  <Icon size={16} />
                </ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>{activity.title}</ActivityTitle>
                  <ActivityTime>{activity.time}</ActivityTime>
                </ActivityContent>
              </ActivityItem>
            );
          })}
        </RecentActivity>
      </Section>
    </DashboardContainer>
  );
};

export default Dashboard; 