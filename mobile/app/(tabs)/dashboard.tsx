// SwasthyaAI Mobile Dashboard Screen
// Patient dashboard with health overview, quick actions, upcoming appointments, reminders

import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Image, Alert, RefreshControl, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons, MaterialCommunityIcons, FontAwesome5 } from '@expo/vector-icons';
import { useAuth } from '../../src/context/AuthContext';
import { theme } from '../../src/utils/theme';
import api from '../../src/services/api';
import { PatientProfile, Appointment, Reminder } from '../../src/types';

interface DashboardData {
  profile: PatientProfile | null;
  upcomingAppointments: Appointment[];
  upcomingReminders: Reminder[];
  healthStats: {
    bmi?: number;
    bmiCategory?: string;
  };
}

export default function DashboardScreen() {
  const router = useRouter();
  const { user, patientProfile, refreshProfile, isAuthenticated } = useAuth();
  const [data, setData] = useState<DashboardData>({
    profile: null,
    upcomingAppointments: [],
    upcomingReminders: [],
    healthStats: {},
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      if (patientProfile) {
        setData(prev => ({ ...prev, profile: patientProfile }));
      }

      // Load upcoming appointments and reminders in parallel
      const [appointmentsRes, remindersRes] = await Promise.all([
        api.getUpcomingAppointments(3),
        api.getUpcomingReminders(24),
      ]);

      // Calculate BMI if height and weight available
      let bmi: number | undefined;
      let bmiCategory: string | undefined;
      if (patientProfile?.height_cm && patientProfile?.weight_kg) {
        const heightM = patientProfile.height_cm / 100;
        bmi = Math.round((patientProfile.weight_kg / (heightM * heightM)) * 10) / 10;
        if (bmi < 18.5) bmiCategory = 'Underweight';
        else if (bmi < 25) bmiCategory = 'Normal';
        else if (bmi < 30) bmiCategory = 'Overweight';
        else bmiCategory = 'Obese';
      }

      setData({
        profile: patientProfile || data.profile,
        upcomingAppointments: appointmentsRes.appointments || [],
        upcomingReminders: remindersRes.reminders || [],
        healthStats: { bmi, bmiCategory },
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await refreshProfile();
    await loadData();
  };

  useEffect(() => {
    loadData();
  }, [patientProfile]);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  if (!isAuthenticated) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: theme.spacing.xl }}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  const name = user?.full_name?.split(' ')[0] || 'there';

  return (
    <ScrollView
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[theme.colors.primary]} />
      }
      contentContainerStyle={{ paddingBottom: theme.spacing.xxl }}
      style={{ backgroundColor: theme.colors.background }}
    >
      {/* Greeting Header */}
      <View style={{ padding: theme.spacing.xl, paddingBottom: theme.spacing.md }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <View>
            <Text style={{ ...theme.typography.h3, color: theme.colors.text }}>
              {getGreeting()}, {name} 👋
            </Text>
            <Text style={{ ...theme.typography.body, color: theme.colors.textSecondary, marginTop: theme.spacing.xs }}>
              Here's your health overview today
            </Text>
          </View>
          <TouchableOpacity
            style={{
              width: 44,
              height: 44,
              borderRadius: theme.borderRadius.full,
              backgroundColor: theme.colors.surfaceVariant,
              justifyContent: 'center',
              alignItems: 'center',
            }}
            onPress={() => router.push('/settings')}
          >
            <Ionicons name="settings-outline" size={22} color={theme.colors.text} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Emergency Banner */}
      <TouchableOpacity
        style={{
          marginHorizontal: theme.spacing.xl,
          marginBottom: theme.spacing.lg,
          padding: theme.spacing.md,
          borderRadius: theme.borderRadius.lg,
          backgroundColor: theme.colors.emergency,
          flexDirection: 'row',
          alignItems: 'center',
          ...theme.shadows.md,
        }}
        onPress={() => router.push('/emergency')}
      >
        <View
          style={{
            width: 40,
            height: 40,
            borderRadius: theme.borderRadius.full,
            backgroundColor: 'rgba(255,255,255,0.2)',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Ionicons name="alert-circle" size={22} color={theme.colors.textOnPrimary} />
        </View>
        <View style={{ marginLeft: theme.spacing.md, flex: 1 }}>
          <Text style={{ color: theme.colors.textOnPrimary, ...theme.typography.h4 }}>
            Emergency Help
          </Text>
          <Text style={{ color: 'rgba(255,255,255,0.9)', ...theme.typography.bodySmall }}>
            Call 112/108 for immediate medical assistance
          </Text>
        </View>
        <Ionicons name="chevron-forward" size={22} color={theme.colors.textOnPrimary} />
      </TouchableOpacity>

      {/* Quick Actions Grid */}
      <View style={{ paddingHorizontal: theme.spacing.xl, marginBottom: theme.spacing.lg }}>
        <Text style={{ ...theme.typography.h3, color: theme.colors.text, marginBottom: theme.spacing.md }}>
          Quick Actions
        </Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.md }}>
          <QuickActionCard
            icon="medical"
            label="Symptom Checker"
            color={theme.colors.primary}
            onPress={() => router.push('/symptom-checker')}
          />
          <QuickActionCard
            icon="chatbubbles"
            label="AI Assistant"
            color={theme.colors.secondary}
            onPress={() => router.push('/chat')}
          />
          <QuickActionCard
            icon="calendar"
            label="Book Appointment"
            color={theme.colors.accent}
            onPress={() => router.push('/appointments')}
          />
          <QuickActionCard
            icon="document-text"
            label="Medical Records"
            color={theme.colors.warning}
            onPress={() => router.push('/medical-records')}
          />
        </View>
      </View>

      {/* Health Stats */}
      {(data.healthStats.bmi || data.profile?.height_cm || data.profile?.weight_kg) && (
        <View style={{ paddingHorizontal: theme.spacing.xl, marginBottom: theme.spacing.lg }}>
          <Text style={{ ...theme.typography.h3, color: theme.colors.text, marginBottom: theme.spacing.md }}>
            Health Stats
          </Text>
          <View style={{ flexDirection: 'row', gap: theme.spacing.md }}>
            <StatCard
              title="BMI"
              value={data.healthStats.bmi?.toString() || '--'}
              subtitle={data.healthStats.bmiCategory || 'Add height & weight'}
              icon="scale"
              color={theme.colors.primary}
            />
            <StatCard
              title="Height"
              value={data.profile?.height_cm ? `${data.profile.height_cm} cm` : '--'}
              subtitle="Tap to update"
              icon="resize"
              color={theme.colors.secondary}
              onPress={() => router.push('/profile')}
            />
            <StatCard
              title="Weight"
              value={data.profile?.weight_kg ? `${data.profile.weight_kg} kg` : '--'}
              subtitle="Tap to update"
              icon="weight"
              color={theme.colors.accent}
              onPress={() => router.push('/profile')}
            />
          </View>
        </View>
      )}

      {/* Upcoming Appointments */}
      <View style={{ paddingHorizontal: theme.spacing.xl, marginBottom: theme.spacing.lg }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.md }}>
          <Text style={{ ...theme.typography.h3, color: theme.colors.text }}>
            Upcoming Appointments
          </Text>
          <TouchableOpacity onPress={() => router.push('/appointments')}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.primary }}>
              View All
            </Text>
          </TouchableOpacity>
        </View>
        {loading ? (
          <View style={{ padding: theme.spacing.lg, alignItems: 'center' }}>
            <ActivityIndicator color={theme.colors.primary} />
          </View>
        ) : data.upcomingAppointments.length === 0 ? (
          <EmptyState
            icon="calendar"
            title="No upcoming appointments"
            subtitle="Book your next consultation"
            actionLabel="Book Appointment"
            onAction={() => router.push('/appointments')}
          />
        ) : (
          <View style={{ gap: theme.spacing.md }}>
            {data.upcomingAppointments.map((appt) => (
              <AppointmentCard key={appt.id} appointment={appt} onPress={() => router.push(`/appointment-detail/${appt.id}`)} />
            ))}
          </View>
        )}
      </View>

      {/* Upcoming Reminders */}
      <View style={{ paddingHorizontal: theme.spacing.xl }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.md }}>
          <Text style={{ ...theme.typography.h3, color: theme.colors.text }}>
            Reminders
          </Text>
          <TouchableOpacity onPress={() => router.push('/reminders')}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.primary }}>
              View All
            </Text>
          </TouchableOpacity>
        </View>
        {data.upcomingReminders.length === 0 ? (
          <EmptyState
            icon="bell"
            title="No reminders due"
            subtitle="Add medication or appointment reminders"
            actionLabel="Add Reminder"
            onAction={() => router.push('/reminders')}
          />
        ) : (
          <View style={{ gap: theme.spacing.sm }}>
            {data.upcomingReminders.slice(0, 3).map((reminder) => (
              <ReminderCard key={reminder.id} reminder={reminder} />
            ))}
          </View>
        )}
      </View>
    </ScrollView>
  );
}

