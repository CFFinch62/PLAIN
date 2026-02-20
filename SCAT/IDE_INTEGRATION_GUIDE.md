# SCAT IDE Integration Guide

**Complete guide for integrating SCAT (Source Code Analysis Tool) directly into your IDE**

## 🎯 **Overview**

IDE Integration provides direct, programmatic access to SCAT's analysis engine without requiring a separate running application. This method is ideal for embedding code analysis directly into your IDE's workflow with immediate results.

## ✨ **Key Benefits**

- ✅ **Immediate Results** - Get analysis data directly in your IDE
- ✅ **No External Dependencies** - No need to run separate SCAT application
- ✅ **Lightweight** - Minimal overhead, no network communication
- ✅ **Synchronous** - Results available immediately after function call
- ✅ **Programmatic Access** - Full control over analysis data
- ✅ **Easy Integration** - Simple function calls, no complex setup

## 📋 **Prerequisites**

### **System Requirements**
- Python 3.8 or higher
- SCAT core modules (no PyQt6 required for IDE integration)

### **File Dependencies**
Ensure these SCAT files are accessible in your project:
```
SCAT/
├── launcher.py          # Main integration interface
├── core/               # Core analysis engine
│   ├── analyzer.py     # Main analyzer class
│   ├── models.py       # Data models and configuration
│   └── ...
├── languages/          # Language-specific analyzers
│   ├── python_analyzer.py
│   ├── ruby_analyzer.py
│   ├── lua_analyzer.py
│   └── ...
└── main.py            # Alternative entry point
```

## 🚀 **Quick Start**

### **Basic Integration Example**
```python
# Import SCAT integration functions
from SCAT.launcher import ide_analyze_code, ide_get_supported_languages

# Analyze code directly
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

# Get analysis results
result = ide_analyze_code(code, "python", "MyIDE")

# Process results
if result.get("status") != "error":
    print(f"Time Complexity: {result['time_complexity']}")
    print(f"Space Complexity: {result['space_complexity']}")
    print(f"Quality Score: {result['quality_score']}/100")
else:
    print(f"Analysis Error: {result['message']}")
```

## 📚 **Core Integration Functions**

### **1. Analyze Code Directly**
```python
ide_analyze_code(code: str, language: str = "python", ide_name: str = "IDE") -> Dict[str, Any]
```

**Parameters:**
- `code` (str): Source code to analyze
- `language` (str): Programming language ("python", "ruby", "lua", "basic", "pseudocode")
- `ide_name` (str): Name of your IDE (for logging/tracking)

**Returns:** Dictionary with analysis results

**Example:**
```python
from SCAT.launcher import ide_analyze_code

code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

result = ide_analyze_code(code, "python", "MyIDE")
```

### **2. Analyze File**
```python
ide_analyze_file(file_path: str, language: Optional[str] = None, ide_name: str = "IDE") -> bool
```

**Parameters:**
- `file_path` (str): Path to code file
- `language` (str, optional): Language override (auto-detected if None)
- `ide_name` (str): Name of your IDE

**Returns:** Boolean success status

**Example:**
```python
from SCAT.launcher import ide_analyze_file

# Auto-detect language from file extension
success = ide_analyze_file("script.py", None, "MyIDE")

# Or specify language explicitly
success = ide_analyze_file("code.txt", "python", "MyIDE")
```

### **3. Get Supported Languages**
```python
ide_get_supported_languages() -> Dict[str, Dict[str, Any]]
```

**Returns:** Dictionary of supported languages with metadata

**Example:**
```python
from SCAT.launcher import ide_get_supported_languages

languages = ide_get_supported_languages()
for lang_key, info in languages.items():
    print(f"{info['name']}: {', '.join(info['extensions'])}")
    print(f"  Description: {info['description']}")
    print(f"  Features: {', '.join(info['supported_features'])}")
```

### **4. Launch SCAT Application**
```python
ide_launch_analyzer(mode: str = 'gui') -> bool
```

**Parameters:**
- `mode` (str): Launch mode ("gui" or "cli")

**Returns:** Boolean success status

**Example:**
```python
from SCAT.launcher import ide_launch_analyzer

# Launch GUI for visual analysis
success = ide_launch_analyzer('gui')

# Or launch CLI for terminal-based analysis
success = ide_launch_analyzer('cli')
```

## 📊 **Analysis Result Structure**

