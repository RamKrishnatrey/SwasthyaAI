// SwasthyaAI Mobile Root Layout
// Expo Router root layout with providers

import React from 'react';
import { Stack } from 'expo-router';
import { AuthProvider } from '../src/context/AuthContext';
import { SplashScreen } from 'expo-splash-screen';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  return (
    <AuthProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="onboarding" />
        <Stack.Screen name="symptom-checker" />
        <Stack.Screen name="chat" />
        <Stack.Screen name="appointment-detail" />
        <Stack.Screen name="book-appointment" />
        <Stack.Screen name="medical-record-detail" />
        <Stack.Screen name="reminder-detail" />
        <Stack.Screen name="doctor-detail" />
        <Stack.Screen name="settings" />
        <Stack.Screen name="language" />
        <Stack.Screen name="emergency" />
        <Stack.Screen name="health-insights" />
      </Stack>
    </AuthProvider>
  );
}