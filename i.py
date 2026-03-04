#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          CodeDroid Setup v3 — Full Rewrite                   ║
║                                                              ║
║  New in v3:                                                  ║
║  ✅ Python via Chaquopy (embedded, no Termux needed)         ║
║  ✅ .lua   → LuaJ (pure Java, offline)                       ║
║  ✅ .luau  → Luau CLI (download binary)                       ║
║  ✅ .py    → Chaquopy embedded Python 3.11                   ║
║  ✅ .c     → clang via Termux                                ║
║  ✅ .sh    → sh built-in                                     ║
║  ✅ .js    → Rhino JS engine (pure Java)                     ║
║  ✅ Fix: TextMateLanguage dihapus (build error fix)          ║
║  ✅ Fix: Unclosed string literal di CRunner                  ║
║  ✅ Fix: Illegal escape di ProjectManager                    ║
║  ✅ Fix: gradlew wrapper di root                             ║
║  ✅ GitHub Actions workflow included                         ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, sys, subprocess, shutil, time, stat, urllib.request

# ═══════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════

PACKAGE  = "com.codedroid.ide"
BASE_DIR = os.path.expanduser("~/CodeDroid-project")
GRADLE_V = "8.4"
STEPS    = 8

JAR_URL  = "https://github.com/gradle/gradle/raw/v8.4.0/gradle/wrapper/gradle-wrapper.jar"

# ═══════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════

RD="\033[91m"; GR="\033[92m"; YL="\033[93m"
CY="\033[96m"; WH="\033[97m"; DM="\033[2m"; RS="\033[0m"

def cl(t,c): return f"{c}{t}{RS}"
def ok(m):   print(f"  {cl('✓',GR)} {m}")
def warn(m): print(f"  {cl('⚠',YL)} {m}")
def info(m): print(f"  {cl('·',DM)} {cl(m,DM)}")
def die(m):  print(f"  {cl('✗',RD)} {m}"); sys.exit(1)
def step(n,msg): print(f"\n{cl(f'[{n}/{STEPS}]',CY)} {cl('━'*38,DM)} {cl(msg,WH)}")

def banner():
    print(cl(r"""
  ____          _       ____                _     _
 / ___|___   __| | ___ |  _ \ _ __ ___  (_) __| |
| |   / _ \ / _` |/ _ \| | | | '__/ _ \ | |/ _` |
| |__| (_) | (_| |  __/| |_| | | | (_) || | (_| |
 \____\___/ \__,_|\___||____/|_|  \___/ |_|\__,_|
    """, CY))
    print(cl("  Android Mini IDE — Setup v3.0\n", DM))

def run(cmd, cwd=None, timeout=180):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, cwd=cwd, timeout=timeout)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)

def write(path, content):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    ok(f"Written: {os.path.relpath(path, BASE_DIR)}")

def jp(s=""): return os.path.join(BASE_DIR,"app/src/main/java/com/codedroid/ide",s)
def rp(s=""): return os.path.join(BASE_DIR,"app/src/main/res",s)

# ═══════════════════════════════════════════════════
# STEP 1 — CHECK ENV
# ═══════════════════════════════════════════════════

def check_env():
    step(1, "Checking environment...")
    is_termux = os.path.isdir("/data/data/com.termux")
    ok("Termux ✓") if is_termux else warn("Not Termux")
    v = sys.version_info
    if not (v.major==3 and v.minor>=8): die(f"Need Python 3.8+")
    ok(f"Python {v.major}.{v.minor} ✓")
    print()
    info("Runner support in v3:")
    info("  .py   → Chaquopy (embedded Python 3.11, no Termux needed)")
    info("  .lua  → LuaJ (pure Java, offline)")
    info("  .luau → Luau CLI (auto-download binary)")
    info("  .js   → Rhino (pure Java JS engine)")
    info("  .c    → clang via Termux")
    info("  .sh   → sh built-in")
    return is_termux

# ═══════════════════════════════════════════════════
# STEP 2 — INSTALL PACKAGES
# ═══════════════════════════════════════════════════

def install_pkgs(is_termux):
    step(2, "Installing Termux packages...")
    if not is_termux:
        warn("Skipped — not in Termux")
        return
    run("pkg update -y")
    for pkg in ["openjdk-17","gradle","clang","git","wget","unzip","lua54"]:
        s,_ = run(f"pkg install -y {pkg}")
        (ok if s else warn)(f"pkg install {pkg}")
    jh = "/data/data/com.termux/files/usr/lib/jvm/java-17-openjdk"
    if os.path.isdir(jh):
        os.environ["JAVA_HOME"] = jh
        ok(f"JAVA_HOME set ✓")

# ═══════════════════════════════════════════════════
# STEP 3 — DIRECTORIES
# ═══════════════════════════════════════════════════

def create_dirs():
    step(3, "Creating directories...")
    for d in [
        "gradle/wrapper",
        ".github/workflows",
        "app/src/main/java/com/codedroid/ide",
        "app/src/main/java/com/codedroid/ide/runner",
        "app/src/main/java/com/codedroid/ide/project",
        "app/src/main/java/com/codedroid/ide/editor",
        "app/src/main/res/layout",
        "app/src/main/res/drawable",
        "app/src/main/res/values",
        "app/src/main/res/anim",
        "app/src/main/res/mipmap-hdpi",
    ]:
        os.makedirs(os.path.join(BASE_DIR,d), exist_ok=True)
    ok(f"Root: {BASE_DIR} ✓")

# ═══════════════════════════════════════════════════
# STEP 4 — GRADLE WRAPPER + GITHUB ACTIONS
# ═══════════════════════════════════════════════════

