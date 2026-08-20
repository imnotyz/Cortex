import { Search, ChevronDown, ChevronRight } from 'lucide-react';
import { SwitchField } from '@components/forms';
import WindowDots from '@components/layout/WindowDots';

export default function MCPToolsPanel({
  servers,
  selectedServer,
  serverTools,
  expandedTools,
  onSelectServer,
  onDiscoverTools,
  onToggleTool,
  onToggleExpanded,
}) {
  return (
    <div className="mcp-tools-container">
      <div className="mcp-tools-sidebar">
        <div className="tools-sidebar-header">
          <WindowDots />
          <span>服务器</span>
        </div>
        <div className="tools-server-list">
          {servers.map((server) => (
            <button
              key={server.name}
              className={`tools-server-item ${selectedServer?.name === server.name ? 'active' : ''}`}
              onClick={() => onSelectServer(server.name)}
            >
              <span className="server-item-name">{server.name}</span>
              <span className={`server-item-status ${server.connected ? 'connected' : 'disconnected'}`}>
                {server.connected ? '●' : '○'}
              </span>
            </button>
          ))}
        </div>
      </div>
      <div className="mcp-tools-content">
        {selectedServer ? (
          <>
            <div className="tools-content-header">
              <WindowDots />
              <span className="tools-server-title">{selectedServer.name}</span>
              <span className={`tools-server-badge ${selectedServer.connected ? 'connected' : 'disconnected'}`}>
                {selectedServer.connected ? '已连接' : '未连接'}
              </span>
            </div>
            {serverTools.length === 0 ? (
              <div className="mcp-empty">
                <span>此服务器暂无工具</span>
                <button
                  className="pixel-button"
                  onClick={() => onDiscoverTools(selectedServer.name)}
                >
                  <Search size={14} /> Discover
                </button>
              </div>
            ) : (
              <div className="mcp-tools-list">
                {serverTools.map((tool) => {
                  const isExpanded = expandedTools.has(tool.name);
                  return (
                    <div key={tool.name} className={`mcp-tool-card ${isExpanded ? 'expanded' : 'collapsed'}`}>
                      <div className="tool-header">
                        <button
                          className="tool-expand-btn"
                          onClick={() => onToggleExpanded(tool.name)}
                          title={isExpanded ? '收起' : '展开'}
                        >
                          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                          <span className="tool-name">{tool.name}</span>
                        </button>
                        <SwitchField
                          label=""
                          checked={tool.enabled}
                          onChange={(v) => onToggleTool(tool.name, selectedServer.name, v)}
                        />
                      </div>
                      {isExpanded && (
                        <>
                          <div className="tool-description">
                            {tool.description || '暂无描述'}
                          </div>
                          {tool.parameters && (
                            <div className="tool-params">
                              <span className="params-label">Parameters:</span>
                              <pre className="params-json">
                                {JSON.stringify(tool.parameters, null, 2)}
                              </pre>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </>
        ) : (
          <div className="mcp-empty">
            <span>选择一个服务器查看其工具</span>
          </div>
        )}
      </div>
    </div>
  );
}
