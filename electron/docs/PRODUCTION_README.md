# Subtitle Translator - Production-Ready App

## Overview

This is a comprehensive, production-ready Electron + Python application for translating Japanese drama subtitles into multiple languages with professional error handling, recovery mechanisms, and user-friendly error reporting.

## Key Features

### ✅ Robust Error Handling

- **File-Level Error Tracking**: Each translation error is tracked individually with context
- **Automatic Retry Logic**: Retryable errors (rate limits, timeouts) automatically retry with exponential backoff
- **Error Categorization**: Errors are categorized by type (API, File, Parsing, Timeout, Auth, etc.)
- **Error Logging**: All errors are logged to `logs/translation_errors.log` for debugging

### ✅ Error Recovery

- **Automatic Retries**: Rate limit errors, timeouts, and connection errors automatically retry
- **Exponential Backoff**: Retry delays: 1s, 2s, 4s, 8s (max 60s)
- **User-Friendly Messages**: Clear error messages in the UI
- **Retranslation**: Failed files can be retranslated individually or in batch

### ✅ Comprehensive Validation

- **Post-Translation Validation**: Automatically validates translated files after completion
- **Block Count Validation**: Ensures all blocks are present
- **Timestamp Validation**: Verifies timestamps match between source and target
- **Text Content Validation**: Checks for empty or malformed content

### ✅ User Interface

- **Real-Time Progress**: Live progress updates for translation process
- **Error Display Panel**: Shows file-level errors with context
- **Failed File List**: Clear display of which files failed and which language
- **Batch Retranslation**: Retry all failed files at once
- **Status Messages**: Descriptive status updates throughout the process

### ✅ Performance Optimizations

- **Parallel Processing**: Support for parallel file and language translation
- **Efficient Token Calculation**: Realistic token estimation for cost prediction
- **Resource Management**: Thread pooling with configurable worker limits
- **Memory Efficiency**: Stream processing for large files

### ✅ Production Readiness

- **Comprehensive Testing**: 7 core test scenarios covering all critical paths
- **Error Logging**: Structured JSON error logs for debugging
- **Settings Persistence**: User settings saved across sessions
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Built-in Documentation**: Clear error messages and help text

## Installation & Setup

### Requirements

```
- Node.js >= 16
- Python >= 3.8
- Electron >= 28
- OpenAI API Key
```

### Install Dependencies

```bash
npm install
pip install -r requirements.txt
```

