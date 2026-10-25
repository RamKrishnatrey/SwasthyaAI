// SwasthyaAI Mobile Chat Screen
// AI Assistant with orb animation, message bubbles, voice input, TinyFish citations

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput, KeyboardAvoidingView, Platform, ActivityIndicator, Alert, Animated, Image, FlatList } from 'react-native';
import { useRouter } from 'expo-router';
import { Audio } from 'expo-av';
import * as Speech from 'expo-speech';
import { Ionicons, MaterialCommunityIcons, FontAwesome5 } from '@expo/vector-icons';
import { useAuth } from '../../src/context/AuthContext';
import { theme } from '../../src/utils/theme';
import api from '../../src/services/api';
import { Message, Conversation } from '../../src/types';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  metadata?: Record<string, any>;
  citations?: Array<{title: string; url: string; snippet: string}>;
  isStreaming?: boolean;
}

export default function ChatScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const recordingRef = useRef<Audio.Recording | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showCitations, setShowCitations] = useState<string | null>(null);
  const [orbScale, setOrbScale] = useState(new Animated.Value(1));
  const [orbOpacity, setOrbOpacity] = useState(new Animated.Value(0.5));
  const scrollRef = useRef<ScrollView>(null);
  const messagesEndRef = useRef<View>(null);

  const animateOrb = useCallback((active: boolean) => {
    if (active) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(orbScale, { toValue: 1.1, duration: 800, useNativeDriver: true }),
          Animated.timing(orbScale, { toValue: 1, duration: 800, useNativeDriver: true }),
        ])
      ).start();
      Animated.timing(orbOpacity, { toValue: 1, duration: 300, useNativeDriver: true }).start();
    } else {
      orbScale.stopAnimation();
      orbScale.setValue(1);
      Animated.timing(orbOpacity, { toValue: 0.5, duration: 300, useNativeDriver: true }).start();
    }
  }, [orbScale, orbOpacity]);

  const scrollToBottom = useCallback(() => {
    scrollRef.current?.scrollToEnd({ animated: true });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const loadConversation = async (convId?: string) => {
    try {
      if (convId) {
        const res = await api.getConversationMessages(convId, 50);
        setMessages(res.messages?.map((m: any) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          created_at: m.created_at,
          metadata: m.metadata,
          citations: m.metadata?.citations,
        })) || []);
        setConversationId(convId);
      } else {
        // Create new conversation
        const res = await api.createConversation({
          type: 'general_chat',
          language: 'en',
        });
        setConversationId(res.conversation.id);
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
    }
  };

  useEffect(() => {
    loadConversation();
  }, []);

  const sendMessage = async () => {
    if (!inputText.trim() || loading || !conversationId) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    const textToSend = inputText;
    setInputText('');
    setLoading(true);
    animateOrb(true);

    try {
      const res = await api.sendMessage(conversationId, {
        content: textToSend,
        content_type: 'text',
      });

      const assistantMessage: ChatMessage = {
        id: res.message.id,
        role: 'assistant',
        content: res.message.content,
        created_at: res.message.created_at,
        metadata: res.message.metadata,
        citations: res.message.metadata?.citations,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      Alert.alert('Error', err.response?.data?.detail || 'Failed to send message');
      // Remove user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
      animateOrb(false);
    }
  };

  const handleVoiceInput = async () => {
    try {
      if (recordingRef.current) {
        const recording = recordingRef.current;
        recordingRef.current = null;
        await recording.stopAndUnloadAsync();
        setIsRecording(false);
        const uri = recording.getURI();
        if (!uri) throw new Error('Could not read the audio recording.');
        setLoading(true);
        const transcript = await api.transcribeAudio(uri);
        if (transcript.text?.trim()) setInputText(prev => prev ? prev + ' ' + transcript.text.trim() : transcript.text.trim());
        else Alert.alert('Voice Input', 'No speech was detected. Please try again.');
        setLoading(false);
        return;
      }
      const permission = await Audio.requestPermissionsAsync();
      if (!permission.granted) { Alert.alert('Microphone permission', 'Allow microphone access in device settings to use voice input.'); return; }
      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const recording = new Audio.Recording();
      await recording.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await recording.startAsync();
      recordingRef.current = recording;
      setIsRecording(true);
      Alert.alert('Recording', 'Speak clearly, then tap the microphone again to stop and transcribe.');
    } catch (err: any) {
      recordingRef.current = null; setIsRecording(false); setLoading(false);
      Alert.alert('Voice Input', err?.response?.data?.detail || err?.message || 'Could not record or transcribe audio.');
    }
  };

  const speakMessage = (message: ChatMessage) => { if (message.role === 'assistant') { Speech.stop(); Speech.speak(message.content, { language: 'en-IN', rate: 0.95 }); } };

  const renderMessage = ({ item }: { item: ChatMessage }) => (
    <MessageBubble
      message={item}
      showCitations={showCitations === item.id}
      onToggleCitations={() => setShowCitations(showCitations === item.id ? null : item.id)}
      isUser={item.role === 'user'}
      onSpeak={() => speakMessage(item)}
    />
  );

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1, backgroundColor: theme.colors.background }}>
      {/* Header */}
      <View style={{ padding: theme.spacing.md, paddingTop: theme.spacing.lg, borderBottomWidth: 1, borderBottomColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.md }}>
            <Animated.View style={[
              { width: 44, height: 44, borderRadius: 22, backgroundColor: theme.colors.primary, justifyContent: 'center', alignItems: 'center' },
              { transform: [{ scale: orbScale }] }
            ]}>
              <Ionicons name="sparkles" size={22} color={theme.colors.textOnPrimary} />
            </Animated.View>
            <View>
              <Text style={{ ...theme.typography.h4, color: theme.colors.text }}>AI Assistant</Text>
              <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>Powered by TinyFish</Text>
            </View>
          </View>
          <TouchableOpacity style={{ padding: theme.spacing.sm }} onPress={() => router.push('/chat-history')}>
            <Ionicons name="time-outline" size={24} color={theme.colors.text} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Messages */}
      <ScrollView
        ref={scrollRef}
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: theme.spacing.md, paddingBottom: theme.spacing.xxl }}
        keyboardShouldPersistTaps="handled"
      >
        {messages.length === 0 && (
          <WelcomeMessage onQuickAction={(text) => {
            setInputText(text);
            sendMessage();
          }} />
        )}

        <FlatList
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id}
          ListFooterComponent={<View ref={messagesEndRef} />}
        />
        {loading && <TypingIndicator />}
      </ScrollView>

      {/* Input Area */}
      <View style={{ padding: theme.spacing.md, backgroundColor: theme.colors.surface, borderTopWidth: 1, borderTopColor: theme.colors.border }}>
        <View style={{ flexDirection: 'row', alignItems: 'flex-end', gap: theme.spacing.sm }}>
          <TouchableOpacity
            style={{
              width: 44,
              height: 44,
              borderRadius: theme.borderRadius.full,
              backgroundColor: theme.colors.surfaceVariant,
              justifyContent: 'center',
              alignItems: 'center',
            }}
            onPress={handleVoiceInput}
            disabled={loading}
          >
            <MaterialCommunityIcons name="microphone" size={22} color={loading ? theme.colors.textMuted : theme.colors.primary} />
          </TouchableOpacity>
          <TouchableOpacity
            style={{
              width: 44,
              height: 44,
              borderRadius: theme.borderRadius.full,
              backgroundColor: theme.colors.surfaceVariant,
              justifyContent: 'center',
              alignItems: 'center',
            }}
            onPress={() => Alert.alert('Attachments', 'Image and file upload coming soon')}
            disabled={loading}
          >
            <Ionicons name="attach-outline" size={22} color={loading ? theme.colors.textMuted : theme.colors.text} />
          </TouchableOpacity>
          <View style={{ flex: 1, flexDirection: 'row', alignItems: 'flex-end', gap: theme.spacing.sm, backgroundColor: theme.colors.surfaceVariant, borderRadius: theme.borderRadius.full, paddingHorizontal: theme.spacing.md, paddingVertical: theme.spacing.sm }}>
            <TextInput
              style={{ flex: 1, ...theme.typography.body, color: theme.colors.text, paddingVertical: 0 }}
              placeholder="Ask a health question..."
              value={inputText}
              onChangeText={setInputText}
              onSubmitEditing={sendMessage}
              multiline
              maxLength={2000}
              placeholderTextColor={theme.colors.textMuted}
              disabled={loading}
            />
          </View>
          <TouchableOpacity
            style={{
              width: 48,
              height: 48,
              borderRadius: theme.borderRadius.full,
              backgroundColor: inputText.trim() && !loading ? theme.colors.primary : theme.colors.surfaceVariant,
              justifyContent: 'center',
              alignItems: 'center',
            }}
            onPress={sendMessage}
            disabled={!inputText.trim() || loading}
          >
            <Ionicons name="send" size={22} color={inputText.trim() && !loading ? theme.colors.textOnPrimary : theme.colors.textMuted} />
          </TouchableOpacity>
        </View>
        <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted, textAlign: 'center', marginTop: theme.spacing.xs }}>
          AI responses are informational only. For emergencies, call 112/108.
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}

