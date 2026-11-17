#!/bin/bash
# Сборка Tushi-ogon.apk без Gradle. Инструменты: ~/.local/share/android-build (JDK 17 + SDK build-tools 34).
# Ключ подписи там же (tushi.keystore) — не терять: им подписываются обновления.
# Игра берётся из ../index.html через сборку для Яндекса (шрифт внутри), только без SDK Яндекса.
set -e
T=~/.local/share/android-build; BT=$T/sdk/build-tools/34.0.0; AJ=$T/sdk/platforms/android-34/android.jar
export JAVA_HOME=$T/jdk PATH=$T/jdk/bin:$PATH
cd "$(dirname "$0")"; B=build; rm -rf $B; mkdir -p $B/assets $B/gen $B/classes
python3 ../tools/build_yandex.py >/dev/null
grep -v '<script src="/sdk.js"></script>' ../yandex/build/index.html > $B/assets/index.html
cp -r ../yandex/build/fonts $B/assets/
# иконки приложения из промо-иконки
for d in mdpi:48 hdpi:72 xhdpi:96 xxhdpi:144 xxxhdpi:192; do
  mkdir -p res/mipmap-${d%%:*}; magick ../yandex/promo/icon-512.png -filter point -resize ${d##*:}x${d##*:} res/mipmap-${d%%:*}/ic_launcher.png
done
if [ ! -f $T/tushi.keystore ]; then
  head -c 24 /dev/urandom | base64 | tr -d '/+=' > $T/tushi.keystore.pass
  keytool -genkeypair -keystore $T/tushi.keystore -alias tushi -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass:file $T/tushi.keystore.pass -keypass:file $T/tushi.keystore.pass -dname "CN=Tushi ogon" >/dev/null 2>&1
fi
$BT/aapt2 compile --dir res -o $B/res.zip
$BT/aapt2 link -o $B/unsigned.apk -I $AJ --manifest AndroidManifest.xml -A $B/assets --java $B/gen $B/res.zip
javac -nowarn -source 8 -target 8 -bootclasspath $AJ -d $B/classes $(find src $B/gen -name '*.java') 2>&1 | grep -v "^warning\|^Note\|^1 warning" || true
$BT/d8 --release --lib $AJ --min-api 26 --output $B $(find $B/classes -name '*.class')
(cd $B && zip -q unsigned.apk classes.dex)
$BT/zipalign -f -p 4 $B/unsigned.apk $B/aligned.apk
$BT/apksigner sign --ks $T/tushi.keystore --ks-pass file:$T/tushi.keystore.pass --out ../Tushi-ogon.apk $B/aligned.apk
rm -f ../Tushi-ogon.apk.idsig
$BT/apksigner verify ../Tushi-ogon.apk && echo "Готово: $(cd .. && pwd)/Tushi-ogon.apk"
