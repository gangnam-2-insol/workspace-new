import React, { useState, useEffect } from 'react';
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
import dashboardApi from '../../services/dashboardApi';

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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;

  @media (min-width: 1200px) {
    grid-template-columns: repeat(3, 1fr);
  }

  @media (max-width: 1199px) and (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 767px) {
    grid-template-columns: 1fr;
  }
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

const Dashboard = () => {
  const [stats, setStats] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [pieData, setPieData] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  // 아이콘 매핑
  const iconMap = {
    FiUsers,
    FiFileText,
    FiVideo,
    FiCheckCircle,
    FiStar
  };

  // 데이터 로딩
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);

        // 1. 지원자 통계 조회
        const applicantStats = await dashboardApi.getApplicantStats();

        // 2. 채용공고 통계 조회
        const jobPostingStats = await dashboardApi.getJobPostingStats();

        // 3. 최근 지원자 조회
        const recentApplicants = await dashboardApi.getRecentApplicants(10);

        // 3. 통계 카드 데이터 생성
        const statsData = [
          {
            title: '총 지원자',
            value: applicantStats.total_applicants.toLocaleString(),
            change: '+12%',
            isPositive: true,
            icon: FiUsers,
            color: '#00c851'
          },
          {
            title: '서류 검토중',
            value: (applicantStats.status_distribution?.pending || 0).toLocaleString(),
            change: '+8%',
            isPositive: true,
            icon: FiFileText,
            color: '#007bff'
          },
          {
            title: '면접 예정',
            value: (applicantStats.status_distribution?.interview_scheduled || 0).toLocaleString(),
            change: '+15%',
            isPositive: true,
            icon: FiVideo,
            color: '#ff6b35'
          },
          {
            title: '최종 합격',
            value: (applicantStats.status_distribution?.passed || 0).toLocaleString(),
            change: '+23%',
            isPositive: true,
            icon: FiCheckCircle,
            color: '#28a745'
          },
          {
            title: '채용공고',
            value: jobPostingStats.total_job_postings.toLocaleString(),
            change: '+5%',
            isPositive: true,
            icon: FiStar,
            color: '#9c27b0'
          },
          {
            title: '전체 공고',
            value: jobPostingStats.total_job_postings.toLocaleString(),
            change: '+3%',
            isPositive: true,
            icon: FiClock,
            color: '#ff9800'
          }
        ];

        // 4. 차트 데이터 생성
        const monthlyData = dashboardApi.generateMonthlyTrendData(recentApplicants);
        const statusData = dashboardApi.generateStatusDistributionData(applicantStats);

        // 5. 최근 활동 데이터 생성
        const activityData = dashboardApi.generateRecentActivities(recentApplicants);

        setStats(statsData);
        setChartData(monthlyData);
        setPieData(statusData);
        setActivities(activityData);

      } catch (error) {
        console.error('대시보드 데이터 로딩 실패:', error);

        // 에러 시 기본 데이터 설정
        setStats([
          {
            title: '총 지원자',
            value: '0',
            change: '+0%',
            isPositive: true,
            icon: FiUsers,
            color: '#00c851'
          },
          {
            title: '서류 검토중',
            value: '0',
            change: '+0%',
            isPositive: true,
            icon: FiFileText,
            color: '#007bff'
          },
          {
            title: '면접 예정',
            value: '0',
            change: '+0%',
            isPositive: true,
            icon: FiVideo,
            color: '#ff6b35'
          },
          {
            title: '최종 합격',
            value: '0',
            change: '+0%',
            isPositive: true,
            icon: FiCheckCircle,
            color: '#28a745'
          },
          {
            title: '채용공고',
            value: '0',
            change: '+0%',
            isPositive: true,
            icon: FiStar,
            color: '#9c27b0'
          },
          {
            title: '전체 공고',
            value: '0',
            change: '+0%',
            isPositive: true,
            icon: FiClock,
            color: '#ff9800'
          }
        ]);

        setChartData([
          { name: '1월', 지원자: 0, 합격: 0 },
          { name: '2월', 지원자: 0, 합격: 0 },
          { name: '3월', 지원자: 0, 합격: 0 },
          { name: '4월', 지원자: 0, 합격: 0 },
          { name: '5월', 지원자: 0, 합격: 0 },
          { name: '6월', 지원자: 0, 합격: 0 }
        ]);

        setPieData([
          { name: '서류 접수', value: 0, color: '#00c851' },
          { name: '면접 진행', value: 0, color: '#007bff' },
          { name: '최종 합격', value: 0, color: '#ff6b35' },
          { name: '불합격', value: 0, color: '#6c757d' }
        ]);

        setActivities([
          {
            title: '데이터를 불러올 수 없습니다',
            time: '방금 전',
            icon: FiAlertCircle,
            color: '#ff6b35'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <DashboardContainer>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '400px',
          fontSize: '18px',
          color: '#666'
        }}>
          대시보드 데이터를 불러오는 중...
        </div>
      </DashboardContainer>
    );
  }

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
            const Icon = iconMap[activity.icon] || FiUsers;
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
