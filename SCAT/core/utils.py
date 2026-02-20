"""
Utility functions for the Code Analysis Tool.

This module provides common utility functions used throughout the application
for file operations, language detection, and other helper functions.
"""

import re
from pathlib import Path
from typing import Optional, Dict, List


# Language detection mappings
EXTENSION_TO_LANGUAGE = {
    '.py': 'python',
    '.pyw': 'python',
    '.rb': 'ruby',
    '.rbw': 'ruby',
    '.lua': 'lua',
    '.plain': 'plain',
    '.bas': 'basic',
    '.basic': 'basic',
    '.pseudo': 'pseudocode',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.cxx': 'cpp',
    '.cc': 'cpp',
    '.c': 'c',
    '.h': 'c',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.r': 'r',
    '.R': 'r',
    '.step': 'steps',
    '.building': 'steps',
    '.floor': 'steps'
}

# Language detection patterns for content analysis
LANGUAGE_PATTERNS = {
    'python': [
        r'^\s*def\s+\w+\s*\(',
        r'^\s*class\s+\w+\s*\(',
        r'^\s*import\s+\w+',
        r'^\s*from\s+\w+\s+import',
        r'if\s+__name__\s*==\s*["\']__main__["\']',
        r'^\s*#.*python',
    ],
    'ruby': [
        r'^\s*def\s+\w+',
        r'^\s*class\s+\w+',
        r'^\s*module\s+\w+',
        r'^\s*require\s+["\']',
        r'^\s*puts\s+',
        r'\.each\s+do\s*\|',
        r'end\s*$',
    ],
    'lua': [
        r'^\s*function\s+\w+\s*\(',
        r'^\s*local\s+\w+\s*=',
        r'^\s*require\s*\(',
        r'--.*lua',
        r'\.lua\s*$',
        r'^\s*if\s+.*\s+then',
        r'^\s*for\s+.*\s+do',
    ],
    'plain': [
        r'^\s*task\s+\w+',
        r'^\s*rem:',
        r'^\s*note:',
        r'^\s*loop\s+\w+\s+from',
        r'^\s*loop\s+\w+\s+in',
        r'^\s*deliver\s+',
        r'^\s*var\s+\w+',
        r'^\s*fxd\s+\w+',
        r'^\s*display\s*\(',
        r'^\s*record\s+\w+:',
    ],
    'basic': [
        r'^\s*\d+\s+',  # Line numbers
        r'^\s*PRINT\s+',
        r'^\s*INPUT\s+',
        r'^\s*GOTO\s+',
        r'^\s*GOSUB\s+',
        r'^\s*FOR\s+.*\s+TO\s+',
        r'^\s*NEXT\s+',
    ],
    'pseudocode': [
        r'^\s*BEGIN\s*$',
        r'^\s*END\s*$',
        r'^\s*ALGORITHM\s+',
        r'^\s*PROCEDURE\s+',
        r'^\s*FUNCTION\s+',
        r'^\s*INPUT\s+',
        r'^\s*OUTPUT\s+',
    ],
    'javascript': [
        r'^\s*function\s+\w+\s*\(',
        r'^\s*const\s+\w+\s*=',
        r'^\s*let\s+\w+\s*=',
        r'^\s*var\s+\w+\s*=',
        r'console\.log\s*\(',
        r'document\.',
        r'window\.',
    ],
    'steps': [
        r'^\s*building:',
        r'^\s*floor:',
        r'^\s*step:\s+\w+',
        r'^\s*riser:\s+\w+',
        r'^\s*belongs\s+to:',
        r'^\s*set\s+\w+\s+to\b',
        r'^\s*call\s+\w+',
        r'^\s*display\b',
        r'^\s*repeat\s+\d+\s+times',
        r'^\s*repeat\s+for\s+each\b',
        r'^\s*storing\s+result\s+in\b',
        r'^\s*note:',
    ]
}


def detect_language_from_extension(file_path: str) -> Optional[str]:
    """
    Detect programming language from file extension.

    Args:
        file_path: Path to the file

    Returns:
        Detected language name or None if not recognized
    """
    if not file_path:
        return None

    path = Path(file_path)
    extension = path.suffix.lower()

    return EXTENSION_TO_LANGUAGE.get(extension)


def detect_language_from_content(code: str) -> Optional[str]:
    """
    Detect programming language from code content using pattern matching.

    Args:
        code: Source code content

    Returns:
        Detected language name or None if not recognized
    """
    if not code or not code.strip():
        return None

    # Score each language based on pattern matches
    language_scores = {}

    for language, patterns in LANGUAGE_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
            score += matches

        if score > 0:
            language_scores[language] = score

    # Return language with highest score
    if language_scores:
        return max(language_scores, key=language_scores.get)

    return None


