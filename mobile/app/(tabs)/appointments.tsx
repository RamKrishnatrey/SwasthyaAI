// SwasthyaAI Mobile Appointments Screen
// Appointment booking, management, clinician search, available slots

import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Alert, ActivityIndicator, RefreshControl, FlatList, TextInput } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons, MaterialCommunityIcons, FontAwesome5 } from '@expo/vector-icons';
import { useAuth } from '../../src/context/AuthContext';
import { theme } from '../../src/utils/theme';
import api from '../../src/services/api';
import { Appointment, ClinicianProfile } from '../../src/types';

type FilterTab = 'upcoming' | 'past' | 'all';

export default function AppointmentsScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [filter, setFilter] = useState<FilterTab>('upcoming');
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showBooking, setShowBooking] = useState(false);
  const [clinicians, setClinicians] = useState<ClinicianProfile[]>([]);
  const [selectedClinician, setSelectedClinician] = useState<ClinicianProfile | null>(null);
  const [availableSlots, setAvailableSlots] = useState<Array<{date: string; slots: string[]}>>([]);
  const [selectedSlot, setSelectedSlot] = useState<{date: string; time: string} | null>(null);
  const [bookingStep, setBookingStep] = useState<'search' | 'slots' | 'confirm'>('search');
  const [bookingLoading, setBookingLoading] = useState(false);

  const loadAppointments = async () => {
    try {
      let res;
      if (filter === 'upcoming') {
        res = await api.getUpcomingAppointments(50);
      } else {
        res = await api.getAppointments({ status: filter === 'past' ? 'completed' : undefined, limit: 50 });
      }
      setAppointments(res.appointments || []);
    } catch (err) {
      console.error('Failed to load appointments:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const searchClinicians = async (query: string) => {
    if (!query.trim()) {
      setClinicians([]);
      return;
    }
    try {
      const res = await api.searchClinicians({ query, limit: 10 });
      setClinicians(res.clinicians || []);
    } catch (err) {
      console.error('Failed to search clinicians:', err);
    }
  };

  const loadAvailableSlots = async (clinicianId: string) => {
    try {
      const res = await api.getAvailableSlots(clinicianId, 30);
      setAvailableSlots(res.slots || []);
      setBookingStep('slots');
    } catch (err) {
      console.error('Failed to load slots:', err);
      Alert.alert('Error', 'Failed to load available slots');
    }
  };

  const bookAppointment = async () => {
    if (!selectedClinician || !selectedSlot) return;

    setBookingLoading(true);
    try {
      await api.bookAppointment({
        clinician_id: selectedClinician.id,
        scheduled_at: `${selectedSlot.date}T${selectedSlot.time}:00`,
        type: 'teleconsult',
        duration_minutes: 30,
        chief_complaint: 'General consultation',
      });
      Alert.alert('Success', 'Appointment booked successfully!');
      setShowBooking(false);
      setBookingStep('search');
      setSelectedClinician(null);
      setSelectedSlot(null);
      setAvailableSlots([]);
      setSearchQuery('');
      loadAppointments();
    } catch (err: any) {
      Alert.alert('Error', err.response?.data?.detail || 'Failed to book appointment');
    } finally {
      setBookingLoading(false);
    }
  };

  useEffect(() => {
    loadAppointments();
  }, [filter]);

  const cancelAppointment = async (appointmentId: string) => {
    Alert.alert(
      'Cancel Appointment',
      'Are you sure you want to cancel this appointment?',
      [
        { text: 'No', style: 'cancel' },
        { text: 'Yes', onPress: async () => {
          try {
            await api.cancelAppointment(appointmentId, 'Cancelled by patient');
            loadAppointments();
          } catch (err) {
            Alert.alert('Error', 'Failed to cancel appointment');
          }
        }}
      ]
    );
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: theme.colors.warning,
      confirmed: theme.colors.primary,
      in_progress: theme.colors.info,
      completed: theme.colors.success,
      cancelled: theme.colors.error,
      no_show: theme.colors.error,
      rescheduled: theme.colors.accent,
    };
    return colors[status] || theme.colors.textMuted;
  };

  const renderAppointment = ({ item }: { item: Appointment }) => (
    <TouchableOpacity style={styles.appointmentCard} onPress={() => router.push(`/appointment-detail/${item.id}`)}>
      <View style={{ width: 4, borderRadius: 2, backgroundColor: getStatusColor(item.status), marginRight: theme.spacing.md }} />
      <View style={{ flex: 1 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text style={{ ...theme.typography.body, color: theme.colors.text, fontWeight: '600' }}>
            {item.chief_complaint || 'Consultation'}
          </Text>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.xs }}>
            <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: getStatusColor(item.status) }} />
            <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted, textTransform: 'capitalize' }}>
              {item.status.replace('_', ' ')}
            </Text>
          </View>
        </View>
        <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textSecondary, marginTop: theme.spacing.xs }}>
          {formatDate(item.scheduled_at)} at {formatTime(item.scheduled_at)}
        </Text>
        <View style={{ flexDirection: 'row', gap: theme.spacing.md, marginTop: theme.spacing.xs }}>
          {item.type !== 'in_person' && (
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.xs }}>
              <Ionicons name={item.type === 'teleconsult' ? 'videocam' : 'home'} size={14} color={theme.colors.textMuted} />
              <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted, textTransform: 'capitalize' }}>
                {item.type.replace('_', ' ')}
              </Text>
            </View>
          )}
          {item.clinician_id && (
            <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>Dr. {item.clinician_id}</Text>
          )}
        </View>
      </View>
      {item.status === 'pending' || item.status === 'confirmed' ? (
        <TouchableOpacity style={{ padding: theme.spacing.xs, marginLeft: theme.spacing.md }} onPress={() => cancelAppointment(item.id)}>
          <Text style={{ ...theme.typography.caption, color: theme.colors.error }}>Cancel</Text>
        </TouchableOpacity>
      ) : (
        <Ionicons name="chevron-forward" size={20} color={theme.colors.textMuted} />
      )}
    </TouchableOpacity>
  );

  if (showBooking) {
    return (
      <BookingFlow
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        clinicians={clinicians}
        onSearchClinicians={searchClinicians}
        onSelectClinician={setSelectedClinician}
        selectedClinician={selectedClinician}
        availableSlots={availableSlots}
        onLoadSlots={loadAvailableSlots}
        onSelectSlot={setSelectedSlot}
        selectedSlot={selectedSlot}
        bookingStep={bookingStep}
        setBookingStep={setBookingStep}
        onBook={bookAppointment}
        bookingLoading={bookingLoading}
        onClose={() => {
          setShowBooking(false);
          setBookingStep('search');
          setSelectedClinician(null);
          setSelectedSlot(null);
          setAvailableSlots([]);
          setSearchQuery('');
        }}
      />
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
      {/* Header */}
      <View style={{ padding: theme.spacing.xl, paddingBottom: theme.spacing.md, backgroundColor: theme.colors.surface }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <View>
            <Text style={{ ...theme.typography.h2, color: theme.colors.text }}>Appointments</Text>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textSecondary }}>Manage your consultations</Text>
          </View>
          <TouchableOpacity
            style={{
              paddingHorizontal: theme.spacing.md,
              paddingVertical: theme.spacing.sm,
              backgroundColor: theme.colors.primary,
              borderRadius: theme.borderRadius.full,
            }}
            onPress={() => {
              setShowBooking(true);
              searchClinicians('');
            }}
          >
            <Text style={{ ...theme.typography.button, color: theme.colors.textOnPrimary }}>
              + Book New
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Filter Tabs */}
      <View style={{ flexDirection: 'row', paddingHorizontal: theme.spacing.md, backgroundColor: theme.colors.surface, borderBottomWidth: 1, borderBottomColor: theme.colors.border }}>
        {(['upcoming', 'past', 'all'] as FilterTab[]).map((tab) => (
          <TouchableOpacity
            key={tab}
            style={{
              flex: 1,
              paddingVertical: theme.spacing.md,
              alignItems: 'center',
              borderBottomWidth: 2,
              borderBottomColor: filter === tab ? theme.colors.primary : 'transparent',
            }}
            onPress={() => setFilter(tab)}
          >
            <Text style={{ ...theme.typography.bodySmall, fontWeight: '600', color: filter === tab ? theme.colors.primary : theme.colors.textMuted }}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Search Bar */}
      <View style={{ padding: theme.spacing.md, backgroundColor: theme.colors.surface }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: theme.colors.surfaceVariant, borderRadius: theme.borderRadius.full, paddingHorizontal: theme.spacing.md }}>
          <Ionicons name="search" size={20} color={theme.colors.textMuted} />
          <TextInput
            style={{ flex: 1, ...theme.typography.body, color: theme.colors.text, paddingVertical: theme.spacing.sm }}
            placeholder="Search appointments..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor={theme.colors.textMuted}
          />
        </View>
      </View>

      {/* Appointments List */}
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={loadAppointments} colors={[theme.colors.primary]} />
        }
        contentContainerStyle={{ paddingBottom: theme.spacing.xxl }}
        style={{ flex: 1 }}
      >
        {loading ? (
          <View style={{ padding: theme.spacing.xl, alignItems: 'center' }}>
            <ActivityIndicator color={theme.colors.primary} size="large" />
          </View>
        ) : appointments.length === 0 ? (
          <EmptyState
            icon={filter === 'upcoming' ? 'calendar' : 'calendar-outline'}
            title={filter === 'upcoming' ? 'No upcoming appointments' : filter === 'past' ? 'No past appointments' : 'No appointments yet'}
            subtitle={filter === 'upcoming' ? 'Book your next consultation' : 'Your appointment history will appear here'}
            actionLabel={filter === 'upcoming' ? 'Book Appointment' : undefined}
            onAction={filter === 'upcoming' ? () => { setShowBooking(true); searchClinicians(''); } : undefined}
          />
        ) : (
          <FlatList
            data={appointments}
            renderItem={renderAppointment}
            keyExtractor={item => item.id}
            contentContainerStyle={{ padding: theme.spacing.md, gap: theme.spacing.md }}
            ListEmptyComponent={
              <EmptyState
                icon="calendar"
                title="No appointments found"
                subtitle="Try adjusting your search or filter"
              />
            }
          />
        )}
      </ScrollView>
    </View>
  );
}