def setup_gradle():
    step(4, "Setting up Gradle wrapper + GitHub Actions...")

    write(f"{BASE_DIR}/gradle/wrapper/gradle-wrapper.properties",
f"""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-{GRADLE_V}-bin.zip
networkTimeout=10000
""")

    gw = os.path.join(BASE_DIR,"gradlew")
    with open(gw,"w",newline="\n") as f:
        f.write("""#!/bin/sh
APP_HOME=$(cd "$(dirname "$0")" && pwd -P)
CLASSPATH="$APP_HOME/gradle/wrapper/gradle-wrapper.jar"
JAVACMD="${JAVA_HOME:+$JAVA_HOME/bin/}java"
exec "$JAVACMD" -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
""")
    os.chmod(gw, os.stat(gw).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    ok("gradlew chmod +x ✓")

    write(f"{BASE_DIR}/gradlew.bat",
"""@rem Gradle wrapper Windows
@if "%DEBUG%"=="" @echo off
set CLASSPATH=%~dp0gradle\\wrapper\\gradle-wrapper.jar
"%JAVA_HOME%\\bin\\java.exe" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
""")

    # Download wrapper jar
    jar = os.path.join(BASE_DIR,"gradle/wrapper/gradle-wrapper.jar")
    try:
        info("Downloading gradle-wrapper.jar...")
        urllib.request.urlretrieve(JAR_URL, jar)
        if os.path.getsize(jar) > 5000:
            ok(f"gradle-wrapper.jar ✓")
    except Exception as e:
        warn(f"Download failed: {e}")
        s,_ = run(f"gradle wrapper --gradle-version {GRADLE_V}", cwd=BASE_DIR)
        (ok if s else warn)("gradle wrapper fallback")

    # GitHub Actions workflow
    write(f"{BASE_DIR}/.github/workflows/build.yml",
"""name: Build CodeDroid APK

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17

      - name: Setup Android SDK
        uses: android-actions/setup-android@v3

      - name: Make gradlew executable
        run: chmod +x gradlew

      - name: Build APK
        run: ./gradlew assembleDebug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: CodeDroid-APK
          path: app/build/outputs/apk/debug/app-debug.apk
          retention-days: 30
""")
    ok("GitHub Actions workflow ✓")

# ═══════════════════════════════════════════════════
# STEP 5 — GRADLE BUILD FILES
# ═══════════════════════════════════════════════════

def write_gradle():
    step(5, "Writing Gradle build files...")

    write(f"{BASE_DIR}/settings.gradle",
"""pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url 'https://jitpack.io' }
    }
}
rootProject.name = "CodeDroid"
include ':app'
""")

    write(f"{BASE_DIR}/build.gradle",
"""plugins {
    id 'com.android.application' version '8.2.0' apply false
}
""")

    # app/build.gradle — Chaquopy for Python, Rhino for JS, LuaJ for Lua
    write(f"{BASE_DIR}/app/build.gradle",
"""plugins {
    id 'com.android.application'
    id 'com.chaquo.python' version '15.0.1'
}

android {
    namespace "com.codedroid.ide"
    compileSdk 34

    defaultConfig {
        applicationId "com.codedroid.ide"
        minSdk 26
        targetSdk 34
        versionCode 1
        versionName "1.0"
        ndk { abiFilters "arm64-v8a", "x86_64" }

        python {
            version "3.11"
            pip { install "requests" }
        }
    }

    buildTypes {
        release { minifyEnabled false }
        debug   { debuggable true }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }

    packagingOptions {
        resources.excludes += ['META-INF/LICENSE*', 'META-INF/NOTICE*']
    }
}

dependencies {
    // UI
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.core:core:1.12.0'
    implementation 'com.google.android.material:material:1.11.0'

    // Sora Code Editor (syntax highlight — basic only, no textmate)
    implementation 'io.github.Rosemoe.sora-editor:editor:0.23.4'

    // Lua — pure Java, no install needed
    implementation 'org.luaj:luaj-jse:3.0.1'

    // JS — Rhino engine, pure Java
    implementation 'org.mozilla:rhino:1.7.15'

    // File utils
    implementation 'androidx.documentfile:documentfile:1.0.1'
}
""")

    write(f"{BASE_DIR}/gradle.properties",
"""android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
org.gradle.daemon=true
org.gradle.parallel=true
""")

# ═══════════════════════════════════════════════════
# STEP 6 — MANIFEST + RESOURCES
# ═══════════════════════════════════════════════════

def write_resources():
    step(6, "Writing manifest & resources...")

    write(f"{BASE_DIR}/app/src/main/AndroidManifest.xml",
"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28"/>

    <application
        android:label="CodeDroid"
        android:hardwareAccelerated="true"
        android:largeHeap="true"
        android:allowBackup="true"
        android:theme="@style/AppTheme">

        <activity android:name=".MainActivity" android:exported="true"
            android:windowSoftInputMode="adjustResize"
            android:configChanges="orientation|screenSize|keyboard">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <activity android:name=".FileExplorerActivity"   android:exported="false"/>
        <activity android:name=".ProjectManagerActivity" android:exported="false"/>
        <activity android:name=".SettingsActivity"       android:exported="false"/>
    </application>
</manifest>
""")

    write(rp("values/styles.xml"),
"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.NoActionBar">
        <item name="colorPrimary">#00D4FF</item>
        <item name="colorPrimaryDark">#080A0F</item>
        <item name="colorAccent">#7C5BF7</item>
        <item name="android:windowBackground">#080A0F</item>
    </style>
</resources>
""")
    write(rp("values/colors.xml"),
"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="bg">#080A0F</color>
    <color name="surface">#0E1119</color>
    <color name="surface2">#141824</color>
    <color name="border">#1F2840</color>
    <color name="accent">#00D4FF</color>
    <color name="text">#D4E0F7</color>
    <color name="muted">#5A6A8A</color>
    <color name="green">#00F5A0</color>
    <color name="red">#FF4757</color>
</resources>
""")
    write(rp("values/strings.xml"),
'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="app_name">CodeDroid</string>\n</resources>\n')

    for name,content in {
"btn_run_bg.xml":        '<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#00D4FF"/><corners android:radius="8dp"/></shape>',
"btn_stop_bg.xml":       '<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#FF4757"/><corners android:radius="8dp"/></shape>',
"key_btn_bg.xml":        '<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#141824"/><corners android:radius="6dp"/><stroke android:width="1dp" android:color="#1F2840"/></shape>',
"input_bg.xml":          '<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#0A0D18"/><corners android:radius="8dp"/><stroke android:width="1dp" android:color="#1F2840"/></shape>',
"file_tab_bg.xml":       '<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#0E1119"/></shape>',
"file_tab_active.xml":   '<layer-list xmlns:android="http://schemas.android.com/apk/res/android"><item><shape><solid android:color="#080A0F"/></shape></item><item android:gravity="bottom"><shape android:shape="rectangle"><solid android:color="#00D4FF"/><size android:height="2dp"/></shape></item></layer-list>',
"lang_btn_bg.xml":       '<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#0E1119"/><corners android:radius="8dp"/><stroke android:width="1dp" android:color="#1F2840"/></shape>',
"lang_btn_selected.xml": '<shape xmlns:android="http://schemas.android.com/apk/res/android"><solid android:color="#001A22"/><corners android:radius="8dp"/><stroke android:width="1dp" android:color="#00D4FF"/></shape>',
    }.items():
        write(rp(f"drawable/{name}"), '<?xml version="1.0" encoding="utf-8"?>\n'+content)

    write(rp("anim/slide_up.xml"),   '<?xml version="1.0" encoding="utf-8"?>\n<translate xmlns:android="http://schemas.android.com/apk/res/android" android:fromYDelta="100%p" android:toYDelta="0%p" android:duration="280" android:interpolator="@android:anim/decelerate_interpolator"/>\n')
    write(rp("anim/slide_down.xml"), '<?xml version="1.0" encoding="utf-8"?>\n<translate xmlns:android="http://schemas.android.com/apk/res/android" android:fromYDelta="0%p" android:toYDelta="100%p" android:duration="220" android:interpolator="@android:anim/accelerate_interpolator"/>\n')

# ═══════════════════════════════════════════════════
# STEP 7 — JAVA FILES
# ═══════════════════════════════════════════════════

def write_java():
    step(7, "Writing Java source files...")

    # ── Interfaces ────────────────────────────────
    write(jp("runner/RunCallback.java"),
"package com.codedroid.ide.runner;\npublic interface RunCallback {\n    void onOutput(String line);\n    void onError(String line);\n    void onFinish(int exitCode);\n}\n")

    write(jp("runner/CodeRunner.java"),
"package com.codedroid.ide.runner;\nimport java.io.File;\npublic interface CodeRunner {\n    void run(File file, RunCallback cb);\n    default void stop() {}\n}\n")

    # ── RunnerFactory — supports .py .lua .luau .js .c .sh ──
    write(jp("runner/RunnerFactory.java"),
"""package com.codedroid.ide.runner;
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
""")

    # ── ShellRunner ───────────────────────────────
    write(jp("runner/ShellRunner.java"),
"""package com.codedroid.ide.runner;
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
""")

    # ── LuaRunner — LuaJ pure Java ────────────────
    write(jp("runner/LuaRunner.java"),
"""package com.codedroid.ide.runner;
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
""")

    # ── LuauRunner — Luau CLI binary ──────────────
    write(jp("runner/LuauRunner.java"),
"""package com.codedroid.ide.runner;
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
""")

    # ── PythonRunner — Chaquopy embedded ─────────
    write(jp("runner/PythonRunner.java"),
"""package com.codedroid.ide.runner;
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
            if (!out.isEmpty()) for (String l : out.split("\\n")) cb.onOutput(l);
            if (!err.isEmpty()) for (String l : err.split("\\n")) cb.onError(l);
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
""")

    # ── JsRunner — Rhino pure Java ────────────────
    write(jp("runner/JsRunner.java"),
"""package com.codedroid.ide.runner;
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
""")

    # ── CRunner — FIXED unclosed string literal ───
    write(jp("runner/CRunner.java"),
"""package com.codedroid.ide.runner;
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
                // FIXED: was "Compiled OK!\\n" causing unclosed string literal
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
""")

    # ── Project.java ──────────────────────────────
    write(jp("project/Project.java"),
"""package com.codedroid.ide.project;
import java.io.File;
public class Project {
    private final String name, language;
    private final File dir, mainFile;
    public Project(String n, String l, File d, File m) {
        name=n; language=l; dir=d; mainFile=m;
    }
    public String getName()     { return name; }
    public String getLanguage() { return language; }
    public File   getDir()      { return dir; }
    public File   getMainFile() { return mainFile; }
}
""")

    # ── ProjectManager — FIXED illegal escape ─────
    write(jp("project/ProjectManager.java"),
"""package com.codedroid.ide.project;
import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray; import org.json.JSONObject;
import java.io.*; import java.util.*;

public class ProjectManager {
    private final Context ctx;
    private final File projectsRoot;
    private final SharedPreferences prefs;

    public ProjectManager(Context ctx) {
        this.ctx   = ctx;
        this.prefs = ctx.getSharedPreferences("codedroid", Context.MODE_PRIVATE);
        File ext = ctx.getExternalFilesDir(null);
        if (ext == null) ext = ctx.getFilesDir();
        projectsRoot = new File(ext, "projects");
        if (!projectsRoot.exists()) projectsRoot.mkdirs();
    }

    public File getProjectsRoot() { return projectsRoot; }

    public Project createProject(String name, String lang) throws Exception {
        // FIXED: was "[^a-zA-Z0-9_\\-]" — illegal escape in Java string
        File dir = new File(projectsRoot, name.replaceAll("[^a-zA-Z0-9_-]", "_"));
        if (dir.exists()) throw new Exception("Already exists: " + name);
        dir.mkdirs();
        new File(dir,"src").mkdirs();
        new File(dir,"out").mkdirs();
        JSONObject meta = new JSONObject();
        meta.put("name",name); meta.put("language",lang);
        meta.put("created",System.currentTimeMillis());
        meta.put("main","main."+ext(lang));
        save(new File(dir,"project.json"), meta.toString(2));
        File main = new File(dir,"main."+ext(lang));
        save(main, template(name,lang));
        addToList(dir.getAbsolutePath());
        prefs.edit().putString("last_project",dir.getAbsolutePath()).apply();
        return new Project(name,lang,dir,main);
    }

    public Project loadProject(String path) {
        try {
            File dir=new File(path), metaF=new File(dir,"project.json");
            if (!metaF.exists()) return null;
            JSONObject o=new JSONObject(read(metaF));
            String name=o.optString("name",dir.getName()), lang=o.optString("language","python");
            File main=new File(dir,o.optString("main","main.py"));
            prefs.edit().putString("last_project",path).apply();
            return new Project(name,lang,dir,main.exists()?main:null);
        } catch(Exception e){ return null; }
    }

    public Project getLastProject(){
        String l=prefs.getString("last_project",null);
        return l!=null ? loadProject(l) : null;
    }

    public List<Project> getAllProjects(){
        List<Project> list=new ArrayList<>();
        try {
            JSONArray a=new JSONArray(prefs.getString("project_list","[]"));
            for(int i=0;i<a.length();i++){
                Project p=loadProject(a.getString(i));
                if(p!=null) list.add(p);
            }
        } catch(Exception ignored){}
        return list;
    }

    private String ext(String l){
        switch(l){
            case"python": return"py"; case"lua": return"lua";
            case"luau": return"luau"; case"js": return"js";
            case"c": return"c"; default: return"sh";
        }
    }

    private String template(String n, String l){
        switch(l){
            case"python": return "# "+n+"\n\ndef main():\n    print(\"Hello from "+n+"!\")\n\nif __name__ == \"__main__\":\n    main()\n";
            case"lua":    return "-- "+n+"\n\nlocal function main()\n    print(\"Hello from "+n+"!\")\nend\n\nmain()\n";
            case"luau":   return "-- "+n+" (Luau)\n\nlocal function main()\n    print(\"Hello from "+n+"!\")\nend\n\nmain()\n";
            case"js":     return "// "+n+"\n\nfunction main() {\n    print(\"Hello from "+n+"!\");\n}\n\nmain();\n";
            case"c":      return "#include <stdio.h>\n\nint main() {\n    printf(\"Hello from "+n+"!\\n\");\n    return 0;\n}\n";
            default:      return "#!/bin/sh\necho \"Hello from "+n+"!\"\n";
        }
    }

    private void save(File f,String s) throws Exception {
        try(FileWriter w=new FileWriter(f)){w.write(s);}
    }
    private String read(File f) throws Exception {
        return new String(java.nio.file.Files.readAllBytes(f.toPath()));
    }
    private void addToList(String path){
        try{
            JSONArray a=new JSONArray(prefs.getString("project_list","[]"));
            for(int i=0;i<a.length();i++) if(a.getString(i).equals(path)) return;
            a.put(path);
            prefs.edit().putString("project_list",a.toString()).apply();
        } catch(Exception ignored){}
    }
}
""")

    # ── EditorTheme ───────────────────────────────
    write(jp("editor/EditorTheme.java"),
"""package com.codedroid.ide.editor;
import android.graphics.Color;
import io.github.rosemoe.sora.widget.CodeEditor;
import io.github.rosemoe.sora.widget.schemes.SchemeDarcula;
public class EditorTheme {
    public static void apply(CodeEditor editor) {
        SchemeDarcula s = new SchemeDarcula();
        s.setColor(SchemeDarcula.WHOLE_BACKGROUND,       Color.parseColor("#080A0F"));
        s.setColor(SchemeDarcula.LINE_NUMBER_BACKGROUND, Color.parseColor("#0E1119"));
        s.setColor(SchemeDarcula.LINE_NUMBER,            Color.parseColor("#2A3A55"));
        s.setColor(SchemeDarcula.CURRENT_LINE,           Color.parseColor("#0D1525"));
        s.setColor(SchemeDarcula.SELECTION_INSERT,       Color.parseColor("#00D4FF"));
        s.setColor(SchemeDarcula.TEXT_NORMAL,            Color.parseColor("#D4E0F7"));
        editor.setColorScheme(s);
    }
}
""")

    # ── MainActivity — FIXED: no TextMateLanguage ─
    write(jp("MainActivity.java"),
"""package com.codedroid.ide;

import android.Manifest; import android.app.Activity; import android.app.AlertDialog;
import android.content.Intent; import android.content.pm.PackageManager;
import android.graphics.Color; import android.os.Build; import android.os.Bundle;
import android.os.Handler; import android.os.Looper;
import android.text.SpannableString; import android.text.style.ForegroundColorSpan;
import android.view.KeyEvent; import android.view.View; import android.view.ViewGroup;
import android.widget.*;
import java.io.*; import java.nio.file.Files; import java.util.*;

import io.github.rosemoe.sora.widget.CodeEditor;
import com.codedroid.ide.editor.EditorTheme;
import com.codedroid.ide.project.*; import com.codedroid.ide.runner.*;

public class MainActivity extends Activity {

    private CodeEditor   codeEditor;
    private TextView     terminalOutput, btnRun, tvProjectName;
    private EditText     terminalInput;
    private ScrollView   termScrollView;
    private LinearLayout fileTabs, keyToolbar, terminalPanel;

    private ProjectManager pm;
    private Project        currentProject;
    private File           currentFile;
    private final List<File> openFiles = new ArrayList<>();
    private CodeRunner     activeRunner;
    private boolean        running = false;
    private final Handler  h = new Handler(Looper.getMainLooper());

    private static final int REQ_FILE=3001, REQ_PROJ=3002, REQ_PERM=3003;
    private static final String[][] KEYS = {
        {"Tab","    "}, {"{ }","{ }"}, {"[ ]","[]"}, {"( )","()"},
        {";",";"}, {":",":" }, {"#","#"}, {"Undo",null}, {"Redo",null}
    };

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_main);
        pm = new ProjectManager(this);
        bindViews(); setupEditor(); setupTerminal(); setupKeyToolbar(); setupButtons();
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P &&
            checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[]{Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQ_PERM);
        else loadLast();
    }

    private void bindViews() {
        codeEditor=findViewById(R.id.codeEditor);
        terminalOutput=findViewById(R.id.terminalOutput);
        terminalInput=findViewById(R.id.terminalInput);
        termScrollView=findViewById(R.id.termScrollView);
        fileTabs=findViewById(R.id.fileTabs);
        keyToolbar=findViewById(R.id.keyToolbar);
        terminalPanel=findViewById(R.id.terminalPanel);
        tvProjectName=findViewById(R.id.tvProjectName);
        btnRun=findViewById(R.id.btnRun);
    }

    private void setupEditor() {
        EditorTheme.apply(codeEditor);
        codeEditor.setTextSize(14);
        codeEditor.setLineNumberEnabled(true);
        codeEditor.setWordwrap(false);
    }

    private void setupTerminal() {
        terminalInput.setOnEditorActionListener((v,id,ev) -> {
            if (ev != null && ev.getKeyCode() == KeyEvent.KEYCODE_ENTER) { sendCmd(); return true; }
            return false;
        });
        findViewById(R.id.btnInputSend).setOnClickListener(v -> sendCmd());
        findViewById(R.id.btnClearTerminal).setOnClickListener(v -> terminalOutput.setText(""));
        findViewById(R.id.btnTerminalClose).setOnClickListener(v -> terminalPanel.setVisibility(View.GONE));
        print("CodeDroid v3.0 \\u26a1", "#00D4FF");
        print("Runners: Python(Chaquopy) Lua(LuaJ) Luau JS(Rhino) C Shell", "#5A6A8A");
    }

    private void sendCmd() {
        String cmd = terminalInput.getText().toString().trim();
        if (cmd.isEmpty()) return;
        terminalInput.setText("");
        print("\\u276f " + cmd, "#00D4FF");
        new Thread(() -> {
            try {
                File cwd = currentProject != null ? currentProject.getDir() : getFilesDir();
                Process p = new ProcessBuilder("sh","-c",cmd).directory(cwd).redirectErrorStream(true).start();
                try (BufferedReader r=new BufferedReader(new InputStreamReader(p.getInputStream()))) {
                    String l; while((l=r.readLine())!=null){final String fl=l; h.post(()->print(fl,"#C0D4F0"));}
                }
                int ex=p.waitFor();
                if (ex!=0) h.post(()->print("Exit: "+ex,"#FF4757"));
            } catch(Exception e){ h.post(()->print("Error: "+e.getMessage(),"#FF4757")); }
        }).start();
    }

    private void setupKeyToolbar() {
        for (String[] kv : KEYS) {
            TextView btn = new TextView(this);
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.MATCH_PARENT);
            lp.setMargins(2,4,2,4); btn.setLayoutParams(lp);
            btn.setText(kv[0]); btn.setTextColor(Color.parseColor("#D4E0F7"));
            btn.setTextSize(12); btn.setGravity(android.view.Gravity.CENTER);
            btn.setPadding(18,0,18,0);
            btn.setBackground(getDrawable(R.drawable.key_btn_bg));
            btn.setClickable(true); btn.setFocusable(true);
            final String ins = kv[1];
            btn.setOnClickListener(v -> {
                if (kv[0].equals("Undo"))      codeEditor.undo();
                else if (kv[0].equals("Redo")) codeEditor.redo();
                else if (ins != null)           codeEditor.insertText(ins, ins.length());
            });
            keyToolbar.addView(btn);
        }
    }

    private void setupButtons() {
        btnRun.setOnClickListener(v -> { if (running) stopRun(); else runCurrent(); });
        tvProjectName.setOnClickListener(v ->
            startActivityForResult(new Intent(this, ProjectManagerActivity.class), REQ_PROJ));
        findViewById(R.id.btnFiles).setOnClickListener(v -> openExplorer());
        findViewById(R.id.btnMenu).setOnClickListener(v -> showMenu());
    }

    private void runCurrent() {
        if (currentFile == null) { toast("No file open"); return; }
        saveFile();
        running = true;
        btnRun.setText("\\u25a0 Stop");
        btnRun.setBackgroundResource(R.drawable.btn_stop_bg);
        terminalPanel.setVisibility(View.VISIBLE);
        print("\\n\\u25b6 " + currentFile.getName(), "#00F5A0");

        // Pass context to runners that need it (Python, Luau)
        String ext = RunnerFactory.ext(currentFile.getName());
        switch (ext) {
            case "py":   activeRunner = new PythonRunner(this); break;
            case "luau": activeRunner = new LuauRunner(this);  break;
            default:     activeRunner = RunnerFactory.getRunner(currentFile);
        }

        activeRunner.run(currentFile, new RunCallback() {
            @Override public void onOutput(String l) { h.post(()->print(l,"#C0D4F0")); }
            @Override public void onError(String l)  { h.post(()->print(l,"#FF4757")); }
            @Override public void onFinish(int code) {
                h.post(()->{
                    running = false;
                    btnRun.setText("\\u25b6  Run");
                    btnRun.setBackgroundResource(R.drawable.btn_run_bg);
                    print(code==0 ? "\\u2713 Done" : "\\u2717 Exit "+code,
                        code==0 ? "#00F5A0" : "#FF4757");
                });
            }
        });
    }

    private void stopRun() {
        if (activeRunner != null) activeRunner.stop();
        running = false;
        btnRun.setText("\\u25b6  Run");
        btnRun.setBackgroundResource(R.drawable.btn_run_bg);
        print("\\u25a0 Stopped","#FFD32A");
    }

    private void openFile(File file) {
        if (!openFiles.contains(file)) openFiles.add(file);
        currentFile = file;
        try {
            codeEditor.setText(new String(Files.readAllBytes(file.toPath())));
        } catch (Exception e) { toast("Cannot open: " + e.getMessage()); }
        refreshTabs();
    }

    private void saveFile() {
        if (currentFile == null) return;
        try (FileWriter fw = new FileWriter(currentFile)) {
            fw.write(codeEditor.getText().toString());
        } catch (Exception e) { toast("Save failed"); }
    }

    private void refreshTabs() {
        fileTabs.removeAllViews();
        for (File f : openFiles) {
            TextView t = new TextView(this);
            t.setLayoutParams(new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.MATCH_PARENT));
            t.setText("  " + f.getName() + "  ");
            t.setTextSize(12); t.setGravity(android.view.Gravity.CENTER);
            boolean act = f.equals(currentFile);
            t.setTextColor(Color.parseColor(act ? "#00D4FF" : "#5A6A8A"));
            t.setBackground(getDrawable(act ? R.drawable.file_tab_active : R.drawable.file_tab_bg));
            t.setOnClickListener(v -> openFile(f));
            fileTabs.addView(t);
        }
    }

    private void openExplorer() {
        Intent i = new Intent(this, FileExplorerActivity.class);
        i.putExtra("root_path", currentProject!=null
            ? currentProject.getDir().getAbsolutePath()
            : pm.getProjectsRoot().getAbsolutePath());
        startActivityForResult(i, REQ_FILE);
    }

    private void showMenu() {
        new AlertDialog.Builder(this).setTitle("CodeDroid v3 \\u26a1")
            .setItems(new String[]{
                "\\ud83d\\udcbe Save",
                "\\ud83d\\udcc2 Open File",
                "\\ud83d\\uddc2 Projects",
                "\\u2699\\ufe0f Settings",
                "\\ud83d\\udc0d Python — Chaquopy info",
                "\\ud83c\\udf19 Lua / Luau info",
                "\\u2615 JS (Rhino) info",
                "\\u2699 C — install clang"
            }, (d,w) -> {
                switch(w) {
                    case 0: saveFile(); toast("Saved \\u2713"); break;
                    case 1: openExplorer(); break;
                    case 2: startActivityForResult(new Intent(this,ProjectManagerActivity.class),REQ_PROJ); break;
                    case 3: startActivity(new Intent(this,SettingsActivity.class)); break;
                    case 4: info("Python (Chaquopy)", "Python 3.11 embedded in APK.\\nNo Termux needed.\\nAdd packages in build.gradle:\\n  pip { install \\"requests\\" }"); break;
                    case 5: info("Lua / Luau", ".lua  → LuaJ (pure Java, offline)\\n.luau → Luau CLI (auto-downloaded)\\n\\nOr via Termux: pkg install lua54 luau"); break;
                    case 6: info("JavaScript", "Rhino JS engine (pure Java).\\nSupports ES5 + partial ES6.\\nUse print() or console.log()"); break;
                    case 7: info("C Compiler","Install via Termux:\\npkg install clang\\n\\nThen .c files compile automatically."); break;
                }
            }).show();
    }

    private void info(String title, String msg) {
        new AlertDialog.Builder(this).setTitle(title).setMessage(msg).setPositiveButton("OK",null).show();
    }

    @Override protected void onActivityResult(int req, int res, Intent data) {
        if (res != RESULT_OK || data == null) return;
        if (req == REQ_FILE) {
            String fp = data.getStringExtra("file_path");
            if (fp != null) openFile(new File(fp));
        } else if (req == REQ_PROJ) {
            String pp = data.getStringExtra("project_path");
            if (pp != null) {
                Project p = pm.loadProject(pp);
                if (p != null) {
                    currentProject = p;
                    tvProjectName.setText(p.getName());
                    if (p.getMainFile() != null) openFile(p.getMainFile());
                }
            }
        }
    }

    @Override public void onRequestPermissionsResult(int req, String[] p, int[] g) { loadLast(); }

    private void loadLast() {
        Project last = pm.getLastProject();
        if (last != null) {
            currentProject = last;
            tvProjectName.setText(last.getName());
            if (last.getMainFile() != null) openFile(last.getMainFile());
        } else {
            startActivityForResult(new Intent(this,ProjectManagerActivity.class), REQ_PROJ);
        }
    }

    public void print(String text, String hex) {
        SpannableString s = new SpannableString(text+"\\n");
        s.setSpan(new ForegroundColorSpan(Color.parseColor(hex)),0,s.length(),0);
        terminalOutput.append(s);
        termScrollView.post(()->termScrollView.fullScroll(View.FOCUS_DOWN));
    }

    @Override public boolean onKeyDown(int code, KeyEvent ev) {
        if (code == KeyEvent.KEYCODE_BACK) {
            saveFile();
            if (isTaskRoot()) {
                new AlertDialog.Builder(this).setTitle("Exit?")
                    .setPositiveButton("Exit",(d,w)->finish())
                    .setNegativeButton("Cancel",null).show();
                return true;
            }
        }
        return super.onKeyDown(code, ev);
    }

    @Override protected void onPause() { saveFile(); super.onPause(); }
    private void toast(String m) { Toast.makeText(this,m,Toast.LENGTH_SHORT).show(); }
}
""")

    # ── ProjectManagerActivity ────────────────────
    write(jp("ProjectManagerActivity.java"),
"""package com.codedroid.ide;
import android.app.Activity; import android.app.AlertDialog; import android.content.Intent;
import android.graphics.Color; import android.os.Bundle; import android.view.*;
import android.widget.*; import com.codedroid.ide.project.*; import java.util.List;

