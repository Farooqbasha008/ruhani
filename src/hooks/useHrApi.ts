import { useQuery } from '@tanstack/react-query';
import api from '../lib/api';

export function useHrApi() {
  // Get organizational insights
  const getInsights = useQuery({
    queryKey: ['hr-insights'],
    queryFn: async () => {
      const res = await api.get('/hr/insights');
      return res.data;
    },
    refetchInterval: 300000, // Refetch every 5 minutes
  });

  // Get wellness trends
  const getTrends = useQuery({
    queryKey: ['hr-trends'],
    queryFn: async () => {
      const res = await api.get('/hr/trends');
      return res.data;
    },
    refetchInterval: 600000, // Refetch every 10 minutes
  });

  // Get at-risk employees
  const getAtRisk = useQuery({
    queryKey: ['hr-at-risk'],
    queryFn: async () => {
      const res = await api.get('/hr/at-risk');
      return res.data;
    },
    refetchInterval: 300000, // Refetch every 5 minutes
  });

  // Get all employees
  const getAllEmployees = useQuery({
    queryKey: ['hr-employees'],
    queryFn: async () => {
      const res = await api.get('/hr/employees');
      return res.data;
    },
    refetchInterval: 600000, // Refetch every 10 minutes
  });

  return {
    getInsights,
    getTrends,
    getAtRisk,
    getAllEmployees
  };
} 