function QuickActionCard({ icon, label, color, onPress }: { icon: string; label: string; color: string; onPress: () => void }) {
  return (
    <TouchableOpacity
      style={{
        width: '48%',
        aspectRatio: 1,
        borderRadius: theme.borderRadius.lg,
        backgroundColor: theme.colors.surface,
        justifyContent: 'center',
        alignItems: 'center',
        padding: theme.spacing.md,
        ...theme.shadows.sm,
      }}
      onPress={onPress}
    >
      <View
        style={{
          width: 56,
          height: 56,
          borderRadius: theme.borderRadius.lg,
          backgroundColor: color + '15',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Ionicons name={icon} size={26} color={color} />
      </View>
      <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, marginTop: theme.spacing.sm, textAlign: 'center' }}>
        {label}
      </Text>
    </TouchableOpacity>
  );
}

function StatCard({ title, value, subtitle, icon, color, onPress }: { title: string; value: string; subtitle: string; icon: string; color: string; onPress?: () => void }) {
  return (
    <TouchableOpacity
      style={{
        flex: 1,
        padding: theme.spacing.md,
        borderRadius: theme.borderRadius.lg,
        backgroundColor: theme.colors.surface,
        ...theme.shadows.sm,
      }}
      onPress={onPress}
    >
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: theme.spacing.xs }}>
        <View
          style={{
            width: 32,
            height: 32,
            borderRadius: theme.borderRadius.md,
            backgroundColor: color + '15',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Ionicons name={icon} size={16} color={color} />
        </View>
        <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted, marginLeft: theme.spacing.xs }}>
          {title}
        </Text>
      </View>
      <Text style={{ ...theme.typography.h2, color: theme.colors.text }}>{value}</Text>
      <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>{subtitle}</Text>
    </TouchableOpacity>
  );
}

