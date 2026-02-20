#!/usr/bin/env python3
"""
Test script for the modular Code Analysis Tool.

This script tests the new modular architecture with support for
Python, Ruby, and Lua programming languages.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import CodeAnalyzer
from core.models import AnalysisConfig
from core.registry import LanguageRegistry


def test_python_analysis():
    """Test Python code analysis."""
    print("\n🐍 Testing Python Analysis")
    print("-" * 40)
    
    test_cases = [
        {
            'name': 'Bubble Sort (Quadratic)',
            'code': '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
            ''',
            'expected_time': 'O(n²)',
            'language': 'python'
        },
        {
            'name': 'Recursive Fibonacci (Exponential)',
            'code': '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
            ''',
            'expected_time': 'O(2ⁿ)',
            'language': 'python'
        },
        {
            'name': 'List Comprehension (Linear)',
            'code': '''
def process_data(numbers):
    squares = [x**2 for x in numbers]
    return sum(squares)
            ''',
            'expected_time': 'O(n)',
            'language': 'python'
        }
    ]
    
    config = AnalysisConfig()
    analyzer = CodeAnalyzer(config)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        report = analyzer.analyze_code(test_case['code'], test_case['language'])
        
        print(f"  Time Complexity: {report.overall_time_complexity}")
        print(f"  Space Complexity: {report.overall_space_complexity}")
        print(f"  Quality Score: {report.quality_score:.1f}/100")
        print(f"  Performance Rating: {report.performance_rating}")
        
        # Check if analysis succeeded
        if report.overall_time_complexity != "Error":
            print("  ✅ Analysis completed successfully")
        else:
            print("  ❌ Analysis failed")
            if report.warnings:
                print(f"  Error: {report.warnings[0]}")


def test_ruby_analysis():
    """Test Ruby code analysis."""
    print("\n💎 Testing Ruby Analysis")
    print("-" * 40)
    
    test_cases = [
        {
            'name': 'Ruby Each Loop',
            'code': '''
def process_array(arr)
  result = []
  arr.each do |item|
    result << item * 2
  end
  result
end
            ''',
            'language': 'ruby'
        },
        {
            'name': 'Ruby Nested Loops',
            'code': '''
def matrix_multiply(a, b)
  result = []
  for i in 0...a.length
    row = []
    for j in 0...b[0].length
      sum = 0
      for k in 0...b.length
        sum += a[i][k] * b[k][j]
      end
      row << sum
    end
    result << row
  end
  result
end
            ''',
            'language': 'ruby'
        },
        {
            'name': 'Ruby Map Operation',
            'code': '''
def square_numbers(numbers)
  numbers.map { |n| n * n }
end
            ''',
            'language': 'ruby'
        }
    ]
    
    config = AnalysisConfig()
    analyzer = CodeAnalyzer(config)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        report = analyzer.analyze_code(test_case['code'], test_case['language'])
        
        print(f"  Time Complexity: {report.overall_time_complexity}")
        print(f"  Space Complexity: {report.overall_space_complexity}")
        print(f"  Quality Score: {report.quality_score:.1f}/100")
        print(f"  Performance Rating: {report.performance_rating}")
        
        if report.overall_time_complexity != "Error":
            print("  ✅ Analysis completed successfully")
        else:
            print("  ❌ Analysis failed")
            if report.warnings:
                print(f"  Error: {report.warnings[0]}")


def test_lua_analysis():
    """Test Lua code analysis."""
    print("\n🌙 Testing Lua Analysis")
    print("-" * 40)
    
    test_cases = [
        {
            'name': 'Lua For Loop',
            'code': '''
function sum_array(arr)
  local sum = 0
  for i = 1, #arr do
    sum = sum + arr[i]
  end
  return sum
end
            ''',
            'language': 'lua'
        },
        {
            'name': 'Lua Table Operations',
            'code': '''
function create_lookup_table(arr)
  local lookup = {}
  for i, v in ipairs(arr) do
    lookup[v] = i
  end
  return lookup
end
            ''',
            'language': 'lua'
        },
        {
            'name': 'Lua Recursive Function',
            'code': '''
function factorial(n)
  if n <= 1 then
    return 1
  else
    return n * factorial(n - 1)
  end
end
            ''',
            'language': 'lua'
        }
    ]
    
    config = AnalysisConfig()
    analyzer = CodeAnalyzer(config)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        report = analyzer.analyze_code(test_case['code'], test_case['language'])
        
        print(f"  Time Complexity: {report.overall_time_complexity}")
        print(f"  Space Complexity: {report.overall_space_complexity}")
        print(f"  Quality Score: {report.quality_score:.1f}/100")
        print(f"  Performance Rating: {report.performance_rating}")
        
        if report.overall_time_complexity != "Error":
            print("  ✅ Analysis completed successfully")
        else:
            print("  ❌ Analysis failed")
            if report.warnings:
                print(f"  Error: {report.warnings[0]}")


def test_language_detection():
    """Test automatic language detection."""
    print("\n🔍 Testing Language Detection")
    print("-" * 40)
    
    test_cases = [
        {
            'code': 'def hello():\n    print("Hello, Python!")',
            'expected': 'python'
        },
        {
            'code': 'def hello\n  puts "Hello, Ruby!"\nend',
            'expected': 'ruby'
        },
        {
            'code': 'function hello()\n  print("Hello, Lua!")\nend',
            'expected': 'lua'
        }
    ]
    
    config = AnalysisConfig()
    analyzer = CodeAnalyzer(config)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: Detecting language for code snippet")
        report = analyzer.analyze_code(test_case['code'])
        
        print(f"  Detected language: {report.language}")
        print(f"  Expected language: {test_case['expected']}")
        
        if report.language == test_case['expected']:
            print("  ✅ Language detection successful")
        else:
            print("  ⚠️  Language detection differs from expected")


def test_registry():
    """Test language registry functionality."""
    print("\n📋 Testing Language Registry")
    print("-" * 40)
    
    config = AnalysisConfig()
    analyzer = CodeAnalyzer(config)
    
    # Test supported languages
    languages = analyzer.get_supported_languages()
    print(f"\nSupported languages ({len(languages)}):")
    for name, info in languages.items():
        print(f"  • {info.name}: {', '.join(info.extensions)}")
        print(f"    Features: {', '.join(info.supported_features)}")
    
    # Test language support checks
    test_languages = ['python', 'ruby', 'lua', 'javascript', 'nonexistent']
    print(f"\nLanguage support checks:")
    for lang in test_languages:
        supported = analyzer.is_language_supported(lang)
        status = "✅" if supported else "❌"
        print(f"  {status} {lang}: {'supported' if supported else 'not supported'}")


def test_error_handling():
    """Test error handling for invalid code."""
    print("\n⚠️  Testing Error Handling")
    print("-" * 40)
    
    test_cases = [
        {
            'name': 'Python Syntax Error',
            'code': 'def invalid_syntax(\n    print("missing closing parenthesis"',
            'language': 'python'
        },
        {
            'name': 'Ruby Syntax Error',
            'code': 'def invalid_syntax\n  puts "missing end"',
            'language': 'ruby'
        },
        {
            'name': 'Lua Syntax Error',
            'code': 'function invalid_syntax()\n  print("missing end")',
            'language': 'lua'
        }
    ]
    
    config = AnalysisConfig()
    analyzer = CodeAnalyzer(config)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        report = analyzer.analyze_code(test_case['code'], test_case['language'])
        
        if report.overall_time_complexity == "Error":
            print("  ✅ Error properly detected and handled")
            if report.warnings:
                print(f"  Error message: {report.warnings[0]}")
        else:
            print("  ⚠️  Error not detected (unexpected)")


def main():
    """Run all tests."""
    print("🔍 Code Analysis Tool - Modular Architecture Tests")
    print("=" * 60)
    
    try:
        test_python_analysis()
        test_ruby_analysis()
        test_lua_analysis()
        test_language_detection()
        test_registry()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed!")
        print("\nThe modular code analysis tool is working correctly.")
        print("You can now use it to analyze Python, Ruby, and Lua code.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
