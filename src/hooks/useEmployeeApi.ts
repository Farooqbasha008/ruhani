import { useMutation, useQuery } from '@tanstack/react-query';
import api from '../lib/api';

// Types
export interface OnboardRequest {
  name: string;
  email: string;
  department: string;
  role: string;
  github?: string;
  linkedin?: string;
  cultural_background?: string;
  preferred_language?: string;
}

export interface LoginRequest {
  email: string;
}

export interface VoiceSessionRequest {
  employee_id: string;
  audio_data: string; // Base64 encoded audio
  session_context?: string;
  mood_rating?: string;
}

export interface WellnessCheckRequest {
  employee_id: string;
  mood_rating: string;
  stress_level: number;
  sleep_quality: number;
  work_satisfaction: number;
  social_support: number;
  notes?: string;
}

export interface SentimentLogRequest {
  employee_id: string;
  source: string;
  sentiment: string;
  score: number;
  text_content?: string;
  context?: any;
}

export function useEmployeeApi() {
  // Employee login
  const loginEmployee = useMutation({
    mutationFn: async (data: LoginRequest) => {
      const res = await api.post('/employee/login', data);
      return res.data;
    },
    onSuccess: (data) => {
      // Store the access token and employee info
      if (data.access_token) {
        localStorage.setItem('jwt', data.access_token);
        localStorage.setItem('employee_id', data.employee_id);
        localStorage.setItem('employee_name', data.name);
      }
    }
  });

  // Employee onboarding
  const onboardEmployee = useMutation({
    mutationFn: async (data: OnboardRequest) => {
      const res = await api.post('/employee/onboard', data);
      return res.data;
    },
    onSuccess: (data) => {
      // Store the access token
      if (data.access_token) {
        localStorage.setItem('jwt', data.access_token);
        localStorage.setItem('employee_id', data.employee_id);
        localStorage.setItem('employee_name', data.name);
      }
    }
  });

  // Voice session processing
  const processVoiceSession = useMutation({
    mutationFn: async (data: VoiceSessionRequest) => {
      const res = await api.post('/employee/voice-session', data);
      return res.data;
    }
  });

  // Wellness check submission
  const submitWellnessCheck = useMutation({
    mutationFn: async (data: WellnessCheckRequest) => {
      const res = await api.post('/employee/wellness-check', data);
      return res.data;
    }
  });

  // Sentiment logging
  const logSentiment = useMutation({
    mutationFn: async (data: SentimentLogRequest) => {
      const res = await api.post('/employee/sentiment', data);
      return res.data;
    }
  });

  // Get employee profile
  const getEmployeeProfile = (employeeId: string) => {
    return useQuery({
      queryKey: ['employee-profile', employeeId],
      queryFn: async () => {
        const res = await api.get(`/employee/profile/${employeeId}`);
        return res.data;
      },
      enabled: !!employeeId
    });
  };

  // Get wellness summary
  const getWellnessSummary = (employeeId: string) => {
    return useQuery({
      queryKey: ['wellness-summary', employeeId],
      queryFn: async () => {
        const res = await api.get(`/employee/wellness-summary/${employeeId}`);
        return res.data;
      },
      enabled: !!employeeId
    });
  };

  return {
    loginEmployee,
    onboardEmployee,
    processVoiceSession,
    submitWellnessCheck,
    logSentiment,
    getEmployeeProfile,
    getWellnessSummary
  };
} 