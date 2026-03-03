package com.codedroid.ide.runner;
import java.io.File;
public class RunnerFactory {
    public static CodeRunner getRunner(File file) {
        switch (ext(file.getName())) {
            case "py":  return new PythonRunner();
            case "lua": return new LuaRunner();
            case "c":   return new CRunner();
            default:    return new ShellRunner();
        }
    }
    static String ext(String n) { int i=n.lastIndexOf('.'); return i>=0?n.substring(i+1).toLowerCase():""; }
}