function AppointmentCard({ appointment, onPress }: { appointment: Appointment; onPress: () => void }) {
  const date = new Date(appointment.scheduled_at);
  const statusColors = {
    pending: theme.colors.warning,
    confirmed: theme.colors.primary,
    completed: theme.colors.success,
    cancelled: theme.colors.error,
    in_progress: theme.colors.info,
  };

  return (
    <TouchableOpacity
      style={{
        padding: theme.spacing.md,
        borderRadius: theme.borderRadius.lg,
        backgroundColor: theme.colors.surface,
        flexDirection: 'row',
        ...theme.shadows.sm,
      }}
      onPress={onPress}
    >
      <View
        style={{
          width: 4,
          borderRadius: 2,
          backgroundColor: statusColors[appointment.status as keyof typeof statusColors] || theme.colors.textMuted,
          marginRight: theme.spacing.md,
        }}
      />
      <View style={{ flex: 1 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <Text style={{ ...theme.typography.body, color: theme.colors.text, fontWeight: '600' }}>
            {appointment.chief_complaint || 'Appointment'}
          </Text>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.xs }}>
            <View
              style={{
                width: 8,
                height: 8,
                borderRadius: 4,
                backgroundColor: statusColors[appointment.status as keyof typeof statusColors] || theme.colors.textMuted,
              }}
            />
            <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted, textTransform: 'capitalize' }}>
              {appointment.status.replace('_', ' ')}
            </Text>
          </View>
        </View>
        <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textSecondary, marginTop: theme.spacing.xs }}>
          {date.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })} at {date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
        </Text>
        {appointment.clinician_id && (
          <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted, marginTop: theme.spacing.xs }}>
            Dr. {appointment.clinician_id}
          </Text>
        )}
      </View>
      <Ionicons name="chevron-forward" size={20} color={theme.colors.textMuted} />
    </TouchableOpacity>
  );
}

