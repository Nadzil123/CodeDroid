package com.codedroid.ide.project;
import java.io.File;
public class Project {
    private final String name, language;
    private final File dir, mainFile;
    public Project(String n, String l, File d, File m){ name=n; language=l; dir=d; mainFile=m; }
    public String getName()     { return name; }
    public String getLanguage() { return language; }
    public File   getDir()      { return dir; }
    public File   getMainFile() { return mainFile; }
}
