/**
 * 全局配置常量
 *
 * 后端端口在开发模式下默认 18791。
 * Electron 运行时通过 IPC `get-api-port` 动态获取实际端口（可能因端口占用而偏移），
 * 因此 BACKEND_PORT 是一个可变引用，需通过 `getBackendPort()` 异步获取。
 */

const DEFAULT_PORT = Number(import.meta.env.VITE_BACKEND_PORT) || 18791;

/** 默认后端端口（在 Electron IPC 返回值之前使用） */
export const BACKEND_PORT = DEFAULT_PORT;

/** 异步获取实际后端端口（Electron 运行时通过 IPC 动态分配） */
export async function getBackendPort(): Promise<number> {
  if (typeof window !== 'undefined' && window.electronAPI?.getApiPort) {
    try {
      const port = await window.electronAPI.getApiPort();
      if (port && typeof port === 'number') return port;
    } catch {
      // IPC 不可用时回退默认值
    }
  }
  return DEFAULT_PORT;
}

/** WebSocket URL（静态默认值，动态端口请用 getBackendPort() 后自行拼接） */
export const WS_URL = `ws://127.0.0.1:${DEFAULT_PORT}/ws`;

/** HTTP API 基础地址（静态默认值，动态端口请用 getBackendPort() 后自行拼接） */
export const API_BASE = `http://localhost:${DEFAULT_PORT}`;