public class ProjectManagerActivity extends Activity {
    private ProjectManager pm; private ListView list;

    @Override protected void onCreate(Bundle b){
        super.onCreate(b); pm=new ProjectManager(this);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(Color.parseColor("#080A0F"));
        LinearLayout hdr=new LinearLayout(this);hdr.setOrientation(LinearLayout.HORIZONTAL);hdr.setGravity(android.view.Gravity.CENTER_VERTICAL);hdr.setBackgroundColor(Color.parseColor("#0E1119"));hdr.setPadding(8,0,12,0);hdr.setMinimumHeight(dp(50));
        TextView back=new TextView(this);back.setText("\\u2190");back.setTextSize(20);back.setTextColor(Color.parseColor("#5A6A8A"));back.setGravity(android.view.Gravity.CENTER);back.setMinWidth(dp(44));back.setMinimumHeight(dp(44));back.setOnClickListener(v->finish());
        TextView title=new TextView(this);title.setText("Projects");title.setTextSize(17);title.setTextColor(Color.parseColor("#D4E0F7"));title.setTypeface(null,android.graphics.Typeface.BOLD);LinearLayout.LayoutParams tlp=new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1);tlp.leftMargin=dp(4);title.setLayoutParams(tlp);
        TextView newBtn=new TextView(this);newBtn.setText("+ New");newBtn.setTextSize(13);newBtn.setTextColor(Color.parseColor("#080A0F"));newBtn.setBackgroundResource(R.drawable.btn_run_bg);newBtn.setGravity(android.view.Gravity.CENTER);newBtn.setPadding(dp(14),0,dp(14),0);newBtn.setMinimumHeight(dp(34));newBtn.setOnClickListener(v->newDialog());
        hdr.addView(back);hdr.addView(title);hdr.addView(newBtn);
        list=new ListView(this);list.setBackgroundColor(Color.parseColor("#080A0F"));list.setDivider(null);
        root.addView(hdr);root.addView(list,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        setContentView(root);refresh();
    }

