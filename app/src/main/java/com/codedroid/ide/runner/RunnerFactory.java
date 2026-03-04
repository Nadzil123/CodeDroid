package com.codedroid.ide.runner;
import java.io.File;

/**
 * Language support:
 *   .py   → PythonRunner  (Chaquopy — embedded Python 3.11)
 *   .lua  → LuaRunner     (LuaJ — pure Java, offline)
 *   .luau → LuauRunner    (Luau CLI binary)
 *   .js   → JsRunner      (Rhino — pure Java, offline)
 *   .c    → CRunner       (clang via Termux)
 *   .sh   → ShellRunner   (sh built-in)
 */
public class RunnerFactory {
    public static CodeRunner getRunner(File file) {
        switch (ext(file.getName())) {
            case "py":   return new PythonRunner();
            case "lua":  return new LuaRunner();
            case "luau": return new LuauRunner();
            case "js":   return new JsRunner();
            case "c":    return new CRunner();
            default:     return new ShellRunner();
        }
    }
    public static String ext(String n) {
        int i = n.lastIndexOf('.');
        return i >= 0 ? n.substring(i+1).toLowerCase() : "";
    }
}
