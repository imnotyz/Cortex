import React, { useState, useEffect } from 'react';
import { X, Check, AlertCircle } from 'lucide-react';
import { useI18n } from '@i18n';

const MODEL_TYPE_KEYS = [
  { value: 'chat', labelKey: 'config.model_type_chat', descKey: 'config.model_type_chat_desc' },
  { value: 'completion', labelKey: 'config.model_type_completion', descKey: 'config.model_type_completion_desc' },
  { value: 'embedding', labelKey: 'config.model_type_embedding', descKey: 'config.model_type_embedding_desc' },
  { value: 'image', labelKey: 'config.model_type_image', descKey: 'config.model_type_image_desc' },
  { value: 'audio', labelKey: 'config.model_type_audio', descKey: 'config.model_type_audio_desc' },
  { value: 'tts', labelKey: 'config.model_type_tts', descKey: 'config.model_type_tts_desc' },
  { value: 'vision', labelKey: 'config.model_type_vision', descKey: 'config.model_type_vision_desc' },
];

const AddModelPopup = ({ isOpen, onClose, onAdd, provider }) => {
  const { t } = useI18n();
  const [formData, setFormData] = useState({
    modelId: '',
    displayName: '',
    modelTypes: ['chat'],
    groupName: '',
    contextWindow: 128,
    enabled: true,
    pricingInput: '',
    pricingOutput: '',
    pricingCached: '',
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setFormData({
        modelId: '',
        displayName: '',
        modelTypes: ['chat'],
        groupName: '',
        contextWindow: 128,
        enabled: true,
        pricingInput: '',
        pricingOutput: '',
        pricingCached: '',
      });
      setErrors({});
      setIsSubmitting(false);
    }
  }, [isOpen]);

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.modelId.trim()) {
      newErrors.modelId = t('config.model_id_required');
    }

    if (!formData.displayName.trim()) {
      newErrors.displayName = t('config.display_name_required');
    }

    if (formData.modelTypes.length === 0) {
      newErrors.modelTypes = t('config.model_type_required');
    }

    if (!formData.groupName.trim()) {
      newErrors.groupName = t('config.group_name_required');
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    try {
      const pricing = {};
      if (formData.pricingInput) pricing.input = Number(formData.pricingInput);
      if (formData.pricingOutput) pricing.output = Number(formData.pricingOutput);
      if (formData.pricingCached) pricing.cached_input = Number(formData.pricingCached);

      await onAdd({
        providerId: provider?.id,
        modelId: formData.modelId.trim(),
        displayName: formData.displayName.trim(),
        modelType: formData.modelTypes[0], // Primary type
        modelTypes: formData.modelTypes, // All selected types
        groupName: formData.groupName.trim(),
        contextWindow: (Number(formData.contextWindow) >= 1000 ? Number(formData.contextWindow) : Number(formData.contextWindow) * 1000) || 128000,
        enabled: formData.enabled,
        pricing: Object.keys(pricing).length > 0 ? pricing : undefined,
      });
      onClose();
    } catch (error) {
      console.error('添加模型失败:', error);
      setErrors({ submit: error.message || t('config.add_model_failed') });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleModelTypeToggle = (typeValue) => {
    setFormData(prev => {
      const currentTypes = prev.modelTypes;
      let newTypes;
      
      if (currentTypes.includes(typeValue)) {
        // Remove type if already selected (but keep at least one)
        newTypes = currentTypes.filter(t => t !== typeValue);
        if (newTypes.length === 0) {
          newTypes = [typeValue]; // Prevent empty selection
        }
      } else {
        // Add type
        newTypes = [...currentTypes, typeValue];
      }
      
      return {
        ...prev,
        modelTypes: newTypes,
      };
    });
    // Clear error when user makes selection
    if (errors.modelTypes) {
      setErrors(prev => ({ ...prev, modelTypes: null }));
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container add-model-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{t('config.add_model_title')}</h3>
          <button className="modal-close-btn" onClick={onClose} disabled={isSubmitting}>
            <X size={18} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="add-model-form">
          {errors.submit && (
            <div className="error-banner">
              <AlertCircle size={16} />
              <span>{errors.submit}</span>
            </div>
          )}
          
          <div className="form-item">
            <label className="form-label required">{t('config.model_id')}</label>
            <input
              type="text"
              value={formData.modelId}
              onChange={(e) => handleChange('modelId', e.target.value)}
              placeholder="e.g., gpt-4o, claude-3-opus-20240229"
              className={`form-input ${errors.modelId ? 'error' : ''}`}
              disabled={isSubmitting}
              autoFocus
            />
            {errors.modelId && <span className="form-error">{errors.modelId}</span>}
            <span className="form-hint">{t('config.model_id_hint')}</span>
          </div>
          
          <div className="form-item">
            <label className="form-label required">{t('config.display_name')}</label>
            <input
              type="text"
              value={formData.displayName}
              onChange={(e) => handleChange('displayName', e.target.value)}
              placeholder="e.g., GPT-4o, Claude 3 Opus"
              className={`form-input ${errors.displayName ? 'error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.displayName && <span className="form-error">{errors.displayName}</span>}
            <span className="form-hint">A user-friendly name shown in the UI</span>
          </div>
          
          <div className="form-item">
            <label className="form-label required">Model Types (Multi-select)</label>
            <div className={`model-type-options multi-select ${errors.modelTypes ? 'error' : ''}`}>
              {MODEL_TYPE_KEYS.map((type) => (
                <div
                  key={type.value}
                  className={`model-type-option ${formData.modelTypes.includes(type.value) ? 'selected' : ''}`}
                  onClick={() => handleModelTypeToggle(type.value)}
                >
                  <div className="model-type-checkbox">
                    {formData.modelTypes.includes(type.value) && <Check size={12} />}
                  </div>
                  <div className="model-type-content">
                    <span className="model-type-label">{t(type.labelKey)}</span>
                    <span className="model-type-desc">{t(type.descKey)}</span>
                  </div>
                </div>
              ))}
            </div>
            {errors.modelTypes && <span className="form-error">{errors.modelTypes}</span>}
            <span className="form-hint">{t('config.model_capabilities_hint')}</span>
          </div>
          
          <div className="form-item">
            <label className="form-label required">{t('config.group_name_label')}</label>
            <input
              type="text"
              value={formData.groupName}
              onChange={(e) => handleChange('groupName', e.target.value)}
              placeholder="e.g., Chat Models, Image Models"
              className={`form-input ${errors.groupName ? 'error' : ''}`}
              disabled={isSubmitting}
            />
            {errors.groupName && <span className="form-error">{errors.groupName}</span>}
            <span className="form-hint">{t('config.group_name_hint')}</span>
          </div>

          <div className="form-item">
            <label className="form-label">Context Window (K)</label>
            <input
              type="number"
              min={1}
              step={1}
              value={formData.contextWindow}
              onChange={(e) => handleChange('contextWindow', e.target.value)}
              placeholder="128"
              className="form-input"
              disabled={isSubmitting}
            />
            <span className="form-hint">Model context window in thousands of tokens (e.g. 128 = 128000)</span>
          </div>
          
          <div className="form-item">
            <label className="form-label">Pricing (per 1M tokens, USD)</label>
            <div className="pricing-inputs">
              <div className="pricing-field">
                <input
                  type="number"
                  min={0}
                  step={0.01}
                  value={formData.pricingInput}
                  onChange={(e) => handleChange('pricingInput', e.target.value)}
                  placeholder="0.00"
                  className="form-input"
                  disabled={isSubmitting}
                />
                <span className="pricing-label">{t('config.pricing_input')}</span>
              </div>
              <div className="pricing-field">
                <input
                  type="number"
                  min={0}
                  step={0.01}
                  value={formData.pricingOutput}
                  onChange={(e) => handleChange('pricingOutput', e.target.value)}
                  placeholder="0.00"
                  className="form-input"
                  disabled={isSubmitting}
                />
                <span className="pricing-label">{t('config.pricing_output')}</span>
              </div>
              <div className="pricing-field">
                <input
                  type="number"
                  min={0}
                  step={0.01}
                  value={formData.pricingCached}
                  onChange={(e) => handleChange('pricingCached', e.target.value)}
                  placeholder="0.00"
                  className="form-input"
                  disabled={isSubmitting}
                />
                <span className="pricing-label">{t('config.pricing_cache')}</span>
              </div>
            </div>
            <span className="form-hint">{t('config.pricing_hint')}</span>
          </div>

          <div className="form-item">
            <label className="switch-row">
              <div className="switch-label-content">
                <span className="switch-label-text">{t('config.enabled_label')}</span>
                <span className="switch-label-desc">{t('config.enabled_desc')}</span>
              </div>
              <input
                type="checkbox"
                checked={formData.enabled}
                onChange={(e) => handleChange('enabled', e.target.checked)}
                disabled={isSubmitting}
              />
              <span className="switch-slider"></span>
            </label>
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={onClose}
              disabled={isSubmitting}
            >
              {t('action.cancel')}
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : t('config.create_model')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddModelPopup;
