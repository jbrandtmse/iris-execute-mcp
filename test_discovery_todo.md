# Test Discovery Debugging TODO List

## Task Progress
- [x] Create new unit test examples in src (TestDiscovery package)
  - [x] Created TestDiscovery.SimpleTest with 3 test methods
  - [x] Created TestDiscovery.AdvancedTest with 5 test methods
- [x] Copy TestDiscovery files to C:\temp\TestDiscovery\
- [x] Test with /load qualifier (job ID: 03238618) - Still only found 3 tests
- [x] Compile TestDiscovery classes directly using MCP compile tools - Classes not in IRIS
- [x] Manually load classes using $system.OBJ.Load() 
- [x] Verify classes exist in IRIS after loading
- [x] Test discovery after manual loading (job ID: 96476050) - SUCCESS! 11 tests discovered
- [x] Confirm root cause: VS Code extension sync issue

## Root Cause Analysis - RESOLVED
- [x] Why VS Code isn't syncing TestDiscovery classes to IRIS
  - VS Code ObjectScript extension auto-sync not working for new classes
  - Only ExecuteMCP.Test.SampleUnitTest was synced
- [x] Why only SampleUnitTest.cls exists in C:\temp\ExecuteMCP\Test\
  - VS Code extension only synced that one file, not others
- [x] How %UnitTest.Manager discovers test classes
  - Discovers classes that are compiled in IRIS and extend %UnitTest.TestCase
  - /noload qualifier expects classes already in IRIS (VS Code workflow)
  - /load qualifier loads from filesystem (traditional workflow)
- [x] Impact of disabling auto-prefix feature
  - No impact on discovery - the issue was missing classes in IRIS

## Solution Summary
- **Problem**: TestDiscovery classes weren't being synced to IRIS by VS Code extension
- **Solution**: Manually load classes using $system.OBJ.Load() before running tests
- **Result**: All 11 tests now discoverable and passing (3 from SampleUnitTest, 3 from SimpleTest, 5 from AdvancedTest)
- **Workaround Commands**:
  ```objectscript
  do $system.OBJ.Load("C:\\iris-execute-mcp\\src\\TestDiscovery\\SimpleTest.cls","bck")
  do $system.OBJ.Load("C:\\iris-execute-mcp\\src\\TestDiscovery\\AdvancedTest.cls","bck")
  ```
