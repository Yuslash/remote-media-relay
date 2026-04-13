import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
  confirmDelete: () => ipcRenderer.invoke('confirm-delete'),
  // Standard VPS connection config could be fetched via IPC 
  // but for MVP we will load .env in the frontend vite build directly
});
