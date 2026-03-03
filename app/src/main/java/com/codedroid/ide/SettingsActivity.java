package com.codedroid.ide;

import android.app.Activity; import android.content.SharedPreferences;
import android.graphics.Color; import android.os.Bundle; import android.view.*;
import android.widget.*;

public class SettingsActivity extends Activity {
    private SharedPreferences prefs;

    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        prefs=getSharedPreferences("codedroid_settings",MODE_PRIVATE);
        ScrollView sv=new ScrollView(this); sv.setBackgroundColor(Color.parseColor("#080A0F"));
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(16),dp(8),dp(16),dp(24));

        addHeader(root); addDivider(root,"EDITOR");
        addSlider(root,"Font Size","font_size",10,24,14);
        addSwitch(root,"Word Wrap","word_wrap",false);
        addSwitch(root,"Line Numbers","line_numbers",true);
        addSwitch(root,"Auto Save","auto_save",true);
        addDivider(root,"TERMINAL");
        addSwitch(root,"Show Terminal on Run","show_terminal",true);

        sv.addView(root); setContentView(sv);
    }

    private void addHeader(LinearLayout p){
        LinearLayout h=new LinearLayout(this); h.setOrientation(LinearLayout.HORIZONTAL);
        h.setGravity(android.view.Gravity.CENTER_VERTICAL); h.setPadding(0,dp(4),0,dp(20));
        TextView back=new TextView(this); back.setText("←"); back.setTextSize(20);
        back.setTextColor(Color.parseColor("#5A6A8A")); back.setGravity(android.view.Gravity.CENTER);
        back.setMinWidth(dp(44)); back.setMinimumHeight(dp(44)); back.setOnClickListener(v->finish());
        TextView t=new TextView(this); t.setText("Settings"); t.setTextSize(18);
        t.setTypeface(null,android.graphics.Typeface.BOLD); t.setTextColor(Color.parseColor("#D4E0F7"));
        t.setPadding(dp(8),0,0,0); h.addView(back); h.addView(t); p.addView(h);
    }

    private void addDivider(LinearLayout p,String label){
        TextView t=new TextView(this); t.setText(label); t.setTextSize(10);
        t.setTextColor(Color.parseColor("#5A6A8A")); t.setPadding(0,dp(14),0,dp(6));
        t.setLetterSpacing(.1f); p.addView(t);
    }

    private void addSwitch(LinearLayout parent,String label,String key,boolean def){
        LinearLayout row=new LinearLayout(this); row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(android.view.Gravity.CENTER_VERTICAL); row.setBackgroundColor(Color.parseColor("#0E1119"));
        row.setPadding(dp(14),dp(14),dp(14),dp(14));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin=dp(2); row.setLayoutParams(lp);
        TextView t=new TextView(this); t.setText(label); t.setTextSize(14);
        t.setTextColor(Color.parseColor("#D4E0F7"));
        t.setLayoutParams(new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        Switch sw=new Switch(this); sw.setChecked(prefs.getBoolean(key,def));
        sw.setOnCheckedChangeListener((v,c)->prefs.edit().putBoolean(key,c).apply());
        row.addView(t); row.addView(sw); parent.addView(row);
    }

    private void addSlider(LinearLayout parent,String label,String key,int min,int max,int def){
        LinearLayout col=new LinearLayout(this); col.setOrientation(LinearLayout.VERTICAL);
        col.setBackgroundColor(Color.parseColor("#0E1119")); col.setPadding(dp(14),dp(12),dp(14),dp(12));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin=dp(2); col.setLayoutParams(lp);
        LinearLayout row=new LinearLayout(this); row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(android.view.Gravity.CENTER_VERTICAL);
        TextView t=new TextView(this); t.setText(label); t.setTextSize(14); t.setTextColor(Color.parseColor("#D4E0F7"));
        t.setLayoutParams(new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        TextView val=new TextView(this); val.setTextSize(13); val.setTextColor(Color.parseColor("#00D4FF"));
        val.setText(String.valueOf(prefs.getInt(key,def)));
        row.addView(t); row.addView(val); col.addView(row);
        SeekBar sb=new SeekBar(this); sb.setMax(max-min); sb.setProgress(prefs.getInt(key,def)-min);
        sb.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar s,int p,boolean u){int v=p+min;val.setText(String.valueOf(v));prefs.edit().putInt(key,v).apply();}
            public void onStartTrackingTouch(SeekBar s){} public void onStopTrackingTouch(SeekBar s){}
        });
        col.addView(sb); parent.addView(col);
    }

    private int dp(int d){return Math.round(d*getResources().getDisplayMetrics().density);}
}
