import React from 'react';
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { DistillTaskProvider } from './contexts/DistillTaskContext'
import { WebSocketProvider } from './contexts/WebSocketContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { I18nProvider } from '@i18n'
import './pixel-theme.css'

// Polyfill for URL.parse (used by react-pdf / pdfjs-dist in some environments)
if (typeof URL !== 'undefined' && !URL.parse) {
  URL.parse = function (url, base) {
    try {
      return new URL(url, base);
    } catch {
      return null;
    }
  };
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <I18nProvider>
      <ThemeProvider>
        <WebSocketProvider>
          <DistillTaskProvider>
            <div className="crt-overlay" />
            <App />
          </DistillTaskProvider>
        </WebSocketProvider>
      </ThemeProvider>
    </I18nProvider>
  </BrowserRouter>,
)
