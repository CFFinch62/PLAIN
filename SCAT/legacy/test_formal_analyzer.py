#!/usr/bin/env python3
"""
Test script for the formal Code Analysis Professional application.
Tests the analysis engine without the GUI.
"""

from code_analyzer_app import AdvancedComplexityAnalyzer

def test_formal_analyzer():
    """Test the formal analyzer with comprehensive examples."""
    analyzer = AdvancedComplexityAnalyzer()
    
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
            'expected_space': 'O(1)'
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
            'expected_space': 'O(n)'
        },
        {
            'name': 'Linear Search (Linear)',
            'code': '''
def linear_search(arr, target):
    for i, element in enumerate(arr):
        if element == target:
            return i
    return -1
            ''',
            'expected_time': 'O(n)',
            'expected_space': 'O(1)'
        },
        {
            'name': 'Sorting with Built-in (Linearithmic)',
            'code': '''
def sort_and_process(data):
    sorted_data = sorted(data)
    return max(sorted_data)
            ''',
            'expected_time': 'O(n log n)',
            'expected_space': 'O(n)'
        },
        {
            'name': 'List Comprehension (Linear)',
            'code': '''
def process_data(numbers):
    squares = [x**2 for x in numbers]
    return sum(squares)
            ''',
            'expected_time': 'O(n)',
            'expected_space': 'O(n)'
        }
    ]
    
    print("🔍 Formal Code Analysis Professional - Test Results")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 40)
        
        # Perform analysis
        report = analyzer.analyze_code(test_case['code'], 'python')
        
        # Check for errors
        if report.overall_time_complexity == "Error":
            print(f"❌ Error: {report.warnings[0] if report.warnings else 'Unknown error'}")
            continue
        
        # Display results
        print(f"📊 Time Complexity: {report.overall_time_complexity}")
        print(f"💾 Space Complexity: {report.overall_space_complexity}")
        print(f"⭐ Quality Score: {report.quality_score:.1f}/100")
        print(f"🎯 Performance Rating: {report.performance_rating}")
        
        # Check expectations
        time_match = report.overall_time_complexity == test_case['expected_time']
        space_match = report.overall_space_complexity == test_case['expected_space']
        
        if time_match and space_match:
            print("✅ PASS - Both time and space complexity match expectations")
        elif time_match:
            print("🟡 PARTIAL - Time complexity matches, space complexity differs")
            print(f"   Expected space: {test_case['expected_space']}, Got: {report.overall_space_complexity}")
        elif space_match:
            print("🟡 PARTIAL - Space complexity matches, time complexity differs")
            print(f"   Expected time: {test_case['expected_time']}, Got: {report.overall_time_complexity}")
        else:
            print("⚠️  DIFFERS - Both complexities differ from expectations")
            print(f"   Expected: Time {test_case['expected_time']}, Space {test_case['expected_space']}")
            print(f"   Got: Time {report.overall_time_complexity}, Space {report.overall_space_complexity}")
        
        # Show detailed analysis
        if report.detailed_results:
            print("\n📋 Detailed Analysis:")
            for detail in report.detailed_results:
                print(f"   Line {detail.line_number} [{detail.analysis_type}]: "
                      f"Time {detail.time_complexity}, Space {detail.space_complexity}")
                print(f"      {detail.description}")
        
        # Show warnings and suggestions
        if report.warnings:
            print("\n⚠️  Warnings:")
            for warning in report.warnings:
                print(f"   • {warning}")
        
        if report.suggestions:
            print("\n💡 Suggestions:")
            for suggestion in report.suggestions:
                print(f"   • {suggestion}")
    
    print("\n" + "=" * 60)
    print("🎉 Formal analyzer testing completed!")
    print("\nTo test the full GUI application, run:")
    print("   python code_analyzer_app.py")
    print("\nTo test API integration, start the app and use the API menu.")

def test_api_format():
    """Test the API data format."""
    print("\n🌐 API Integration Test")
    print("-" * 30)
    
    # Example of how IDEs would send data to the analyzer
    api_request = {
        "code": """
def example_function(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
        """,
        "language": "python",
        "source_app": "PyDE"
    }
    
    print("📤 Example API request format:")
    import json
    print(json.dumps(api_request, indent=2))
    
    # Test analysis
    analyzer = AdvancedComplexityAnalyzer()
    report = analyzer.analyze_code(api_request["code"], api_request["language"])
    
    print(f"\n📥 Analysis result:")
    print(f"Time Complexity: {report.overall_time_complexity}")
    print(f"Space Complexity: {report.overall_space_complexity}")
    print(f"Quality Score: {report.quality_score:.1f}/100")
    
    print("\n✅ API format test completed!")

if __name__ == "__main__":
    test_formal_analyzer()
    test_api_format()