    private void refresh(){
        List<Project> ps=pm.getAllProjects();
        if(ps.isEmpty()){newDialog();return;}
        String[] names=ps.stream().map(Project::getName).toArray(String[]::new);
        list.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_list_item_1,names));
        list.setOnItemClickListener((p,v,i,id)->pick(ps.get(i)));
        list.setOnItemLongClickListener((p,v,i,id)->{new AlertDialog.Builder(this).setTitle(ps.get(i).getName()).setItems(new String[]{"Open","Delete"},(d,w)->{if(w==0)pick(ps.get(i));else del(ps.get(i));}).show();return true;});
    }

    private void pick(Project p){Intent i=new Intent();i.putExtra("project_path",p.getDir().getAbsolutePath());setResult(RESULT_OK,i);finish();}

    private void newDialog(){
        View v=getLayoutInflater().inflate(R.layout.dialog_new_project,null);
        EditText name=v.findViewById(R.id.etProjectName);
        String[] sel={"python"};
        int[] ids={R.id.langPython,R.id.langLua,R.id.langC,R.id.langShell};
        String[] langs={"python","lua","c","shell"};
        for(int i=0;i<ids.length;i++){final int idx=i;v.findViewById(ids[i]).setOnClickListener(x->{sel[0]=langs[idx];for(int j=0;j<ids.length;j++)((TextView)v.findViewById(ids[j])).setBackgroundResource(j==idx?R.drawable.lang_btn_selected:R.drawable.lang_btn_bg);});}
        new AlertDialog.Builder(this).setView(v)
            .setPositiveButton("Create",(d,w)->{String n=name.getText().toString().trim();if(n.isEmpty()){Toast.makeText(this,"Enter name",Toast.LENGTH_SHORT).show();return;}try{pick(pm.createProject(n,sel[0]));}catch(Exception e){Toast.makeText(this,"Error: "+e.getMessage(),Toast.LENGTH_SHORT).show();}})
            .setNegativeButton("Cancel",(d,w)->{if(pm.getAllProjects().isEmpty())finish();}).setCancelable(false).show();
    }

    private void del(Project p){new AlertDialog.Builder(this).setTitle("Delete "+p.getName()+"?").setPositiveButton("Delete",(d,w)->{delDir(p.getDir());refresh();}).setNegativeButton("Cancel",null).show();}
    private void delDir(java.io.File f){if(f.isDirectory())for(java.io.File c:f.listFiles())delDir(c);f.delete();}
    private int dp(int d){return Math.round(d*getResources().getDisplayMetrics().density);}
}
""")

    # ── FileExplorerActivity ──────────────────────
    write(jp("FileExplorerActivity.java"),
"""package com.codedroid.ide;
import android.app.Activity;import android.app.AlertDialog;import android.content.Intent;
import android.os.Bundle;import android.view.*;import android.widget.*;
import java.io.File;import java.text.SimpleDateFormat;import java.util.*;

