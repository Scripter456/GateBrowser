const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('gateAPI', {
  platform: process.platform,
  version: '0.0.1',
  windowControl: (action) => ipcRenderer.invoke('window-control', action),
  getExtensions: () => ipcRenderer.invoke('get-extensions'),
  addExtensionDialog: () => ipcRenderer.invoke('add-extension-dialog'),
  removeExtension: (id) => ipcRenderer.invoke('remove-extension', id),
  getPluginsConfig: () => ipcRenderer.invoke('get-plugins-config'),
  setPluginState: (pluginName, enabled) => ipcRenderer.invoke('set-plugin-state', { pluginName, enabled })
});
