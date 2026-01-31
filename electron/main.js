const { app, BrowserWindow, ipcMain, dialog, Notification, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let pythonProcess;

// Set app name early to fix notification title
app.setName('Subtitle Translator');
// Explicit AppUserModelID for Windows toast notifications
app.setAppUserModelId('com.subtitletranslator.app');

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    backgroundColor: '#0f172a',
    titleBarStyle: 'hiddenInset', // macOS style
    frame: true,
    icon: path.join(__dirname, '..', 'src', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Remove the menu bar (File, Edit, View, Window, Help)
  Menu.setApplicationMenu(null);

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

// Verify Python environment on startup
async function verifyPythonEnvironment() {
  return new Promise((resolve) => {
    const pythonPath = getPythonPath();
    const checkProcess = spawn(pythonPath, ['--version']);
    
    let hasOutput = false;
    checkProcess.stdout.on('data', () => { hasOutput = true; });
    checkProcess.stderr.on('data', () => { hasOutput = true; });
    
    checkProcess.on('close', (code) => {
      if (code === 0 || hasOutput) {
        console.log('Python environment verified');
        resolve(true);
      } else {
        const { dialog } = require('electron');
        dialog.showErrorBox(
          'Python Not Found',
          'Python is required but not found on your system.\n\n' +
          'Please install Python 3.8+ from python.org and try again.'
        );
        resolve(false);
      }
    });
    
    checkProcess.on('error', () => {
      const { dialog } = require('electron');
      dialog.showErrorBox(
        'Python Not Found',
        'Python is required but not found on your system.\n\n' +
        'Please install Python 3.8+ from python.org and try again.'
      );
      resolve(false);
    });
  });
}

app.whenReady().then(async () => {
  const pythonOk = await verifyPythonEnvironment();
  if (pythonOk) {
    createWindow();
  } else {
    app.quit();
  }
});

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
  // Use system Python for both development and production
  return process.platform === 'win32' ? 'python' : 'python3';
}

// Get script path
function getScriptPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'python', 'translator_bridge.py');
  } else {
    return path.join(__dirname, '..', 'python', 'translator_bridge.py');
  }
}

// Helper function to show notifications
function showNotification(title, options = {}) {
  if (Notification.isSupported()) {
    new Notification({
      title: title,
      icon: path.join(__dirname, '..', 'src', 'icon.png'),
      ...options
    }).show();
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
    // Validate folders exist
    if (!fs.existsSync(data.sourceFolder)) {
      reject(new Error('Source folder does not exist'));
      return;
    }
    
    if (!fs.existsSync(data.outputFolder)) {
      try {
        fs.mkdirSync(data.outputFolder, { recursive: true });
      } catch (err) {
        reject(new Error('Cannot create output folder: ' + err.message));
        return;
      }
    }
    
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
    
    // Add parallel options if specified
    if (data.parallelLanguages) {
      args.push('--parallel-langs');
    }
    if (data.parallelFiles) {
      args.push('--parallel-files');
    }

    pythonProcess = spawn(pythonPath, args, {
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });
    let hasError = false;
    let failedFiles = {};

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      
      // Parse different message types from Python
      try {
        const lines = output.split('\n').filter(l => l.trim());
        lines.forEach(line => {
          if (line.startsWith('PROGRESS:')) {
            const progressData = JSON.parse(line.substring(9));
            mainWindow.webContents.send('translation-progress', progressData);
          } else if (line.startsWith('STATUS:')) {
            const status = line.substring(7);
            mainWindow.webContents.send('translation-status', status);
          } else if (line.startsWith('ERROR:')) {
            // Handle ERROR messages from Python
            const errorData = JSON.parse(line.substring(6));
            mainWindow.webContents.send('translation-file-error', errorData);
            
            // Track failed files
            const key = errorData.language ? `${errorData.filename}_${errorData.language}` : errorData.filename;
            failedFiles[key] = errorData.message;
            hasError = true;
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
      // Only treat as critical error if it contains traceback
      if (error.includes('Traceback')) {
        mainWindow.webContents.send('translation-error', error);
        hasError = true;
      }
    });

    pythonProcess.on('close', (code) => {
      pythonProcess = null;
      if (code === 0) {
        showNotification('Translation Complete! ✅', {
          body: 'All files have been translated. Starting validation...',
          sound: true
        });
        resolve({ 
          success: true, 
          had_errors: hasError,
          failed_files: failedFiles 
        });
      } else {
        showNotification('Translation Failed! ❌', {
          body: 'An error occurred during translation. Check the app for details.',
          sound: true
        });
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
    // Validate folders exist
    if (!fs.existsSync(data.outputFolder)) {
      reject(new Error('Output folder does not exist. Please translate files first.'));
      return;
    }
    
    if (!fs.existsSync(data.sourceFolder)) {
      reject(new Error('Source folder does not exist'));
      return;
    }
    
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
          const failedCount = result.failed_files ? result.failed_files.length : 0;
          
          if (failedCount === 0) {
            showNotification('Validation Complete! ✅', { 
              body: 'All subtitle files passed validation.',
              sound: true 
            });
          } else {
            showNotification('Some files failed validation ⚠️', { 
              body: `${failedCount} file(s) need retranslation.`,
              sound: true 
            });
          }
          resolve(result);
        } catch (e) {
          showNotification('Validation Error! ❌', { 
            body: 'Failed to parse validation result.',
            sound: true 
          });
          reject(new Error('Failed to parse validation result'));
        }
      } else {
        showNotification('Validation Failed! ❌', { 
          body: 'An error occurred during validation.',
          sound: true 
        });
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
          } else if (line.startsWith('ERROR:')) {
            const errorData = JSON.parse(line.substring(6));
            mainWindow.webContents.send('translation-file-error', errorData);
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
        showNotification('Retranslation Complete! ✅', { 
          body: `File "${data.filename}" has been retranslated.`,
          sound: true 
        });
        resolve({ success: true, message: 'File retranslated' });
      } else {
        showNotification('Retranslation Failed! ❌', { 
          body: `Failed to retranslate "${data.filename}".`,
          sound: true 
        });
        reject(new Error(errorOutput || 'Retranslation failed'));
      }
    });

    pythonProc.on('error', (err) => {
      reject(err);
    });
  });
});

// Retranslate multiple failed files
ipcMain.handle('retranslate-failed-files', async (event, data) => {
  return new Promise((resolve, reject) => {
    const failedFiles = data.failedFiles; // Array of {filename, language}
    const results = [];
    let completed = 0;

    const retranslateNext = async () => {
      if (completed >= failedFiles.length) {
        resolve({ 
          success: true, 
          total: failedFiles.length,
          successful: results.filter(r => r.success).length,
          failed: results.filter(r => !r.success).length,
          results: results
        });
        return;
      }

      const file = failedFiles[completed];
      try {
        const result = await ipcMain._handle['retranslate-file'](event, {
          sourceFolder: data.sourceFolder,
          outputFolder: data.outputFolder,
          filename: file.filename,
          language: file.language,
          model: data.model,
          apiKey: data.apiKey
        });
        results.push({ ...file, success: true, message: result.message });
      } catch (error) {
        results.push({ ...file, success: false, error: error.message });
      }

      completed++;
      const progress = (completed / failedFiles.length) * 100;
      mainWindow.webContents.send('retranslation-progress', { 
        percentage: progress, 
        current: completed, 
        total: failedFiles.length 
      });
      
      retranslateNext();
    };

    retranslateNext();
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
    
    // WARNING: API keys are stored in plain text
    // For production, consider using electron-store with encryption
    // or system keychain (keytar package)
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