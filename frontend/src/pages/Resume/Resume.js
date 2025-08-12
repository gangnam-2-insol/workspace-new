const mongoose = require('mongoose');

const ResumeSchema = new mongoose.Schema({
  name: String,
  position: String,
  resumeText: String,
  analysisScore: Number,
  analysisResult: String,
  analyzedAt: Date,
  // 기타 필드 
});

module.exports = mongoose.model('Resume', ResumeSchema);