function BookingFlow({
  searchQuery,
  setSearchQuery,
  clinicians,
  onSearchClinicians,
  onSelectClinician,
  selectedClinician,
  availableSlots,
  onLoadSlots,
  onSelectSlot,
  selectedSlot,
  bookingStep,
  setBookingStep,
  onBook,
  bookingLoading,
  onClose,
}: any) {
  const handleSearch = (text: string) => {
    setSearchQuery(text);
    onSearchClinicians(text);
  };

  if (bookingStep === 'search') {
    return (
      <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
        <View style={{ padding: theme.spacing.md, backgroundColor: theme.colors.surface, borderBottomWidth: 1, borderBottomColor: theme.colors.border, flexDirection: 'row', alignItems: 'center', gap: theme.spacing.md }}>
          <TouchableOpacity onPress={onClose}>
            <Ionicons name="close" size={28} color={theme.colors.text} />
          </TouchableOpacity>
          <View style={{ flex: 1, flexDirection: 'row', alignItems: 'center', backgroundColor: theme.colors.surfaceVariant, borderRadius: theme.borderRadius.full, paddingHorizontal: theme.spacing.md }}>
            <Ionicons name="search" size={20} color={theme.colors.textMuted} />
            <TextInput
              style={{ flex: 1, ...theme.typography.body, color: theme.colors.text, paddingVertical: theme.spacing.sm }}
              placeholder="Search doctors by name, specialty..."
              value={searchQuery}
              onChangeText={handleSearch}
              placeholderTextColor={theme.colors.textMuted}
              autoFocus
            />
          </View>
        </View>
        <ScrollView contentContainerStyle={{ padding: theme.spacing.md, paddingBottom: theme.spacing.xxl }}>
          {clinicians.length === 0 && searchQuery ? (
            <View style={{ padding: theme.spacing.xl, alignItems: 'center' }}>
              <Ionicons name="search-outline" size={48} color={theme.colors.textMuted} />
              <Text style={{ ...theme.typography.h4, color: theme.colors.text, marginTop: theme.spacing.md }}>No doctors found</Text>
              <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textMuted, textAlign: 'center', marginTop: theme.spacing.xs }}>Try a different search term</Text>
            </View>
          ) : clinicians.length === 0 ? (
            <View style={{ padding: theme.spacing.xl, alignItems: 'center' }}>
              <Ionicons name="medical-outline" size={48} color={theme.colors.textMuted} />
              <Text style={{ ...theme.typography.h4, color: theme.colors.text, marginTop: theme.spacing.md }}>Search for a Doctor</Text>
              <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textMuted, textAlign: 'center', marginTop: theme.spacing.xs }}>Enter a name, specialty, or condition to find available doctors</Text>
            </View>
          ) : (
            <View style={{ gap: theme.spacing.md }}>
              {clinicians.map((clinician: any) => (
                <TouchableOpacity
                  key={clinician.id}
                  style={styles.clinicianCard}
                  onPress={() => {
                    onSelectClinician(clinician);
                    onLoadSlots(clinician.id);
                  }}
                >
                  <View style={{ flexDirection: 'row', gap: theme.spacing.md }}>
                    <View style={{ width: 56, height: 56, borderRadius: theme.borderRadius.full, backgroundColor: theme.colors.primary + '15', justifyContent: 'center', alignItems: 'center' }}>
                      <MaterialCommunityIcons name="account" size={26} color={theme.colors.primary} />
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={{ ...theme.typography.body, color: theme.colors.text, fontWeight: '600' }}>Dr. {clinician.name}</Text>
                      <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted, marginTop: theme.spacing.xs }}>{clinician.specialization}</Text>
                      <View style={{ flexDirection: 'row', gap: theme.spacing.md, marginTop: theme.spacing.xs }}>
                        <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.xs }}>
                          <Ionicons name="star" size={14} color={theme.colors.warning} />
                          <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>{clinician.rating?.toFixed(1) || '4.5'}</Text>
                        </View>
                        <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.xs }}>
                          <MaterialCommunityIcons name="currency-inr" size={14} color={theme.colors.textMuted} />
                          <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>₹{clinician.consultation_fee || '500'}</Text>
                        </View>
                        <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.xs }}>
                          <Ionicons name={clinician.available_for_teleconsult ? 'videocam' : 'videocam-off'} size={14} color={theme.colors.textMuted} />
                          <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>{clinician.available_for_teleconsult ? 'Video' : 'In-person'}</Text>
                        </View>
                      </View>
                    </View>
                    <Ionicons name="chevron-forward" size={20} color={theme.colors.textMuted} />
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </ScrollView>
      </View>
    );
  }

  if (bookingStep === 'slots') {
    return (
      <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
        <View style={{ padding: theme.spacing.md, backgroundColor: theme.colors.surface, borderBottomWidth: 1, borderBottomColor: theme.colors.border, flexDirection: 'row', alignItems: 'center', gap: theme.spacing.md }}>
          <TouchableOpacity onPress={() => setBookingStep('search')}>
            <Ionicons name="chevron-back" size={28} color={theme.colors.text} />
          </TouchableOpacity>
          <View style={{ flex: 1 }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textMuted }}>Select Time Slot</Text>
            <Text style={{ ...theme.typography.h4, color: theme.colors.text }}>Dr. {selectedClinician?.name}</Text>
          </View>
        </View>
        <ScrollView contentContainerStyle={{ padding: theme.spacing.md, paddingBottom: theme.spacing.xxl }}>
          {availableSlots.length === 0 ? (
            <View style={{ padding: theme.spacing.xl, alignItems: 'center' }}>
              <Ionicons name="calendar-outline" size={48} color={theme.colors.textMuted} />
              <Text style={{ ...theme.typography.h4, color: theme.colors.text, marginTop: theme.spacing.md }}>No slots available</Text>
              <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textMuted, textAlign: 'center', marginTop: theme.spacing.xs }}>No available slots for the next 30 days</Text>
            </View>
          ) : (
            <View style={{ gap: theme.spacing.lg }}>
              {availableSlots.map((day: any) => (
                <View key={day.date} style={{ gap: theme.spacing.md }}>
                  <Text style={{ ...theme.typography.h4, color: theme.colors.text, marginBottom: theme.spacing.sm }}>
                    {new Date(day.date).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
                  </Text>
                  <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.sm }}>
                    {day.slots.map((time: string) => (
                      <TouchableOpacity
                        key={time}
                        style={[
                          styles.slotButton,
                          selectedSlot?.date === day.date && selectedSlot?.time === time && styles.slotButtonSelected,
                        ]}
                        onPress={() => onSelectSlot({ date: day.date, time })}
                      >
                        <Text style={[
                          styles.slotButtonText,
                          selectedSlot?.date === day.date && selectedSlot?.time === time && styles.slotButtonTextSelected,
                        ]}>
                          {new Date(`${day.date}T${time}`).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
              ))}
            </View>
          )}
          {selectedSlot && (
            <TouchableOpacity style={[styles.confirmButton, bookingLoading && { opacity: 0.7 }]} onPress={onBook} disabled={bookingLoading}>
              {bookingLoading ? (
                <ActivityIndicator color={theme.colors.textOnPrimary} size="small" />
              ) : (
                <Text style={styles.confirmButtonText}>Confirm Booking</Text>
              )}
            </TouchableOpacity>
          )}
        </ScrollView>
      </View>
    );
  }

  return null;
}