public class FileExplorerActivity extends Activity {
    private ListView list;private TextView tvPath;
    private File cur,root;private List<File> entries=new ArrayList<>();

    @Override protected void onCreate(Bundle b){
        super.onCreate(b);setContentView(R.layout.activity_file_explorer);
        list=findViewById(R.id.fileList);tvPath=findViewById(R.id.tvCurrentPath);
        String rp=getIntent().getStringExtra("root_path");
        root=new File(rp!=null?rp:getFilesDir().getAbsolutePath());cur=root;
        findViewById(R.id.btnBack).setOnClickListener(v->finish());
        findViewById(R.id.btnNewFile).setOnClickListener(v->et("New File","file.py",n->{try{new File(cur,n).createNewFile();load(cur);}catch(Exception e){}}));
        findViewById(R.id.btnNewFolder).setOnClickListener(v->et("New Folder","folder",n->{new File(cur,n).mkdirs();load(cur);}));
        list.setOnItemClickListener((p,v,i,id)->{File f=entries.get(i);if(f.isDirectory())load(f);else ret(f);});
        list.setOnItemLongClickListener((p,v,i,id)->{menu(entries.get(i));return true;});
        load(root);
    }

    private void load(File dir){
        cur=dir;tvPath.setText(dir.getAbsolutePath());entries.clear();
        if(!dir.equals(root)&&dir.getParentFile()!=null)entries.add(dir.getParentFile());
        File[] files=dir.listFiles();
        if(files!=null){Arrays.sort(files,(a,c)->a.isDirectory()!=c.isDirectory()?(a.isDirectory()?-1:1):a.getName().compareToIgnoreCase(c.getName()));Collections.addAll(entries,files);}
        SimpleDateFormat sdf=new SimpleDateFormat("dd/MM HH:mm",Locale.getDefault());
        list.setAdapter(new ArrayAdapter<File>(this,R.layout.item_file,entries){
            @Override public View getView(int pos,View cv,ViewGroup parent){
                if(cv==null)cv=getLayoutInflater().inflate(R.layout.item_file,parent,false);
                File f=entries.get(pos);boolean up=!cur.equals(root)&&pos==0;
                ((TextView)cv.findViewById(R.id.fileIcon)).setText(up?"\\ud83d\\udcc2":icon(f));
                ((TextView)cv.findViewById(R.id.fileName)).setText(up?"..":f.getName());
                ((TextView)cv.findViewById(R.id.fileMeta)).setText(up?"parent folder":f.isDirectory()?"folder":fmt(f.length())+" \\u00b7 "+sdf.format(new Date(f.lastModified())));
                return cv;
            }
        });
    }

