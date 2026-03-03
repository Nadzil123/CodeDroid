package com.codedroid.ide.project;
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
        // FIXED: replaced deprecated getExternalStorageDirectory() ✅
        File ext = ctx.getExternalFilesDir(null);
        if (ext == null) ext = ctx.getFilesDir(); // internal fallback
        projectsRoot = new File(ext, "projects");
        if (!projectsRoot.exists()) projectsRoot.mkdirs();
    }

    public File getProjectsRoot() { return projectsRoot; }

    public Project createProject(String name, String lang) throws Exception {
        File dir = new File(projectsRoot, sanitize(name));
        if (dir.exists()) throw new Exception("Already exists: " + name);
        dir.mkdirs();
        new File(dir,"src").mkdirs(); new File(dir,"out").mkdirs();
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
            JSONObject o = new JSONObject(read(metaF));
            String name=o.optString("name",dir.getName()), lang=o.optString("language","python");
            File main=new File(dir,o.optString("main","main.py"));
            prefs.edit().putString("last_project",path).apply();
            return new Project(name,lang,dir,main.exists()?main:null);
        } catch(Exception e){ return null; }
    }

    public Project getLastProject(){ String l=prefs.getString("last_project",null); return l!=null?loadProject(l):null; }

    public List<Project> getAllProjects(){
        List<Project> list=new ArrayList<>();
        try{ JSONArray a=new JSONArray(prefs.getString("project_list","[]")); for(int i=0;i<a.length();i++){Project p=loadProject(a.getString(i));if(p!=null)list.add(p);} }catch(Exception ignored){}
        return list;
    }

    private String ext(String l){switch(l){case"python":return"py";case"lua":return"lua";case"c":return"c";default:return"sh";}}
    private String sanitize(String s){return s.replaceAll("[^a-zA-Z0-9_\-]","_");}
    private void save(File f,String s)throws Exception{try(FileWriter w=new FileWriter(f)){w.write(s);}}
    private String read(File f)throws Exception{return new String(java.nio.file.Files.readAllBytes(f.toPath()));}
    private String template(String n,String l){switch(l){
        case"python":return"# "+n+"\n\ndef main():\n    print(\"Hello from "+n+"!\")\n\nif __name__==\"__main__\":\n    main()\n";
        case"lua":return"-- "+n+"\n\nlocal function main()\n    print(\"Hello from "+n+"!\")\nend\n\nmain()\n";
        case"c":return"#include <stdio.h>\n\nint main(){\n    printf(\"Hello from "+n+"!\\n\");\n    return 0;\n}\n";
        default:return"#!/bin/sh\necho \"Hello from "+n+"!\"\n";}}
    private void addToList(String path){try{JSONArray a=new JSONArray(prefs.getString("project_list","[]"));for(int i=0;i<a.length();i++)if(a.getString(i).equals(path))return;a.put(path);prefs.edit().putString("project_list",a.toString()).apply();}catch(Exception ignored){}}
}
