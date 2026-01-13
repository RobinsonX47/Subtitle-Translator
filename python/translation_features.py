#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced translation features: caching, glossary, context-aware translation
"""

import json
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import os

@dataclass
class CacheEntry:
    """Represents a cached translation"""
    source_text: str
    source_hash: str
    target_text: str
    language: str
    model: str

class TranslationCache:
    """Manages translation caching to avoid re-translating identical content"""
    
    def __init__(self, cache_file: Optional[str] = None):
        self.cache: Dict[str, str] = {}
        self.cache_file = cache_file or os.path.expanduser('~/.subtitle-translator/cache.json')
        self.load_cache()
    
    def _hash_text(self, text: str) -> str:
        """Generate hash for source text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _make_key(self, source_text: str, language: str, model: str) -> str:
        """Create cache key from source text, language, and model"""
        text_hash = self._hash_text(source_text)
        return f"{language}:{model}:{text_hash}"
    
    def get(self, source_text: str, language: str, model: str) -> Optional[str]:
        """Get cached translation if available"""
        key = self._make_key(source_text, language, model)
        return self.cache.get(key)
    
    def set(self, source_text: str, target_text: str, language: str, model: str) -> None:
        """Store translation in cache"""
        key = self._make_key(source_text, language, model)
        self.cache[key] = target_text
    
    def load_cache(self) -> None:
        """Load cache from file"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")
            self.cache = {}
    
    def save_cache(self) -> None:
        """Save cache to file"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")


class GlossaryManager:
    """Manages terminology database for consistent translations"""
    
    def __init__(self, glossary_data: List[Dict] = None):
        """Initialize glossary with provided terms"""
        self.terms: Dict[str, str] = {}
        if glossary_data:
            for term in glossary_data:
                self.add_term(term.get('source', ''), term.get('target', ''))
    
    def add_term(self, source: str, target: str) -> None:
        """Add a term to the glossary"""
        if source and target:
            self.terms[source.lower()] = target
    
    def get_term(self, source: str) -> Optional[str]:
        """Get translation for a term"""
        return self.terms.get(source.lower())
    
    def apply_to_text(self, text: str) -> str:
        """Apply glossary terms to text"""
        result = text
        for source, target in self.terms.items():
            # Case-insensitive replacement with word boundaries
            import re
            pattern = r'\b' + re.escape(source) + r'\b'
            result = re.sub(pattern, target, result, flags=re.IGNORECASE)
        return result
    
    def get_context_string(self) -> str:
        """Generate context string for AI to consider glossary"""
        if not self.terms:
            return ""
        
        terms_list = [f"'{k}' → '{v}'" for k, v in list(self.terms.items())[:20]]
        return f"Important terminology to maintain consistency: {', '.join(terms_list)}"


class ContextAwareTranslator:
    """Enhances translations with user-provided context"""
    
    def __init__(self, context_instructions: str = ""):
        self.context = context_instructions.strip()
    
    def get_enhanced_prompt(self, original_prompt: str, language: str) -> str:
        """Enhance the translation prompt with context"""
        if not self.context:
            return original_prompt
        
        enhancement = f"\n\nContext/Style Guide: {self.context}"
        return original_prompt + enhancement
    
    def get_system_message(self) -> str:
        """Get enhanced system message"""
        base_message = "You are a professional subtitle translator."
        
        if self.context:
            return f"{base_message} {self.context}"
        
        return base_message


class ParallelTranslationManager:
    """Manages parallel/concurrent translation processing"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.completed = 0
        self.total = 0
    
    def get_batch_size(self, total_items: int) -> int:
        """Determine optimal batch size for parallel processing"""
        return max(1, total_items // self.max_workers)
    
    def should_use_parallel(self, total_items: int) -> bool:
        """Check if parallel processing is beneficial"""
        return total_items > self.max_workers


def optimize_translation_order(blocks: List[Dict]) -> List[Dict]:
    """Reorder blocks for optimal parallel processing"""
    # Group by similarity to batch similar translations
    # This improves model efficiency through prompt caching
    sorted_blocks = sorted(blocks, key=lambda x: len(x.get('text', '')))
    return sorted_blocks


def merge_glossary_and_context(glossary: Optional[GlossaryManager], 
                               context: Optional[ContextAwareTranslator]) -> str:
    """Merge glossary and context into a single prompt enhancement"""
    enhancements = []
    
    if glossary and glossary.terms:
        enhancements.append(glossary.get_context_string())
    
    if context and context.context:
        enhancements.append(f"Additional Instructions: {context.context}")
    
    return "\n".join(enhancements)
