const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    backgroundColor: '#0f172a',
    titleBarStyle: 'hiddenInset', // macOS style
    frame: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the app
  mainWindow.loadFile(path.join(__dirname, '..', 'src', 'index.html'));

  // Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (pythonProcess) {
      pythonProcess.kill();
    }
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Get Python path
function getPythonPath() {
  if (app.isPackaged) {
    // In production, use bundled Python
    const platform = process.platform;
    if (platform === 'win32') {
      return path.join(process.resourcesPath, 'python', 'python.exe');
    } else {
      return path.join(process.resourcesPath, 'python', 'bin', 'python3');
    }
  } else {
    // In development, use system Python
    return process.platform === 'win32' ? 'python' : 'python3';
  }
}

// Get script path
function getScriptPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'python', 'translator_bridge.py');
  } else {
    return path.join(__dirname, '..', 'python', 'translator_bridge.py');
  }
}

// IPC Handlers

// Select folder dialog
ipcMain.handle('select-folder', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: options.title || 'Select Folder'
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Select file dialog
ipcMain.handle('select-file', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: options.filters || [],
    title: options.title || 'Select File'
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Analyze files
ipcMain.handle('analyze-files', async (event, data) => {
  return new Promise((resolve, reject) => {
    const pythonPath = getPythonPath();
    const scriptPath = getScriptPath();
    
    const args = [
      scriptPath,
      'analyze',
      '--source', data.sourceFolder,
      '--model', data.model
    ];

    const pythonProc = spawn(pythonPath, args, {
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });
    let output = '';
    let errorOutput = '';

    pythonProc.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProc.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProc.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);
          resolve(result);
        } catch (e) {
          reject(new Error('Failed to parse analysis result'));
        }
      } else {
        reject(new Error(errorOutput || 'Analysis failed'));
      }
    });

    pythonProc.on('error', (err) => {
      reject(err);
    });
  });
});

// Start translation
ipcMain.handle('start-translation', async (event, data) => {
  return new Promise((resolve, reject) => {
    const pythonPath = getPythonPath();
    const scriptPath = getScriptPath();
    
    const args = [
      scriptPath,
      'translate',
      '--source', data.sourceFolder,
      '--output', data.outputFolder,
      '--langs',
      ...data.languages,
      '--model', data.model,
      '--api-key', data.apiKey
    ];

    pythonProcess = spawn(pythonPath, args, {
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });
    let hasError = false;

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      
      // Parse progress updates
      try {
        const lines = output.split('\n').filter(l => l.trim());
        lines.forEach(line => {
          if (line.startsWith('PROGRESS:')) {
            const progressData = JSON.parse(line.substring(9));
            mainWindow.webContents.send('translation-progress', progressData);
          } else if (line.startsWith('STATUS:')) {
            const status = line.substring(7);
            mainWindow.webContents.send('translation-status', status);
          }
        });
      } catch (e) {
        // Not JSON, just log it
        console.log(output);
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error('Python Error:', error);
      // Only treat as error if it contains "Traceback" or "Error:"
      if (error.includes('Traceback') || error.includes('Error:')) {
        mainWindow.webContents.send('translation-error', error);
        hasError = true;
      }
    });

    pythonProcess.on('close', (code) => {
      pythonProcess = null;
      if (code === 0 && !hasError) {
        resolve({ success: true });
      } else {
        reject(new Error('Translation failed'));
      }
    });

    pythonProcess.on('error', (err) => {
      pythonProcess = null;
      reject(err);
    });
  });
});

// Validate translations
ipcMain.handle('validate-translations', async (event, data) => {
  return new Promise((resolve, reject) => {
    const pythonPath = getPythonPath();
    const scriptPath = getScriptPath();
    
    const args = [
      scriptPath,
      'validate',
      '--output', data.outputFolder,
      '--source', data.sourceFolder
    ];

    const pythonProc = spawn(pythonPath, args, {
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });
    let output = '';
    let errorOutput = '';

    pythonProc.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProc.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProc.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output);
          resolve(result);
        } catch (e) {
          reject(new Error('Failed to parse validation result'));
        }
      } else {
        reject(new Error(errorOutput || 'Validation failed'));
      }
    });

    pythonProc.on('error', (err) => {
      reject(err);
    });
  });
});

// Retranslate specific file
ipcMain.handle('retranslate-file', async (event, data) => {
  return new Promise((resolve, reject) => {
    const pythonPath = getPythonPath();
    const scriptPath = getScriptPath();
    
    const args = [
      scriptPath,
      'retranslate',
      '--source', data.sourceFolder,
      '--output', data.outputFolder,
      '--file', data.filename,
      '--language', data.language,
      '--model', data.model,
      '--api-key', data.apiKey
    ];

    const pythonProc = spawn(pythonPath, args, {
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });
    let output = '';
    let errorOutput = '';

    pythonProc.stdout.on('data', (data) => {
      const outputStr = data.toString();
      
      // Send progress updates to frontend
      try {
        const lines = outputStr.split('\n').filter(l => l.trim());
        lines.forEach(line => {
          if (line.startsWith('PROGRESS:')) {
            const progressData = JSON.parse(line.substring(9));
            mainWindow.webContents.send('translation-progress', progressData);
          } else if (line.startsWith('STATUS:')) {
            const status = line.substring(7);
            mainWindow.webContents.send('translation-status', status);
          }
        });
      } catch (e) {
        // Not JSON
      }
      
      output += outputStr;
    });

    pythonProc.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProc.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, message: 'File retranslated' });
      } else {
        reject(new Error(errorOutput || 'Retranslation failed'));
      }
    });

    pythonProc.on('error', (err) => {
      reject(err);
    });
  });
});

// Cancel translation
ipcMain.handle('cancel-translation', async () => {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
    return { success: true };
  }
  return { success: false };
});

// Save settings
ipcMain.handle('save-settings', async (event, settings) => {
  try {
    const userDataPath = app.getPath('userData');
    const settingsPath = path.join(userDataPath, 'settings.json');
    fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Load settings
ipcMain.handle('load-settings', async () => {
  try {
    const userDataPath = app.getPath('userData');
    const settingsPath = path.join(userDataPath, 'settings.json');
    
    if (fs.existsSync(settingsPath)) {
      const data = fs.readFileSync(settingsPath, 'utf8');
      return JSON.parse(data);
    }
    return null;
  } catch (error) {
    return null;
  }
});