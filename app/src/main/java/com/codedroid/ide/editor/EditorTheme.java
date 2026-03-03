package com.codedroid.ide.editor;
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
