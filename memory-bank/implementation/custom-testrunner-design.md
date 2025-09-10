# ExecuteMCP.TestRunner - Custom Test Manager Design

## Executive Summary
A custom test manager implementation that bypasses %UnitTest.Manager's filesystem dependencies and VS Code sync issues by working directly with compiled ObjectScript packages. This provides full control over test discovery, execution, and reporting while maintaining compatibility with %UnitTest.TestCase and assertion macros.

## Problem Statement
- **VS Code Sync Issues**: Classes exist as files but aren't always compiled in IRIS
- **Filesystem Dependency**: %UnitTest.Manager requires filesystem paths and /load qualifiers
- **Discovery Problems**: Tests not discovered despite being loaded and compiled
- **Complex Workarounds**: Current solution requires WorkMgr pattern and manual class loading

## Solution Architecture

### Core Components

```
ExecuteMCP.TestRunner/
├── Manager.cls          - Main orchestrator and LogAssert interface
├── Discovery.cls        - Package-based test discovery using %Dictionary
├── Executor.cls         - Test execution engine with lifecycle support
├── Context.cls          - Execution state and assertion tracking
├── Reporter.cls         - JSON result formatting and filtering
└── Filter.cls           - Test filtering capabilities
```

### Component Responsibilities

#### 1. ExecuteMCP.TestRunner.Manager
**Purpose**: Main entry point and orchestrator
```objectscript
Class ExecuteMCP.TestRunner.Manager Extends %RegisteredObject
{
    Property Context As ExecuteMCP.TestRunner.Context;
    Property Discovery As ExecuteMCP.TestRunner.Discovery;
    Property Executor As ExecuteMCP.TestRunner.Executor;
    Property Reporter As ExecuteMCP.TestRunner.Reporter;
    
    /// Main entry point - run tests by package
    ClassMethod RunTests(pPackage As %String, pFilter As %String = "") As %String
    
    /// LogAssert interface for assertion macros
    Method LogAssert(pSuccess As %Boolean, pAction As %String, pDescription As %String = "")
    
    /// LogMessage interface for test output
    Method LogMessage(pMessage As %String)
}
```

#### 2. ExecuteMCP.TestRunner.Discovery
**Purpose**: Find test classes and methods using %Dictionary
```objectscript
Class ExecuteMCP.TestRunner.Discovery Extends %RegisteredObject
{
    /// Discover all test classes in a package
    ClassMethod DiscoverTestClasses(pPackage As %String) As %List
    
    /// Check if class extends %UnitTest.TestCase
    ClassMethod IsTestClass(pClassName As %String) As %Boolean
    
    /// Find all Test* methods in a class
    ClassMethod DiscoverTestMethods(pClassName As %String) As %List
    
    /// Build complete test manifest
    ClassMethod BuildTestManifest(pPackage As %String) As %DynamicObject
}
```

#### 3. ExecuteMCP.TestRunner.Executor
**Purpose**: Execute tests with lifecycle support
```objectscript
Class ExecuteMCP.TestRunner.Executor Extends %RegisteredObject
{
    Property Manager As ExecuteMCP.TestRunner.Manager;
    
    /// Execute a single test method
    Method ExecuteTest(pClassName As %String, pMethodName As %String) As %Status
    
    /// Run OnBeforeAllTests
    Method RunBeforeAll(pTestInstance As %UnitTest.TestCase) As %Status
    
    /// Run OnAfterAllTests
    Method RunAfterAll(pTestInstance As %UnitTest.TestCase) As %Status
    
    /// Run OnBeforeOneTest
    Method RunBeforeOne(pTestInstance As %UnitTest.TestCase, pMethodName As %String) As %Status
    
    /// Run OnAfterOneTest
    Method RunAfterOne(pTestInstance As %UnitTest.TestCase, pMethodName As %String) As %Status
}
```

#### 4. ExecuteMCP.TestRunner.Context
**Purpose**: Track execution state and results
```objectscript
Class ExecuteMCP.TestRunner.Context Extends %RegisteredObject
{
    Property CurrentClass As %String;
    Property CurrentMethod As %String;
    Property StartTime As %TimeStamp;
    Property EndTime As %TimeStamp;
    
    /// Store assertion results
    Property Assertions As list Of %DynamicObject;
    
    /// Store test messages
    Property Messages As list Of %String;
    
    /// Add assertion result
    Method AddAssertion(pSuccess As %Boolean, pAction As %String, pDescription As %String)
    
    /// Add test message
    Method AddMessage(pMessage As %String)
    
    /// Get results as JSON
    Method GetResults() As %DynamicObject
}
```

#### 5. ExecuteMCP.TestRunner.Reporter
**Purpose**: Format and filter results
```objectscript
Class ExecuteMCP.TestRunner.Reporter Extends %RegisteredObject
{
    /// Format results as JSON
    ClassMethod FormatResults(pContext As ExecuteMCP.TestRunner.Context) As %String
    
    /// Apply filters to results
    ClassMethod FilterResults(pResults As %DynamicObject, pFilter As %String) As %DynamicObject
    
    /// Generate summary statistics
    ClassMethod GenerateSummary(pResults As %DynamicObject) As %DynamicObject
}
```

#### 6. ExecuteMCP.TestRunner.Filter
**Purpose**: Test filtering capabilities
```objectscript
Class ExecuteMCP.TestRunner.Filter Extends %RegisteredObject
{
    /// Parse filter string
    ClassMethod ParseFilter(pFilter As %String) As %DynamicObject
    
    /// Check if test matches filter
    ClassMethod MatchesFilter(pClassName As %String, pMethodName As %String, pFilter As %DynamicObject) As %Boolean
}
```

