const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const resumeAnalysisRouter = require('./routes/resumeAnalysis');
const resumeRoutes = require('./routes/resumeRoutes');

const app = express();

// 미들웨어 설정
app.use(cors());
app.use(express.json());

// MongoDB 연결
mongoose.connect('mongodb://localhost:27017/admin_dashboard', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('MongoDB connected'))
.catch(err => console.error('MongoDB connection error:', err));

// 기본 테스트용 엔드포인트
app.get('/', (req, res) => {  
    res.send('Backend server is running!');
});

// API 라우터 연결
app.use('/api/resume-analysis', resumeAnalysisRouter);
app.use('/api/resumes', resumeRoutes);

const PORT = 8000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});