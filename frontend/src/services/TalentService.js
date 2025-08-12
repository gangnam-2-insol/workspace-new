import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const TalentService = {
  // 모든 인재 조회
  getAllTalents: async () => {
    try {
      const response = await api.get('/talents');
      return response.data;
    } catch (error) {
      console.error('Error fetching talents:', error);
      throw error;
    }
  },

  // AI 매칭 인재 조회
  matchTalents: async (requirements) => {
    try {
      const response = await api.post('/talents/match', {
        requirements: requirements
      });
      return response.data;
    } catch (error) {
      console.error('Error matching talents:', error);
      throw error;
    }
  },

  // 특정 인재 조회
  getTalent: async (talentId) => {
    try {
      const response = await api.get(`/talents/${talentId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching talent:', error);
      throw error;
    }
  }
};

export default TalentService;