### **Successful Analysis Result**
```python
{
    "status": "success",
    "language": "python",
    "time_complexity": "O(n²)",
    "space_complexity": "O(1)",
    "quality_score": 75,
    "performance_rating": "Fair",
    "confidence": 0.95,
    "analysis_details": {
        "loops": [
            {
                "type": "nested_loop",
                "line": 3,
                "complexity": "O(n²)",
                "description": "Nested for loops"
            }
        ],
        "functions": [
            {
                "name": "bubble_sort",
                "complexity": "O(n²)",
                "line": 1
            }
        ]
    },
    "suggestions": [
        "Consider using a more efficient sorting algorithm like quicksort or mergesort",
        "The nested loop structure creates quadratic time complexity"
    ],
    "metadata": {
        "analysis_time": 0.023,
        "lines_analyzed": 8,
        "timestamp": "2024-01-15T10:30:45"
    }
}
```

### **Error Result**
```python
{
    "status": "error",
    "message": "Syntax error in code",
    "language": "python",
    "error_details": {
        "type": "SyntaxError",
        "line": 5,
        "description": "Invalid syntax"
    }
}
```

## 🔧 **Advanced Integration Patterns**

### **1. Real-time Analysis**
```python
class CodeAnalysisIntegration:
    def __init__(self):
        self.last_analysis = None
        
    def analyze_on_save(self, code, language):
        """Analyze code when file is saved."""
        result = ide_analyze_code(code, language, "MyIDE")
        self.last_analysis = result
        self.update_ui_indicators(result)
        
    def update_ui_indicators(self, result):
        """Update IDE UI with analysis results."""
        if result.get("status") == "success":
            complexity = result.get("time_complexity", "Unknown")
            score = result.get("quality_score", 0)
            
            # Update status bar
            self.status_bar.setText(f"Complexity: {complexity} | Score: {score}/100")
            
            # Update code highlighting
            self.highlight_complex_sections(result.get("analysis_details", {}))
```

### **2. Batch File Analysis**
```python
def analyze_project_files(project_path, file_extensions=[".py", ".rb", ".lua"]):
    """Analyze all code files in a project."""
    results = {}
    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # Detect language from extension
                    ext = os.path.splitext(file)[1]
                    language_map = {'.py': 'python', '.rb': 'ruby', '.lua': 'lua'}
                    language = language_map.get(ext, 'python')
                    
                    # Analyze file
                    result = ide_analyze_code(code, language, "MyIDE")
                    results[file_path] = result
                    
                except Exception as e:
                    results[file_path] = {"status": "error", "message": str(e)}
    
    return results
```

### **3. Custom Configuration**
```python
def analyze_with_custom_config(code, language, custom_settings):
    """Analyze code with custom configuration."""
    # For advanced configuration, use direct analyzer access
    import sys
    from pathlib import Path
    
    # Add SCAT to path
    scat_path = Path("path/to/SCAT")
    sys.path.insert(0, str(scat_path))
    
    from core.analyzer import CodeAnalyzer
    from core.models import AnalysisConfig
    
    # Create custom configuration
    config = AnalysisConfig()
    config.max_depth = custom_settings.get('max_depth', 10)
    config.include_space_analysis = custom_settings.get('space_analysis', True)
    config.confidence_threshold = custom_settings.get('confidence', 0.8)
    
    # Analyze with custom config
    analyzer = CodeAnalyzer(config)
    report = analyzer.analyze_code(code, language)
    
    return report.to_dict()
```

## 🎨 **UI Integration Examples**

### **1. Status Bar Integration**
```python
def update_status_bar(self, analysis_result):
    """Update IDE status bar with analysis info."""
    if analysis_result.get("status") == "success":
        complexity = analysis_result.get("time_complexity", "Unknown")
        score = analysis_result.get("quality_score", 0)
        rating = analysis_result.get("performance_rating", "Unknown")
        
        status_text = f"Complexity: {complexity} | Quality: {score}/100 ({rating})"
        self.status_bar.setText(status_text)
        
        # Color-code based on quality score
        if score >= 80:
            self.status_bar.setStyleSheet("color: green")
        elif score >= 60:
            self.status_bar.setStyleSheet("color: orange")
        else:
            self.status_bar.setStyleSheet("color: red")
```

### **2. Tooltip Integration**
```python
def show_complexity_tooltip(self, line_number, analysis_result):
    """Show complexity information in tooltip."""
    details = analysis_result.get("analysis_details", {})
    
    # Find relevant information for this line
    tooltip_text = []
    
    for loop in details.get("loops", []):
        if loop.get("line") == line_number:
            tooltip_text.append(f"Loop: {loop['complexity']} - {loop['description']}")
    
    for func in details.get("functions", []):
        if func.get("line") == line_number:
            tooltip_text.append(f"Function: {func['complexity']}")
    
    if tooltip_text:
        self.show_tooltip("\n".join(tooltip_text))
```