    private void menu(File f){new AlertDialog.Builder(this).setTitle(f.getName()).setItems(new String[]{"Open","Rename","Delete"},(d,w)->{if(w==0){if(f.isDirectory())load(f);else ret(f);}else if(w==1)et("Rename",f.getName(),n->{f.renameTo(new File(f.getParent(),n));load(cur);});else new AlertDialog.Builder(this).setTitle("Delete?").setPositiveButton("Delete",(d2,w2)->{del(f);load(cur);}).setNegativeButton("Cancel",null).show();}).show();}
    private void et(String t,String h,java.util.function.Consumer<String> cb){EditText e=new EditText(this);e.setHint(h);new AlertDialog.Builder(this).setTitle(t).setView(e).setPositiveButton("OK",(d,w)->{String n=e.getText().toString().trim();if(!n.isEmpty())cb.accept(n);}).setNegativeButton("Cancel",null).show();}
    private void ret(File f){setResult(RESULT_OK,new Intent().putExtra("file_path",f.getAbsolutePath()));finish();}
    private void del(File f){if(f.isDirectory())for(File c:f.listFiles())del(c);f.delete();}
    private String icon(File f){if(f.isDirectory())return"\\ud83d\\udcc2";String n=f.getName().toLowerCase();if(n.endsWith(".py"))return"\\ud83d\\udc0d";if(n.endsWith(".lua")||n.endsWith(".luau"))return"\\ud83c\\udf19";if(n.endsWith(".js"))return"\\u2615";if(n.endsWith(".c")||n.endsWith(".h"))return"\\u2699";if(n.endsWith(".sh"))return"$";return"\\ud83d\\udcc4";}
    private String fmt(long b){if(b<1024)return b+"B";if(b<1048576)return String.format("%.1fKB",b/1024f);return String.format("%.1fMB",b/1048576f);}
    @Override public void onBackPressed(){if(!cur.equals(root)&&cur.getParentFile()!=null)load(cur.getParentFile());else super.onBackPressed();}
}
""")

    # ── SettingsActivity ──────────────────────────
    write(jp("SettingsActivity.java"),
"""package com.codedroid.ide;
import android.app.Activity;import android.content.SharedPreferences;
import android.graphics.Color;import android.os.Bundle;import android.view.*;import android.widget.*;
public class SettingsActivity extends Activity {
    private SharedPreferences prefs;
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);prefs=getSharedPreferences("codedroid_settings",MODE_PRIVATE);
        ScrollView sv=new ScrollView(this);sv.setBackgroundColor(Color.parseColor("#080A0F"));
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(16),dp(8),dp(16),dp(24));
        addHeader(root);addDiv(root,"EDITOR");
        addSlider(root,"Font Size","font_size",10,24,14);
        addSwitch(root,"Word Wrap","word_wrap",false);
        addSwitch(root,"Line Numbers","line_numbers",true);
        addSwitch(root,"Auto Save","auto_save",true);
        addDiv(root,"TERMINAL");
        addSwitch(root,"Show Terminal on Run","show_terminal",true);
        sv.addView(root);setContentView(sv);
    }
    private void addHeader(LinearLayout p){LinearLayout h=new LinearLayout(this);h.setOrientation(LinearLayout.HORIZONTAL);h.setGravity(android.view.Gravity.CENTER_VERTICAL);h.setPadding(0,dp(4),0,dp(20));TextView back=new TextView(this);back.setText("\\u2190");back.setTextSize(20);back.setTextColor(Color.parseColor("#5A6A8A"));back.setGravity(android.view.Gravity.CENTER);back.setMinWidth(dp(44));back.setMinimumHeight(dp(44));back.setOnClickListener(v->finish());TextView t=new TextView(this);t.setText("Settings");t.setTextSize(18);t.setTypeface(null,android.graphics.Typeface.BOLD);t.setTextColor(Color.parseColor("#D4E0F7"));t.setPadding(dp(8),0,0,0);h.addView(back);h.addView(t);p.addView(h);}
    private void addDiv(LinearLayout p,String l){TextView t=new TextView(this);t.setText(l);t.setTextSize(10);t.setTextColor(Color.parseColor("#5A6A8A"));t.setPadding(0,dp(14),0,dp(6));t.setLetterSpacing(.1f);p.addView(t);}
    private void addSwitch(LinearLayout parent,String label,String key,boolean def){LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(android.view.Gravity.CENTER_VERTICAL);row.setBackgroundColor(Color.parseColor("#0E1119"));row.setPadding(dp(14),dp(14),dp(14),dp(14));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);lp.bottomMargin=dp(2);row.setLayoutParams(lp);TextView t=new TextView(this);t.setText(label);t.setTextSize(14);t.setTextColor(Color.parseColor("#D4E0F7"));t.setLayoutParams(new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));Switch sw=new Switch(this);sw.setChecked(prefs.getBoolean(key,def));sw.setOnCheckedChangeListener((v,c)->prefs.edit().putBoolean(key,c).apply());row.addView(t);row.addView(sw);parent.addView(row);}
    private void addSlider(LinearLayout parent,String label,String key,int min,int max,int def){LinearLayout col=new LinearLayout(this);col.setOrientation(LinearLayout.VERTICAL);col.setBackgroundColor(Color.parseColor("#0E1119"));col.setPadding(dp(14),dp(12),dp(14),dp(12));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);lp.bottomMargin=dp(2);col.setLayoutParams(lp);LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(android.view.Gravity.CENTER_VERTICAL);TextView t=new TextView(this);t.setText(label);t.setTextSize(14);t.setTextColor(Color.parseColor("#D4E0F7"));t.setLayoutParams(new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));TextView val=new TextView(this);val.setTextSize(13);val.setTextColor(Color.parseColor("#00D4FF"));val.setText(String.valueOf(prefs.getInt(key,def)));row.addView(t);row.addView(val);col.addView(row);SeekBar sb=new SeekBar(this);sb.setMax(max-min);sb.setProgress(prefs.getInt(key,def)-min);sb.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){public void onProgressChanged(SeekBar s,int p,boolean u){int v=p+min;val.setText(String.valueOf(v));prefs.edit().putInt(key,v).apply();}public void onStartTrackingTouch(SeekBar s){}public void onStopTrackingTouch(SeekBar s){}});col.addView(sb);parent.addView(col);}
    private int dp(int d){return Math.round(d*getResources().getDisplayMetrics().density);}
}
""")
    ok("All Java files written ✓")

# ═══════════════════════════════════════════════════
# STEP 8 — LAYOUTS
# ═══════════════════════════════════════════════════

def write_layouts():
    step(8, "Writing layouts...")

    write(rp("layout/activity_main.xml"), """\
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:orientation="vertical" android:background="@color/bg">
    <LinearLayout android:id="@+id/topBar" android:layout_width="match_parent" android:layout_height="48dp"
        android:background="@color/surface" android:orientation="horizontal"
        android:gravity="center_vertical" android:paddingStart="10dp" android:paddingEnd="6dp" android:elevation="4dp">
        <TextView android:id="@+id/tvProjectName" android:layout_width="0dp" android:layout_weight="1"
            android:layout_height="wrap_content" android:text="CodeDroid" android:textColor="@color/accent"
            android:textSize="15sp" android:textStyle="bold" android:clickable="true" android:focusable="true"/>
        <TextView android:id="@+id/btnRun" android:layout_width="72dp" android:layout_height="32dp"
            android:text="&#9654;  Run" android:gravity="center" android:textColor="@color/bg"
            android:textSize="12sp" android:textStyle="bold" android:background="@drawable/btn_run_bg"
            android:clickable="true" android:focusable="true" android:layout_marginEnd="6dp"/>
        <TextView android:id="@+id/btnFiles" android:layout_width="36dp" android:layout_height="36dp"
            android:text="&#128194;" android:textSize="18sp" android:gravity="center"
            android:clickable="true" android:focusable="true"/>
        <TextView android:id="@+id/btnMenu" android:layout_width="36dp" android:layout_height="36dp"
            android:text="&#8942;" android:textSize="20sp" android:textColor="@color/muted"
            android:gravity="center" android:clickable="true" android:focusable="true"/>
    </LinearLayout>
    <HorizontalScrollView android:layout_width="match_parent" android:layout_height="36dp"
        android:background="@color/surface" android:scrollbars="none">
        <LinearLayout android:id="@+id/fileTabs" android:layout_width="wrap_content"
            android:layout_height="match_parent" android:orientation="horizontal"/>
    </HorizontalScrollView>
    <io.github.rosemoe.sora.widget.CodeEditor android:id="@+id/codeEditor"
        android:layout_width="match_parent" android:layout_height="0dp" android:layout_weight="1"/>
    <View android:layout_width="match_parent" android:layout_height="4dp" android:background="@color/border"/>
    <LinearLayout android:id="@+id/terminalPanel" android:layout_width="match_parent"
        android:layout_height="220dp" android:orientation="vertical" android:background="#060810">
        <LinearLayout android:layout_width="match_parent" android:layout_height="30dp"
            android:orientation="horizontal" android:gravity="center_vertical"
            android:background="@color/surface2" android:paddingStart="12dp" android:paddingEnd="4dp">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="TERMINAL" android:textColor="@color/muted" android:textSize="9sp"/>
            <View android:layout_width="0dp" android:layout_weight="1" android:layout_height="1dp"/>
            <TextView android:id="@+id/btnClearTerminal" android:layout_width="wrap_content"
                android:layout_height="24dp" android:text="clear" android:textColor="@color/muted"
                android:textSize="10sp" android:gravity="center" android:paddingStart="8dp"
                android:paddingEnd="8dp" android:clickable="true" android:focusable="true"/>
            <TextView android:id="@+id/btnTerminalClose" android:layout_width="30dp"
                android:layout_height="30dp" android:text="&#10005;" android:textColor="@color/muted"
                android:textSize="12sp" android:gravity="center" android:clickable="true" android:focusable="true"/>
        </LinearLayout>
        <ScrollView android:id="@+id/termScrollView" android:layout_width="match_parent"
            android:layout_height="0dp" android:layout_weight="1">
            <TextView android:id="@+id/terminalOutput" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:textColor="@color/text"
                android:textSize="12sp" android:fontFamily="monospace"
                android:padding="10dp" android:lineSpacingMultiplier="1.4"/>
        </ScrollView>
        <LinearLayout android:layout_width="match_parent" android:layout_height="38dp"
            android:orientation="horizontal" android:gravity="center_vertical"
            android:background="@color/surface2" android:paddingStart="10dp">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="&#10095;" android:textColor="@color/accent"
                android:textSize="13sp" android:layout_marginEnd="6dp"/>
            <EditText android:id="@+id/terminalInput" android:layout_width="0dp" android:layout_weight="1"
                android:layout_height="match_parent" android:background="@null"
                android:textColor="@color/text" android:textSize="12sp" android:fontFamily="monospace"
                android:hint="Enter command..." android:singleLine="true" android:imeOptions="actionDone"/>
            <TextView android:id="@+id/btnInputSend" android:layout_width="38dp" android:layout_height="32dp"
                android:text="&#8629;" android:textColor="@color/accent" android:textSize="16sp"
                android:gravity="center" android:clickable="true" android:focusable="true"/>
        </LinearLayout>
    </LinearLayout>
    <HorizontalScrollView android:layout_width="match_parent" android:layout_height="40dp"
        android:background="@color/surface2" android:scrollbars="none">
        <LinearLayout android:id="@+id/keyToolbar" android:layout_width="wrap_content"
            android:layout_height="40dp" android:orientation="horizontal"
            android:gravity="center_vertical" android:paddingStart="4dp" android:paddingEnd="4dp"/>
    </HorizontalScrollView>
