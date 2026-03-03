package com.codedroid.ide;

import android.app.Activity; import android.app.AlertDialog; import android.content.Intent;
import android.os.Bundle; import android.view.*; import android.widget.*;
import java.io.File; import java.text.SimpleDateFormat; import java.util.*;

public class FileExplorerActivity extends Activity {
    private ListView list; private TextView tvPath;
    private File currentDir, rootDir;
    private List<File> entries = new ArrayList<>();

    @Override protected void onCreate(Bundle b){
        super.onCreate(b); setContentView(R.layout.activity_file_explorer);
        list=findViewById(R.id.fileList); tvPath=findViewById(R.id.tvCurrentPath);
        String root=getIntent().getStringExtra("root_path");
        rootDir=new File(root!=null?root:getFilesDir().getAbsolutePath()); currentDir=rootDir;
        findViewById(R.id.btnBack).setOnClickListener(v->finish());
        findViewById(R.id.btnNewFile).setOnClickListener(v->et("New File","file.py",n->{try{new File(currentDir,n).createNewFile();load(currentDir);}catch(Exception e){}}));
        findViewById(R.id.btnNewFolder).setOnClickListener(v->et("New Folder","folder",n->{new File(currentDir,n).mkdirs();load(currentDir);}));
        list.setOnItemClickListener((p,v,i,id)->{File f=entries.get(i);if(f.isDirectory())load(f);else ret(f);});
        list.setOnItemLongClickListener((p,v,i,id)->{menu(entries.get(i));return true;});
        load(rootDir);
    }

    private void load(File dir){
        currentDir=dir; tvPath.setText(dir.getAbsolutePath()); entries.clear();
        if(!dir.equals(rootDir)&&dir.getParentFile()!=null) entries.add(dir.getParentFile());
        File[] files=dir.listFiles();
        if(files!=null){Arrays.sort(files,(a,c)->a.isDirectory()!=c.isDirectory()?(a.isDirectory()?-1:1):a.getName().compareToIgnoreCase(c.getName()));Collections.addAll(entries,files);}
        SimpleDateFormat sdf=new SimpleDateFormat("dd/MM HH:mm",Locale.getDefault());
        list.setAdapter(new ArrayAdapter<File>(this,R.layout.item_file,entries){
            @Override public View getView(int pos,View cv,ViewGroup parent){
                if(cv==null)cv=getLayoutInflater().inflate(R.layout.item_file,parent,false);
                File f=entries.get(pos); boolean up=!currentDir.equals(rootDir)&&pos==0;
                ((TextView)cv.findViewById(R.id.fileIcon)).setText(up?"📂":icon(f));
                ((TextView)cv.findViewById(R.id.fileName)).setText(up?"..":f.getName());
                ((TextView)cv.findViewById(R.id.fileMeta)).setText(up?"parent folder":f.isDirectory()?"folder":fmt(f.length())+" · "+sdf.format(new Date(f.lastModified())));
                return cv;
            }
        });
    }

    private void menu(File f){new AlertDialog.Builder(this).setTitle(f.getName()).setItems(new String[]{"Open","Rename","Delete"},(d,w)->{
        if(w==0){if(f.isDirectory())load(f);else ret(f);}
        else if(w==1)et("Rename",f.getName(),n->{f.renameTo(new File(f.getParent(),n));load(currentDir);});
        else new AlertDialog.Builder(this).setTitle("Delete?").setPositiveButton("Delete",(d2,w2)->{del(f);load(currentDir);}).setNegativeButton("Cancel",null).show();
    }).show();}

    private void et(String title,String hint,java.util.function.Consumer<String> cb){
        EditText e=new EditText(this);e.setHint(hint);
        new AlertDialog.Builder(this).setTitle(title).setView(e).setPositiveButton("OK",(d,w)->{String n=e.getText().toString().trim();if(!n.isEmpty())cb.accept(n);}).setNegativeButton("Cancel",null).show();
    }
    private void ret(File f){setResult(RESULT_OK,new Intent().putExtra("file_path",f.getAbsolutePath()));finish();}
    private void del(File f){if(f.isDirectory())for(File c:f.listFiles())del(c);f.delete();}
    private String icon(File f){if(f.isDirectory())return"📂";String n=f.getName().toLowerCase();if(n.endsWith(".py"))return"🐍";if(n.endsWith(".lua"))return"🌙";if(n.endsWith(".c")||n.endsWith(".h"))return"⚙";if(n.endsWith(".sh"))return"$";return"📄";}
    private String fmt(long b){if(b<1024)return b+"B";if(b<1048576)return String.format("%.1fKB",b/1024f);return String.format("%.1fMB",b/1048576f);}
    @Override public void onBackPressed(){if(!currentDir.equals(rootDir)&&currentDir.getParentFile()!=null)load(currentDir.getParentFile());else super.onBackPressed();}
}
