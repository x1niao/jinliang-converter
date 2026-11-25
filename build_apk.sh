#!/usr/bin/env bash
set -euo pipefail

BASE="C:/Users/Administrator/WorkBuddy/2026-11-25-13-01-49/android-build"
JDK_DIR=$(find "$BASE" -maxdepth 1 -type d -name "jdk-17*" | head -1)
export JAVA_HOME="$JDK_DIR"
export PATH="$JAVA_HOME/bin:$PATH"

BT="$BASE/sdk/android-14"
AJAR="$BASE/sdk/android-35/android.jar"
APP="$BASE/app/src/main"
OUT="$BASE/out"
STAGE="$OUT/stage"

rm -rf "$STAGE"
mkdir -p "$STAGE/gen" "$STAGE/classes" "$STAGE/dex"

echo "[1/7] compile resources..."
"$BT/aapt2.exe" compile --dir "$APP/res" -o "$STAGE/compiled.flata"

echo "[2/7] link resources..."
"$BT/aapt2.exe" link \
  -o "$STAGE/base.apk" \
  -I "$AJAR" \
  --manifest "$APP/AndroidManifest.xml" \
  "$STAGE/compiled.flata" \
  --java "$STAGE/gen" \
  --min-sdk-version 21 \
  --target-sdk-version 35 \
  --version-code 6 \
  --version-name "1.5"

echo "[3/7] javac..."
"$JAVA_HOME/bin/javac.exe" -encoding UTF-8 -source 17 -target 17 -cp "$AJAR" \
  -d "$STAGE/classes" \
  "$STAGE/gen/com/workbuddy/liangconverter/R.java" \
  "$APP/java/com/workbuddy/liangconverter/MainActivity.java" \
  "$APP/java/com/workbuddy/liangconverter/ReferenceActivity.java"

echo "[4/7] d8 dex..."
find "$STAGE/classes" -name "*.class" > "$STAGE/classlist.txt"
"$BT/d8.bat" --lib "$AJAR" --output "$STAGE/dex" @"$STAGE/classlist.txt"

echo "[5/7] inject dex and assets into apk..."
python -c "
import os, zipfile
with zipfile.ZipFile(r'$STAGE/base.apk', 'a') as z:
    z.write(r'$STAGE/dex/classes.dex', 'classes.dex')
    asset_dir = r'$APP/assets'
    for root, dirs, files in os.walk(asset_dir):
        for f in files:
            full = os.path.join(root, f)
            arc = 'assets/' + os.path.relpath(full, asset_dir).replace(os.sep, '/')
            z.write(full, arc)
"

echo "[6/7] zipalign + sign..."
"$BT/zipalign.exe" -f 4 "$STAGE/base.apk" "$STAGE/aligned.apk"
"$JAVA_HOME/bin/keytool.exe" -genkeypair -v \
  -keystore "$STAGE/debug.jks" \
  -storepass android -keypass android \
  -alias debug -keyalg RSA -keysize 2048 -validity 3650 \
  -dname "CN=LiangConverter, OU=Dev, O=Dev, L=CN, ST=CN, C=CN" >/dev/null 2>&1
"$BT/apksigner.bat" sign \
  --ks "$STAGE/debug.jks" \
  --ks-pass pass:android --key-pass pass:android \
  --out "$OUT/LiangConverter.apk" \
  "$STAGE/aligned.apk"

echo "[7/7] verify..."
"$BT/apksigner.bat" verify --print-certs "$OUT/LiangConverter.apk"
ls -lh "$OUT/LiangConverter.apk"
echo "BUILD OK: $OUT/LiangConverter.apk"