</LinearLayout>
""")

    write(rp("layout/activity_file_explorer.xml"), """\
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:orientation="vertical" android:background="@color/bg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="50dp"
        android:background="@color/surface" android:orientation="horizontal"
        android:gravity="center_vertical" android:paddingStart="4dp" android:paddingEnd="10dp" android:elevation="4dp">
        <TextView android:id="@+id/btnBack" android:layout_width="44dp" android:layout_height="44dp"
            android:text="&#8592;" android:textSize="20sp" android:textColor="@color/muted"
            android:gravity="center" android:clickable="true" android:focusable="true"/>
        <LinearLayout android:layout_width="0dp" android:layout_weight="1"
            android:layout_height="wrap_content" android:orientation="vertical">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Files" android:textColor="@color/text" android:textSize="16sp" android:textStyle="bold"/>
            <TextView android:id="@+id/tvCurrentPath" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:textColor="@color/muted"
                android:textSize="10sp" android:maxLines="1" android:ellipsize="start"/>
        </LinearLayout>
        <TextView android:id="@+id/btnNewFile" android:layout_width="32dp" android:layout_height="32dp"
            android:text="+" android:textSize="22sp" android:textColor="@color/accent"
            android:gravity="center" android:layout_marginEnd="4dp" android:clickable="true" android:focusable="true"/>
        <TextView android:id="@+id/btnNewFolder" android:layout_width="32dp" android:layout_height="32dp"
            android:text="&#128193;" android:textSize="16sp" android:gravity="center"
            android:clickable="true" android:focusable="true"/>
    </LinearLayout>
    <ListView android:id="@+id/fileList" android:layout_width="match_parent"
        android:layout_height="match_parent" android:divider="#0D1020"
        android:dividerHeight="1dp" android:background="@color/bg"/>
