package com.codedroid.ide;
import android.app.Activity; import android.app.AlertDialog; import android.content.Intent;
import android.graphics.Color; import android.os.Bundle; import android.view.*;
import android.widget.*; import com.codedroid.ide.project.*; import java.util.List;

public class ProjectManagerActivity extends Activity {
    private ProjectManager pm; private ListView list;

    @Override protected void onCreate(Bundle b){
        super.onCreate(b); pm=new ProjectManager(this);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(Color.parseColor("#080A0F"));
        LinearLayout hdr=new LinearLayout(this);hdr.setOrientation(LinearLayout.HORIZONTAL);hdr.setGravity(android.view.Gravity.CENTER_VERTICAL);hdr.setBackgroundColor(Color.parseColor("#0E1119"));hdr.setPadding(8,0,12,0);hdr.setMinimumHeight(dp(50));
        TextView back=new TextView(this);back.setText("\u2190");back.setTextSize(20);back.setTextColor(Color.parseColor("#5A6A8A"));back.setGravity(android.view.Gravity.CENTER);back.setMinWidth(dp(44));back.setMinimumHeight(dp(44));back.setOnClickListener(v->finish());
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
