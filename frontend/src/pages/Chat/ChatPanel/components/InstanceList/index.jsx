import React, { useRef } from 'react';
import { RefreshCw, Plus } from 'lucide-react';
import WindowDots from '@components/layout/WindowDots';
import InstanceItem from './InstanceItem.jsx';
import { useI18n } from '@i18n';
import './InstanceList.css';

function InstanceList({
  instances,
  selectedInstance,
  loading,
  initialLoading,
  error,
  hasMore,
  isLoadingMore,
  sendWSMessage,
  onSelect,
  onDelete,
  onCreateNew,
  onRefresh,
  isCreatingNew,
  onScrollEnd
}) {
  const { t } = useI18n();
  const instanceListRef = useRef(null);

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    if (scrollHeight - scrollTop - clientHeight < 50 && hasMore && !isLoadingMore && !loading) {
      if (onScrollEnd) {
        onScrollEnd();
      }
    }
  };

  return (
    <div className="chat-sidebar">
      <div className="window-header">
        <WindowDots />
        <span className="window-title">{t('chat.title')}</span>
        <button
          className="refresh-btn"
          onClick={onRefresh}
          disabled={loading || !sendWSMessage}
          title={!sendWSMessage ? t('chat.not_connected') : t('chat.refresh_list')}
        >
          <RefreshCw size={10} className={loading ? 'spin' : ''} />
        </button>
      </div>

      <div className="new-chat-section">
        <button
          className={`new-chat-btn ${isCreatingNew ? '活跃' : ''}`}
          onClick={onCreateNew}
        >
          <Plus size={12} />
          <span>{t('chat.new_conversation')}</span>
        </button>
      </div>

      <div 
        className="chat-instance-list" 
        ref={instanceListRef}
        onScroll={handleScroll}
      >
        {initialLoading && (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <div className="loading-text">{t('chat.loading_chats')}</div>
          </div>
        )}
        {error && !initialLoading && (
          <div className="empty-state-small" style={{ color: 'var(--error)', fontSize: '11px' }}>
            {t('status.error')}: {error}
          </div>
        )}
        {!sendWSMessage && !initialLoading && (
          <div className="empty-state-small" style={{ color: 'var(--warning)', fontSize: '11px' }}>
            {t('chat.websocket_not_connected')}
          </div>
        )}
        {instances.length === 0 && !error && sendWSMessage && !initialLoading && (
          <div className="empty-state-small">
            {t('chat.no_chats')}
          </div>
        )}

        {instances.map((instance) => (
          <InstanceItem
            key={instance.id}
            instance={instance}
            isSelected={selectedInstance?.id === instance.id}
            onSelect={onSelect}
            onDelete={onDelete}
          />
        ))}

        {isLoadingMore && (
          <div className="loading-more">
            <div className="loading-spinner-small"></div>
            <span>{t('chat.loading_more')}</span>
          </div>
        )}

        {!hasMore && instances.length > 0 && !initialLoading && (
          <div className="no-more-data">
            {t('chat.no_more_chats')}
          </div>
        )}
      </div>
    </div>
  );
}

export default InstanceList;
