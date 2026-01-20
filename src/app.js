const { useState, useEffect } = React;

// Icon component
const Icon = ({ name, className = "w-5 h-5" }) => {
  const icons = {
    settings: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
    folder: "M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z",
    play: "M5 3l14 9-14 9V3z",
    check: "M5 13l4 4L19 7",
    eye: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z",
    eyeOff: "M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21",
    languages: "M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129",
    alert: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
  };
  
  return React.createElement('svg', 
    { className, fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' },
    React.createElement('path', {
      strokeLinecap: 'round',
      strokeLinejoin: 'round',
      strokeWidth: 2,
      d: icons[name]
    })
  );
};

function App() {
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [sourceFolder, setSourceFolder] = useState('');
  const [outputFolder, setOutputFolder] = useState('');
  const [selectedLanguages, setSelectedLanguages] = useState([]);
  const [selectedModel, setSelectedModel] = useState('gpt-4o-mini');
  const [isTranslating, setIsTranslating] = useState(false);
  const [useParallelLanguages, setUseParallelLanguages] = useState(false);
  const [useParallelFiles, setUseParallelFiles] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Ready to translate');
  const [isValidating, setIsValidating] = useState(false);
  const [validationResults, setValidationResults] = useState(null);
  const [showValidation, setShowValidation] = useState(false);
  const [failedFiles, setFailedFiles] = useState([]);
  const [isRetranslating, setIsRetranslating] = useState(false);
  const [fileErrors, setFileErrors] = useState({});

  const languages = [
    { code: 'hinglish', name: 'Hinglish', flag: '🇮🇳', desc: 'Hindi + English' },
    { code: 'taglish', name: 'Taglish', flag: '🇵🇭', desc: 'Tagalog + English' },
    { code: 'vietnamese', name: 'Vietnamese', flag: '🇻🇳', desc: 'Tiếng Việt' },
    { code: 'thai', name: 'Thai', flag: '🇹🇭', desc: 'ภาษาไทย' },
    { code: 'malay', name: 'Malay', flag: '🇲🇾', desc: 'Bahasa Melayu' },
    { code: 'spanish', name: 'Spanish', flag: '🇪🇸', desc: 'Español' },
    { code: 'indonesian', name: 'Indonesian', flag: '🇮🇩', desc: 'Bahasa Indonesia' }
  ];

  const models = [
    { id: 'gpt-4o-mini', name: 'GPT-4o Mini', desc: 'Fast & Cost-effective' },
    { id: 'gpt-5-mini', name: 'GPT-5 Mini', desc: 'Balanced Quality' },
    { id: 'gpt-4o', name: 'GPT-4o', desc: 'High Quality' },
    { id: 'gpt-5', name: 'GPT-5', desc: 'Premium Quality' }
  ];

  // Load settings
  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.loadSettings().then(settings => {
        if (settings) {
          if (settings.apiKey) setApiKey(settings.apiKey);
          if (settings.sourceFolder) setSourceFolder(settings.sourceFolder);
          if (settings.outputFolder) setOutputFolder(settings.outputFolder);
          if (settings.selectedModel) setSelectedModel(settings.selectedModel);
          if (settings.useParallelLanguages !== undefined) setUseParallelLanguages(settings.useParallelLanguages);
          if (settings.useParallelFiles !== undefined) setUseParallelFiles(settings.useParallelFiles);
        }
      });

      window.electronAPI.onTranslationProgress((data) => {
        setProgress(data.percentage);
      });

      window.electronAPI.onTranslationStatus((statusMsg) => {
        setStatus(statusMsg);
      });

      window.electronAPI.onTranslationError((error) => {
        setStatus(`❌ Error: ${error}`);
        setIsTranslating(false);
      });

      window.electronAPI.onTranslationFileError((errorData) => {
        setFileErrors(prev => ({
          ...prev,
          [`${errorData.filename}_${errorData.language || 'unknown'}`]: errorData
        }));
        setStatus(`⚠️ Error in ${errorData.filename}: ${errorData.message}`);
      });

      return () => {
        window.electronAPI.removeProgressListener();
        window.electronAPI.removeStatusListener();
        window.electronAPI.removeErrorListener();
        window.electronAPI.removeFileErrorListener();
      };
    }
  }, []);

  // Save settings
  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.saveSettings({ apiKey, sourceFolder, outputFolder, selectedModel, useParallelLanguages, useParallelFiles });
    }
  }, [apiKey, sourceFolder, outputFolder, selectedModel, useParallelLanguages, useParallelFiles]);

  const selectSourceFolder = async () => {
    const folder = await window.electronAPI.selectFolder({ title: 'Select Source Folder' });
    if (folder) {
      setSourceFolder(folder);
      setStatus('✅ Source folder selected');
    }
  };

  const selectOutputFolder = async () => {
    const folder = await window.electronAPI.selectFolder({ title: 'Select Output Folder' });
    if (folder) {
      setOutputFolder(folder);
      setStatus('✅ Output folder selected');
    }
  };

  const toggleLanguage = (code) => {
    setSelectedLanguages(prev => 
      prev.includes(code) ? prev.filter(l => l !== code) : [...prev, code]
    );
  };

  const selectAllLanguages = () => {
    setSelectedLanguages(languages.map(l => l.code));
  };

  const clearAllLanguages = () => {
    setSelectedLanguages([]);
  };

  const validateTranslations = async () => {
    setIsValidating(true);
    try {
      const results = await window.electronAPI.validateTranslations({
        outputFolder,
        sourceFolder
      });
      setValidationResults(results);
      setShowValidation(true);
      
      // Extract failed files for potential retranslation
      const failed = [];
      if (results.results) {
        results.results.forEach(langResult => {
          if (langResult.files) {
            langResult.files.forEach(fileResult => {
              if (!fileResult.passed) {
                failed.push({
                  file: fileResult.filename,
                  language: langResult.language
                });
              }
            });
          }
        });
      }
      setFailedFiles(failed);
      
      if (failed.length === 0) {
        setStatus('✅ All translations passed validation!');
      } else {
        setStatus(`⚠️ ${failed.length} file(s) need retranslation`);
      }
    } catch (error) {
      setStatus(`❌ Validation failed: ${error.message}`);
    } finally {
      setIsValidating(false);
    }
  };

  const retranslateFailedFiles = async () => {
    if (failedFiles.length === 0) {
      setStatus('✅ No files to retranslate');
      return;
    }

    setIsRetranslating(true);
    setStatus(`🔄 Retranslating ${failedFiles.length} file(s)...`);
    
    try {
      for (const failed of failedFiles) {
        await window.electronAPI.retranslateFile({
          sourceFolder,
          outputFolder,
          filename: failed.file,
          language: failed.language,
          model: selectedModel,
          apiKey
        });
      }
      
      // Validate again after retranslation
      setStatus('🔍 Validating retranslated files...');
      await validateTranslations();
    } catch (error) {
      setStatus(`❌ Retranslation failed: ${error.message}`);
    } finally {
      setIsRetranslating(false);
    }
  };

  const startTranslation = async () => {
    if (!apiKey || !sourceFolder || !outputFolder || selectedLanguages.length === 0) {
      setStatus('❌ Please fill all required fields');
      return;
    }

    setIsTranslating(true);
    setProgress(0);
    setStatus('🚀 Starting translation...');
    setShowValidation(false);
    setFailedFiles([]);

    try {
      await window.electronAPI.startTranslation({
        sourceFolder, outputFolder, languages: selectedLanguages, model: selectedModel, apiKey,
        parallelLanguages: useParallelLanguages, parallelFiles: useParallelFiles
      });
      setProgress(100);
      setStatus('🎉 Translation completed! Validating files...');
      
      // Automatically validate translations after completion
      setTimeout(() => validateTranslations(), 500);
    } catch (error) {
      setStatus(`❌ Failed: ${error.message}`);
    } finally {
      setIsTranslating(false);
    }
  };

  const cancelTranslation = async () => {
    await window.electronAPI.cancelTranslation();
    setIsTranslating(false);
    setProgress(0);
    setStatus('⏹️ Translation cancelled');
  };

  return React.createElement('div', 
    { className: 'h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6 overflow-auto' },
    React.createElement('div', { className: 'max-w-6xl mx-auto' },
      
      // Header
      React.createElement('div', {
        className: 'backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-8 mb-6'
      },
        React.createElement('div', { className: 'flex items-center gap-4 mb-2' },
          React.createElement('div', {
            className: 'w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg'
          },
            React.createElement(Icon, { name: 'languages', className: 'w-8 h-8 text-white' })
          ),
          React.createElement('div', null,
            React.createElement('h1', { className: 'text-4xl font-bold text-white mb-1' }, 'Subtitle Translator'),
            React.createElement('p', { className: 'text-purple-200' }, 'Japanese Drama Localization Tool')
          )
        )
      ),

      // Main Grid
      React.createElement('div', { className: 'grid grid-cols-1 lg:grid-cols-3 gap-6' },
        
        // Left Panel
        React.createElement('div', { className: 'lg:col-span-1 space-y-6' },
          
          // API Key
          React.createElement('div', {
            className: 'backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6'
          },
            React.createElement('h3', { className: 'text-lg font-semibold text-white mb-4 flex items-center gap-2' },
              React.createElement(Icon, { name: 'settings' }),
              'API Configuration'
            ),
            React.createElement('label', { className: 'block text-sm font-medium text-purple-200 mb-2' }, 'OpenAI API Key'),
            React.createElement('div', { className: 'relative' },
              React.createElement('input', {
                type: showApiKey ? 'text' : 'password',
                value: apiKey,
                onChange: (e) => setApiKey(e.target.value),
                placeholder: 'sk-proj-...',
                className: 'w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-purple-500 pr-10'
              }),
              React.createElement('button', {
                onClick: () => setShowApiKey(!showApiKey),
                className: 'absolute right-3 top-1/2 -translate-y-1/2 text-purple-300 hover:text-white'
              },
                React.createElement(Icon, { name: showApiKey ? 'eyeOff' : 'eye' })
              )
            ),
            React.createElement('p', { className: 'text-xs text-purple-300 mt-2' }, 'Auto-saved securely')
          ),

          // Model Selection
          React.createElement('div', {
            className: 'backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6'
          },
            React.createElement('h3', { className: 'text-lg font-semibold text-white mb-4' }, 'Model Selection'),
            React.createElement('div', { className: 'space-y-2' },
              ...models.map(model =>
                React.createElement('button', {
                  key: model.id,
                  onClick: () => setSelectedModel(model.id),
                  className: `w-full p-3 rounded-xl text-left ${
                    selectedModel === model.id
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                      : 'bg-white/5 text-purple-200 hover:bg-white/10'
                  }`
                },
                  React.createElement('div', { className: 'font-semibold' }, model.name),
                  React.createElement('div', { className: 'text-xs opacity-80' }, model.desc)
                )
              )
            )
          ),

          // Parallel Translation Settings
          React.createElement('div', {
            className: 'backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6'
          },
            React.createElement('h3', { className: 'text-lg font-semibold text-white mb-4' }, 'Translation Mode'),
            React.createElement('div', { className: 'space-y-3' },
              React.createElement('label', { className: 'flex items-center gap-3 cursor-pointer' },
                React.createElement('input', {
                  type: 'checkbox',
                  checked: useParallelLanguages,
                  onChange: (e) => setUseParallelLanguages(e.target.checked),
                  className: 'w-5 h-5 rounded cursor-pointer'
                }),
                React.createElement('div', null,
                  React.createElement('span', { className: 'text-white font-medium block' }, 'Parallel Languages'),
                  React.createElement('p', { className: 'text-xs text-purple-300' }, `All ${selectedLanguages.length} language(s) per file simultaneously`)
                )
              ),
              React.createElement('label', { className: 'flex items-center gap-3 cursor-pointer' },
                React.createElement('input', {
                  type: 'checkbox',
                  checked: useParallelFiles,
                  onChange: (e) => setUseParallelFiles(e.target.checked),
                  className: 'w-5 h-5 rounded cursor-pointer'
                }),
                React.createElement('div', null,
                  React.createElement('span', { className: 'text-white font-medium block' }, 'Parallel Files'),
                  React.createElement('p', { className: 'text-xs text-purple-300' }, 'Multiple SRT files at the same time')
                )
              ),
              (useParallelLanguages || useParallelFiles) && React.createElement('div', { className: 'bg-white/5 rounded-lg p-3 border border-white/10 mt-2' },
                React.createElement('p', { className: 'text-xs text-purple-300' },
                  `⚡ Mode: ${
                    useParallelLanguages && useParallelFiles 
                      ? 'Maximum speed - files & languages in parallel'
                      : useParallelLanguages
                      ? `${selectedLanguages.length} languages per file`
                      : 'Multiple files at once'
                  }`
                )
              )
            )
          ),

          // Folders
          React.createElement('div', {
            className: 'backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6'
          },
            React.createElement('h3', { className: 'text-lg font-semibold text-white mb-4 flex items-center gap-2' },
              React.createElement(Icon, { name: 'folder' }),
              'Folders'
            ),
            React.createElement('div', { className: 'space-y-4' },
              React.createElement('div', null,
                React.createElement('label', { className: 'block text-sm font-medium text-purple-200 mb-2' }, 'Source Folder'),
                React.createElement('div', { className: 'flex gap-2' },
                  React.createElement('input', {
                    type: 'text',
                    value: sourceFolder,
                    readOnly: true,
                    placeholder: 'No folder selected...',
                    className: 'flex-1 px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 text-sm'
                  }),
                  React.createElement('button', {
                    onClick: selectSourceFolder,
                    className: 'px-4 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white border border-white/20'
                  }, 'Browse')
                )
              ),
              React.createElement('div', null,
                React.createElement('label', { className: 'block text-sm font-medium text-purple-200 mb-2' }, 'Output Folder'),
                React.createElement('div', { className: 'flex gap-2' },
                  React.createElement('input', {
                    type: 'text',
                    value: outputFolder,
                    readOnly: true,
                    placeholder: 'No folder selected...',
                    className: 'flex-1 px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 text-sm'
                  }),
                  React.createElement('button', {
                    onClick: selectOutputFolder,
                    className: 'px-4 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white border border-white/20'
                  }, 'Browse')
                )
              )
            )
          )
        ),

        // Right Panel
        React.createElement('div', { className: 'lg:col-span-2 space-y-6' },
          
          // Languages
          React.createElement('div', {
            className: 'backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6'
          },
            React.createElement('div', { className: 'flex items-center justify-between mb-4' },
              React.createElement('h3', { className: 'text-lg font-semibold text-white flex items-center gap-2' },
                React.createElement(Icon, { name: 'languages' }),
                `Target Languages (${selectedLanguages.length})`
              ),
              React.createElement('div', { className: 'flex gap-2' },
                React.createElement('button', {
                  onClick: selectAllLanguages,
                  className: 'px-3 py-1 text-xs bg-white/10 hover:bg-white/20 text-white rounded-lg'
                }, 'Select All'),
                React.createElement('button', {
                  onClick: clearAllLanguages,
                  className: 'px-3 py-1 text-xs bg-white/10 hover:bg-white/20 text-white rounded-lg'
                }, 'Clear')
              )
            ),
            React.createElement('div', { className: 'grid grid-cols-2 gap-3' },
              languages.map(lang =>
                React.createElement('button', {
                  key: lang.code,
                  onClick: () => toggleLanguage(lang.code),
                  className: `p-3 rounded-xl text-left transition-all ${
                    selectedLanguages.includes(lang.code)
                      ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg'
                      : 'bg-white/5 text-purple-200 hover:bg-white/10'
                  }`
                },
                  React.createElement('div', { className: 'flex items-start justify-between gap-2' },
                    React.createElement('div', { className: 'flex items-start gap-2 min-w-0 flex-1' },
                      React.createElement('span', { className: 'text-xl flex-shrink-0' }, lang.flag),
                      React.createElement('div', { className: 'min-w-0' },
                        React.createElement('div', { className: 'font-semibold text-sm' }, lang.name),
                        React.createElement('div', { className: 'text-xs opacity-80' }, lang.desc)
                      )
                    ),
                    selectedLanguages.includes(lang.code) && React.createElement(Icon, { name: 'check', className: 'w-4 h-4 flex-shrink-0 mt-0.5' })
                  )
                )
              )
            )
          ),

          // Progress
          (isTranslating || progress > 0) && React.createElement('div', {
            className: 'backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6'
          },
            React.createElement('div', { className: 'flex items-center justify-between mb-3' },
              React.createElement('h3', { className: 'text-lg font-semibold text-white' }, 'Translation Progress'),
              React.createElement('span', { className: 'text-purple-200 font-mono' }, `${Math.round(progress)}%`)
            ),
            React.createElement('div', { className: 'w-full h-3 bg-white/10 rounded-full overflow-hidden' },
              React.createElement('div', {
                className: 'h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full',
                style: { width: `${progress}%`, transition: 'width 0.3s ease' }
              })
            )
          ),

          // Status
          status && React.createElement('div', {
            className: 'backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-4'
          },
            React.createElement('div', { className: 'flex items-center gap-3 text-white' },
              React.createElement(Icon, { name: 'alert' }),
              React.createElement('span', null, status)
            )
          ),

          // File Errors
          Object.keys(fileErrors).length > 0 && React.createElement('div', {
            className: 'backdrop-blur-xl bg-red-500/10 rounded-2xl border border-red-500/30 shadow-xl p-6'
          },
            React.createElement('h3', { className: 'text-lg font-semibold text-red-300 mb-4 flex items-center gap-2' },
              React.createElement(Icon, { name: 'alert' }),
              `File Errors (${Object.keys(fileErrors).length})`
            ),
            React.createElement('div', { className: 'space-y-2 max-h-40 overflow-y-auto' },
              Object.entries(fileErrors).map(([key, error]) =>
                React.createElement('div', { key, className: 'bg-red-500/5 rounded-lg p-2 text-sm' },
                  React.createElement('div', { className: 'font-mono text-red-300 text-xs break-all' }, error.filename),
                  React.createElement('div', { className: 'text-red-200 text-xs mt-1' }, error.message)
                )
              )
            )
          ),

          // Validation Results
          showValidation && validationResults && React.createElement('div', {
            className: 'backdrop-blur-xl bg-white/10 rounded-2xl border border-green-500/30 shadow-xl p-6'
          },
            React.createElement('h3', { className: 'text-lg font-semibold text-white mb-4 flex items-center gap-2' },
              React.createElement(Icon, { name: 'check' }),
              '✅ Validation Results'
            ),
            React.createElement('div', { className: 'space-y-3 mb-4 max-h-48 overflow-y-auto' },
              validationResults.results ? validationResults.results.map((langResult, idx) =>
                React.createElement('div', { key: idx, className: 'bg-white/5 rounded-lg p-3' },
                  React.createElement('div', { className: 'font-semibold text-purple-200' }, `${langResult.language}`),
                  React.createElement('div', { className: 'text-sm text-purple-300 mt-1' },
                    `${langResult.files ? langResult.files.filter(f => f.passed).length : 0} / ${langResult.files ? langResult.files.length : 0} files passed`
                  )
                )
              ) : React.createElement('div', { className: 'text-purple-200' }, 'Validation complete'),
              failedFiles.length > 0 && React.createElement('div', { className: 'bg-red-500/10 border border-red-500/30 rounded-lg p-3 mt-3' },
                React.createElement('div', { className: 'font-semibold text-red-300' }, `${failedFiles.length} file(s) need retranslation`)
              )
            )
          ),

          // Actions
          React.createElement('div', { className: 'grid grid-cols-1 gap-4' },
            isTranslating 
              ? React.createElement('button', {
                  onClick: cancelTranslation,
                  className: 'w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-4 px-6 rounded-2xl shadow-xl flex items-center justify-center gap-2'
                }, 'Cancel Translation')
              : React.createElement('div', { className: 'grid grid-cols-1 gap-2' },
                  React.createElement('button', {
                    onClick: startTranslation,
                    className: 'w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-4 px-6 rounded-2xl shadow-xl flex items-center justify-center gap-2'
                  },
                    React.createElement(Icon, { name: 'play' }),
                    'Start Translation'
                  ),
                  failedFiles.length > 0 && !isValidating && !isRetranslating && React.createElement('button', {
                    onClick: retranslateFailedFiles,
                    className: 'w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-2xl shadow-xl flex items-center justify-center gap-2'
                  },
                    React.createElement(Icon, { name: 'play' }),
                    `Retranslate ${failedFiles.length} Failed File(s)`
                  ),
                  isValidating && React.createElement('div', {
                    className: 'w-full bg-blue-500 text-white font-semibold py-3 px-6 rounded-2xl text-center'
                  }, 'Validating...')
                )
          )
        )
      ),

      // Footer
      React.createElement('div', { className: 'mt-6 text-center text-purple-300 text-sm' },
        React.createElement('p', null, 'Optimized for Japanese Drama Subtitles • Supports 7 Languages'),
        React.createElement('p', { className: 'mt-2 text-purple-400 text-xs' }, 'Made by Robinson Minj')
      )
    )
  );
}

ReactDOM.render(React.createElement(App), document.getElementById('root'));