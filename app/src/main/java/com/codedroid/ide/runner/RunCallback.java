package com.codedroid.ide.runner;
public interface RunCallback {
    void onOutput(String line);
    void onError(String line);
    void onFinish(int exitCode);
}
