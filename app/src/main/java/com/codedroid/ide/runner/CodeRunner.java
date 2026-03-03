package com.codedroid.ide.runner;
import java.io.File;
public interface CodeRunner {
    void run(File file, RunCallback cb);
    default void stop() {}
}