def normalize_language_name(language: str) -> str:
    """
    Normalize language name to standard format.

    Args:
        language: Language name in any case

    Returns:
        Normalized language name in lowercase
    """
    if not language:
        return 'unknown'

    # Handle common variations
    language = language.lower().strip()

    language_aliases = {
        'py': 'python',
        'rb': 'ruby',
        'js': 'javascript',
        'ts': 'typescript',
        'cpp': 'cpp',
        'c++': 'cpp',
        'cxx': 'cpp',
        'cc': 'cpp',
        'cs': 'csharp',
        'c#': 'csharp',
    }

    return language_aliases.get(language, language)


def get_file_info(file_path: str) -> Dict[str, any]:
    """
    Get information about a code file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return {'error': 'File does not exist'}

        if not path.is_file():
            return {'error': 'Path is not a file'}

        # Get basic file info
        stat = path.stat()

        # Try to read content for analysis
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]

            return {
                'path': str(path.absolute()),
                'name': path.name,
                'extension': path.suffix,
                'size_bytes': stat.st_size,
                'total_lines': len(lines),
                'non_empty_lines': len(non_empty_lines),
                'detected_language': detect_language_from_extension(str(path)) or
                                   detect_language_from_content(content),
                'encoding': 'utf-8',
                'readable': True
            }

        except UnicodeDecodeError:
            return {
                'path': str(path.absolute()),
                'name': path.name,
                'extension': path.suffix,
                'size_bytes': stat.st_size,
                'encoding': 'unknown',
                'readable': False,
                'error': 'Unable to decode file as UTF-8'
            }

    except Exception as e:
        return {'error': f'Error reading file: {str(e)}'}


def validate_code_content(code: str) -> Dict[str, any]:
    """
    Validate code content for analysis.

    Args:
        code: Source code content

    Returns:
        Dictionary with validation results
    """
    if not code:
        return {
            'valid': False,
            'error': 'Code content is empty',
            'warnings': []
        }

    warnings = []

    # Check for very long lines
    lines = code.splitlines()
    long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 120]
    if long_lines:
        warnings.append(f'Lines longer than 120 characters: {long_lines[:5]}')

    # Check for very large files
    if len(lines) > 10000:
        warnings.append(f'Large file with {len(lines)} lines may take longer to analyze')

    # Check for binary content
    if '\x00' in code:
        return {
            'valid': False,
            'error': 'Content appears to be binary',
            'warnings': warnings
        }

    return {
        'valid': True,
        'line_count': len(lines),
        'character_count': len(code),
        'warnings': warnings
    }


def format_complexity(complexity: str) -> str:
    """
    Format complexity string for display.

    Args:
        complexity: Raw complexity string

    Returns:
        Formatted complexity string
    """
    if not complexity:
        return 'Unknown'

    # Handle special characters
    complexity = complexity.replace('²', '²').replace('³', '³').replace('ⁿ', 'ⁿ')

    return complexity


def calculate_quality_score(time_complexity: str, space_complexity: str,
                          warnings_count: int, suggestions_count: int) -> float:
    """
    Calculate overall quality score based on analysis results.

    Args:
        time_complexity: Time complexity string
        space_complexity: Space complexity string
        warnings_count: Number of warnings
        suggestions_count: Number of suggestions

    Returns:
        Quality score from 0.0 to 100.0
    """
    base_score = 100.0

    # More reasonable complexity penalties (reduced)
    complexity_penalties = {
        'O(1)': 0,
        'O(log n)': 2,
        'O(n)': 5,
        'O(n log n)': 10,
        'O(n²)': 20,
        'O(n³)': 30,
        'O(n^2)': 20,  # Alternative notation
        'O(n^3)': 30,  # Alternative notation
        'O(2ⁿ)': 40,
        'O(2^n)': 40,  # Alternative notation
        'O(n!)': 50
    }

    # Get penalties with pattern matching for unknown complexities
    time_penalty = complexity_penalties.get(time_complexity, 0)
    if time_penalty == 0 and time_complexity not in complexity_penalties:
        # Pattern matching for unknown complexities
        complexity_lower = time_complexity.lower()
        if 'n^3' in complexity_lower or 'n³' in complexity_lower:
            time_penalty = 30
        elif 'n^2' in complexity_lower or 'n²' in complexity_lower:
            time_penalty = 20
        elif '^n' in complexity_lower or 'ⁿ' in complexity_lower:
            time_penalty = 40
        elif '!' in complexity_lower:
            time_penalty = 50
        elif 'log' in complexity_lower:
            time_penalty = 2
        elif 'n' in complexity_lower:
            time_penalty = 5

    space_penalty = complexity_penalties.get(space_complexity, 0) * 0.3  # Reduced weight

    # Reduced warning and suggestion penalties
    warning_penalty = min(warnings_count * 2, 20)  # Cap at 20 points
    suggestion_penalty = min(suggestions_count * 1, 15)  # Cap at 15 points

    final_score = base_score - time_penalty - space_penalty - warning_penalty - suggestion_penalty

    return max(5.0, min(100.0, final_score))  # Minimum score of 5.0