### **3. Sidebar Panel Integration**
```python
class AnalysisPanel:
    """Dedicated panel for showing analysis results."""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the analysis panel UI."""
        # Create widgets for displaying:
        # - Overall complexity
        # - Quality score
        # - Detailed breakdown
        # - Suggestions
        pass
        
    def update_analysis(self, result):
        """Update panel with new analysis results."""
        if result.get("status") == "success":
            self.complexity_label.setText(result.get("time_complexity", "Unknown"))
            self.score_label.setText(f"{result.get('quality_score', 0)}/100")
            self.update_suggestions(result.get("suggestions", []))
            self.update_details(result.get("analysis_details", {}))
```

## 🔍 **Language-Specific Considerations**

### **Python Analysis**
```python
# Python code gets full AST-based analysis
python_code = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
"""

result = ide_analyze_code(python_code, "python", "MyIDE")
# Expects detailed AST analysis with high confidence
```

### **Ruby Analysis**
```python
# Ruby code uses pattern-based analysis
ruby_code = """
def fibonacci(n)
  return n if n <= 1
  fibonacci(n-1) + fibonacci(n-2)
end
"""

result = ide_analyze_code(ruby_code, "ruby", "MyIDE")
# Pattern-based analysis, may have lower confidence
```

### **Multi-Language Projects**
```python
def analyze_mixed_project(files):
    """Handle projects with multiple languages."""
    results_by_language = {}
    
    for file_path, code in files.items():
        # Auto-detect language
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python',
            '.rb': 'ruby', 
            '.lua': 'lua',
            '.bas': 'basic'
        }
        
        language = language_map.get(ext, 'python')
        
        # Analyze with appropriate language
        result = ide_analyze_code(code, language, "MyIDE")
        
        if language not in results_by_language:
            results_by_language[language] = []
        results_by_language[language].append({
            'file': file_path,
            'result': result
        })
    
    return results_by_language
```

## ⚠️ **Error Handling**

### **Robust Error Handling**
```python
def safe_analyze_code(code, language="python", ide_name="MyIDE"):
    """Analyze code with comprehensive error handling."""
    try:
        # Validate inputs
        if not code or not code.strip():
            return {
                "status": "error",
                "message": "Empty code provided",
                "language": language
            }
        
        if language not in ["python", "ruby", "lua", "basic", "pseudocode"]:
            return {
                "status": "error", 
                "message": f"Unsupported language: {language}",
                "language": language
            }
        
        # Perform analysis
        result = ide_analyze_code(code, language, ide_name)
        
        # Validate result
        if not isinstance(result, dict):
            return {
                "status": "error",
                "message": "Invalid analysis result format",
                "language": language
            }
        
        return result
        
    except ImportError as e:
        return {
            "status": "error",
            "message": f"SCAT modules not found: {e}",
            "language": language
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Analysis failed: {e}",
            "language": language
        }
```

### **Connection Testing**
```python
def test_scat_integration():
    """Test SCAT integration functionality."""
    try:
        # Test basic import
        from SCAT.launcher import ide_analyze_code, ide_get_supported_languages
        
        # Test language support
        languages = ide_get_supported_languages()
        if not languages or "error" in languages:
            return False, "Failed to get supported languages"
        
        # Test basic analysis
        test_code = "print('Hello, World!')"
        result = ide_analyze_code(test_code, "python", "TestIDE")
        
        if result.get("status") == "error":
            return False, f"Analysis test failed: {result.get('message')}"
        
        return True, "SCAT integration working correctly"
        
    except Exception as e:
        return False, f"Integration test failed: {e}"
```

## 📈 **Performance Optimization**

### **Caching Results**
```python
class AnalysisCache:
    """Cache analysis results to improve performance."""
    
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        
    def get_cache_key(self, code, language):
        """Generate cache key for code."""
        import hashlib
        content = f"{code}:{language}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_analysis(self, code, language, ide_name):
        """Get analysis with caching."""
        cache_key = self.get_cache_key(code, language)
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Perform analysis
        result = ide_analyze_code(code, language, ide_name)
        
        # Cache result
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = result
        return result

# Usage
cache = AnalysisCache()
result = cache.get_analysis(code, "python", "MyIDE")
```

