// SwasthyaAI Mobile Auth Context
// Global authentication state management

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthTokens, PatientProfile } from '../types';
import api from '../services/api';
import * as SecureStore from 'expo-secure-store';

interface AuthContextType {
  user: User | null;
  patientProfile: PatientProfile | null;
  tokens: AuthTokens | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  role?: 'patient' | 'clinician';
  language?: 'en' | 'hi' | 'hinglish';
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [patientProfile, setPatientProfile] = useState<PatientProfile | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!tokens?.access_token;

  // Initialize auth state on app start
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const [storedUser, storedAccessToken, storedRefreshToken] = await Promise.all([
        SecureStore.getItemAsync('user'),
        SecureStore.getItemAsync('access_token'),
        SecureStore.getItemAsync('refresh_token'),
      ]);

      if (storedUser && storedAccessToken && storedRefreshToken) {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        setTokens({
          access_token: storedAccessToken,
          refresh_token: storedRefreshToken,
          token_type: 'bearer',
          expires_in: 604800,
          user: parsedUser,
        });

        // Verify token is still valid by fetching current user
        try {
          const currentUser = await api.getCurrentUser();
          setUser(currentUser);
          await SecureStore.setItemAsync('user', JSON.stringify(currentUser));

          // Load patient profile if patient
          if (currentUser.role === 'patient') {
            await loadPatientProfile();
          }
        } catch (error) {
          // Token invalid, try refresh
          try {
            await refreshAuth();
          } catch {
            await clearAuth();
          }
        }
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshAuth = async () => {
    try {
      const newAccessToken = await api.refreshToken();
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      await SecureStore.setItemAsync('user', JSON.stringify(currentUser));

      if (currentUser.role === 'patient') {
        await loadPatientProfile();
      }
    } catch (error) {
      await clearAuth();
      throw error;
    }
  };

  const loadPatientProfile = async () => {
    try {
      const profile = await api.getPatientProfile();
      setPatientProfile(profile);
    } catch (error) {
      console.error('Failed to load patient profile:', error);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const result = await api.login(email, password);
      setUser(result.user);
      setTokens(result);

      if (result.user.role === 'patient') {
        await loadPatientProfile();
      }
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterData) => {
    setIsLoading(true);
    try {
      const result = await api.register(data);
      setUser(result.user);
      setTokens(result);

      if (result.user.role === 'patient') {
        await loadPatientProfile();
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await api.logout();
    } finally {
      await clearAuth();
      setIsLoading(false);
    }
  };

  const clearAuth = async () => {
    setUser(null);
    setPatientProfile(null);
    setTokens(null);
    await SecureStore.deleteItemAsync('user');
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
  };

  const refreshProfile = async () => {
    try {
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      await SecureStore.setItemAsync('user', JSON.stringify(currentUser));

      if (currentUser.role === 'patient') {
        await loadPatientProfile();
      }
    } catch (error) {
      console.error('Failed to refresh profile:', error);
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      const updatedUser = await api.updateProfile(data);
      setUser(updatedUser);
      await SecureStore.setItemAsync('user', JSON.stringify(updatedUser));
    } catch (error) {
      console.error('Failed to update profile:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        patientProfile,
        tokens,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        refreshProfile,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}