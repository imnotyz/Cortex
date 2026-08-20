import { Server, Plus, RefreshCw, Eye, Search, Pencil } from 'lucide-react';
import { ConfigCard, DynamicItemCard } from '@components/config';
import { InputField } from '@components/forms';

export default function MCPServerList({
  servers,
  discoveringServer,
  onDiscover,
  onReconnect,
  onEdit,
  onDelete,
  onToggle,
  onViewTools,
  onAdd,
}) {
  return (
    <ConfigCard
      title="MCP 服务器"
      icon={<Server size={14} />}
      actions={
        <button className="add-btn" onClick={onAdd} title="添加 Server">
          <Plus size={14} />
        </button>
      }
    >
      {servers.length === 0 ? (
        <div className="empty-config">
          <span>暂无 MCP Server，点击 [+] 添加</span>
        </div>
      ) : (
        <div className="dynamic-items-list">
          {servers.map((server) => (
            <DynamicItemCard
              key={server.name}
              title={server.name}
              itemKey={server.name}
              onDelete={onDelete}
              defaultExpanded={false}
              enabled={server.enabled !== false}
              onToggleEnabled={onToggle}
              showEnabledSwitch={true}
            >
              <div className="server-detail-content">
                <div className="server-meta-row">
                  <span className="server-tools-badge">Tools: {server.tools?.length || 0}</span>
                  <span className={`server-status-badge ${server.connected ? 'connected' : 'disconnected'}`}>
                    {server.connected ? '已连接' : '未连接'}
                  </span>
                  <span className="server-protocol-badge">{server.protocol?.toUpperCase() || 'STDIO'}</span>
                </div>
                {server.protocol === 'stdio' || !server.protocol ? (
                  <>
                    <InputField
                      label="命令"
                      value={server.command || ''}
                      disabled={true}
                    />
                    {server.args && server.args.length > 0 && (
                      <div className="form-field">
                        <label className="form-label">参数</label>
                        <div className="args-display">
                          {server.args.map((arg, idx) => (
                            <span key={idx} className="arg-tag">{arg}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    <InputField
                      label="URL"
                      value={server.url || ''}
                      disabled={true}
                    />
                    <InputField
                      label="协议"
                      value={server.protocol || ''}
                      disabled={true}
                    />
                  </>
                )}
                {server.env && Object.keys(server.env).length > 0 && (
                  <div className="form-field">
                    <label className="form-label">环境变量</label>
                    <div className="env-display">
                      {Object.keys(server.env).map((key) => (
                        <span key={key} className="env-tag">{key}</span>
                      ))}
                    </div>
                  </div>
                )}
                <div className="server-actions-row">
                  <button
                    className="pixel-button small secondary"
                    onClick={() => onViewTools(server.name, true)}
                    title="查看工具"
                  >
                    <Eye size={14} />
                  </button>
                  <button
                    className={`pixel-button small ${discoveringServer === server.name ? 'loading' : ''}`}
                    onClick={() => onDiscover(server.name)}
                    disabled={discoveringServer === server.name}
                    title="发现工具"
                  >
                    {discoveringServer === server.name ? '...' : <Search size={14} />}
                  </button>
                  <button
                    className="pixel-button small"
                    onClick={() => onReconnect(server.name)}
                    title="重新连接"
                  >
                    <RefreshCw size={14} />
                  </button>
                  <button
                    className="pixel-button small secondary"
                    onClick={() => onEdit(server)}
                    title="编辑"
                  >
                    <Pencil size={14} />
                  </button>
                </div>
              </div>
            </DynamicItemCard>
          ))}
        </div>
      )}
    </ConfigCard>
  );
}
