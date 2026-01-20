const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Folder/File selection
  selectFolder: (options) => ipcRenderer.invoke('select-folder', options),
  selectFile: (options) => ipcRenderer.invoke('select-file', options),
  
  // Translation operations
  analyzeFiles: (data) => ipcRenderer.invoke('analyze-files', data),
  startTranslation: (data) => ipcRenderer.invoke('start-translation', data),
  validateTranslations: (data) => ipcRenderer.invoke('validate-translations', data),
  retranslateFile: (data) => ipcRenderer.invoke('retranslate-file', data),
  retranslateFailedFiles: (data) => ipcRenderer.invoke('retranslate-failed-files', data),
  cancelTranslation: () => ipcRenderer.invoke('cancel-translation'),
  
  // Settings
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  loadSettings: () => ipcRenderer.invoke('load-settings'),
  
  // Progress listeners
  onTranslationProgress: (callback) => {
    ipcRenderer.on('translation-progress', (event, data) => callback(data));
  },
  onTranslationStatus: (callback) => {
    ipcRenderer.on('translation-status', (event, status) => callback(status));
  },
  onTranslationError: (callback) => {
    ipcRenderer.on('translation-error', (event, error) => callback(error));
  },
  onTranslationFileError: (callback) => {
    ipcRenderer.on('translation-file-error', (event, errorData) => callback(errorData));
  },
  onRetranslationProgress: (callback) => {
    ipcRenderer.on('retranslation-progress', (event, data) => callback(data));
  },
  
  // Remove listeners
  removeProgressListener: () => {
    ipcRenderer.removeAllListeners('translation-progress');
  },
  removeStatusListener: () => {
    ipcRenderer.removeAllListeners('translation-status');
  },
  removeErrorListener: () => {
    ipcRenderer.removeAllListeners('translation-error');
  },
  removeFileErrorListener: () => {
    ipcRenderer.removeAllListeners('translation-file-error');
  },
  removeRetranslationProgressListener: () => {
    ipcRenderer.removeAllListeners('retranslation-progress');
  }
});
