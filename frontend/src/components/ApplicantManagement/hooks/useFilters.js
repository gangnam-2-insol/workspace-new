import { useState, useEffect, useCallback } from 'react';
import jobPostingApi from '../services/jobPostingApi';

export default function useFilters() {
  const [search, setSearch] = useState('');
  const [jobPostings, setJobPostings] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [jobs, setJobs] = useState([]);
  const [experience, setExperience] = useState([]);
  const [status, setStatus] = useState([]);

  const loadJobPostings = useCallback(async () => {
    try {
      const data = await jobPostingApi.getJobPostings();
      setJobPostings(data);
    } catch (error) {
      console.error('채용공고 로딩 실패:', error);
    }
  }, []);

  useEffect(() => {
    loadJobPostings();
  }, [loadJobPostings]);

  return { search, setSearch, jobPostings, selectedJob, setSelectedJob, jobs, setJobs, experience, setExperience, status, setStatus };
}
