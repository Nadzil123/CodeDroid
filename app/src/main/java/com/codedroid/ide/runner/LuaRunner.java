package com.codedroid.ide.runner;
import org.luaj.vm2.*;
import org.luaj.vm2.lib.jse.JsePlatform;
import java.io.*;

/**
 * Runs .lua files using LuaJ — 100% pure Java.
 * No Termux, no install needed. Works offline.
 */
public class LuaRunner implements CodeRunner {
    @Override public void run(File file, RunCallback cb) {
        new Thread(() -> {
            Globals globals = JsePlatform.standardGlobals();
            PrintStream ps = new PrintStream(System.out) {
                @Override public void println(String x) { cb.onOutput(x); }
                @Override public void print(String x)   { cb.onOutput(x); }
            };
            globals.STDOUT = ps;
            globals.STDERR = ps;
            try {
                globals.load(new FileInputStream(file), "@" + file.getName(), "t", globals).call();
                cb.onFinish(0);
            } catch (LuaError e) {
                cb.onError("Lua error: " + e.getMessage());
                cb.onFinish(1);
            } catch (Exception e) {
                cb.onError("Error: " + e.getMessage());
                cb.onFinish(1);
            }
        }).start();
    }
}
