package com.codedroid.ide.runner;
import java.io.*;

/**
 * Compiles and runs .c files using clang.
 * Requires Termux: pkg install clang
 */
public class CRunner implements CodeRunner {
    private static final String[] CC = {
        "/data/data/com.termux/files/usr/bin/clang",
        "/data/data/com.termux/files/usr/bin/gcc",
        "/data/data/com.termux/files/usr/bin/tcc",
        "clang", "gcc", "tcc"
    };

    @Override public void run(File src, RunCallback cb) {
        new Thread(() -> {
            String cc = detect();
            if (cc == null) {
                cb.onError("No C compiler. Install: pkg install clang");
                cb.onFinish(1); return;
            }
            File out = new File(src.getParent(), src.getName().replace(".c", ""));
            cb.onOutput("Compiling with " + new File(cc).getName() + "...");
            try {
                // Compile
                Process cp = new ProcessBuilder(cc,
                    src.getAbsolutePath(), "-o", out.getAbsolutePath())
                    .directory(src.getParentFile())
                    .redirectErrorStream(true).start();
                try (BufferedReader r = new BufferedReader(new InputStreamReader(cp.getInputStream()))) {
                    String l; while ((l = r.readLine()) != null) cb.onError(l);
                }
                if (cp.waitFor() != 0) {
                    cb.onError("Compile failed.");
                    cb.onFinish(1); return;
                }
                // FIXED: was "Compiled OK!\n" causing unclosed string literal
                cb.onOutput("Compiled OK!");
                out.setExecutable(true);

                // Run
                Process run = new ProcessBuilder(out.getAbsolutePath())
                    .directory(src.getParentFile())
                    .redirectErrorStream(false).start();
                pipe(run.getInputStream(), cb::onOutput);
                pipe(run.getErrorStream(),  cb::onError);
                int ex = run.waitFor();
                out.delete();
                cb.onFinish(ex);
            } catch (Exception e) {
                cb.onError("Error: " + e.getMessage());
                cb.onFinish(1);
            }
        }).start();
    }

    private String detect() {
        for (String c : CC) {
            try { File f = new File(c); if (f.exists() && f.canExecute()) return c; }
            catch (Exception ignored) {}
        }
        return null;
    }

    private void pipe(InputStream is, java.util.function.Consumer<String> s) {
        new Thread(() -> {
            try (BufferedReader r = new BufferedReader(new InputStreamReader(is))) {
                String l; while ((l = r.readLine()) != null) s.accept(l);
            } catch (Exception ignored) {}
        }).start();
    }
}
