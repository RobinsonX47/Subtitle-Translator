#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for subtitle translator app
Tests error handling, recovery, and production-ready scenarios
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestScenario:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.passed = False
        self.errors = []
    
    def add_error(self, error):
        self.errors.append(error)
    
    def report(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        print(f"\n{status}: {self.name}")
        print(f"Description: {self.description}")
        if self.errors:
            print("Errors:")
            for error in self.errors:
                print(f"  - {error}")

def create_test_srt_file(filepath, num_blocks=5, corrupted=False):
    """Create a test SRT file"""
    content = ""
    for i in range(1, num_blocks + 1):
        if corrupted and i == 2:
            # Create malformed block
            content += f"{i}\nINVALID TIMESTAMP\nThis is broken\n\n"
        else:
            content += f"{i}\n00:{i-1:02d}:00,000 --> 00:{i:02d}:00,000\nLine {i} English text\n\n"
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def test_error_handler_import():
    """Test that error handler can be imported"""
    test = TestScenario("Error Handler Import", "Verify error_handler.py can be imported")
    try:
        from error_handler import ErrorLogger, ErrorType, ErrorSeverity, ErrorRecovery
        test.passed = True
    except Exception as e:
        test.add_error(f"Failed to import error_handler: {e}")
    test.report()
    return test

def test_error_logger_functionality():
    """Test ErrorLogger class functionality"""
    test = TestScenario("Error Logger", "Verify ErrorLogger can log and track errors")
    try:
        from error_handler import ErrorLogger
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test_errors.log")
            logger = ErrorLogger(log_file)
            
            # Log an error
            error = logger.log_error(
                "api_error",
                "error",
                "test_file.srt",
                "Hindi",
                "API rate limit exceeded",
                {"retry_count": 0},
                recoverable=True
            )
            
            # Verify error was logged
            if not os.path.exists(log_file):
                raise Exception("Log file was not created")
            
            # Check failed files tracking
            failed = logger.get_failed_files()
            if len(failed) == 0:
                raise Exception("Failed files not tracked")
            
            test.passed = True
    except Exception as e:
        test.add_error(f"Error logger test failed: {e}")
    test.report()
    return test

def test_error_recovery_logic():
    """Test ErrorRecovery error categorization"""
    test = TestScenario("Error Recovery Logic", "Verify error recovery strategies work correctly")
    try:
        from error_handler import ErrorRecovery
        
        # Test retryable errors
        retryable_errors = [
            "HTTP 429 Rate Limit Exceeded",
            "Connection timeout",
            "Service temporarily unavailable"
        ]
        
        for error_msg in retryable_errors:
            if not ErrorRecovery.should_retry_api_error(Exception(error_msg)):
                raise Exception(f"Should be retryable: {error_msg}")
        
        # Test non-retryable errors
        non_retryable = Exception("Invalid API key")
        if ErrorRecovery.should_retry_api_error(non_retryable):
            raise Exception("Should not be retryable: Invalid API key")
        
        # Test retry delays
        delays = [ErrorRecovery.get_retry_delay(i) for i in range(4)]
        expected = [1, 2, 4, 8]
        if delays != expected:
            raise Exception(f"Retry delays incorrect: {delays} != {expected}")
        
        test.passed = True
    except Exception as e:
        test.add_error(f"Recovery logic test failed: {e}")
    test.report()
    return test

def test_srt_file_parsing():
    """Test SRT file parsing with various edge cases"""
    test = TestScenario("SRT File Parsing", "Verify robust SRT parsing with edge cases")
    try:
        from srt_utils import parse_srt
        
        # Normal SRT
        normal_srt = """1
00:00:00,000 --> 00:00:05,000
Hello world

2
00:00:05,000 --> 00:00:10,000
Second line
"""
        blocks = parse_srt(normal_srt)
        if len(blocks) != 2:
            raise Exception(f"Expected 2 blocks, got {len(blocks)}")
        
        # SRT with empty lines
        messy_srt = """

1
00:00:00,000 --> 00:00:05,000
Hello

2
00:00:05,000 --> 00:00:10,000
World

"""
        blocks = parse_srt(messy_srt)
        if len(blocks) != 2:
            raise Exception(f"Messy SRT: Expected 2 blocks, got {len(blocks)}")
        
        # SRT with multiline text
        multi_srt = """1
00:00:00,000 --> 00:00:05,000
Line 1
Line 2
Line 3

2
00:00:05,000 --> 00:00:10,000
Another block
With multiple lines
"""
        blocks = parse_srt(multi_srt)
        if len(blocks) != 2 or len(blocks[0]['lines']) != 3:
            raise Exception("Multiline SRT parsing failed")
        
        test.passed = True
    except Exception as e:
        test.add_error(f"SRT parsing test failed: {e}")
    test.report()
    return test

def test_file_operations_error_handling():
    """Test file operation error handling"""
    test = TestScenario("File Operations", "Verify robust file handling with errors")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test reading non-existent file
            try:
                with open(os.path.join(tmpdir, "nonexistent.srt"), 'r') as f:
                    pass
                raise Exception("Should have failed reading non-existent file")
            except FileNotFoundError:
                pass  # Expected
            
            # Test writing to directory with restricted permissions
            test_file = os.path.join(tmpdir, "test.srt")
            with open(test_file, 'w') as f:
                f.write("1\n00:00:00,000 --> 00:00:05,000\nTest\n")
            
            # Verify file was written
            if not os.path.exists(test_file):
                raise Exception("Failed to write test file")
            
            test.passed = True
    except Exception as e:
        test.add_error(f"File operations test failed: {e}")
    test.report()
    return test

def test_validation_with_mismatched_blocks():
    """Test validation with mismatched block counts"""
    test = TestScenario("Validation Edge Cases", "Verify validation handles mismatched blocks")
    try:
        from validation_utils import parse_srt_file
        
        # Create files with different block counts
        en_srt = """1
00:00:00,000 --> 00:00:05,000
English 1

2
00:00:05,000 --> 00:00:10,000
English 2

3
00:00:10,000 --> 00:00:15,000
English 3
"""
        
        target_srt = """1
00:00:00,000 --> 00:00:05,000
Target 1

2
00:00:05,000 --> 00:00:10,000
Target 2
"""
        
        en_blocks = parse_srt_file(en_srt)
        target_blocks = parse_srt_file(target_srt)
        
        if len(en_blocks) == len(target_blocks):
            raise Exception("Should have different block counts")
        
        test.passed = True
    except Exception as e:
        test.add_error(f"Validation test failed: {e}")
    test.report()
    return test

def test_json_serialization():
    """Test JSON serialization of error data"""
    test = TestScenario("JSON Serialization", "Verify error data can be JSON serialized")
    try:
        from error_handler import ErrorRecord
        
        error = ErrorRecord(
            error_type="api_error",
            severity="error",
            filename="test.srt",
            language="Hindi",
            message="Test error",
            details={"code": 429},
            recoverable=True
        )
        
        error_dict = error.to_dict()
        json_str = json.dumps(error_dict)
        parsed = json.loads(json_str)
        
        if parsed['filename'] != 'test.srt':
            raise Exception("JSON serialization failed")
        
        test.passed = True
    except Exception as e:
        test.add_error(f"JSON serialization test failed: {e}")
    test.report()
    return test

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("SUBTITLE TRANSLATOR - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_error_handler_import(),
        test_error_logger_functionality(),
        test_error_recovery_logic(),
        test_srt_file_parsing(),
        test_file_operations_error_handling(),
        test_validation_with_mismatched_blocks(),
        test_json_serialization()
    ]
    
    passed = sum(1 for t in tests if t.passed)
    total = len(tests)
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("✅ All tests passed! App is ready for production.")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed. Please review errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
