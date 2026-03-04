package com.codedroid.ide.runner;
import org.mozilla.javascript.*;
import java.io.*;
import java.nio.file.Files;

/**
 * Runs .js files using Mozilla Rhino — pure Java JS engine.
 * No install needed. Works offline.
 * Supports ES5, partial ES6.
 */
public class JsRunner implements CodeRunner {
    @Override public void run(File file, RunCallback cb) {
        new Thread(() -> {
            Context cx = Context.enter();
            try {
                cx.setOptimizationLevel(-1);
                cx.setLanguageVersion(Context.VERSION_ES6);
                Scriptable scope = cx.initStandardObjects();

                // Override print() to pipe to terminal
                ScriptableObject.putProperty(scope, "print",
                    new BaseFunction() {
                        @Override public Object call(Context cx, Scriptable s, Scriptable t, Object[] args) {
                            StringBuilder sb = new StringBuilder();
                            for (Object a : args) sb.append(Context.toString(a));
                            cb.onOutput(sb.toString());
                            return Undefined.instance;
                        }
                    });
                // console.log
                ScriptableObject.putProperty(scope, "console",
                    cx.evaluateString(scope, "({log:print,error:print,warn:print})", "console", 1, null));

                String code = new String(Files.readAllBytes(file.toPath()));
                cx.evaluateString(scope, code, file.getName(), 1, null);
                cb.onFinish(0);

            } catch (EcmaError e) {
                cb.onError("JS error: " + e.getMessage());
                cb.onFinish(1);
            } catch (Exception e) {
                cb.onError("Error: " + e.getMessage());
                cb.onFinish(1);
            } finally {
                Context.exit();
            }
        }).start();
    }
}