### Configuration

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Enter your API key in the app (it's securely saved)
3. Select source and output folders
4. Choose target languages and translation model

## Error Messages & Solutions

### API Errors

#### "Rate Limit Exceeded (429)"

- **Cause**: Too many API requests too quickly
- **Solution**: Automatic retry with exponential backoff
- **User Action**: Wait for retries to complete

#### "Authentication Failed"

- **Cause**: Invalid API key
- **Solution**: Check and re-enter your API key
- **User Action**: Get a new API key from OpenAI dashboard

#### "Service Temporarily Unavailable (503)"

- **Cause**: OpenAI API is down
- **Solution**: Automatic retry with exponential backoff
- **User Action**: Wait and retry later

### File Errors

#### "File not found"

- **Cause**: SRT file was deleted or moved
- **Solution**: None (non-retryable)
- **User Action**: Verify source files exist

#### "Cannot parse SRT file"

- **Cause**: Corrupted or invalid SRT format
- **Solution**: None (non-retryable)
- **User Action**: Verify SRT file format

#### "Cannot write output file"

- **Cause**: Permission denied or disk full
- **Solution**: None (non-retryable)
- **User Action**: Check folder permissions and disk space

### Validation Errors

#### "Block count mismatch"

- **Cause**: Translation lost or added blocks
- **Solution**: Retranslate the file
- **User Action**: Click "Retranslate Failed Files"

#### "Timestamp mismatch"

- **Cause**: Translation modified timestamps
- **Solution**: Retranslate the file
- **User Action**: Click "Retranslate Failed Files"

## Running the App

### Development Mode

```bash
npm run dev
```

Opens DevTools automatically for debugging.

### Production Mode

```bash
npm start
```

### Building

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

## Testing

Run the comprehensive test suite:

```bash
python python/test_suite.py
```

Expected output:

```
============================================================
TEST RESULTS: 7/7 tests passed
============================================================
✅ All tests passed! App is ready for production.
```

## Debugging

### Error Logs

Check `logs/translation_errors.log` for detailed error records:

```json
{
  "error_type": "api_error",
  "severity": "error",
  "filename": "drama_episode_01.srt",
  "language": "Hinglish",
  "message": "HTTP 429 Rate Limit Exceeded",
  "retry_count": 2,
  "timestamp": "2024-01-20T10:30:45.123456"
}
```

### Console Output

In development mode, check the DevTools console for:

- IPC message logs
- Python process stdout/stderr
- React component state changes

### File Locations

- **Settings**: `~/.config/Subtitle Translator/settings.json` (Linux/Mac) or `AppData/Local/Subtitle Translator/settings.json` (Windows)
- **Error Logs**: `python/logs/translation_errors.log`
- **Temp Files**: System temp directory

## Architecture

### Electron Process (main.js)

- Handles IPC communication with React frontend
- Spawns Python subprocess for translation
- Manages file dialogs and OS interactions
- Streams progress/status/error messages from Python

### React Frontend (app.js)

- Manages UI state and user interactions
- Displays progress, status, and error information
- Handles retranslation workflows
- Manages language and model selection

### Python Backend (translator_bridge.py)

- Orchestrates translation workflow
- Handles parallel processing
- Manages OpenAI API communication
- Streams progress updates via stdout

### Error Handler (error_handler.py)

- Centralized error logging and tracking
- Error categorization and severity levels
- Retry strategy logic
- JSON serialization for IPC

### Translator (translator.py)

- Core translation logic using OpenAI API
- Language-specific prompts and settings
- Token-based cost estimation

### Validation (validation_utils.py)

- Post-translation validation
- Block count and timestamp checks
- Quality assurance

## API Usage & Costs

### Token Estimation

The app accurately estimates token usage based on:

- File size and content
- Model-specific tokenization
- Batch processing overhead
- 5% overhead for retries/edge cases

### Cost Calculation

Real-time cost shown in INR and USD:

- **Input tokens**: ~$0.00015 per 1K tokens (gpt-4o-mini)
- **Output tokens**: ~$0.0006 per 1K tokens (gpt-4o-mini)
- Prices vary by model

### Cost Optimization

- Use `gpt-4o-mini` for cost-effective translations
- Use `gpt-4o` or `gpt-5` for higher quality
- Parallel processing doesn't increase token cost
- Token count estimated before translation begins

## Languages Supported

1. **Hinglish** (Hindi + English) - 🇮🇳
2. **Taglish** (Tagalog + English) - 🇵🇭
3. **Vietnamese** (Tiếng Việt) - 🇻🇳
4. **Thai** (ภาษาไทย) - 🇹🇭
5. **Malay** (Bahasa Melayu) - 🇲🇾
6. **Spanish** (Español) - 🇪🇸
7. **Indonesian** (Bahasa Indonesia) - 🇮🇩

## Performance

### Benchmarks

- **Parse SRT**: < 100ms for standard files
- **Translate 100 blocks**: ~2-5 seconds per language
- **Validate**: < 500ms per file
- **Parallel Translation**: ~50% faster with parallel-files enabled

### Optimization Tips

1. Use parallel-files for multiple SRT files
2. Use parallel-languages for all target languages
3. Use gpt-4o-mini for faster translations
4. Enable both options for maximum speed

## Troubleshooting

### App Won't Start

1. Verify Node.js is installed: `node --version`
2. Verify Python is installed: `python --version`
3. Clear npm cache: `npm cache clean --force`
4. Reinstall dependencies: `npm install && pip install -r requirements.txt`

### Translation Takes Too Long

1. Check internet connection
2. Check API quota at https://platform.openai.com/usage
3. Try again later (API might be overloaded)
4. Use fewer languages or smaller files

### Validation Always Fails

1. Check SRT file format is valid
2. Verify timestamps haven't been modified
3. Check for empty translation blocks
4. Retranslate the file

### Can't Find Error Log

1. Check `python/logs/translation_errors.log`
2. Create logs directory if missing: `mkdir logs`
3. Check file permissions

## Best Practices

### Before Translation

✅ Verify SRT files are valid (use a subtitle editor)
✅ Back up original files
✅ Have sufficient API credit
✅ Test with one file first

### During Translation

✅ Keep app window in focus
✅ Don't close the app
✅ Monitor status messages
✅ Note any error messages

### After Translation

✅ Review translations manually
✅ Check for formatting issues
✅ Validate audio sync is correct
✅ Save final translations

## Contributing & Support

For issues, feature requests, or questions:

1. Check error logs for detailed context
2. Try running the test suite
3. Review error messages in UI
4. Check this documentation

## License

MIT License - See LICENSE file for details

## Credits

Built by Robinson Minj
Designed for Japanese drama enthusiasts

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Status**: Production Ready ✅
