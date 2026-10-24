import type { Language } from '../types/agent';

export const translations: Record<Language, Record<string, string>> = {
  en: {
    overview: 'Overview', care: 'Care check', caregivers: 'Find care', future: 'Future radar', privacy: 'Privacy',
    start: 'Start a care check', title: 'Care, made clearer.', subtitle: 'A calmer way to understand your next step and find care that fits.',
    describe: 'Tell us what is happening…', submit: 'Continue', demo: 'Interactive demo',
    language: 'Language', safety: 'SafetyShield', privacyTitle: 'Your care story stays yours',
  },
  hi: {
    overview: 'अवलोकन', care: 'स्वास्थ्य जानकारी', caregivers: 'देखभाल खोजें', future: 'भविष्य रडार', privacy: 'निजता',
    start: 'देखभाल शुरू करें', title: 'देखभाल, अब और स्पष्ट।', subtitle: 'अगला सही कदम समझने और उपयुक्त देखभाल खोजने का आसान तरीका।',
    describe: 'बताइए क्या हो रहा है…', submit: 'आगे बढ़ें', demo: 'इंटरैक्टिव डेमो',
    language: 'भाषा', safety: 'सेफ्टीशील्ड', privacyTitle: 'आपकी जानकारी पर आपका नियंत्रण',
  },
  hinglish: {
    overview: 'Overview', care: 'Care check', caregivers: 'Care dhoondein', future: 'Future radar', privacy: 'Privacy',
    start: 'Care check shuru karein', title: 'Care, ab aur clear.', subtitle: 'Apna next step samajhne aur sahi care dhoondhne ka simple tareeka.',
    describe: 'Batayein kya ho raha hai…', submit: 'Continue karein', demo: 'Interactive demo',
    language: 'Language', safety: 'SafetyShield', privacyTitle: 'Aapki information, aapke control mein',
  },
};
