/// Test Discovery Module - Package-based discovery using %Dictionary
/// Finds test classes and methods without filesystem dependencies
Class ExecuteMCP.TestRunner.Discovery Extends %RegisteredObject
{

/// Discover all test classes in a package that extend %UnitTest.TestCase
/// Returns a JSON string array of class names
ClassMethod DiscoverTestClasses(pPackage As %String) As %String
{
    Set tTestClasses = []
    Try {
        // Alternative approach: iterate through compiled classes
        // Use %Dictionary.CompiledClass which we know works
        Set tClassName = pPackage_"."
        Set tSQL = "SELECT ID FROM %Dictionary.CompiledClass WHERE ID %STARTSWITH ?"
        Set tStatement = ##class(%SQL.Statement).%New()
        Set tSC = tStatement.%Prepare(tSQL)
        If $$$ISERR(tSC) {
            Return tTestClasses.%ToJSON()
        }
        
        // Execute query with package prefix
        Set tResultSet = tStatement.%Execute(tClassName)
        
        // Check each class for TestCase inheritance
        While tResultSet.%Next() {
            Set tClassName = tResultSet.%Get("ID")
            If ..IsTestClass(tClassName) {
                Do tTestClasses.%Push(tClassName)
            }
        }
    }
    Catch ex {
        // Return empty array on error
    }
    
    Return tTestClasses.%ToJSON()
}

/// Check if a class extends %UnitTest.TestCase
/// Uses %Dictionary.CompiledClass to check inheritance chain
ClassMethod IsTestClass(pClassName As %String) As %Boolean
{
    Try {
        // Get the compiled class definition
        Set tClassDef = ##class(%Dictionary.CompiledClass).%OpenId(pClassName)
        If '$ISOBJECT(tClassDef) {
            Return 0
        }
        
        // Check the Super property for inheritance
        Set tSuper = tClassDef.Super
        
        // Direct check for %UnitTest.TestCase in super chain
        If tSuper [ "%UnitTest.TestCase" {
            Return 1
        }
        
        // Check each parent class recursively
        // Split the Super string by commas (multiple inheritance)
        For i=1:1:$LENGTH(tSuper, ",") {
            Set tParentClass = $ZSTRIP($PIECE(tSuper, ",", i), "<>W")
            If tParentClass = "%UnitTest.TestCase" {
                Return 1
            }
            // Recursively check parent classes
            If (tParentClass '= "") && (tParentClass '= "%RegisteredObject") && (tParentClass '= "%Library.RegisteredObject") {
                If ..IsTestClass(tParentClass) {
                    Return 1
                }
            }
        }
    }
    Catch ex {
        // Not a test class if we can't check
        Return 0
    }
    
    Return 0
}

/// Find all methods starting with "Test" in a class
/// Returns a JSON string array of method names
ClassMethod DiscoverTestMethods(pClassName As %String) As %String
{
    Set tMethods = []
    Try {
        // Open the compiled class
        Set tClassDef = ##class(%Dictionary.CompiledClass).%OpenId(pClassName)
        If '$ISOBJECT(tClassDef) {
            Return tMethods.%ToJSON()
        }
        
        // Get the methods collection
        Set tMethodDef = tClassDef.Methods
        Set tKey = ""
        For {
            Set tMethod = tMethodDef.GetNext(.tKey)
            Quit:tKey=""
            
            // Check if method name starts with "Test"
            If $EXTRACT(tMethod.Name, 1, 4) = "Test" {
                Do tMethods.%Push(tMethod.Name)
            }
        }
    }
    Catch ex {
        // Return empty array on error
    }
    
    Return tMethods.%ToJSON()
}

