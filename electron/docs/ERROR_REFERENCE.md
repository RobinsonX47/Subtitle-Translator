# Error Reference Guide

## Error Categories

### 1. API Errors (api_error)

**When it occurs**: During translation API calls to OpenAI

| Error                     | Status  | Retryable | Solution                                       |
| ------------------------- | ------- | --------- | ---------------------------------------------- |
| Rate Limit (429)          | Warning | ✅ Yes    | Wait for automatic retry (exponential backoff) |
| Authentication (401)      | Error   | ❌ No     | Verify API key in settings                     |
| Service Unavailable (503) | Warning | ✅ Yes    | Wait for automatic retry                       |
| Connection Timeout        | Warning | ✅ Yes    | Check internet connection, retry               |
| Invalid Request           | Error   | ❌ No     | Check prompt/parameters, retranslate           |

**Example Log Entry**:

```json
{
  "error_type": "api_error",
  "severity": "warning",
  "filename": "episode_01.srt",
  "language": "Hinglish",
  "message": "HTTP 429 Rate Limit Exceeded",
  "details": { "retry_count": 1, "error": "..." },
  "recoverable": true,
  "timestamp": "2024-01-20T10:30:45.123456"
}
```

### 2. File Read Errors (file_read_error)

**When it occurs**: Cannot open or read SRT file

| Error             | Cause                      | Retryable | Solution                                |
| ----------------- | -------------------------- | --------- | --------------------------------------- |
| File not found    | File deleted/moved         | ❌ No     | Verify source folder, check file exists |
| Permission denied | No read access             | ❌ No     | Check folder permissions                |
| Encoding error    | Invalid character encoding | ❌ No     | Re-save file as UTF-8                   |
| File is empty     | No content                 | ❌ No     | Verify SRT file has content             |

**Example Log Entry**:

```json
{
  "error_type": "file_read_error",
  "severity": "error",
  "filename": "missing.srt",
  "language": null,
  "message": "File not found",
  "recoverable": false,
  "timestamp": "2024-01-20T10:30:46.000000"
}
```

### 3. File Write Errors (file_write_error)

**When it occurs**: Cannot save translated SRT file

| Error             | Cause              | Retryable | Solution                                       |
| ----------------- | ------------------ | --------- | ---------------------------------------------- |
| Permission denied | No write access    | ❌ No     | Check folder permissions, use different folder |
| Disk full         | No space available | ❌ No     | Free up disk space, use different location     |
| Path too long     | Path exceeds limit | ❌ No     | Move to folder with shorter path               |
| Invalid filename  | Special characters | ❌ No     | Use valid filename                             |

**Example Log Entry**:

```json
{
  "error_type": "file_write_error",
  "severity": "error",
  "filename": "episode_01_HINDI.srt",
  "language": "Hinglish",
  "message": "Permission denied: No write access to output folder",
  "recoverable": false,
  "timestamp": "2024-01-20T10:30:47.000000"
}
```

### 4. Parsing Errors (parsing_error)

**When it occurs**: SRT file format is invalid

| Error             | Cause              | Retryable | Solution                            |
| ----------------- | ------------------ | --------- | ----------------------------------- |
| No blocks found   | Empty file         | ❌ No     | Verify SRT file has content         |
| Invalid timestamp | Malformed timing   | ❌ No     | Fix timestamp format (HH:MM:SS,mmm) |
| Corrupt blocks    | Missing separators | ❌ No     | Re-save file in valid SRT format    |

**Example Log Entry**:

```json
{
  "error_type": "parsing_error",
  "severity": "error",
  "filename": "corrupted.srt",
  "language": null,
  "message": "Failed to parse/parse file: No subtitle blocks found",
  "recoverable": true,
  "timestamp": "2024-01-20T10:30:48.000000"
}
```

### 5. Translation Errors (translation_error)

**When it occurs**: Translation API returned error

| Error             | Cause                | Retryable | Solution                              |
| ----------------- | -------------------- | --------- | ------------------------------------- |
| API rate limit    | Too many requests    | ✅ Yes    | Wait for automatic retry              |
| API timeout       | Request too slow     | ✅ Yes    | Check internet, retry                 |
| Invalid response  | Unexpected format    | ✅ Yes    | Retranslate file                      |
| Model unavailable | Model not accessible | ❌ No     | Use different model, check API status |

**Example Log Entry**:

```json
{
  "error_type": "translation_error",
  "severity": "error",
  "filename": "episode_02.srt",
  "language": "Taglish",
  "message": "Translation failed: API timeout after 30 seconds",
  "details": { "retry_count": 0, "error": "..." },
  "recoverable": true,
  "timestamp": "2024-01-20T10:30:49.000000"
}
```

### 6. Validation Errors (validation_error)

**When it occurs**: Post-translation validation fails

| Error                | Cause                    | Retryable | Solution         |
| -------------------- | ------------------------ | --------- | ---------------- |
| Block count mismatch | Translation lost blocks  | ✅ Yes    | Retranslate file |
| Timestamp mismatch   | Timestamps were modified | ✅ Yes    | Retranslate file |
| Empty blocks         | Missing translation      | ✅ Yes    | Retranslate file |
| Format issues        | Malformed output         | ✅ Yes    | Retranslate file |

