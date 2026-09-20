# -*- coding: utf-8 -*-
"""
字宝宝奇遇记 (Kids Literacy App) - 一键生成完整安卓工程脚本
运行方式：
    python setup_project.py
运行后会在当前目录下创建完整的 kids-literacy-app 工程结构。
"""

import os

# 定义工程文件内容字典
FILES = {
    # 1. GitHub Actions 自动编译打包工作流
    ".github/workflows/build_apk.yml": """name: Build Android APK

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 配置 JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: 赋予 Gradle 执行权限
        run: chmod +x gradlew || true

      - name: 设置 Gradle 缓存
        uses: gradle/actions/setup-gradle@v3

      - name: 编译 Debug APK
        run: ./gradlew assembleDebug --stacktrace

      - name: 上传 APK 安装包
        uses: actions/upload-artifact@v4
        with:
          name: 字宝宝奇遇记-测试版
          path: app/build/outputs/apk/debug/app-debug.apk
""",

    # 2. 根目录 settings.gradle.kts
    "settings.gradle.kts": """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "KidsLiteracy"
include(":app")
""",

    # 3. 根目录 build.gradle.kts
    "build.gradle.kts": """plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}
""",

    # 4. gradle-wrapper.properties
    "gradle/wrapper/gradle-wrapper.properties": """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.5-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""",

    # 5. gradlew (Linux/macOS wrapper 脚本)
    "gradlew": """#!/bin/sh
APP_BASE_NAME=`basename "$0"`
CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar
exec gradle wrapper "$@"
""",

    # 6. app/build.gradle.kts
    "app/build.gradle.kts": """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.kids.literacy"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.kids.literacy"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.8"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
}
""",

    # 7. app/proguard-rules.pro
    "app/proguard-rules.pro": """# Add project specific ProGuard rules here.
""",

    # 8. AndroidManifest.xml (横屏锁定、TTS支持、应用名)
    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <queries>
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
    </queries>

    <application
        android:allowBackup="true"
        android:icon="@android:drawable/sym_def_app_icon"
        android:label="字宝宝奇遇记"
        android:roundIcon="@android:drawable/sym_def_app_icon"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="sensorLandscape"
            android:configChanges="orientation|screenSize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
""",

    # 9. app/src/main/java/com/kids/literacy/MainActivity.kt (核心界面逻辑与字库)
    "app/src/main/java/com/kids/literacy/MainActivity.kt": """package com.kids.literacy

import android.os.Bundle
import android.speech.tts.TextToSpeech
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.util.Locale

data class WordItem(val char: String, val pinyin: String, val category: String)

class MainActivity : ComponentActivity(), TextToSpeech.OnInitListener {
    private var tts: TextToSpeech? = null
    private var isTtsReady by mutableStateOf(false)

    // 精选生活启蒙 20 字词表（可无缝扩展）
    private val wordList = listOf(
        WordItem("日", "rì", "自然"),
        WordItem("月", "yuè", "自然"),
        WordItem("水", "shuǐ", "自然"),
        WordItem("火", "huǒ", "自然"),
        WordItem("土", "tǔ", "自然"),
        WordItem("木", "mù", "自然"),
        WordItem("山", "shān", "自然"),
        WordItem("石", "shí", "自然"),
        WordItem("天", "tiān", "自然"),
        WordItem("地", "dì", "自然"),
        WordItem("人", "rén", "身体"),
        WordItem("口", "kǒu", "身体"),
        WordItem("目", "mù", "身体"),
        WordItem("耳", "ěr", "身体"),
        WordItem("手", "shǒu", "身体"),
        WordItem("足", "zú", "身体"),
        WordItem("大", "dà", "比较"),
        WordItem("小", "xiǎo", "比较"),
        WordItem("多", "duō", "比较"),
        WordItem("少", "shǎo", "比较")
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        tts = TextToSpeech(this, this)

        setContent {
            var currentWordIndex by remember { mutableStateOf(0) }
            var currentMode by remember { mutableStateOf(0) } // 0: 字卡, 1: 描红, 2: 喂兔子
            var carrotEatenCount by remember { mutableStateOf(0) }

            val currentWord = wordList[currentWordIndex]

            fun speak(text: String) {
                if (isTtsReady) {
                    tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
                }
            }

            // 主界面（横屏左右分栏）
            Row(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color(0xFFFFF9E6))
                    .padding(16.dp)
            ) {
                // 左侧学习与互动核心区 (占 70%)
                Column(
                    modifier = Modifier
                        .weight(0.72f)
                        .fillMaxHeight(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // 顶部导航模式标签
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        Button(
                            onClick = { currentMode = 0; speak(currentWord.char) },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (currentMode == 0) Color(0xFFFF9800) else Color(0xFFFFE0B2),
                                contentColor = if (currentMode == 0) Color.White else Color(0xFF5D4037)
                            ),
                            shape = RoundedCornerShape(14.dp)
                        ) { Text("📖 大字卡", fontSize = 18.sp, fontWeight = FontWeight.Bold) }

                        Button(
                            onClick = { currentMode = 1; speak("跟小兔子一起写写看") },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (currentMode == 1) Color(0xFFFF9800) else Color(0xFFFFE0B2),
                                contentColor = if (currentMode == 1) Color.White else Color(0xFF5D4037)
                            ),
                            shape = RoundedCornerShape(14.dp)
                        ) { Text("✏️ 手指描红", fontSize = 18.sp, fontWeight = FontWeight.Bold) }

                        Button(
                            onClick = { currentMode = 2; speak("小兔子想吃 ${currentWord.char}，快喂给它吧！") },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (currentMode == 2) Color(0xFFFF9800) else Color(0xFFFFE0B2),
                                contentColor = if (currentMode == 2) Color.White else Color(0xFF5D4037)
                            ),
                            shape = RoundedCornerShape(14.dp)
                        ) { Text("🥕 喂食小兔子", fontSize = 18.sp, fontWeight = FontWeight.Bold) }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // 核心卡片容器
                    Card(
                        modifier = Modifier
                            .fillMaxSize()
                            .shadow(6.dp, RoundedCornerShape(24.dp)),
                        shape = RoundedCornerShape(24.dp),
                        colors = CardDefaults.cardColors(containerColor = Color.White)
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(16.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            when (currentMode) {
                                0 -> FlashCardView(currentWord) { speak(currentWord.char) }
                                1 -> TracingView(currentWord.char)
                                2 -> FeedingGameView(
                                    targetWord = currentWord,
                                    allWords = wordList,
                                    onFeedSuccess = {
                                        carrotEatenCount++
                                        speak("太棒啦！小兔子吃饱啦！")
                                        if (currentWordIndex < wordList.size - 1) {
                                            currentWordIndex++
                                        } else {
                                            currentWordIndex = 0
                                        }
                                    }
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                // 右侧小兔子互动伴读区 (占 28%)
                Card(
                    modifier = Modifier
                        .weight(0.28f)
                        .fillMaxHeight()
                        .shadow(4.dp, RoundedCornerShape(24.dp)),
                    shape = RoundedCornerShape(24.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFFFECB3))
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "小兔萌萌 🐰",
                            fontWeight = FontWeight.Bold,
                            fontSize = 22.sp,
                            color = Color(0xFF5D4037)
                        )

                        // 小兔子动画/表情
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                text = if (carrotEatenCount > 0) "🐇💨" else "🐰",
                                fontSize = 80.sp
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = if (carrotEatenCount > 0) "“嚼嚼嚼~ 好好吃呀！”" else "“我有点饿啦...”",
                                fontSize = 15.sp,
                                color = Color(0xFF795548),
                                fontWeight = FontWeight.Medium
                            )
                        }

                        // 饱食度徽章
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = Color(0xFFFFCC80),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(
                                text = "已吃胡萝卜: $carrotEatenCount 根",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFFE65100),
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                            )
                        }

                        // 下一个汉字切换按钮
                        Button(
                            onClick = {
                                if (currentWordIndex < wordList.size - 1) currentWordIndex++ else currentWordIndex = 0
                                speak(wordList[currentWordIndex].char)
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50)),
                            shape = RoundedCornerShape(16.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("学下一个字 👉", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = tts?.setLanguage(Locale.CHINESE)
            isTtsReady = result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED
        }
    }

    override fun onDestroy() {
        tts?.stop()
        tts?.shutdown()
        super.onDestroy()
    }
}

// 模块 1：大字卡视图
@Composable
fun FlashCardView(word: WordItem, onSpeakClick: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = word.pinyin, fontSize = 38.sp, color = Color(0xFF757575), fontWeight = FontWeight.SemiBold)
        Spacer(modifier = Modifier.height(6.dp))
        Text(text = word.char, fontSize = 140.sp, fontWeight = FontWeight.ExtraBold, color = Color(0xFF2E7D32))
        Spacer(modifier = Modifier.height(16.dp))
        Button(
            onClick = onSpeakClick,
            shape = RoundedCornerShape(50),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF03A9F4)),
            modifier = Modifier.height(52.dp)
        ) {
            Text("🔊 读给我听", fontSize = 20.sp, fontWeight = FontWeight.Bold)
        }
    }
}

