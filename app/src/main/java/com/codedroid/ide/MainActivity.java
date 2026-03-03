package com.codedroid.ide;

import android.Manifest; import android.app.Activity; import android.app.AlertDialog;
import android.content.Intent; import android.content.pm.PackageManager;
import android.graphics.Color; import android.os.Build; import android.os.Bundle;
import android.os.Handler; import android.os.Looper;
import android.text.SpannableString; import android.text.style.ForegroundColorSpan;
import android.view.KeyEvent; import android.view.View; import android.view.ViewGroup;
import android.widget.*; import java.io.*; import java.nio.file.Files; import java.util.*;

import io.github.rosemoe.sora.langs.textmate.TextMateLanguage;
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
        {"Tab","    "},{"{  }","{ }"}, {"[ ]","[]"}, {"( )","()"},
        {";",";"},{":",":" },{"#","#"},{"Undo",null},{"Redo",null}
    };

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.activity_main);
        pm = new ProjectManager(this);
        bindViews(); setupEditor(); setupTerminal(); setupKeyToolbar(); setupButtons();
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P &&
            checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[]{Manifest.permission.READ_EXTERNAL_STORAGE,Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQ_PERM);
        else loadLast();
    }

    private void bindViews(){
        codeEditor=findViewById(R.id.codeEditor); terminalOutput=findViewById(R.id.terminalOutput);
        terminalInput=findViewById(R.id.terminalInput); termScrollView=findViewById(R.id.termScrollView);
        fileTabs=findViewById(R.id.fileTabs); keyToolbar=findViewById(R.id.keyToolbar);
        terminalPanel=findViewById(R.id.terminalPanel); tvProjectName=findViewById(R.id.tvProjectName);
        btnRun=findViewById(R.id.btnRun);
    }

    private void setupEditor(){
        EditorTheme.apply(codeEditor);
        codeEditor.setTextSize(14); codeEditor.setLineNumberEnabled(true); codeEditor.setWordwrap(false);
    }

    private void setupTerminal(){
        terminalInput.setOnEditorActionListener((v,id,ev)->{
            if(ev!=null&&ev.getKeyCode()==KeyEvent.KEYCODE_ENTER){sendCmd();return true;} return false;
        });
        findViewById(R.id.btnInputSend).setOnClickListener(v->sendCmd());
        findViewById(R.id.btnClearTerminal).setOnClickListener(v->terminalOutput.setText(""));
        findViewById(R.id.btnTerminalClose).setOnClickListener(v->terminalPanel.setVisibility(View.GONE));
        print("CodeDroid v1.0 ⚡","#00D4FF");
        print("Ready.","#5A6A8A");
    }

    private void sendCmd(){
        String cmd=terminalInput.getText().toString().trim(); if(cmd.isEmpty())return;
        terminalInput.setText(""); print("❯ "+cmd,"#00D4FF");
        new Thread(()->{
            try{
                File cwd=currentProject!=null?currentProject.getDir():getFilesDir();
                Process proc=new ProcessBuilder("sh","-c",cmd).directory(cwd).redirectErrorStream(true).start();
                try(BufferedReader r=new BufferedReader(new InputStreamReader(proc.getInputStream()))){
                    String l; while((l=r.readLine())!=null){final String fl=l; h.post(()->print(fl,"#C0D4F0"));}
                }
                int ex=proc.waitFor(); if(ex!=0) h.post(()->print("Exit: "+ex,"#FF4757"));
            }catch(Exception e){h.post(()->print("Error: "+e.getMessage(),"#FF4757"));}
        }).start();
    }

    private void setupKeyToolbar(){
        for(String[] kv:KEYS){
            TextView btn=new TextView(this);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT,ViewGroup.LayoutParams.MATCH_PARENT);
            lp.setMargins(2,4,2,4); btn.setLayoutParams(lp);
            btn.setText(kv[0]); btn.setTextColor(Color.parseColor("#D4E0F7")); btn.setTextSize(12);
            btn.setGravity(android.view.Gravity.CENTER); btn.setPadding(18,0,18,0);
            btn.setBackground(getDrawable(R.drawable.key_btn_bg));
            btn.setClickable(true); btn.setFocusable(true);
            final String ins=kv[1];
            btn.setOnClickListener(v->{
                if(kv[0].equals("Undo"))     codeEditor.undo();
                else if(kv[0].equals("Redo")) codeEditor.redo();
                else if(ins!=null)            codeEditor.insertText(ins,ins.length());
            });
            keyToolbar.addView(btn);
        }
    }

    private void setupButtons(){
        btnRun.setOnClickListener(v->{ if(running)stopRun(); else runCurrent(); });
        tvProjectName.setOnClickListener(v->startActivityForResult(new Intent(this,ProjectManagerActivity.class),REQ_PROJ));
        findViewById(R.id.btnFiles).setOnClickListener(v->openExplorer());
        findViewById(R.id.btnMenu).setOnClickListener(v->showMenu());
    }

    private void runCurrent(){
        if(currentFile==null){toast("No file open");return;} saveFile();
        running=true; btnRun.setText("■ Stop"); btnRun.setBackgroundResource(R.drawable.btn_stop_bg);
        terminalPanel.setVisibility(View.VISIBLE); print("\n▶ "+currentFile.getName(),"#00F5A0");
        activeRunner=RunnerFactory.getRunner(currentFile);
        activeRunner.run(currentFile, new RunCallback(){
            @Override public void onOutput(String l){h.post(()->print(l,"#C0D4F0"));}
            @Override public void onError(String l) {h.post(()->print(l,"#FF4757"));}
            @Override public void onFinish(int code){h.post(()->{
                running=false; btnRun.setText("▶  Run"); btnRun.setBackgroundResource(R.drawable.btn_run_bg);
                print(code==0?"✓ Done":"✗ Exit "+code, code==0?"#00F5A0":"#FF4757");
            });}
        });
    }

    private void stopRun(){
        if(activeRunner!=null)activeRunner.stop(); running=false;
        btnRun.setText("▶  Run"); btnRun.setBackgroundResource(R.drawable.btn_run_bg);
        print("■ Stopped","#FFD32A");
    }

    private void openFile(File file){
        if(!openFiles.contains(file))openFiles.add(file); currentFile=file;
        try{ codeEditor.setText(new String(Files.readAllBytes(file.toPath()))); setLang(file.getName());
        }catch(Exception e){toast("Cannot open: "+e.getMessage());} refreshTabs();
    }

    private void saveFile(){
        if(currentFile==null)return;
        try(FileWriter fw=new FileWriter(currentFile)){fw.write(codeEditor.getText().toString());}
        catch(Exception e){toast("Save failed");}
    }

    private void setLang(String n){
        String ex=n.contains(".")?n.substring(n.lastIndexOf('.')+1):"";
        try{ switch(ex){
            case"py": codeEditor.setEditorLanguage(TextMateLanguage.create("source.python",true)); break;
            case"lua":codeEditor.setEditorLanguage(TextMateLanguage.create("source.lua",true));    break;
            case"c":  codeEditor.setEditorLanguage(TextMateLanguage.create("source.c",true));      break;
            case"sh": codeEditor.setEditorLanguage(TextMateLanguage.create("source.shell",true));  break;
            default:  codeEditor.setEditorLanguage(null);
        }}catch(Exception ignored){}
    }

    private void refreshTabs(){
        fileTabs.removeAllViews();
        for(File f:openFiles){
            TextView t=new TextView(this);
            t.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT,ViewGroup.LayoutParams.MATCH_PARENT));
            t.setText("  "+f.getName()+"  "); t.setTextSize(12); t.setGravity(android.view.Gravity.CENTER);
            boolean act=f.equals(currentFile);
            t.setTextColor(Color.parseColor(act?"#00D4FF":"#5A6A8A"));
            t.setBackground(getDrawable(act?R.drawable.file_tab_active:R.drawable.file_tab_bg));
            t.setOnClickListener(v->openFile(f)); fileTabs.addView(t);
        }
    }

    private void openExplorer(){
        Intent i=new Intent(this,FileExplorerActivity.class);
        i.putExtra("root_path",currentProject!=null?currentProject.getDir().getAbsolutePath():pm.getProjectsRoot().getAbsolutePath());
        startActivityForResult(i,REQ_FILE);
    }

    private void showMenu(){
        new AlertDialog.Builder(this).setTitle("CodeDroid ⚡")
            .setItems(new String[]{"💾 Save","📂 Open File","🗂 Projects","⚙️ Settings","🐍 Python guide","⚙ C guide"},(d,w)->{
                switch(w){
                    case 0:saveFile();toast("Saved ✓");break;
                    case 1:openExplorer();break;
                    case 2:startActivityForResult(new Intent(this,ProjectManagerActivity.class),REQ_PROJ);break;
                    case 3:startActivity(new Intent(this,SettingsActivity.class));break;
                    case 4:guide("Python","pkg install python\n\nThen:\npython3 main.py");break;
                    case 5:guide("C Compiler","pkg install clang\n\nThen:\nclang main.c -o app && ./app");break;
                }
            }).show();
    }

    private void guide(String t,String m){
        new AlertDialog.Builder(this).setTitle(t).setMessage("In Termux:\n\n"+m).setPositiveButton("OK",null).show();
    }

    @Override protected void onActivityResult(int req,int res,Intent data){
        if(res!=RESULT_OK||data==null)return;
        if(req==REQ_FILE){ String fp=data.getStringExtra("file_path"); if(fp!=null)openFile(new File(fp)); }
        else if(req==REQ_PROJ){ String pp=data.getStringExtra("project_path"); if(pp!=null){Project p=pm.loadProject(pp);if(p!=null){currentProject=p;tvProjectName.setText(p.getName());if(p.getMainFile()!=null)openFile(p.getMainFile());}}}
    }

    @Override public void onRequestPermissionsResult(int req,String[] p,int[] g){ loadLast(); }

    private void loadLast(){
        Project last=pm.getLastProject();
        if(last!=null){currentProject=last;tvProjectName.setText(last.getName());if(last.getMainFile()!=null)openFile(last.getMainFile());}
        else startActivityForResult(new Intent(this,ProjectManagerActivity.class),REQ_PROJ);
    }

    public void print(String text,String hex){
        SpannableString s=new SpannableString(text+"\n");
        s.setSpan(new ForegroundColorSpan(Color.parseColor(hex)),0,s.length(),0);
        terminalOutput.append(s);
        termScrollView.post(()->termScrollView.fullScroll(View.FOCUS_DOWN));
    }

    @Override public boolean onKeyDown(int code,KeyEvent ev){
        if(code==KeyEvent.KEYCODE_BACK){
            saveFile();
            if(isTaskRoot()){new AlertDialog.Builder(this).setTitle("Exit?").setPositiveButton("Exit",(d,w)->finish()).setNegativeButton("Cancel",null).show();return true;}
        }
        return super.onKeyDown(code,ev);
    }
    @Override protected void onPause(){ saveFile(); super.onPause(); }
    private void toast(String m){Toast.makeText(this,m,Toast.LENGTH_SHORT).show();}
}
