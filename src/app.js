const { useState, useEffect } = React;

// Icon components (simplified SVG)
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
  
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icons[name]} />
    </svg>
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
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [estimatedCost, setEstimatedCost] = useState(null);
  const [showCostEstimate, setShowCostEstimate] = useState(false);

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

  // Load saved settings on mount
  useEffect(() => {
    window.electronAPI.loadSettings().then(settings => {
      if (settings) {
        if (settings.apiKey) setApiKey(settings.apiKey);
        if (settings.sourceFolder) setSourceFolder(settings.sourceFolder);
        if (settings.outputFolder) setOutputFolder(settings.outputFolder);
        if (settings.selectedModel) setSelectedModel(settings.selectedModel);
      }
    });

    // Set up progress listeners
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

    return () => {
      window.electronAPI.removeProgressListener();
      window.electronAPI.removeStatusListener();
      window.electronAPI.removeErrorListener();
    };
  }, []);

  // Save settings whenever they change
  useEffect(() => {
    const settings = {
      apiKey,
      sourceFolder,
      outputFolder,
      selectedModel
    };
    window.electronAPI.saveSettings(settings);
  }, [apiKey, sourceFolder, outputFolder, selectedModel]);

  const selectSourceFolder = async () => {
    const folder = await window.electronAPI.selectFolder({ title: 'Select Source Folder' });
    if (folder) {
      setSourceFolder(folder);
      setStatus('✅ Source folder selected');
      setTimeout(() => setStatus(''), 2000);
    }
  };

  const selectOutputFolder = async () => {
    const folder = await window.electronAPI.selectFolder({ title: 'Select Output Folder' });
    if (folder) {
      setOutputFolder(folder);
      setStatus('✅ Output folder selected');
      setTimeout(() => setStatus(''), 2000);
    }
  };

  const toggleLanguage = (code) => {
    setSelectedLanguages(prev => 
      prev.includes(code) 
        ? prev.filter(l => l !== code)
        : [...prev, code]
    );
  };

  const selectAllLanguages = () => {
    setSelectedLanguages(languages.map(l => l.code));
  };

  const clearAllLanguages = () => {
    setSelectedLanguages([]);
  };

  const calculateEstimate = async () => {
    if (!sourceFolder || selectedLanguages.length === 0) {
      setStatus('⚠️ Please select source folder and languages');
      return;
    }

    setStatus('💰 Analyzing files...');

    try {
      const result = await window.electronAPI.analyzeFiles({
        sourceFolder,
        model: selectedModel
      });

      if (result.success) {
        const costPerLang = result.costUSD;
        const totalUSD = costPerLang * selectedLanguages.length;
        const totalINR = totalUSD * 83;

        setEstimatedCost({
          files: result.files,
          tokens: result.totalTokens,
          usd: totalUSD,
          inr: totalINR,
          languages: selectedLanguages.length,
          confidence: result.confidence
        });
        setShowCostEstimate(true);
        setStatus('✅ Cost calculated successfully');
      } else {
        setStatus(`❌ ${result.error}`);
      }
    } catch (error) {
      setStatus(`❌ Error: ${error.message}`);
    }
  };

  const startTranslation = async () => {
    if (!apiKey) {
      setStatus('❌ Please enter your OpenAI API key');
      return;
    }
    if (!sourceFolder) {
      setStatus('❌ Please select source folder');
      return;
    }
    if (!outputFolder) {
      setStatus('❌ Please select output folder');
      return;
    }
    if (selectedLanguages.length === 0) {
      setStatus('❌ Please select at least one language');
      return;
    }

    setIsTranslating(true);
    setProgress(0);
    setStatus('🚀 Starting translation...');

    try {
      await window.electronAPI.startTranslation({
        sourceFolder,
        outputFolder,
        languages: selectedLanguages,
        model: selectedModel,
        apiKey
      });
      
      setStatus('🎉 Translation completed successfully!');
      setProgress(100);
    } catch (error) {
      setStatus(`❌ Translation failed: ${error.message}`);
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

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6 overflow-auto">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-8 mb-6">
          <div className="flex items-center gap-4 mb-2">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
              <Icon name="languages" className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white mb-1">Subtitle Translator</h1>
              <p className="text-purple-200">Japanese Drama Localization Tool</p>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* API Key */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Icon name="settings" />
                API Configuration
              </h3>
              
              <label className="block text-sm font-medium text-purple-200 mb-2">
                OpenAI API Key
              </label>
              <div className="relative">
                <input
                  type={showApiKey ? "text" : "password"}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-proj-..."
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 focus:outline-none focus:ring-2 focus:ring-purple-500 pr-10"
                />
                <button
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-300 hover:text-white"
                >
                  <Icon name={showApiKey ? "eyeOff" : "eye"} />
                </button>
              </div>
              <p className="text-xs text-purple-300 mt-2">Auto-saved securely</p>
            </div>

            {/* Model Selection */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Model Selection</h3>
              <div className="space-y-2">
                {models.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => setSelectedModel(model.id)}
                    className={`w-full p-3 rounded-xl text-left ${
                      selectedModel === model.id
                        ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                        : 'bg-white/5 text-purple-200 hover:bg-white/10'
                    }`}
                  >
                    <div className="font-semibold">{model.name}</div>
                    <div className="text-xs opacity-80">{model.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Folders */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Icon name="folder" />
                Folders
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-purple-200 mb-2">
                    Source Folder
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={sourceFolder}
                      readOnly
                      placeholder="No folder selected..."
                      className="flex-1 px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 text-sm"
                    />
                    <button
                      onClick={selectSourceFolder}
                      className="px-4 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white border border-white/20"
                    >
                      Browse
                    </button>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-purple-200 mb-2">
                    Output Folder
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={outputFolder}
                      readOnly
                      placeholder="No folder selected..."
                      className="flex-1 px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-purple-300/50 text-sm"
                    />
                    <button
                      onClick={selectOutputFolder}
                      className="px-4 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white border border-white/20"
                    >
                      Browse
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Languages */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Icon name="languages" />
                  Target Languages ({selectedLanguages.length})
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={selectAllLanguages}
                    className="px-3 py-1 text-xs bg-white/10 hover:bg-white/20 text-white rounded-lg"
                  >
                    Select All
                  </button>
                  <button
                    onClick={clearAllLanguages}
                    className="px-3 py-1 text-xs bg-white/10 hover:bg-white/20 text-white rounded-lg"
                  >
                    Clear
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => toggleLanguage(lang.code)}
                    className={`p-4 rounded-xl text-left ${
                      selectedLanguages.includes(lang.code)
                        ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg scale-105'
                        : 'bg-white/5 text-purple-200 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-2xl">{lang.flag}</span>
                      <div>
                        <div className="font-semibold">{lang.name}</div>
                        <div className="text-xs opacity-80">{lang.desc}</div>
                      </div>
                    </div>
                    {selectedLanguages.includes(lang.code) && (
                      <div className="flex justify-end">
                        <Icon name="check" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Cost Estimate */}
            {showCostEstimate && estimatedCost && (
              <div className="backdrop-blur-xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-2xl border border-green-400/30 shadow-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">💰 Cost Estimate</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-green-200">Files to Process</div>
                    <div className="text-2xl font-bold text-white">{estimatedCost.files}</div>
                  </div>
                  <div>
                    <div className="text-green-200">Target Languages</div>
                    <div className="text-2xl font-bold text-white">{estimatedCost.languages}</div>
                  </div>
                  <div>
                    <div className="text-green-200">Total Tokens</div>
                    <div className="text-2xl font-bold text-white">{estimatedCost.tokens.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-green-200">Total Cost</div>
                    <div className="text-2xl font-bold text-white">
                      ${estimatedCost.usd.toFixed(3)}
                      <span className="text-sm ml-2">~₹{estimatedCost.inr.toFixed(0)}</span>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-green-300 mt-3">{estimatedCost.confidence}</p>
              </div>
            )}

            {/* Progress */}
            {(isTranslating || progress > 0) && (
              <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-white">Translation Progress</h3>
                  <span className="text-purple-200 font-mono">{Math.round(progress)}%</span>
                </div>
                <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                    style={{ width: `${progress}%`, transition: 'width 0.3s ease' }}
                  />
                </div>
              </div>
            )}

            {/* Status */}
            {status && (
              <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 shadow-xl p-4">
                <div className="flex items-center gap-3 text-white">
                  <Icon name="alert" />
                  <span>{status}</span>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={calculateEstimate}
                disabled={isTranslating}
                className="backdrop-blur-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-semibold py-4 px-6 rounded-2xl shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Icon name="settings" />
                Calculate Cost
              </button>

              {isTranslating ? (
                <button
                  onClick={cancelTranslation}
                  className="bg-red-500 hover:bg-red-600 text-white font-semibold py-4 px-6 rounded-2xl shadow-xl flex items-center justify-center gap-2"
                >
                  Cancel
                </button>
              ) : (
                <button
                  onClick={startTranslation}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-4 px-6 rounded-2xl shadow-xl flex items-center justify-center gap-2"
                >
                  <Icon name="play" />
                  Start Translation
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-purple-300 text-sm">
          <p>Optimized for Japanese Drama Subtitles • Supports 7 Languages</p>
        </div>
      </div>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));