### **Async Analysis**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncAnalyzer:
    """Asynchronous analysis for better UI responsiveness."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def analyze_async(self, code, language, ide_name):
        """Analyze code asynchronously."""
        loop = asyncio.get_event_loop()
        
        # Run analysis in thread pool
        result = await loop.run_in_executor(
            self.executor,
            ide_analyze_code,
            code, language, ide_name
        )
        
        return result
    
    async def analyze_multiple_async(self, code_items):
        """Analyze multiple code snippets concurrently."""
        tasks = []
        
        for code, language, ide_name in code_items:
            task = self.analyze_async(code, language, ide_name)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

# Usage
async def main():
    analyzer = AsyncAnalyzer()
    result = await analyzer.analyze_async(code, "python", "MyIDE")
    print(f"Analysis complete: {result}")
```

## 🧪 **Testing Integration**

### **Unit Tests**
```python
import unittest
from SCAT.launcher import ide_analyze_code, ide_get_supported_languages

class TestSCATIntegration(unittest.TestCase):
    
    def test_basic_analysis(self):
        """Test basic code analysis."""
        code = "print('Hello, World!')"
        result = ide_analyze_code(code, "python", "TestIDE")
        
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertNotEqual(result.get("status"), "error")
    
    def test_complex_analysis(self):
        """Test analysis of complex code."""
        code = """
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        """
        
        result = ide_analyze_code(code, "python", "TestIDE")
        
        self.assertEqual(result.get("status"), "success")
        self.assertIn("time_complexity", result)
        self.assertIn("quality_score", result)
    
    def test_supported_languages(self):
        """Test getting supported languages."""
        languages = ide_get_supported_languages()
        
        self.assertIsInstance(languages, dict)
        self.assertIn("python", languages)
        self.assertIn("ruby", languages)
    
    def test_error_handling(self):
        """Test error handling with invalid code."""
        invalid_code = "def invalid_syntax("
        result = ide_analyze_code(invalid_code, "python", "TestIDE")
        
        # Should handle syntax errors gracefully
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)

if __name__ == "__main__":
    unittest.main()
```

## 📝 **Integration Checklist**

### **Pre-Integration**
- [ ] Verify Python 3.8+ is available
- [ ] Confirm SCAT core files are accessible
- [ ] Test basic import: `from SCAT.launcher import ide_analyze_code`
- [ ] Run integration test function

### **Basic Integration**
- [ ] Implement basic `ide_analyze_code()` call
- [ ] Add error handling for analysis failures
- [ ] Test with sample code snippets
- [ ] Verify result format matches expectations

### **Advanced Integration**
- [ ] Add language auto-detection
- [ ] Implement result caching
- [ ] Add UI indicators/feedback
- [ ] Create analysis panel/sidebar
- [ ] Add batch analysis capability

### **Production Ready**
- [ ] Comprehensive error handling
- [ ] Performance optimization
- [ ] User configuration options
- [ ] Documentation for end users
- [ ] Testing with real-world code

## 🆘 **Troubleshooting**

### **Common Issues**

**Import Errors**
```python
# Problem: Cannot import SCAT modules
# Solution: Add SCAT path to sys.path
import sys
from pathlib import Path
scat_path = Path("path/to/SCAT")
sys.path.insert(0, str(scat_path))
```

**Analysis Failures**
```python
# Problem: Analysis returns error status
# Solution: Check code syntax and language support
result = ide_analyze_code(code, language, "MyIDE")
if result.get("status") == "error":
    print(f"Error: {result.get('message')}")
    # Handle error appropriately
```

**Performance Issues**
```python
# Problem: Analysis is slow
# Solution: Implement caching and async analysis
# See Performance Optimization section above
```

### **Debug Mode**
```python
def debug_analysis(code, language="python"):
    """Debug analysis with detailed output."""
    print(f"Analyzing {len(code)} characters of {language} code...")
    
    result = ide_analyze_code(code, language, "DebugIDE")
    
    print(f"Status: {result.get('status')}")
    if result.get("status") == "success":
        print(f"Time Complexity: {result.get('time_complexity')}")
        print(f"Space Complexity: {result.get('space_complexity')}")
        print(f"Quality Score: {result.get('quality_score')}")
        print(f"Confidence: {result.get('confidence')}")
    else:
        print(f"Error: {result.get('message')}")
    
    return result
```

---

**For API Integration (TCP server method), see `API_INTEGRATION_GUIDE.md`**

**For general SCAT usage, see `README.md`**

**For troubleshooting, see `SCAT_TROUBLESHOOTING.md`**
