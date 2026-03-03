package com.codedroid.ide.runner;
import org.luaj.vm2.*; import org.luaj.vm2.lib.jse.JsePlatform;
import java.io.*;
public class LuaRunner implements CodeRunner {
    @Override public void run(File file, RunCallback cb) {
        new Thread(() -> {
            Globals g = JsePlatform.standardGlobals();
            PrintStream ps = new PrintStream(System.out) {
                @Override public void println(String x) { cb.onOutput(x); }
                @Override public void print(String x)   { cb.onOutput(x); }
            };
            g.STDOUT = ps; g.STDERR = ps;
            try {
                g.load(new FileInputStream(file), "@"+file.getName(), "t", g).call();
                cb.onFinish(0);
            } catch (LuaError e) { cb.onError(e.getMessage()); cb.onFinish(1);
            } catch (Exception e) { cb.onError("Error: "+e.getMessage()); cb.onFinish(1); }
        }).start();
    }
}
