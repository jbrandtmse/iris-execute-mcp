ROUTINE %outUnitTest [Type=INC]
///
	; Copyright (c) 2024 by InterSystems Corporation.
	; Cambridge, Massachusetts, U.S.A.  All rights reserved.
	; Confidential property of InterSystems Corporation.
#def1arg AssertEquals(%args)      ..AssertEqualsViaMacro(##quote(%args),%args)
///
#def1arg AssertNotEquals(%args)   ..AssertNotEqualsViaMacro(##quote(%args),%args)
///
#def1arg AssertTrue(%args)        ..AssertTrueViaMacro(##quote(%args),%args)
///
#def1arg AssertNotTrue(%args)     ..AssertNotTrueViaMacro(##quote(%args),%args)
///
#def1arg AssertStatusOK(%args)    ..AssertStatusOKViaMacro(##quote(%args),%args)
///
#def1arg AssertStatusNotOK(%args) ..AssertStatusNotOKViaMacro(##quote(%args),%args)
///
#def1arg AssertStatusEquals(%args) ..AssertStatusEqualsViaMacro(##quote(%args),%args)
///
#def1arg AssertFilesSame(%args)   ..AssertFilesSameViaMacro(##quote(%args),%args)
///
#def1arg AssertFilesSQLUnorderedSame(%args)   ..AssertFilesSQLUnorderedSameViaMacro(##quote(%args),%args)
#;
///
#define LogMessage(%message)    ..LogMessage(%message)
///
#define AssertSuccess(%message)    ..AssertSuccessViaMacro(%message)
///
#define AssertFailure(%message)    ..AssertFailureViaMacro(%message)
///
#define AssertSkipped(%message)    ..AssertSkippedViaMacro(%message)
#;