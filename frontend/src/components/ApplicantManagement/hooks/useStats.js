import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export default function useStats() {
  const [stats, setStats] = useState({ total:0, passed:0, waiting:0, rejected:0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { stats, loading, error, reload: load };
}
