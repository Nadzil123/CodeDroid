package com.codedroid.ide.runner;
import android.content.Context;
import java.io.*;
import java.net.URL;
import java.nio.file.*;

/**
 * Runs .luau files using Luau CLI binary.
 * Luau is Roblox's typed Lua variant.
 *
 * Binary is auto-downloaded from GitHub releases
 * and cached in app's internal storage.
 *
 * Download URL: github.com/luau-lang/luau/releases
 */
public class LuauRunner implements CodeRunner {

    // Luau binary release URL (arm64 Android)
    private static final String LUAU_URL =
        "https://github.com/luau-lang/luau/releases/download/0.617/luau-linux-arm64";

    private final Context ctx;

    public LuauRunner(Context ctx) {
        this.ctx = ctx;
    }

    // Fallback constructor — without context, tries PATH
    public LuauRunner() {
        this.ctx = null;
    }

    @Override public void run(File file, RunCallback cb) {
        new Thread(() -> {
            String bin = detect(cb);
            if (bin == null) return;
            try {
                Process p = new ProcessBuilder(bin, file.getAbsolutePath())
                    .directory(file.getParentFile())
                    .redirectErrorStream(false).start();
                pipe(p.getInputStream(), cb::onOutput);
                pipe(p.getErrorStream(),  cb::onError);
                cb.onFinish(p.waitFor());
            } catch (Exception e) {
                cb.onError("Luau error: " + e.getMessage());
                cb.onFinish(1);
            }
        }).start();
    }

    private String detect(RunCallback cb) {
        // 1. Check Termux
        String[] paths = {
            "/data/data/com.termux/files/usr/bin/luau",
            "/usr/bin/luau", "luau"
        };
        for (String p : paths) {
            try { File f = new File(p); if (f.exists() && f.canExecute()) return p; }
            catch (Exception ignored) {}
        }

        // 2. Check cached binary in app files dir
        if (ctx != null) {
            File cached = new File(ctx.getFilesDir(), "luau");
            if (cached.exists() && cached.canExecute()) return cached.getAbsolutePath();

            // 3. Try to download
            cb.onOutput("Downloading Luau binary...");
            try {
                File tmp = new File(ctx.getFilesDir(), "luau_tmp");
                try (InputStream in = new URL(LUAU_URL).openStream();
                     OutputStream out = new FileOutputStream(tmp)) {
                    byte[] buf = new byte[8192]; int n;
                    while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
                }
                tmp.setExecutable(true);
                tmp.renameTo(cached);
                if (cached.exists() && cached.canExecute()) {
                    cb.onOutput("Luau downloaded OK!");
                    return cached.getAbsolutePath();
                }
            } catch (Exception e) {
                cb.onError("Download failed: " + e.getMessage());
            }
        }

        // 4. Fallback — try pkg install
        cb.onError("Luau not found.");
        cb.onError("Install via Termux: pkg install luau");
        cb.onError("Or: download from github.com/luau-lang/luau/releases");
        cb.onFinish(1);
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
