package com.codedroid.ide.runner;
import java.io.*;
/**
 * Calls python3 binary via ProcessBuilder.
 * SANDBOX NOTE: On Android 12+ without root, accessing Termux
 * binaries may fail with "Permission denied". If so, use the
 * in-app terminal to run: python3 filename.py
 */
public class PythonRunner implements CodeRunner {
    private static final String[] BINS = {
        "/data/data/com.termux/files/usr/bin/python3",
        "/data/data/com.termux/files/usr/bin/python",
        "python3", "python"
    };
    @Override public void run(File file, RunCallback cb) {
        new Thread(() -> {
            String bin = detect();
            if (bin == null) {
                cb.onError("python3 not found.");
                cb.onError("Install via Termux: pkg install python");
                cb.onError("Then run manually: python3 " + file.getName());
                cb.onFinish(1); return;
            }
            try {
                Process proc = new ProcessBuilder(bin, "-u", file.getAbsolutePath())
                    .directory(file.getParentFile())
                    .redirectErrorStream(false).start();
                proc.getOutputStream().close();
                Thread o = rd(proc.getInputStream(), cb::onOutput);
                Thread e = rd(proc.getErrorStream(), cb::onError);
                o.start(); e.start(); o.join(); e.join();
                cb.onFinish(proc.waitFor());
            } catch (Exception ex) {
                cb.onError("Exec error: " + ex.getMessage());
                cb.onError("Try running manually in the terminal tab.");
                cb.onFinish(1);
            }
        }).start();
    }
    private String detect() {
        for (String b : BINS) { try { File f=new File(b); if(f.exists()&&f.canExecute()) return b; } catch(Exception ignored){} }
        return null;
    }
    private Thread rd(InputStream is, java.util.function.Consumer<String> s) {
        return new Thread(() -> { try(BufferedReader r=new BufferedReader(new InputStreamReader(is))){String l;while((l=r.readLine())!=null)s.accept(l);}catch(Exception ignored){} });
    }
}
