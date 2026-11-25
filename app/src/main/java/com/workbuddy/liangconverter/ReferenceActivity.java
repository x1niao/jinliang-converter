package com.workbuddy.liangconverter;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebView;

/** 离线展示“参考资料及文献”页面（内容来自 assets/reference.html） */
public class ReferenceActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_reference);

        WebView web = findViewById(R.id.ref_webview);
        web.getSettings().setDefaultTextEncodingName("utf-8");
        web.getSettings().setUseWideViewPort(true);
        web.getSettings().setLoadWithOverviewMode(true);
        web.loadUrl("file:///android_asset/reference.html");

        findViewById(R.id.btn_ref_back).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    @Override
    public void onBackPressed() {
        finish();
    }
}
