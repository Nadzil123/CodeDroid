package com.codedroid.ide.runner;
import com.chaquo.python.Python;
import com.chaquo.python.PyObject;
import com.chaquo.python.android.AndroidPlatform;
import android.content.Context;
import java.io.*;

/**
 * Runs .py files using Chaquopy — embedded Python 3.11.
 * NO Termux needed. Works fully offline.
 *
 * Chaquopy embeds CPython directly in the APK.
 * Supports: print(), input(), file I/O, most stdlib.
 * Install extra packages via build.gradle pip { install "..." }
 */
public class PythonRunner implements CodeRunner {

    private final Context ctx;

    public PythonRunner(Context ctx) {
        this.ctx = ctx;
    }

    // Fallback — try system python3
    public PythonRunner() {
        this.ctx = null;
    }

    @Override public void run(File file, RunCallback cb) {
        new Thread(() -> {
            // Try Chaquopy first
            if (ctx != null) {
                runWithChaquopy(file, cb);
            } else {
                runWithProcess(file, cb);
            }
        }).start();
    }

    private void runWithChaquopy(File file, RunCallback cb) {
        try {
            if (!Python.isStarted()) {
                Python.start(new AndroidPlatform(ctx));
            }
            Python py = Python.getInstance();

            // Redirect stdout/stderr
            PyObject sys    = py.getModule("sys");
            PyObject io     = py.getModule("io");
            PyObject stdout = io.callAttr("StringIO");
            PyObject stderr = io.callAttr("StringIO");
            sys.put("stdout", stdout);
            sys.put("stderr", stderr);

            // Read and exec script
            String code = new String(java.nio.file.Files.readAllBytes(file.toPath()));
            PyObject builtins = py.getBuiltins();
            builtins.callAttr("exec", code);

            // Get output
            String out = stdout.callAttr("getvalue").toString();
            String err = stderr.callAttr("getvalue").toString();
            if (!out.isEmpty()) for (String l : out.split("\n")) cb.onOutput(l);
            if (!err.isEmpty()) for (String l : err.split("\n")) cb.onError(l);
            cb.onFinish(0);

        } catch (Exception e) {
            cb.onError("Python error: " + e.getMessage());
            cb.onFinish(1);
        }
    }

    private void runWithProcess(File file, RunCallback cb) {
        String[] bins = {
            "/data/data/com.termux/files/usr/bin/python3",
            "/data/data/com.termux/files/usr/bin/python",
            "python3", "python"
        };
        String bin = null;
        for (String b : bins) {
            try { File f=new File(b); if(f.exists()&&f.canExecute()){bin=b;break;} }
            catch (Exception ignored) {}
        }
        if (bin == null) {
            cb.onError("Python not available.");
            cb.onError("Add Chaquopy to build.gradle for embedded Python.");
            cb.onFinish(1); return;
        }
        try {
            Process p = new ProcessBuilder(bin, "-u", file.getAbsolutePath())
                .directory(file.getParentFile())
                .redirectErrorStream(false).start();
            pipe(p.getInputStream(), cb::onOutput);
            pipe(p.getErrorStream(),  cb::onError);
            cb.onFinish(p.waitFor());
        } catch (Exception e) { cb.onError(e.getMessage()); cb.onFinish(1); }
    }

    private void pipe(InputStream is, java.util.function.Consumer<String> s) {
        new Thread(() -> {
            try (BufferedReader r = new BufferedReader(new InputStreamReader(is))) {
                String l; while ((l=r.readLine())!=null) s.accept(l);
            } catch (Exception ignored) {}
        }).start();
    }
}
