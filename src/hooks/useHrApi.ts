import api from '../lib/api';

export function useHrApi() {
  const getInsights = async () => {
    const res = await api.get('/hr/insights');
    return res.data;
  };

  const getTrends = async () => {
    const res = await api.get('/hr/trends');
    return res.data;
  };

  const getAtRisk = async () => {
    const res = await api.get('/hr/at-risk');
    return res.data;
  };

  return { getInsights, getTrends, getAtRisk };
} 