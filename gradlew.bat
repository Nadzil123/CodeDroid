@rem Gradle wrapper for Windows
@if "%DEBUG%"=="" @echo off
set DIRNAME=%~dp0
set CLASSPATH=%DIRNAME%gradle\wrapper\gradle-wrapper.jar
set JAVA_EXE=%JAVA_HOME%\bin\java.exe
"%JAVA_EXE%" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