function ReminderCard({ reminder }: { reminder: Reminder }) {
  const typeIcons: Record<string, string> = {
    medication: 'pill',
    appointment: 'calendar',
    follow_up: 'medical',
    vaccination: 'shield-check',
    checkup: 'heart-pulse',
    lab_test: 'flask',
    prescription_refill: 'refresh',
    health_goal: 'target',
    custom: 'bell',
  };

  const typeColors: Record<string, string> = {
    medication: theme.colors.primary,
    appointment: theme.colors.secondary,
    follow_up: theme.colors.accent,
    vaccination: theme.colors.warning,
    checkup: theme.colors.info,
    lab_test: theme.colors.lavender,
    prescription_refill: theme.colors.coral,
    health_goal: theme.colors.success,
    custom: theme.colors.textMuted,
  };

  const time = new Date(reminder.scheduled_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', padding: theme.spacing.md, backgroundColor: theme.colors.surface, borderRadius: theme.borderRadius.md, ...theme.shadows.sm }}>
      <View
        style={{
          width: 40,
          height: 40,
          borderRadius: theme.borderRadius.full,
          backgroundColor: (typeColors[reminder.type] || theme.colors.primary) + '15',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <MaterialCommunityIcons name={typeIcons[reminder.type] || 'bell'} size={20} color={typeColors[reminder.type] || theme.colors.primary} />
      </View>
      <View style={{ marginLeft: theme.spacing.md, flex: 1 }}>
        <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, fontWeight: '600' }}>
          {reminder.title}
        </Text>
        <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>
          {time} • {reminder.type.replace('_', ' ')}
        </Text>
      </View>
      {reminder.medication_name && (
        <View style={{ backgroundColor: theme.colors.primary + '15', paddingHorizontal: theme.spacing.sm, paddingVertical: theme.spacing.xs, borderRadius: theme.borderRadius.full }}>
          <Text style={{ ...theme.typography.caption, color: theme.colors.primary, fontWeight: '600' }}>
            {reminder.medication_name}
          </Text>
        </View>
      )}
    </View>
  );
}

function EmptyState({ icon, title, subtitle, actionLabel, onAction }: { icon: string; title: string; subtitle: string; actionLabel: string; onAction: () => void }) {
  return (
    <View style={{ padding: theme.spacing.xl, alignItems: 'center', backgroundColor: theme.colors.surface, borderRadius: theme.borderRadius.lg, ...theme.shadows.sm }}>
      <Ionicons name={icon} size={48} color={theme.colors.textMuted} />
      <Text style={{ ...theme.typography.h4, color: theme.colors.text, marginTop: theme.spacing.md }}>
        {title}
      </Text>
      <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textMuted, textAlign: 'center', marginTop: theme.spacing.xs }}>
        {subtitle}
      </Text>
      {actionLabel && onAction && (
        <TouchableOpacity
          style={{
            marginTop: theme.spacing.md,
            paddingHorizontal: theme.spacing.lg,
            paddingVertical: theme.spacing.sm,
            backgroundColor: theme.colors.primary,
            borderRadius: theme.borderRadius.full,
          }}
          onPress={onAction}
        >
          <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textOnPrimary }}>{actionLabel}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}