package com.example.mobile_app

import android.os.Bundle
import io.flutter.embedding.android.FlutterActivity
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "app.channel.shared.data"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val engine = flutterEngine ?: return // Ensure flutterEngine is non-null
        MethodChannel(engine.dartExecutor.binaryMessenger, CHANNEL)
            .setMethodCallHandler { call, result ->
                if (call.method == "getDocumentsDirectory") {
                    try {
                        val documentsDir = applicationContext.filesDir.absolutePath
                        result.success(documentsDir)
                    } catch (e: Exception) {
                        result.error("UNAVAILABLE", "Could not fetch documents directory", null)
                    }
                } else {
                    result.notImplemented()
                }
            }
    }
}
