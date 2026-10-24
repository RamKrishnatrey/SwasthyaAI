// SwasthyaAI Mobile Register Screen

import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, KeyboardAvoidingView, ScrollView, Platform, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../src/context/AuthContext';
import { theme } from '../../src/utils/theme';

export default function RegisterScreen() {
  const router = useRouter();
  const { register } = useAuth();
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    language: 'en' as 'en' | 'hi' | 'hinglish',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async () => {
    if (!form.full_name || !form.email || !form.password) {
      setError('Please fill in all required fields');
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await register({
        email: form.email,
        password: form.password,
        full_name: form.full_name,
        phone: form.phone || undefined,
        role: 'patient',
        language: form.language,
      });
      router.replace('/(tabs)');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'hi', label: 'हिंदी' },
    { value: 'hinglish', label: 'Hinglish' },
  ];

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1, backgroundColor: theme.colors.background }}
    >
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: theme.spacing.xl }}>
        <View style={{ marginTop: theme.spacing.xl, alignItems: 'center' }}>
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
            Create your account
          </Text>
        </View>

        <View style={{ marginTop: theme.spacing.xl, width: '100%' }}>
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

          <View style={{ marginBottom: theme.spacing.md }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              Full Name *
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
              value={form.full_name}
              onChangeText={(v) => setForm({ ...form, full_name: v })}
              autoCapitalize="words"
              placeholder="John Doe"
            />
          </View>

          <View style={{ marginBottom: theme.spacing.md }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              Email Address *
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
              value={form.email}
              onChangeText={(v) => setForm({ ...form, email: v })}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              placeholder="you@example.com"
            />
          </View>

          <View style={{ marginBottom: theme.spacing.md }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              Phone Number
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
              value={form.phone}
              onChangeText={(v) => setForm({ ...form, phone: v })}
              keyboardType="phone-pad"
              autoComplete="tel"
              placeholder="+91 98765 43210"
            />
          </View>

          <View style={{ marginBottom: theme.spacing.md }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              Password * (min 8 chars)
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
              value={form.password}
              onChangeText={(v) => setForm({ ...form, password: v })}
              secureTextEntry
              autoComplete="new-password"
              placeholder="••••••••"
            />
          </View>

          <View style={{ marginBottom: theme.spacing.md }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              Confirm Password *
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
              value={form.confirmPassword}
              onChangeText={(v) => setForm({ ...form, confirmPassword: v })}
              secureTextEntry
              autoComplete="new-password"
              placeholder="••••••••"
            />
          </View>

          <View style={{ marginBottom: theme.spacing.lg }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              Preferred Language
            </Text>
            <View style={{ flexDirection: 'row', gap: theme.spacing.sm }}>
              {languageOptions.map((lang) => (
                <TouchableOpacity
                  key={lang.value}
                  style={{
                    flex: 1,
                    paddingVertical: theme.spacing.md,
                    paddingHorizontal: theme.spacing.md,
                    borderRadius: theme.borderRadius.md,
                    borderWidth: 2,
                    borderColor: form.language === lang.value ? theme.colors.primary : theme.colors.border,
                    backgroundColor: form.language === lang.value ? theme.colors.primaryLight + '20' : theme.colors.surface,
                    alignItems: 'center',
                  }}
                  onPress={() => setForm({ ...form, language: lang.value })}
                >
                  <Text
                    style={{
                      ...theme.typography.bodySmall,
                      color: form.language === lang.value ? theme.colors.primary : theme.colors.text,
                      fontWeight: form.language === lang.value ? '600' : '400',
                    }}
                  >
                    {lang.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <TouchableOpacity
            style={{
              backgroundColor: theme.colors.primary,
              borderRadius: theme.borderRadius.md,
              paddingVertical: theme.spacing.md,
              alignItems: 'center',
              ...theme.shadows.md,
              opacity: loading ? 0.7 : 1,
            }}
            onPress={handleRegister}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color={theme.colors.textOnPrimary} size="large" />
            ) : (
              <Text style={{ ...theme.typography.button, color: theme.colors.textOnPrimary }}>
                Create Account
              </Text>
            )}
          </TouchableOpacity>

          <View style={{ flexDirection: 'row', justifyContent: 'center', marginTop: theme.spacing.lg }}>
            <Text style={{ ...theme.typography.body, color: theme.colors.textSecondary }}>
              Already have an account?{' '}
            </Text>
            <TouchableOpacity onPress={() => router.replace('/(auth)/login')}>
              <Text style={{ ...theme.typography.button, color: theme.colors.primary }}>
                Sign In
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}