function WelcomeMessage({ onQuickAction }: { onQuickAction: (text: string) => void }) {
  const quickActions = [
    { label: 'What causes headaches?', icon: 'help-circle' },
    { label: 'How to manage diabetes?', icon: 'nutrition' },
    { label: 'Symptoms of high blood pressure', icon: 'heart-pulse' },
    { label: 'Healthy diet tips', icon: 'leaf' },
  ];

  return (
    <View style={{ padding: theme.spacing.xl, alignItems: 'center' }}>
      <Animated.View style={[
        { width: 80, height: 80, borderRadius: 40, backgroundColor: theme.colors.primary, justifyContent: 'center', alignItems: 'center' },
        { opacity: orbOpacity, transform: [{ scale: orbScale }] }
      ]}>
        <Ionicons name="sparkles" size={36} color={theme.colors.textOnPrimary} />
      </Animated.View>
      <Text style={{ ...theme.typography.h3, color: theme.colors.text, marginTop: theme.spacing.lg, textAlign: 'center' }}>
        Hello! How can I help you today?
      </Text>
      <Text style={{ ...theme.typography.body, color: theme.colors.textSecondary, marginTop: theme.spacing.sm, textAlign: 'center', paddingHorizontal: theme.spacing.lg }}>
        Ask me about symptoms, conditions, medications, or general health questions. I can also search the web for latest medical information.
      </Text>
      <View style={{ marginTop: theme.spacing.xl, gap: theme.spacing.sm, width: '100%' }}>
        {quickActions.map((action, i) => (
          <TouchableOpacity
            key={i}
            style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.md, padding: theme.spacing.md, backgroundColor: theme.colors.surface, borderRadius: theme.borderRadius.lg, ...theme.shadows.sm }}
            onPress={() => onQuickAction(action.label)}
          >
            <View style={{ width: 36, height: 36, borderRadius: theme.borderRadius.full, backgroundColor: theme.colors.primary + '15', justifyContent: 'center', alignItems: 'center' }}>
              <Ionicons name={action.icon} size={18} color={theme.colors.primary} />
            </View>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text }}>{action.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

function MessageBubble({ message, showCitations, onToggleCitations, isUser, onSpeak }: { message: ChatMessage; showCitations: boolean; onToggleCitations: () => void; isUser: boolean; onSpeak: () => void }) {
  const time = new Date(message.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

  return (
    <View style={{ marginBottom: theme.spacing.md, flexDirection: isUser ? 'row-reverse' : 'row', justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
      {!isUser && (
        <View style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: theme.colors.primary, justifyContent: 'center', alignItems: 'center', marginRight: theme.spacing.sm, marginTop: 2 }}>
          <Ionicons name="sparkles" size={16} color={theme.colors.textOnPrimary} />
        </View>
      )}
      <View style={{ maxWidth: '80%', flexDirection: isUser ? 'row-reverse' : 'row' }}>
        <View
          style={{
            paddingHorizontal: theme.spacing.md,
            paddingVertical: theme.spacing.sm,
            borderRadius: theme.borderRadius.lg,
            backgroundColor: isUser ? theme.colors.primary : theme.colors.surface,
            ...theme.shadows.sm,
            borderWidth: isUser ? 0 : 1,
            borderColor: theme.colors.border,
          }}
        >
          <Text style={{ ...theme.typography.body, color: isUser ? theme.colors.textOnPrimary : theme.colors.text }}>
            {message.content}
          </Text>
          {!isUser && <TouchableOpacity onPress={onSpeak} style={{ marginTop: theme.spacing.xs }}><Text style={{ ...theme.typography.caption, color: theme.colors.primary }}>Read aloud</Text></TouchableOpacity>}
          {message.citations && message.citations.length > 0 && (
            <View style={{ marginTop: theme.spacing.sm }}>
              <TouchableOpacity onPress={onToggleCitations} style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.xs }}>
                <Ionicons name={showCitations ? 'chevron-up' : 'chevron-down'} size={16} color={isUser ? theme.colors.textOnPrimary : theme.colors.textMuted} />
                <Text style={{ ...theme.typography.caption, color: isUser ? 'rgba(255,255,255,0.7)' : theme.colors.textMuted }}>
                  {message.citations.length} Source{message.citations.length > 1 ? 's' : ''} {showCitations ? '▲' : '▼'}
                </Text>
              </TouchableOpacity>
              {showCitations && (
                <View style={{ marginTop: theme.spacing.sm, paddingTop: theme.spacing.sm, borderTopWidth: 1, borderTopColor: isUser ? 'rgba(255,255,255,0.2)' : theme.colors.border }}>
                  {message.citations.map((citation, i) => (
                    <TouchableOpacity key={i} style={{ marginBottom: theme.spacing.xs }} onPress={() => Alert.alert('Open Link', citation.url)}>
                      <Text style={{ ...theme.typography.caption, color: isUser ? 'rgba(255,255,255,0.8)' : theme.colors.primary, textDecorationLine: 'underline' }}>
                        {citation.title}
                      </Text>
                      <Text style={{ ...theme.typography.caption, color: isUser ? 'rgba(255,255,255,0.5)' : theme.colors.textMuted, fontSize: 10 }}>
                        {citation.url}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </View>
          )}
        </View>
        {isUser && (
          <View style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: theme.colors.surfaceVariant, justifyContent: 'center', alignItems: 'center', marginLeft: theme.spacing.sm, marginTop: 2 }}>
            <Ionicons name="person" size={16} color={theme.colors.textMuted} />
          </View>
        )}
      </View>
      <View style={{ width: 32 }} />
    </View>
  );
}

function TypingIndicator() {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.sm, paddingHorizontal: theme.spacing.md, marginBottom: theme.spacing.md }}>
      <View style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: theme.colors.primary, justifyContent: 'center', alignItems: 'center', marginRight: theme.spacing.sm }}>
        <Ionicons name="sparkles" size={16} color={theme.colors.textOnPrimary} />
      </View>
      <View style={{ flexDirection: 'row', gap: 3, paddingHorizontal: theme.spacing.md, paddingVertical: theme.spacing.sm, backgroundColor: theme.colors.surface, borderRadius: theme.borderRadius.lg, ...theme.shadows.sm }}>
        <AnimatedDot delay={0} />
        <AnimatedDot delay={150} />
        <AnimatedDot delay={300} />
      </View>
    </View>
  );
}

function AnimatedDot({ delay }: { delay: number }) {
  const scale = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    const anim = Animated.loop(
      Animated.sequence([
        Animated.delay(delay),
        Animated.timing(scale, { toValue: 1, duration: 300, useNativeDriver: true }),
        Animated.timing(scale, { toValue: 0, duration: 300, useNativeDriver: true }),
      ])
    );
    anim.start();
    return () => anim.stop();
  }, [scale, delay]);

  return (
    <Animated.View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: theme.colors.primary, transform: [{ scale }] }} />
  );
}