function EmptyState({ icon, title, subtitle, actionLabel, onAction }: { icon: string; title: string; subtitle: string; actionLabel?: string; onAction?: () => void }) {
  return (
    <View style={{ padding: theme.spacing.xl, alignItems: 'center', paddingTop: theme.spacing.xxl }}>
      <Ionicons name={icon} size={64} color={theme.colors.textMuted} />
      <Text style={{ ...theme.typography.h3, color: theme.colors.text, marginTop: theme.spacing.md }}>{title}</Text>
      <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textMuted, textAlign: 'center', marginTop: theme.spacing.xs, paddingHorizontal: theme.spacing.lg }}>{subtitle}</Text>
      {actionLabel && onAction && (
        <TouchableOpacity style={{ marginTop: theme.spacing.lg, paddingHorizontal: theme.spacing.xl, paddingVertical: theme.spacing.md, backgroundColor: theme.colors.primary, borderRadius: theme.borderRadius.full }} onPress={onAction}>
          <Text style={{ ...theme.typography.body, color: theme.colors.textOnPrimary }}>{actionLabel}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = {
  appointmentCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    ...theme.shadows.sm,
  },
  clinicianCard: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    ...theme.shadows.sm,
  },
  slotButton: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    minWidth: 70,
    alignItems: 'center',
  },
  slotButtonSelected: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  slotButtonText: {
    ...theme.typography.bodySmall,
    color: theme.colors.text,
  },
  slotButtonTextSelected: {
    color: theme.colors.textOnPrimary,
  },
  confirmButton: {
    marginTop: theme.spacing.lg,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.full,
    alignItems: 'center',
    ...theme.shadows.md,
  },
  confirmButtonText: {
    ...theme.typography.button,
    color: theme.colors.textOnPrimary,
  },
};