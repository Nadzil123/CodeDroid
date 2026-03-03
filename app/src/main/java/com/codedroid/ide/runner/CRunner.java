package com.codedroid.ide.runner;
import java.io.*;
public class CRunner implements CodeRunner {
    private static final String[] CC = {
        "/data/data/com.termux/files/usr/bin/clang",
        "/data/data/com.termux/files/usr/bin/gcc",
        "/data/data/com.termux/files/usr/bin/tcc",
        "clang","gcc","tcc"
    };
    @Override public void run(File src, RunCallback cb) {
        new Thread(() -> {
            String cc = detect();
            if (cc == null) {
                cb.onError("No C compiler found.");
                cb.onError("Install via Termux: pkg install clang");
                cb.onFinish(1); return;
            }
            File bin = new File(src.getParent(), src.getName().replace(".c",""));
            cb.onOutput("Compiling with " + new File(cc).getName() + "...");
            try {
                Process cp = new ProcessBuilder(cc, src.getAbsolutePath(), "-o", bin.getAbsolutePath())
                    .directory(src.getParentFile()).redirectErrorStream(true).start();
                try(BufferedReader r=new BufferedReader(new InputStreamReader(cp.getInputStream()))){
                    String l; while((l=r.readLine())!=null) cb.onError(l);
                }
                if (cp.waitFor() != 0) { cb.onError("Compile failed."); cb.onFinish(1); return; }
                cb.onOutput("Compiled OK!");
                bin.setExecutable(true);
                Process run = new ProcessBuilder(bin.getAbsolutePath())
                    .directory(src.getParentFile()).redirectErrorStream(false).start();
                Thread o=rd(run.getInputStream(),cb::onOutput);
                Thread e=rd(run.getErrorStream(),cb::onError);
                o.start(); e.start(); o.join(); e.join();
                int ex=run.waitFor(); bin.delete(); cb.onFinish(ex);
            } catch(Exception e){ cb.onError("Error: "+e.getMessage()); cb.onFinish(1); }
        }).start();
    }
    private String detect(){for(String c:CC){try{File f=new File(c);if(f.exists()&&f.canExecute())return c;}catch(Exception e){}}return null;}
    private Thread rd(InputStream is,java.util.function.Consumer<String> s){return new Thread(()->{try(BufferedReader r=new BufferedReader(new InputStreamReader(is))){String l;while((l=r.readLine())!=null)s.accept(l);}catch(Exception e){}});}
}
