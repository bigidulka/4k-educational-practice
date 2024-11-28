import 'package:flutter/services.dart';

class PlatformService {
  static const MethodChannel _channel =
      MethodChannel('app.channel.shared.data');

  static Future<String> getDocumentsDirectory() async {
    final String path = await _channel.invokeMethod('getDocumentsDirectory');
    return path;
  }
}
