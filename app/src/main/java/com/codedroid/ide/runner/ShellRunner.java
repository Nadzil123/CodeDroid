package com.codedroid.ide.runner;
import java.io.*;
public class ShellRunner implements CodeRunner {
    @Override public void run(File file, RunCallback cb) {
        new Thread(() -> {
            try {
                Process p = new ProcessBuilder("sh", file.getAbsolutePath())
                    .directory(file.getParentFile()).redirectErrorStream(false).start();
                pipe(p.getInputStream(), cb::onOutput);
                pipe(p.getErrorStream(),  cb::onError);
                cb.onFinish(p.waitFor());
            } catch (Exception e) { cb.onError(e.getMessage()); cb.onFinish(1); }
        }).start();
    }
    private void pipe(InputStream is, java.util.function.Consumer<String> s) {
        new Thread(() -> {
            try (BufferedReader r = new BufferedReader(new InputStreamReader(is))) {
                String l; while ((l = r.readLine()) != null) s.accept(l);
            } catch (Exception ignored) {}
        }).start();
    }
}