/// Build complete test manifest for a package
/// Returns JSON string with hierarchical structure
ClassMethod BuildTestManifest(pPackage As %String, pFilter As %String = "") As %String
{
    Set tManifest = {}
    Set tManifest.package = pPackage
    Set tManifest.filter = pFilter
    Set tManifest.timestamp = $ZDATETIME($HOROLOG, 3, 1, 3)
    Set tManifest.classes = []
    Set tManifest.totalTests = 0
    Set tManifest.totalClasses = 0
    
    Try {
        // Discover all test classes (returns JSON string)
        Set tTestClassesJSON = ..DiscoverTestClasses(pPackage)
        // Parse JSON back to array
        Set tTestClasses = [].%FromJSON(tTestClassesJSON)
        
        // Process each test class
        Set tIter = tTestClasses.%GetIterator()
        While tIter.%GetNext(.tKey, .tClassName) {
            // Check if class matches filter
            If (pFilter '= "") && (pFilter [ "class:") {
                Set tFilterClass = $PIECE($PIECE(pFilter, "class:", 2), " ", 1)
                If tClassName '[ tFilterClass {
                    Continue
                }
            }
            
            // Build class info
            Set tClassInfo = {}
            Set tClassInfo.className = tClassName
            Set tClassInfo.methods = []
            Set tClassInfo.methodCount = 0
            
            // Discover test methods (returns JSON string)
            Set tMethodsJSON = ..DiscoverTestMethods(tClassName)
            // Parse JSON back to array
            Set tMethods = [].%FromJSON(tMethodsJSON)
            
            // Process each method
            Set tMethodIter = tMethods.%GetIterator()
            While tMethodIter.%GetNext(.tMethodKey, .tMethodName) {
                // Check if method matches filter
                If (pFilter '= "") && (pFilter [ "method:") {
                    Set tFilterMethod = $PIECE($PIECE(pFilter, "method:", 2), " ", 1)
                    If tMethodName '[ tFilterMethod {
                        Continue
                    }
                }
                
                // Add method to class info
                Do tClassInfo.methods.%Push(tMethodName)
                Set tClassInfo.methodCount = tClassInfo.methodCount + 1
                Set tManifest.totalTests = tManifest.totalTests + 1
            }
            
            // Only add class if it has methods (after filtering)
            If tClassInfo.methodCount > 0 {
                Do tManifest.classes.%Push(tClassInfo)
                Set tManifest.totalClasses = tManifest.totalClasses + 1
            }
        }
        
        // Add discovery metadata
        Set tManifest.discoveryMethod = "Package-based (%Dictionary.CompiledClass)"
        Set tManifest.requiresFilesystem = $$$NO
        Set tManifest.success = $$$YES
    }
    Catch ex {
        Set tManifest.success = $$$NO
        Set tManifest.error = ex.DisplayString()
    }
    
    Return tManifest.%ToJSON()
}

/// Get all packages that contain test classes
/// Returns JSON array of packages with test classes
ClassMethod GetTestPackages() As %String
{
    Set tPackages = []
    Set tPackageMap = {}
    
    Try {
        // Query all classes using %Dictionary.CompiledClass
        Set tSQL = "SELECT ID FROM %Dictionary.CompiledClass"
        Set tStatement = ##class(%SQL.Statement).%New()
        Set tSC = tStatement.%Prepare(tSQL)
        If $$$ISERR(tSC) {
            Return tPackages.%ToJSON()
        }
        
        Set tResultSet = tStatement.%Execute()
        
        While tResultSet.%Next() {
            Set tClassName = tResultSet.%Get("ID")
            
            // Check if it's a test class
            If ..IsTestClass(tClassName) {
                // Extract package name
                Set tPackage = $PIECE(tClassName, ".", 1, $LENGTH(tClassName, ".") - 1)
                
                // Track package
                If tPackage '= "" {
                    If '$DATA(tPackageMap.%Get(tPackage)) {
                        Set tPackageInfo = {}
                        Set tPackageInfo.package = tPackage
                        Set tPackageInfo.testClassCount = 0
                        Do tPackageMap.%Set(tPackage, tPackageInfo)
                    }
                    Set tInfo = tPackageMap.%Get(tPackage)
                    Set tInfo.testClassCount = tInfo.testClassCount + 1
                }
            }
        }
        
        // Convert map to array
        Set tIter = tPackageMap.%GetIterator()
        While tIter.%GetNext(.tKey, .tValue) {
            Do tPackages.%Push(tValue)
        }
    }
    Catch ex {
        // Return empty array on error
    }
    
    Return tPackages.%ToJSON()
}

/// Quick validation that discovery is working
/// Returns JSON string with discovery status
ClassMethod ValidateDiscovery() As %String
{
    Set tResult = {}
    Try {
        // Test discovering our own test classes
        Set tManifestJSON = ..BuildTestManifest("ExecuteMCP.Test")
        
        // Parse JSON back to object for processing
        Set tManifest = {}.%FromJSON(tManifestJSON)
        
        Set tResult.success = tManifest.success
        Set tResult.testPackage = "ExecuteMCP.Test"
        Set tResult.classesFound = tManifest.totalClasses
        Set tResult.testsFound = tManifest.totalTests
        Set tResult.method = "Package-based discovery (%Dictionary.CompiledClass)"
        
        // Include class list for debugging
        If tManifest.totalClasses > 0 {
            Set tResult.classes = []
            Set tIter = tManifest.classes.%GetIterator()
            While tIter.%GetNext(.tKey, .tClass) {
                Set tClassSummary = tClass.className_" ("_tClass.methodCount_" tests)"
                Do tResult.classes.%Push(tClassSummary)
            }
        }
    }
    Catch ex {
        Set tResult.success = $$$NO
        Set tResult.error = ex.DisplayString()
    }
    
    Return tResult.%ToJSON()
}

}
