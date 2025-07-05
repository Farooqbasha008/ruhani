import api from '../lib/api';

export function useEmployeeApi() {
  const onboard = async (data: any) => {
    const res = await api.post('/employee/onboard', data);
    return res.data;
  };

  const scheduleSession = async (data: any) => {
    const res = await api.post('/employee/session', data);
    return res.data;
  };

  const logSentiment = async (data: any) => {
    const res = await api.post('/employee/sentiment', data);
    return res.data;
  };

  return { onboard, scheduleSession, logSentiment };
} 