// 模块 2：描红练习视图
@Composable
fun TracingView(char: String) {
    val points = remember(char) { mutableStateListOf<Offset>() }

    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        // 田字格底纹与参考字
        Text(text = char, fontSize = 180.sp, color = Color(0xFFE0E0E0), fontWeight = FontWeight.Bold)

        // 手指画笔触控
        Canvas(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(char) {
                    detectDragGestures(
                        onDragStart = { offset -> points.add(offset) },
                        onDrag = { change, _ -> points.add(change.position) }
                    )
                }
        ) {
            val strokeWidth = 28.dp.toPx()
            if (points.size > 1) {
                val path = Path().apply {
                    moveTo(points.first().x, points.first().y)
                    for (i in 1 until points.size) {
                        lineTo(points[i].x, points[i].y)
                    }
                }
                drawPath(
                    path = path,
                    color = Color(0xFFFF5722),
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )
            }
        }

        Button(
            onClick = { points.clear() },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(8.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFFCC80))
        ) {
            Text("🧹 重新写", color = Color(0xFF5D4037), fontWeight = FontWeight.Bold)
        }
    }
}

// 模块 3：喂食小兔子互动游戏
@Composable
fun FeedingGameView(
    targetWord: WordItem,
    allWords: List<WordItem>,
    onFeedSuccess: () -> Unit
) {
    val options = remember(targetWord) {
        (allWords.filter { it.char != targetWord.char }.shuffled().take(2) + targetWord).shuffled()
    }
    var showWrongTip by remember { mutableStateOf(false) }

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "小兔子想吃写着【${targetWord.char}】的胡萝卜！",
            fontSize = 26.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFD84315)
        )
        Spacer(modifier = Modifier.height(30.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(28.dp)) {
            options.forEach { item ->
                Button(
                    onClick = {
                        if (item.char == targetWord.char) {
                            showWrongTip = false
                            onFeedSuccess()
                        } else {
                            showWrongTip = true
                        }
                    },
                    modifier = Modifier.size(110.dp),
                    shape = RoundedCornerShape(20.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF7043)),
                    elevation = ButtonDefaults.buttonElevation(defaultElevation = 6.dp)
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("🥕", fontSize = 32.sp)
                        Text(item.char, fontSize = 32.sp, fontWeight = FontWeight.Bold, color = Color.White)
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(16.dp))
        if (showWrongTip) {
            Text(
                text = "哎呀，这是“${options.firstOrNull()}”不是“${targetWord.char}”哦，再找找看~",
                color = Color(0xFFE53935),
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}
""",

    # 10. README.md
    "README.md": """# 字宝宝奇遇记 (Kids Literacy App)

专为 4 岁幼儿设计的趣味识字安卓应用。包含横屏自适应平板显示、字卡发音、手指描红与喂养小兔子正向激励。

## 自动化构建
本项目已配置 GitHub Actions。代码推送到 `main` 分支后，GitHub 会自动编译生成 APK，可在 Actions 页面直接下载安装包。
"""
}

def main():
    print("==============================================")
    print(" 🚀 正在生成【字宝宝奇遇记】完整安卓工程目录...")
    print("==============================================")
    
    for filepath, content in FILES.items():
        # 确保父目录存在
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            print(f"📁 创建文件夹: {dir_name}")
        
        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"📄 写入文件: {filepath}")

    print("\n✅ 所有工程文件创建完成！")
    print("👉 后续步骤：")
    print("  1. 在 GitHub 上新建仓库 (如 kids-literacy-app)")
    print("  2. 将当前目录所有文件推送 (push) 到 GitHub")
    print("  3. 进入 GitHub 仓库页面的 'Actions' 标签，等待 2-3 分钟即可直接下载编译好的 APK！")

if __name__ == "__main__":
    main()
