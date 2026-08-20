import React, { useState } from 'react';
import { X, Image } from 'lucide-react';
import { useI18n } from '@i18n';

function GenerateImageModal({ isOpen, onClose, onGenerate }) {
  const { t } = useI18n();
  const [prompt, setPrompt] = useState('');
  const [size, setSize] = useState('1024x1024');
  const [quality, setQuality] = useState('standard');
  const [isGenerating, setIsGenerating] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    try {
      await onGenerate({ prompt, size, quality });
      setPrompt('');
      onClose();
    } catch (error) {
      console.error('Generate image error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="image-modal-overlay" onClick={onClose}>
      <div className="image-modal-content generate-modal" onClick={e => e.stopPropagation()}>
        <div className="generate-modal-header">
          <h3>{t('chat.generate_image_title')}</h3>
          <button className="image-modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="generate-modal-body">
          <div className="form-group">
            <label>{t('chat.prompt_label')}</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder={t('chat.prompt_placeholder')}
              rows={4}
              className="pixel-textarea"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>{t('chat.size_label')}</label>
              <select
                value={size}
                onChange={(e) => setSize(e.target.value)}
                className="pixel-select"
              >
                <option value="1024x1024">1024x1024 ({t('chat.size_square')})</option>
                <option value="1024x1792">1024x1792 ({t('chat.size_vertical')})</option>
                <option value="1792x1024">1792x1024 ({t('chat.size_horizontal')})</option>
                <option value="512x512">512x512 ({t('chat.size_small')})</option>
              </select>
            </div>

            <div className="form-group">
              <label>{t('chat.quality_label')}</label>
              <select
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                className="pixel-select"
              >
                <option value="standard">Standard ({t('chat.quality_standard')})</option>
                <option value="hd">HD ({t('chat.quality_hd')})</option>
              </select>
            </div>
          </div>
        </div>

        <div className="generate-modal-footer">
          <button
            className="pixel-button secondary"
            onClick={onClose}
            disabled={isGenerating}
          >
            {t('action.cancel')}
          </button>
          <button
            className="pixel-button primary"
            onClick={handleGenerate}
            disabled={isGenerating || !prompt.trim()}
          >
            {isGenerating ? (
              <>
                <span className="loading-spinner-small"></span>
                {t('chat.generating')}
              </>
            ) : (
              <>
                <Image size={16} />
                {t('chat.generate_image_title')}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default GenerateImageModal;
