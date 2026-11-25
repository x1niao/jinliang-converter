package com.workbuddy.liangconverter;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * 旧两 / 现两 / 克 / 钱 换算器
 * 旧制：1斤 = 16两；现制：1斤 = 10两 = 500克，即现1两 = 50克
 * 钱制：1两 = 10钱（唐至今），旧1钱 = 3.125克，现1钱 = 5克
 * 输入一个数值即自动换算：旧两 -> 现两 -> 克 -> 钱
 */
public class MainActivity extends Activity implements View.OnClickListener {

    private static final BigDecimal OLD_LIANG_PER_JIN = new BigDecimal("16");
    private static final BigDecimal NEW_LIANG_PER_JIN = new BigDecimal("10");
    private static final BigDecimal GRAMS_PER_NEW_LIANG = new BigDecimal("50");
    private static final BigDecimal GRAMS_PER_OLD_LIANG = new BigDecimal("31.25");
    private static final BigDecimal QIAN_PER_LIANG = new BigDecimal("10");

    private boolean oldToNew = true;

    private TextView tabOld, tabNew, labelInput;
    private EditText inputValue;
    private TextView resultOldLiang, resultNewLiang, resultGrams;
    private TextView resultOldQian, resultNewQian, resultOldForm, resultNewForm;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tabOld = findViewById(R.id.tab_old);
        tabNew = findViewById(R.id.tab_new);
        labelInput = findViewById(R.id.label_input);
        inputValue = findViewById(R.id.input_value);
        resultOldLiang = findViewById(R.id.result_old_liang);
        resultNewLiang = findViewById(R.id.result_new_liang);
        resultGrams = findViewById(R.id.result_grams);
        resultOldQian = findViewById(R.id.result_old_qian);
        resultNewQian = findViewById(R.id.result_new_qian);
        resultOldForm = findViewById(R.id.result_old_form);
        resultNewForm = findViewById(R.id.result_new_form);

        tabOld.setOnClickListener(this);
        tabNew.setOnClickListener(this);
        findViewById(R.id.btn_reset).setOnClickListener(this);
        findViewById(R.id.btn_reference).setOnClickListener(this);

        // 输入变化即自动换算
        inputValue.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) { }

            @Override
            public void afterTextChanged(Editable s) {
                convert();
            }
        });

        updateMode();
        // 默认演示“半斤八两”：输入旧 8 两
        inputValue.setText("8");
    }

    @Override
    public void onClick(View v) {
        int id = v.getId();
        if (id == R.id.tab_old) {
            if (!oldToNew) {
                oldToNew = true;
                updateMode();
                inputValue.setText("8");
            }
        } else if (id == R.id.tab_new) {
            if (oldToNew) {
                oldToNew = false;
                updateMode();
                inputValue.setText("5");
            }
        } else if (id == R.id.btn_reset) {
            inputValue.setText("");
        } else if (id == R.id.btn_reference) {
            startActivity(new Intent(this, ReferenceActivity.class));
        }
    }

    private void updateMode() {
        if (oldToNew) {
            tabOld.setBackgroundResource(R.drawable.bg_tab_active);
            tabOld.setTextColor(0xFFFFFFFF);
            tabNew.setBackgroundResource(R.drawable.bg_tab_normal);
            tabNew.setTextColor(0xFF5A6675);
            labelInput.setText("请输入旧两数值");
            inputValue.setHint("例如：8");
        } else {
            tabNew.setBackgroundResource(R.drawable.bg_tab_active);
            tabNew.setTextColor(0xFFFFFFFF);
            tabOld.setBackgroundResource(R.drawable.bg_tab_normal);
            tabOld.setTextColor(0xFF5A6675);
            labelInput.setText("请输入现两数值");
            inputValue.setHint("例如：5");
        }
    }

    private void convert() {
        String text = inputValue.getText().toString().trim();
        if (TextUtils.isEmpty(text)) {
            clearResult();
            return;
        }

        BigDecimal value;
        try {
            value = new BigDecimal(text);
        } catch (NumberFormatException e) {
            clearResult();
            return;
        }
        if (value.signum() < 0) {
            clearResult();
            return;
        }

        BigDecimal totalOldLiang;
        BigDecimal totalNewLiang;
        BigDecimal grams;

        if (oldToNew) {
            totalOldLiang = value;
            grams = totalOldLiang.multiply(GRAMS_PER_OLD_LIANG);
            totalNewLiang = grams.divide(GRAMS_PER_NEW_LIANG, 6, RoundingMode.HALF_UP);
        } else {
            totalNewLiang = value;
            grams = totalNewLiang.multiply(GRAMS_PER_NEW_LIANG);
            totalOldLiang = grams.divide(GRAMS_PER_OLD_LIANG, 6, RoundingMode.HALF_UP);
        }

        resultOldLiang.setText(fmt(totalOldLiang) + " 两");
        resultNewLiang.setText(fmt(totalNewLiang) + " 两");
        resultGrams.setText(fmt(grams) + " 克");
        resultOldQian.setText(fmt(totalOldLiang.multiply(QIAN_PER_LIANG)) + " 钱");
        resultNewQian.setText(fmt(totalNewLiang.multiply(QIAN_PER_LIANG)) + " 钱");
        resultOldForm.setText(jinLiangForm(totalOldLiang, OLD_LIANG_PER_JIN));
        resultNewForm.setText(jinLiangForm(totalNewLiang, NEW_LIANG_PER_JIN));
    }

    private void clearResult() {
        resultOldLiang.setText("—");
        resultNewLiang.setText("—");
        resultGrams.setText("—");
        resultOldQian.setText("—");
        resultNewQian.setText("—");
        resultOldForm.setText("—");
        resultNewForm.setText("—");
    }

    private String jinLiangForm(BigDecimal totalLiang, BigDecimal liangPerJin) {
        BigDecimal jin = totalLiang.divideToIntegralValue(liangPerJin);
        BigDecimal rest = totalLiang.subtract(jin.multiply(liangPerJin));
        BigDecimal liang = rest.divideToIntegralValue(BigDecimal.ONE);
        BigDecimal qian = rest.subtract(liang).multiply(QIAN_PER_LIANG);
        return fmt(jin) + "斤 " + fmt(liang) + "两 " + fmt(qian) + "钱";
    }

    private String fmt(BigDecimal value) {
        BigDecimal v = value.setScale(6, RoundingMode.HALF_UP).stripTrailingZeros();
        if (v.scale() < 0) {
            v = v.setScale(0);
        }
        return v.toPlainString();
    }
}
