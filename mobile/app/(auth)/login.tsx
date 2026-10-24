// SwasthyaAI Mobile Login Screen

import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, KeyboardAvoidingView, ScrollView, Platform, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../src/context/AuthContext';
import { theme } from '../../src/utils/theme';

export default function LoginScreen() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(email, password);
      router.replace('/(tabs)');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1, backgroundColor: theme.colors.background }}
    >
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: theme.spacing.xl }}>
        <View style={{ marginTop: theme.spacing.xxl, alignItems: 'center' }}>
          {/* Logo */}
          <View
            style={{
              width: 80,
              height: 80,
              borderRadius: theme.borderRadius.xl,
              backgroundColor: theme.colors.primary,
              justifyContent: 'center',
              alignItems: 'center',
              ...theme.shadows.lg,
            }}
          >
            <Text style={{ fontSize: 36, color: theme.colors.textOnPrimary }}>🏥</Text>
          </View>

          <Text style={{ ...theme.typography.h1, color: theme.colors.primary, marginTop: theme.spacing.lg }}>
            SwasthyaAI
          </Text>
          <Text style={{ ...theme.typography.body, color: theme.colors.textSecondary, marginTop: theme.spacing.sm }}>
            AI Healthcare Navigation for India
          </Text>
        </View>

        <View style={{ marginTop: theme.spacing.xxl, width: '100%' }}>
          <Text style={{ ...theme.typography.h3, color: theme.colors.text, marginBottom: theme.spacing.md }}>
            Welcome Back
          </Text>
          <Text style={{ ...theme.typography.body, color: theme.colors.textSecondary, marginBottom: theme.spacing.xl }}>
            Sign in to access your health dashboard
          </Text>

          {error && (
            <View
              style={{
                backgroundColor: theme.colors.errorLight,
                borderRadius: theme.borderRadius.md,
                padding: theme.spacing.md,
                marginBottom: theme.spacing.lg,
              }}
            >
              <Text style={{ color: theme.colors.error, ...theme.typography.bodySmall }}>{error}</Text>
            </View>
          )}

          {/* Email Input */}
          <View style={{ marginBottom: theme.spacing.md }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              Email Address
            </Text>
            <TextInput
              style={{
                backgroundColor: theme.colors.surface,
                borderWidth: 1,
                borderColor: theme.colors.border,
                borderRadius: theme.borderRadius.md,
                paddingHorizontal: theme.spacing.md,
                paddingVertical: theme.spacing.md,
                fontSize: theme.typography.body.fontSize,
                color: theme.colors.text,
              }}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              placeholder="you@example.com"
            />
          </View>

          {/* Password Input */}
          <View style={{ marginBottom: theme.spacing.md }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: theme.spacing.xs }}>
              <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text }}>
                Password
              </Text>
              <TouchableOpacity onPress={() => router.push('/(auth)/forgot-password')}>
                <Text style={{ ...theme.typography.bodySmall, color: theme.colors.primary }}>
                  Forgot?
                </Text>
              </TouchableOpacity>
            </View>
            <TextInput
              style={{
                backgroundColor: theme.colors.surface,
                borderWidth: 1,
                borderColor: theme.colors.border,
                borderRadius: theme.borderRadius.md,
                paddingHorizontal: theme.spacing.md,
                paddingVertical: theme.spacing.md,
                fontSize: theme.typography.body.fontSize,
                color: theme.colors.text,
              }}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              autoComplete="password"
              placeholder="••••••••"
            />
          </View>

          {/* Login Button */}
          <TouchableOpacity
            style={{
              backgroundColor: theme.colors.primary,
              borderRadius: theme.borderRadius.md,
              paddingVertical: theme.spacing.md,
              alignItems: 'center',
              ...theme.shadows.md,
              opacity: loading ? 0.7 : 1,
            }}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color={theme.colors.textOnPrimary} size="large" />
            ) : (
              <Text style={{ ...theme.typography.button, color: theme.colors.textOnPrimary }}>
                Sign In
              </Text>
            )}
          </TouchableOpacity>

          {/* Register Link */}
          <View style={{ flexDirection: 'row', justifyContent: 'center', marginTop: theme.spacing.lg }}>
            <Text style={{ ...theme.typography.body, color: theme.colors.textSecondary }}>
              Don't have an account?{' '}
            </Text>
            <TouchableOpacity onPress={() => router.push('/(auth)/register')}>
              <Text style={{ ...theme.typography.button, color: theme.colors.primary }}>
                Sign Up
              </Text>
            </TouchableOpacity>
          </View>

          {/* Demo Notice */}
          <View style={{ marginTop: theme.spacing.xxl, padding: theme.spacing.md, backgroundColor: theme.colors.infoLight, borderRadius: theme.borderRadius.md }}>
            <Text style={{ ...theme.typography.caption, color: theme.colors.info, textAlign: 'center' }}>
              Demo: Use any email/password to test. Backend must be running on port 8000.
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}