"""
Ruby language analyzer for the Code Analysis Tool.

This module provides Ruby-specific code complexity analysis using
regular expressions and pattern matching for parsing and analysis.
"""

import re
from typing import List, Any, Dict, Tuple

from .base import BaseLanguageAnalyzer
from core.models import ComplexityResult


class RubyAnalyzer(BaseLanguageAnalyzer):
    """
    Ruby-specific code complexity analyzer.
    
    This analyzer uses regular expressions and pattern matching to analyze Ruby code
    for complexity patterns including loops, recursion, built-in methods,
    data structures, and iterators.
    """
    
    def __init__(self, config):
        """Initialize the Ruby analyzer."""
        super().__init__(config)
        
        # Ruby built-in method complexities
        self.builtin_complexities = {
            'sort': {'time': 'O(n log n)', 'space': 'O(n)'},
            'sort!': {'time': 'O(n log n)', 'space': 'O(1)'},
            'max': {'time': 'O(n)', 'space': 'O(1)'},
            'min': {'time': 'O(n)', 'space': 'O(1)'},
            'sum': {'time': 'O(n)', 'space': 'O(1)'},
            'length': {'time': 'O(1)', 'space': 'O(1)'},
            'size': {'time': 'O(1)', 'space': 'O(1)'},
            'count': {'time': 'O(n)', 'space': 'O(1)'},
            'each': {'time': 'O(n)', 'space': 'O(1)'},
            'map': {'time': 'O(n)', 'space': 'O(n)'},
            'select': {'time': 'O(n)', 'space': 'O(n)'},
            'reject': {'time': 'O(n)', 'space': 'O(n)'},
            'find': {'time': 'O(n)', 'space': 'O(1)'},
            'include?': {'time': 'O(n)', 'space': 'O(1)'},
            'reverse': {'time': 'O(n)', 'space': 'O(n)'},
            'reverse!': {'time': 'O(n)', 'space': 'O(1)'},
            'uniq': {'time': 'O(n)', 'space': 'O(n)'},
            'flatten': {'time': 'O(n)', 'space': 'O(n)'},
        }
        
        # Ruby syntax patterns
        self.patterns = {
            'loop': [
                r'^\s*for\s+\w+\s+in\s+',
                r'^\s*while\s+',
                r'^\s*until\s+',
                r'\.each\s*\{',
                r'\.each\s+do',
                r'\.times\s*\{',
                r'\.times\s+do',
                r'\.upto\s*\(',
                r'\.downto\s*\(',
            ],
            'function_def': [
                r'^\s*def\s+(\w+)',
            ],
            'method_call': [
                r'\.(\w+)\s*[\(\{]',
                r'\.(\w+)\s*$',
            ],
            'array_creation': [
                r'\[.*\]',
                r'Array\.new',
            ],
            'hash_creation': [
                r'\{.*\}',
                r'Hash\.new',
            ],
            'block_iteration': [
                r'\.each\s*\{.*\}',
                r'\.map\s*\{.*\}',
                r'\.select\s*\{.*\}',
                r'\.reject\s*\{.*\}',
            ]
        }
    
    def get_language_name(self) -> str:
        """Get the language name."""
        return 'ruby'
    
    def parse_code(self, code: str) -> List[str]:
        """
        Parse Ruby code into lines for analysis.
        
        Args:
            code: Ruby source code
            
        Returns:
            List of code lines
            
        Raises:
            SyntaxError: If code has obvious syntax errors
        """
        lines = code.splitlines()
        
        # Basic syntax validation
        self._validate_ruby_syntax(lines)
        
        return lines
    
    def analyze_structure(self, parsed_code: List[str]) -> List[ComplexityResult]:
        """
        Analyze Ruby code lines for complexity patterns.
        
        Args:
            parsed_code: List of code lines
            
        Returns:
            List of complexity analysis results
        """
        results = []
        
        # Track nesting levels
        nesting_stack = []
        function_names = set()
        
        for line_num, line in enumerate(parsed_code, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Analyze different patterns
            self._analyze_loops(line, line_num, len(nesting_stack), results)
            self._analyze_functions(line, line_num, function_names, results)
            self._analyze_method_calls(line, line_num, len(nesting_stack) > 0, results)
            self._analyze_data_structures(line, line_num, results)
            self._analyze_iterators(line, line_num, results)
            
            # Track nesting
            self._update_nesting_stack(line, nesting_stack)
        
        return results
    
    def _validate_ruby_syntax(self, lines: List[str]):
        """Basic Ruby syntax validation."""
        # Check for balanced keywords
        keywords = {'def': 'end', 'class': 'end', 'module': 'end', 'if': 'end', 
                   'unless': 'end', 'while': 'end', 'until': 'end', 'for': 'end',
                   'case': 'end', 'begin': 'end'}
        
        stack = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            for keyword in keywords:
                if re.search(rf'^\s*{keyword}\b', line):
                    stack.append((keyword, line_num))
            
            if re.search(r'^\s*end\b', line):
                if not stack:
                    raise SyntaxError(f"Line {line_num}: Unexpected 'end'")
                stack.pop()
        
        if stack:
            keyword, line_num = stack[-1]
            raise SyntaxError(f"Line {line_num}: Unmatched '{keyword}'")
    
    def _analyze_loops(self, line: str, line_num: int, depth: int, results: List[ComplexityResult]):
        """Analyze loop patterns."""
        for pattern in self.patterns['loop']:
            if re.search(pattern, line):
                # Determine complexity based on nesting depth
                if depth == 0:
                    time_complexity = 'O(n)'
                    description = "Single loop - linear time complexity"
                elif depth == 1:
                    time_complexity = 'O(n²)'
                    description = "Nested loop - quadratic time complexity"
                else:
                    time_complexity = f'O(n^{depth + 1})'
                    description = f"Multiple nested loops (depth {depth + 1}) - polynomial time complexity"
                
                result = ComplexityResult(
                    time_complexity=time_complexity,
                    space_complexity='O(1)',
                    line_number=line_num,
                    description=description,
                    analysis_type="Loop",
                    confidence=0.8,
                    suggestions=self._get_loop_suggestions(depth)
                )
                results.append(result)
                break
    
    def _analyze_functions(self, line: str, line_num: int, function_names: set, 
                          results: List[ComplexityResult]):
        """Analyze function definitions and recursion."""
        match = re.search(r'^\s*def\s+(\w+)', line)
        if match:
            func_name = match.group(1)
            function_names.add(func_name)
            
            # Check for potential recursion (simple heuristic)
            if func_name in line and 'def' not in line:
                result = ComplexityResult(
                    time_complexity='O(2ⁿ)',
                    space_complexity='O(n)',
                    line_number=line_num,
                    description=f"Potential recursive function '{func_name}'",
                    analysis_type="Recursion",
                    confidence=0.6,
                    suggestions=[
                        f"Consider memoization for '{func_name}' if recursive",
                        "Consider iterative approach to reduce space complexity"
                    ]
                )
                results.append(result)
    
    def _analyze_method_calls(self, line: str, line_num: int, in_loop: bool, 
                             results: List[ComplexityResult]):
        """Analyze method calls for known complexity patterns."""
        for pattern in self.patterns['method_call']:
            matches = re.finditer(pattern, line)
            for match in matches:
                method_name = match.group(1)
                if method_name in self.builtin_complexities:
                    complexity_info = self.builtin_complexities[method_name]
                    time_complexity = complexity_info['time']
                    space_complexity = complexity_info['space']
                    
                    # Adjust complexity if inside loop
                    if in_loop and time_complexity != 'O(1)':
                        time_complexity = self._multiply_complexity(time_complexity, 'O(n)')
                    
                    result = ComplexityResult(
                        time_complexity=time_complexity,
                        space_complexity=space_complexity,
                        line_number=line_num,
                        description=f"Ruby method '{method_name}' call",
                        analysis_type="Built-in Method",
                        confidence=0.9,
                        suggestions=self._get_method_suggestions(method_name, in_loop)
                    )
                    results.append(result)
    
    def _analyze_data_structures(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze data structure creation."""
        # Array creation
        if any(re.search(pattern, line) for pattern in self.patterns['array_creation']):
            result = ComplexityResult(
                time_complexity='O(n)',
                space_complexity='O(n)',
                line_number=line_num,
                description="Array creation",
                analysis_type="Data Structure",
                confidence=0.8,
                suggestions=["Consider memory usage for large arrays"]
            )
            results.append(result)
        
        # Hash creation
        elif any(re.search(pattern, line) for pattern in self.patterns['hash_creation']):
            result = ComplexityResult(
                time_complexity='O(n)',
                space_complexity='O(n)',
                line_number=line_num,
                description="Hash creation",
                analysis_type="Data Structure",
                confidence=0.8,
                suggestions=["Consider memory usage for large hashes"]
            )
            results.append(result)
    
    def _analyze_iterators(self, line: str, line_num: int, results: List[ComplexityResult]):
        """Analyze Ruby iterator patterns."""
        for pattern in self.patterns['block_iteration']:
            if re.search(pattern, line):
                result = ComplexityResult(
                    time_complexity='O(n)',
                    space_complexity='O(n)',
                    line_number=line_num,
                    description="Block iteration with collection creation",
                    analysis_type="Iterator",
                    confidence=0.8,
                    suggestions=["Consider using lazy evaluation for large collections"]
                )
                results.append(result)
                break
    
    def _update_nesting_stack(self, line: str, nesting_stack: List[str]):
        """Update nesting stack for tracking depth."""
        # Add to stack for keywords that increase nesting
        nesting_keywords = ['for', 'while', 'until', 'if', 'unless', 'case', 'begin', 'def', 'class', 'module']
        for keyword in nesting_keywords:
            if re.search(rf'^\s*{keyword}\b', line):
                nesting_stack.append(keyword)
                break
        
        # Handle blocks
        if re.search(r'\.(each|map|select|reject|times)\s*[\{\|]', line):
            nesting_stack.append('block')
        
        # Remove from stack for 'end'
        if re.search(r'^\s*end\b', line) and nesting_stack:
            nesting_stack.pop()
        
        # Handle block end
        if re.search(r'\}', line) and nesting_stack and nesting_stack[-1] == 'block':
            nesting_stack.pop()
    
    def _multiply_complexity(self, complexity1: str, complexity2: str) -> str:
        """Multiply two complexity expressions."""
        if complexity1 == 'O(1)':
            return complexity2
        if complexity2 == 'O(1)':
            return complexity1
        if complexity1 == 'O(n)' and complexity2 == 'O(n)':
            return 'O(n²)'
        if 'O(n²)' in [complexity1, complexity2]:
            return 'O(n²)'
        return 'O(n²)'
    
    def _get_loop_suggestions(self, depth: int) -> List[str]:
        """Get optimization suggestions for loops."""
        suggestions = []
        if depth == 1:
            suggestions.extend([
                "Consider if the inner loop can be eliminated",
                "Look for opportunities to use Hash for O(1) lookups",
                "Consider using built-in methods like select, map, or find"
            ])
        elif depth > 1:
            suggestions.extend([
                "Deep nesting indicates potential for significant optimization",
                "Consider breaking down into separate methods",
                "Look for opportunities to use Ruby's enumerable methods"
            ])
        return suggestions
    
    def _get_method_suggestions(self, method_name: str, in_loop: bool) -> List[str]:
        """Get suggestions for method usage."""
        suggestions = []
        if in_loop and method_name in ['sort', 'max', 'min', 'sum']:
            suggestions.append(f"Calling {method_name} inside a loop increases overall complexity")
        if method_name == 'sort':
            suggestions.append("Consider if data can be kept sorted to avoid repeated sorting")
        if method_name in ['map', 'select', 'reject']:
            suggestions.append("Consider using lazy evaluation with .lazy for large collections")
        return suggestions
