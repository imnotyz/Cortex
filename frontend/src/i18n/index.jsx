import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import zhCN from './zh-CN';
import enUS from './en-US';

const translations = {
  'zh-CN': zhCN,
  'en-US': enUS,
};

const STORAGE_KEY = 'cortex-language';

function getInitialLanguage() {
  if (typeof window === 'undefined') return 'zh-CN';
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === 'zh-CN' || saved === 'en-US') return saved;
  return 'zh-CN';
}

const I18nContext = createContext(null);

export function I18nProvider({ children }) {
  const [lang, setLang] = useState(getInitialLanguage);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.setAttribute('lang', lang === 'zh-CN' ? 'zh' : 'en');
  }, [lang]);

  const t = useCallback(
    (key, fallback) => {
      const keys = key.split('.');
      let value = translations[lang];
      for (const k of keys) {
        if (value && typeof value === 'object') {
          value = value[k];
        } else {
          value = undefined;
          break;
        }
      }
      return value !== undefined ? value : fallback || key;
    },
    [lang]
  );

  const toggleLanguage = useCallback(() => {
    setLang((prev) => (prev === 'zh-CN' ? 'en-US' : 'zh-CN'));
  }, []);

  return (
    <I18nContext.Provider value={{ lang, setLang, t, toggleLanguage }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}