## Implementation Details

### Discovery Algorithm
1. Query %Dictionary.CompiledClassDefinition for classes in package
2. Check each class for %UnitTest.TestCase inheritance using %Dictionary.CompiledClass
3. For each test class, query %Dictionary.CompiledMethod for methods starting with "Test"
4. Build manifest with hierarchical structure: Package -> Class -> Method

### Execution Flow
1. **Discovery Phase**
   - Build test manifest from compiled classes
   - Apply filters if specified
   
2. **Setup Phase**
   - Create Manager instance with Context
   - Initialize Reporter
   
3. **Execution Phase**
   - For each test class:
     - Create instance using %New()
     - Set Manager property for assertion support
     - Call OnBeforeAllTests
     - For each test method:
       - Call OnBeforeOneTest
       - Execute test method via $METHOD()
       - Call OnAfterOneTest
     - Call OnAfterAllTests
     
4. **Reporting Phase**
   - Collect results from Context
   - Apply formatting and filters
   - Return JSON response

### Assertion Macro Support
The test instance's Manager property will point to our custom Manager, which implements:
- LogAssert() - Called by assertion macros
- LogMessage() - Called by test logging

This maintains full compatibility with existing %UnitTest.TestCase tests.

## MCP Integration

### New MCP Tools

#### run_custom_tests
```python
@server.tool()
async def run_custom_tests(
    package: str,
    filter: str = "",
    namespace: str = "HSCUSTOM"
) -> str:
    """
    Run tests using custom TestRunner (no filesystem dependency).
    
    Args:
        package: Package name to test (e.g., "ExecuteMCP.Test")
        filter: Optional filter (e.g., "class:SampleUnitTest" or "method:TestAddition")
        namespace: Target namespace
    
    Returns:
        JSON with test results including pass/fail counts and details
    """
```

#### get_test_packages
```python
@server.tool()
async def get_test_packages(
    namespace: str = "HSCUSTOM"
) -> str:
    """
    Discover all packages containing test classes.
    
    Returns:
        JSON list of packages with test class counts
    """
```

## Key Advantages

1. **No Filesystem Dependency**
   - Works entirely with compiled classes
   - No need for ^UnitTestRoot or file paths
   - Eliminates VS Code sync issues

2. **Direct Control**
   - Custom discovery logic
   - Full control over execution order
   - Flexible result formatting

3. **Better Error Handling**
   - Captures all errors without process crashes
   - Detailed failure information
   - No timeout issues

4. **Enhanced Features**
   - Package-based discovery
   - Method-level filtering
   - In-memory results
   - JSON-native output

## Migration Path

### For Existing Tests
- No changes required to test classes
- Continue using %UnitTest.TestCase
- All assertion macros work unchanged

### For New Tests
- Can use same base class and patterns
- Optional: Add metadata properties for enhanced filtering

### Parallel Operation
- Can coexist with UnitTestQueue implementation
- Users can choose which runner to use
- Gradual migration possible

## Implementation Phases

### Phase 1: Core Discovery (2 hours)
- Implement Discovery.cls with %Dictionary queries
- Create test manifest structure
- Validate against existing test classes

### Phase 2: Execution Engine (3 hours)
- Implement Manager.cls with LogAssert interface
- Create Executor.cls with lifecycle support
- Implement Context.cls for state tracking

### Phase 3: Reporting & Filtering (2 hours)
- Implement Reporter.cls for JSON formatting
- Add Filter.cls for test selection
- Create summary statistics

### Phase 4: MCP Integration (1 hour)
- Add run_custom_tests tool
- Add get_test_packages tool
- Update documentation

### Phase 5: Testing & Validation (2 hours)
- Test with existing test classes
- Validate assertion macro support
- Performance comparison
- Edge case handling

## Success Criteria

1. **Functional Requirements**
   - ✅ Discovers all test classes in package
   - ✅ Executes tests with full lifecycle support
   - ✅ Captures assertion results correctly
   - ✅ Returns JSON-formatted results
   - ✅ Supports filtering

2. **Non-Functional Requirements**
   - ✅ No filesystem dependencies
   - ✅ No VS Code sync issues
   - ✅ Sub-second response for discovery
   - ✅ Compatible with existing tests

3. **Quality Metrics**
   - Zero test discovery failures
   - 100% assertion macro compatibility
   - Clear error messages
   - Comprehensive result details

## Risk Mitigation

1. **Risk**: Assertion macro incompatibility
   - **Mitigation**: Implement exact LogAssert interface
   - **Validation**: Test with all macro types

2. **Risk**: Lifecycle method errors
   - **Mitigation**: Proper error handling in Executor
   - **Validation**: Test with complex lifecycle scenarios

3. **Risk**: Performance with large test suites
   - **Mitigation**: Efficient %Dictionary queries
   - **Validation**: Benchmark with 100+ tests

## Conclusion

The ExecuteMCP.TestRunner provides a robust, filesystem-independent solution for test execution in IRIS. By working directly with compiled classes and implementing the %UnitTest.TestCase interface, it maintains full compatibility while solving the core VS Code sync issues.

The modular design allows for easy maintenance and future enhancements, while the JSON-native output integrates seamlessly with modern tooling and MCP clients.
