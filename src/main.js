const { app, BrowserWindow, ipcMain, session, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;

// User extensions & plugins storage
const EXTENSIONS_DIR = path.join(app.getPath('userData'), 'extensions');
const PLUGINS_STORE_PATH = path.join(app.getPath('userData'), 'plugins_config.json');

if (!fs.existsSync(EXTENSIONS_DIR)) {
  fs.mkdirSync(EXTENSIONS_DIR, { recursive: true });
}

function loadSavedPluginsConfig() {
  try {
    if (fs.existsSync(PLUGINS_STORE_PATH)) {
      return JSON.parse(fs.readFileSync(PLUGINS_STORE_PATH, 'utf-8'));
    }
  } catch (err) {
    console.error('Error reading plugins config:', err);
  }
  return {
    adblock: true,
    darkMode: false,
    readerMode: false
  };
}

function savePluginsConfig(config) {
  try {
    fs.writeFileSync(PLUGINS_STORE_PATH, JSON.stringify(config, null, 2), 'utf-8');
  } catch (err) {
    console.error('Error saving plugins config:', err);
  }
}

let activePlugins = loadSavedPluginsConfig();

async function loadExistingExtensions() {
  try {
    const extFolders = fs.readdirSync(EXTENSIONS_DIR);
    for (const folder of extFolders) {
      const fullPath = path.join(EXTENSIONS_DIR, folder);
      if (fs.statSync(fullPath).isDirectory() && fs.existsSync(path.join(fullPath, 'manifest.json'))) {
        try {
          await session.defaultSession.loadExtension(fullPath, { allowFileAccess: true });
          console.log(`Loaded extension: ${folder}`);
        } catch (e) {
          console.warn(`Failed loading extension from ${fullPath}:`, e.message);
        }
      }
    }
  } catch (e) {
    console.error('Error reading extensions dir:', e);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1240,
    height: 820,
    minWidth: 840,
    minHeight: 600,
    title: 'GateBrowser',
    titleBarStyle: 'hidden',
    titleBarOverlay: false,
    frame: false,
    transparent: false,
    backgroundColor: '#16161a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webviewTag: true
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Window control handlers (macOS traffic lights style)
ipcMain.handle('window-control', (event, action) => {
  if (!mainWindow) return;
  if (action === 'close') {
    mainWindow.close();
  } else if (action === 'minimize') {
    mainWindow.minimize();
  } else if (action === 'maximize') {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

// Chrome extension management
ipcMain.handle('get-extensions', async () => {
  const exts = session.defaultSession.getAllExtensions();
  return exts.map(e => ({
    id: e.id,
    name: e.name,
    version: e.version,
    description: e.description || '',
    path: e.path
  }));
});

ipcMain.handle('add-extension-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Select Unpacked Chrome Extension Folder (with manifest.json)',
    properties: ['openDirectory']
  });

  if (result.canceled || !result.filePaths.length) {
    return { success: false, reason: 'canceled' };
  }

  const selectedPath = result.filePaths[0];
  const manifestPath = path.join(selectedPath, 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    return { success: false, reason: 'No manifest.json found in the selected folder.' };
  }

  try {
    const ext = await session.defaultSession.loadExtension(selectedPath, { allowFileAccess: true });
    return {
      success: true,
      extension: {
        id: ext.id,
        name: ext.name,
        version: ext.version,
        description: ext.description || '',
        path: selectedPath
      }
    };
  } catch (err) {
    return { success: false, reason: err.message };
  }
});

ipcMain.handle('remove-extension', async (event, extId) => {
  try {
    session.defaultSession.removeExtension(extId);
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// Built-in Plugins (AdBlock, DarkMode force, Reader)
ipcMain.handle('get-plugins-config', () => {
  return activePlugins;
});

ipcMain.handle('set-plugin-state', (event, { pluginName, enabled }) => {
  activePlugins[pluginName] = enabled;
  savePluginsConfig(activePlugins);
  return { success: true, activePlugins };
});

app.whenReady().then(async () => {
  await loadExistingExtensions();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