</LinearLayout>
""")

    write(rp("layout/item_file.xml"), """\
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="52dp"
    android:orientation="horizontal" android:gravity="center_vertical"
    android:paddingStart="14dp" android:paddingEnd="12dp"
    android:background="?android:attr/selectableItemBackground">
    <TextView android:id="@+id/fileIcon" android:layout_width="30dp" android:layout_height="30dp"
        android:textSize="16sp" android:gravity="center" android:background="@color/surface2"/>
    <LinearLayout android:layout_width="0dp" android:layout_weight="1"
        android:layout_height="wrap_content" android:orientation="vertical" android:layout_marginStart="12dp">
        <TextView android:id="@+id/fileName" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:textColor="@color/text"
            android:textSize="13sp" android:maxLines="1" android:ellipsize="end"/>
        <TextView android:id="@+id/fileMeta" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:textColor="@color/muted"
            android:textSize="11sp" android:layout_marginTop="2dp"/>
    </LinearLayout>
</LinearLayout>
""")

    write(rp("layout/dialog_new_project.xml"), """\
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="wrap_content"
    android:orientation="vertical" android:background="@color/surface" android:padding="20dp">
    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="New Project" android:textColor="@color/text"
        android:textSize="18sp" android:textStyle="bold" android:layout_marginBottom="16dp"/>
    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="Project Name" android:textColor="@color/muted"
        android:textSize="11sp" android:layout_marginBottom="4dp"/>
    <EditText android:id="@+id/etProjectName" android:layout_width="match_parent"
        android:layout_height="42dp" android:background="@drawable/input_bg"
        android:textColor="@color/text" android:textSize="14sp"
        android:paddingStart="12dp" android:paddingEnd="12dp"
        android:hint="my_project" android:layout_marginBottom="14dp"/>
    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="Language" android:textColor="@color/muted"
        android:textSize="11sp" android:layout_marginBottom="8dp"/>
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="horizontal">
        <TextView android:id="@+id/langPython" android:layout_width="0dp" android:layout_weight="1"
            android:layout_height="40dp" android:text="&#128013; Python" android:gravity="center"
            android:textSize="11sp" android:background="@drawable/lang_btn_selected"
            android:textColor="@color/accent" android:layout_marginEnd="3dp"/>
        <TextView android:id="@+id/langLua" android:layout_width="0dp" android:layout_weight="1"
            android:layout_height="40dp" android:text="&#127769; Lua" android:gravity="center"
            android:textSize="11sp" android:background="@drawable/lang_btn_bg"
            android:textColor="@color/muted" android:layout_marginEnd="3dp"/>
        <TextView android:id="@+id/langC" android:layout_width="0dp" android:layout_weight="1"
            android:layout_height="40dp" android:text="&#9881; C" android:gravity="center"
            android:textSize="11sp" android:background="@drawable/lang_btn_bg"
            android:textColor="@color/muted" android:layout_marginEnd="3dp"/>
        <TextView android:id="@+id/langShell" android:layout_width="0dp" android:layout_weight="1"
            android:layout_height="40dp" android:text="$ Shell" android:gravity="center"
            android:textSize="11sp" android:background="@drawable/lang_btn_bg" android:textColor="@color/muted"/>
    </LinearLayout>
</LinearLayout>
""")
    ok("All layouts written ✓")

# ═══════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════

def summary(elapsed):
    print(cl("\n"+"═"*48, CY))
    print(cl(f"  ✅  DONE in {elapsed:.1f}s", GR))
    print(cl("═"*48+"\n", CY))
    print(cl("📁 Project: ", WH) + cl(BASE_DIR, CY))
    print()
    print(cl("🏗  Build:", WH))
    print(f"   {cl('cd '+BASE_DIR, YL)}")
    print(f"   {cl('./gradlew assembleDebug', YL)}")
    print()
    print(cl("📡 GitHub Actions:", WH))
    print(f"   {cl('git init && git add . && git commit -m init', YL)}")
    print(f"   {cl('git push  →  Actions tab → download APK', YL)}")
    print()
    print(cl("Runner support:", WH))
    print(f"   {cl('.py',   CY)}   Chaquopy — embedded Python 3.11 (no Termux!)")
    print(f"   {cl('.lua',  CY)}   LuaJ — pure Java, offline")
    print(f"   {cl('.luau', CY)}   Luau CLI — auto-download binary")
    print(f"   {cl('.js',   CY)}   Rhino — pure Java JS engine, offline")
    print(f"   {cl('.c',    CY)}   clang via Termux: pkg install clang")
    print(f"   {cl('.sh',   CY)}   sh built-in, always works")
    print()

# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

def main():
    banner()
    print(cl(f"  Output : {BASE_DIR}", DM))
    print(cl(f"  Package: {PACKAGE}\n", DM))
    if input(cl("  Continue? [Y/n] ", CY)).strip().lower() == 'n':
        print(cl("  Cancelled.", RD)); return
    t = time.time()
    is_termux = check_env()
    install_pkgs(is_termux)
    create_dirs()
    setup_gradle()
    write_gradle()
    write_resources()
    write_java()
    write_layouts()
    summary(time.time() - t)

if __name__ == "__main__":
    main()
