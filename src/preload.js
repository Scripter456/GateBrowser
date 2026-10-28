const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('gateAPI', {
  platform: process.platform,
  version: '1.0.0'
});