**Example Log Entry**:

```json
{
  "error_type": "validation_error",
  "severity": "error",
  "filename": "episode_03_HINDI.srt",
  "language": "Hinglish",
  "message": "Block count mismatch: Expected 150 blocks, got 148",
  "recoverable": true,
  "timestamp": "2024-01-20T10:30:50.000000"
}
```

### 7. Timeout Errors (timeout_error)

**When it occurs**: Request takes too long

| Error                   | Cause         | Retryable | Solution                |
| ----------------------- | ------------- | --------- | ----------------------- |
| API timeout             | Slow response | ✅ Yes    | Check internet, retry   |
| File processing timeout | Large file    | ✅ Yes    | Try smaller file, retry |

**Example Log Entry**:

```json
{
  "error_type": "timeout_error",
  "severity": "warning",
  "filename": "large_file.srt",
  "language": "Spanish",
  "message": "Request timed out after 60 seconds",
  "recoverable": true,
  "timestamp": "2024-01-20T10:30:51.000000"
}
```

### 8. Rate Limit Errors (rate_limit_error)

**When it occurs**: OpenAI API rate limit exceeded

| Error             | Cause                | Retryable | Solution                                |
| ----------------- | -------------------- | --------- | --------------------------------------- |
| Too many requests | Quota exceeded       | ✅ Yes    | Wait for retry or purchase more credits |
| Per-minute limit  | Request too frequent | ✅ Yes    | Automatic backoff retry                 |

**Example Log Entry**:

```json
{
  "error_type": "rate_limit_error",
  "severity": "warning",
  "filename": "episode_04.srt",
  "language": "Vietnamese",
  "message": "Rate limited by OpenAI API",
  "details": { "retry_count": 0 },
  "recoverable": true,
  "timestamp": "2024-01-20T10:30:52.000000"
}
```

### 9. Authentication Errors (authentication_error)

**When it occurs**: API key is invalid

| Error           | Cause               | Retryable | Solution                    |
| --------------- | ------------------- | --------- | --------------------------- |
| Invalid API key | Wrong key           | ❌ No     | Get new API key from OpenAI |
| Expired key     | Key no longer valid | ❌ No     | Generate new API key        |
| No quota        | No API credits      | ❌ No     | Purchase API credits        |

**Example Log Entry**:

```json
{
  "error_type": "authentication_error",
  "severity": "error",
  "filename": "episode_05.srt",
  "language": null,
  "message": "Authentication failed: Invalid API key",
  "recoverable": false,
  "timestamp": "2024-01-20T10:30:53.000000"
}
```

### 10. Unknown Errors (unknown_error)

**When it occurs**: Unexpected error occurred

| Error            | Cause         | Retryable | Solution                         |
| ---------------- | ------------- | --------- | -------------------------------- |
| Unexpected error | Unknown cause | ❌ No     | Check error message, restart app |

**Example Log Entry**:

```json
{
  "error_type": "unknown_error",
  "severity": "error",
  "filename": "unknown",
  "language": null,
  "message": "Unexpected error: <error details>",
  "recoverable": false,
  "timestamp": "2024-01-20T10:30:54.000000"
}
```

## Severity Levels

| Severity     | Meaning               | Action                      |
| ------------ | --------------------- | --------------------------- |
| **info**     | Informational message | No action required          |
| **warning**  | Non-critical issue    | Monitor, may need attention |
| **error**    | Failed operation      | User action required        |
| **critical** | System failure        | Stop and fix immediately    |

## Retry Strategy

### Automatic Retries

Retryable errors automatically retry with exponential backoff:

```
Retry 1: After 1 second
Retry 2: After 2 seconds
Retry 3: After 4 seconds
Retry 4: After 8 seconds (max 60 seconds)
```

### Manual Retranslation

For failed files, use the "Retranslate Failed Files" button:

1. Click button after translation completes
2. App retranslates all failed files
3. Re-validates translated files
4. Shows updated results

## Error Log Format

Each error is logged as JSON for easy parsing:

```json
{
  "error_type": "string",        // Error category
  "severity": "string",          // info|warning|error|critical
  "filename": "string",          // File that failed
  "language": "string|null",     // Target language
  "message": "string",           // Error description
  "details": {object},           // Additional context
  "timestamp": "ISO8601",        // When it occurred
  "recoverable": boolean,        // Can retry?
  "retry_count": integer         // Number of retries
}
```

## Accessing Error Logs

### File Location

```
Linux/Mac:   python/logs/translation_errors.log
Windows:     python/logs/translation_errors.log
```

### View Logs

```bash
# Show all errors
cat python/logs/translation_errors.log

# Show recent errors
tail -20 python/logs/translation_errors.log

# Pretty print errors
python -m json.tool python/logs/translation_errors.log | less
```

### Parse Errors

```python
import json

with open('python/logs/translation_errors.log', 'r') as f:
    for line in f:
        error = json.loads(line)
        print(f"{error['timestamp']}: {error['message']}")
```

## Debugging Workflow

1. **Identify Error**: Check UI error display
2. **Read Message**: Understand what went wrong
3. **Check Logs**: Get detailed context from error log
4. **Take Action**: Follow solution from this guide
5. **Retry**: Use automatic or manual retry
6. **Verify**: Check validation results
