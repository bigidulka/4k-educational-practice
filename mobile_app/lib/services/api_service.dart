import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import '../models/asset.dart';
import '../models/asset_current.dart';

class ApiService {
  static const String authBaseUrl = 'http://bigidulka2.ddns.net:8001';
  static const String dataBaseUrl = 'http://bigidulka2.ddns.net:8000';

  static Future<Map<String, dynamic>?> login(
      String username, String password) async {
    final response = await http.post(
      Uri.parse('$authBaseUrl/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );

    if (response.statusCode == 200) {
      final decodedBody = utf8.decode(response.bodyBytes);
      return jsonDecode(decodedBody);
    } else {
      print('Ошибка авторизации: ${response.statusCode}');
      final decodedBody = utf8.decode(response.bodyBytes);
      print('Ответ сервера: $decodedBody');
      return null;
    }
  }

  static Future<Map<String, dynamic>?> forgotPassword({
    String? email,
    String? username,
  }) async {
    final url = Uri.parse('$authBaseUrl/forgot-password');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'username': username,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> resetPassword({
    String? email,
    String? username,
    required String code,
    required String newPassword,
    required String newPasswordRepeat,
  }) async {
    final url = Uri.parse('$authBaseUrl/reset-password');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'username': username,
        'code': code,
        'new_password': newPassword,
        'new_password_repeat': newPasswordRepeat,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      return null;
    }
  }

  static Future<bool> register(Map<String, String> userData) async {
    final response = await http.post(
      Uri.parse('$authBaseUrl/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(userData),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      print('Ошибка регистрации: ${response.statusCode}');
      final decodedBody = utf8.decode(response.bodyBytes);
      print('Ответ сервера: $decodedBody');
      return false;
    }
  }

  static Future<List<Asset>> getFavorites(int userId) async {
    final response = await http.get(
      Uri.parse('$authBaseUrl/favorites?user_id=$userId'),
    );

    if (response.statusCode == 200) {
      final decodedBody = utf8.decode(response.bodyBytes);
      return (jsonDecode(decodedBody) as List)
          .map((item) => Asset.fromJson(item))
          .toList();
    } else {
      print('Ошибка при получении избранных: ${response.statusCode}');
      final decodedBody = utf8.decode(response.bodyBytes);
      print('Ответ сервера: $decodedBody');
      return [];
    }
  }

  static Future<bool> addFavorite(int userId, Asset asset) async {
    final uri = Uri.parse('$authBaseUrl/favorites').replace(queryParameters: {
      'user_id': userId.toString(),
    });

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'asset_type': asset.assetType,
        'asset_identifier': asset.assetIdentifier,
        'name': asset.name,
      }),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      print('Ошибка при добавлении в избранное: ${response.statusCode}');
      final decodedBody = utf8.decode(response.bodyBytes);
      print('Ответ сервера: $decodedBody');
      return false;
    }
  }

  static Future<bool> removeFavorite(int userId, int assetId) async {
    final response = await http.delete(
      Uri.parse('$authBaseUrl/favorites/$assetId?user_id=$userId'),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      print('Ошибка при удалении из избранного: ${response.statusCode}');
      final decodedBody = utf8.decode(response.bodyBytes);
      print('Ответ сервера: $decodedBody');
      return false;
    }
  }

  static Future<Map<String, dynamic>?> getRecommendation(
      String market, String symbol) async {
    final String url = '$dataBaseUrl/recommendations/$market/$symbol';
    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        return jsonDecode(decodedBody) as Map<String, dynamic>;
      } else {
        print('Ошибка при получении рекомендации: ${response.statusCode}');
        final decodedBody = utf8.decode(response.bodyBytes);
        print('Ответ сервера: $decodedBody');
        return null;
      }
    } catch (e) {
      print('Ошибка при получении рекомендации: $e');
      return null;
    }
  }

  static Future<List<Asset>> getStocks() async {
    final response = await http.get(
      Uri.parse('$dataBaseUrl/tb_tickers'),
    );

    if (response.statusCode == 200) {
      final decodedBody = utf8.decode(response.bodyBytes);
      return (jsonDecode(decodedBody) as List)
          .map((item) => Asset(
                id: 0,
                assetType: 'stock',
                assetIdentifier: item['ticker'],
                name: item['name'],
              ))
          .toList();
    } else {
      print('Ошибка при получении акций: ${response.statusCode}');
      final decodedBody = utf8.decode(response.bodyBytes);
      print('Ответ сервера: $decodedBody');
      return [];
    }
  }

  static Future<List<Asset>> getCryptocurrencies() async {
    final response = await http.get(
      Uri.parse('$dataBaseUrl/cryptocurrencies'),
    );

    if (response.statusCode == 200) {
      final decodedBody = utf8.decode(response.bodyBytes);
      return (jsonDecode(decodedBody) as List)
          .map((item) => Asset(
                id: 0,
                assetType: 'crypto',
                assetIdentifier: item['symbol'],
                name: item['name'],
              ))
          .toList();
    } else {
      print('Ошибка при получении криптовалют: ${response.statusCode}');
      final decodedBody = utf8.decode(response.bodyBytes);
      print('Ответ сервера: $decodedBody');
      return [];
    }
  }

  static Future<List<Map<String, dynamic>>> getCurrencies() async {
    final response = await http.get(
      Uri.parse('$dataBaseUrl/currency_crosses'),
    );

    if (response.statusCode == 200) {
      final decodedBody = utf8.decode(response.bodyBytes);
      return List<Map<String, dynamic>>.from(jsonDecode(decodedBody));
    } else {
      print('Ошибка при получении валют: ${response.statusCode}');
      final decodedBody = utf8.decode(response.bodyBytes);
      print('Ответ сервера: $decodedBody');
      return [];
    }
  }

  static Future<AssetCurrent?> getCurrentAsset(String ticker) async {
    final String url = '$dataBaseUrl/tb_current/$ticker';
    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        return AssetCurrent.fromJson(jsonDecode(decodedBody), 'stock');
      } else {
        print(
            'Ошибка при получении текущих данных для $ticker: ${response.statusCode}');
        final decodedBody = utf8.decode(response.bodyBytes);
        print('Ответ сервера: $decodedBody');
        return null;
      }
    } catch (e) {
      print('Ошибка при получении текущих данных для $ticker: $e');
      return null;
    }
  }

  static Future<AssetCurrent?> getCurrentCrypto(String ticker) async {
    final String url = '$dataBaseUrl/current/crypto/$ticker';
    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        return AssetCurrent.fromJson(jsonDecode(decodedBody), 'crypto');
      } else {
        print(
            'Ошибка при получении текущих данных для криптовалюты $ticker: ${response.statusCode}');
        final decodedBody = utf8.decode(response.bodyBytes);
        print('Ответ сервера: $decodedBody');
        return null;
      }
    } catch (e) {
      print('Ошибка при получении текущих данных для криптовалюты $ticker: $e');
      return null;
    }
  }

  static Future<AssetCurrent?> fetchCurrentCurrency(String pair) async {
    print(pair);
    String url = '$dataBaseUrl/current/currency/$pair';
    try {
      final response = await http.get(Uri.parse(url));
      print(response);

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        Map<String, dynamic> data = jsonDecode(decodedBody);
        return AssetCurrent.fromJson(data, 'currency');
      } else {
        print(
            'Ошибка при получении текущих данных для валютной пары $pair: ${response.statusCode}');
        final decodedBody = utf8.decode(response.bodyBytes);
        print('Ответ сервера: $decodedBody');
        return null;
      }
    } catch (e) {
      print('Ошибка при получении текущих данных для валютной пары $pair: $e');
      return null;
    }
  }

  static Future<double?> getCurrentPrice(Asset asset) async {
    switch (asset.assetType.toLowerCase()) {
      case 'stock':
        AssetCurrent? data = await getCurrentAsset(asset.assetIdentifier);
        return data?.close;
      case 'crypto':
        AssetCurrent? data = await getCurrentCrypto(asset.assetIdentifier);
        return data?.close;
      case 'currency':
        AssetCurrent? data = await fetchCurrentCurrency(asset.assetIdentifier);
        return data?.close;
      default:
        return null;
    }
  }

  static Future<dynamic> _getData(String url,
      {Map<String, String>? params}) async {
    try {
      Uri uri = Uri.parse(url).replace(queryParameters: params);
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final decodedBody = utf8.decode(response.bodyBytes);
        return json.decode(decodedBody);
      } else {
        print(
            "Ошибка при запросе $url: ${response.statusCode} ${response.reasonPhrase}");
        final decodedBody = utf8.decode(response.bodyBytes);
        print('Ответ сервера: $decodedBody');
        return null;
      }
    } catch (e) {
      print("Произошла ошибка при запросе $url: $e");
      return null;
    }
  }

  static Map<String, dynamic> _standardizeCryptoData(
      Map<String, dynamic> item, String symbol) {
    String? dateValue = item['Date'] ?? item['date'];
    if (dateValue == null) {
      print("Пропуск записи без даты: $item");
      return {};
    }
    return {
      'date': dateValue,
      'open': item['Open_${symbol}-USD']?.toDouble() ?? 0.0,
      'high': item['High_${symbol}-USD']?.toDouble() ?? 0.0,
      'low': item['Low_${symbol}-USD']?.toDouble() ?? 0.0,
      'close': item['Close_${symbol}-USD']?.toDouble() ?? 0.0,
      'volume': item['Volume_${symbol}-USD']?.toDouble() ?? 0.0,
    };
  }

  static List<Map<String, dynamic>> _standardizeCurrencyData(
      Map<String, dynamic> item, String pair) {
    String? dateValue = item['Date'] ?? item['date'];
    if (dateValue == null) {
      print("Пропуск записи без даты: $item");
      return [];
    }
    return [
      {
        'date': dateValue,
        'open': item['Open_${pair}=X']?.toDouble() ?? 0.0,
        'high': item['High_${pair}=X']?.toDouble() ?? 0.0,
        'low': item['Low_${pair}=X']?.toDouble() ?? 0.0,
        'close': item['Close_${pair}=X']?.toDouble() ?? 0.0,
        'volume': item['Volume_${pair}=X']?.toDouble() ?? 0.0,
      }
    ];
  }

  static Future<List<Map<String, dynamic>>?> fetchHistoricalStock(String ticker,
      {String interval = '1d'}) async {
    String url = '$dataBaseUrl/tb_historical/$ticker';
    DateTime toDate = DateTime.now().toUtc();
    DateTime fromDate = toDate.subtract(Duration(days: 30));

    Map<String, String> params = {
      'from_date': DateFormat('yyyy-MM-dd').format(fromDate),
      'to_date': DateFormat('yyyy-MM-dd').format(toDate),
      'utc_offset': '0',
      'interval': interval,
    };

    var data = await _getData(url, params: params);
    if (data != null && data is List) {
      return data.map<Map<String, dynamic>>((item) {
        return {
          'date': item['time'],
          'open': item['open']?.toDouble() ?? 0.0,
          'high': item['high']?.toDouble() ?? 0.0,
          'low': item['low']?.toDouble() ?? 0.0,
          'close': item['close']?.toDouble() ?? 0.0,
          'volume': item['volume']?.toDouble() ?? 0.0,
        };
      }).toList();
    }
    return null;
  }

  static Future<List<Map<String, dynamic>>?> fetchHistoricalCrypto(
      String symbol,
      {String interval = '1d'}) async {
    String url = '$dataBaseUrl/historical/crypto/$symbol';
    DateTime toDate = DateTime.now().toUtc();
    DateTime fromDate = toDate.subtract(Duration(days: 30));

    Map<String, String> params = {
      'from_date': DateFormat('yyyy-MM-dd').format(fromDate),
      'to_date': DateFormat('yyyy-MM-dd').format(toDate),
      'utc_offset': '0',
      'interval': interval,
    };

    var data = await _getData(url, params: params);
    if (data != null && data is List) {
      List<Map<String, dynamic>> standardizedData = [];
      for (var item in data) {
        var standardizedItem = _standardizeCryptoData(item, symbol);
        if (standardizedItem.isNotEmpty) {
          standardizedData.add(standardizedItem);
        }
      }
      return standardizedData;
    }
    return null;
  }

  static Future<List<Map<String, dynamic>>?> fetchHistoricalCurrency(
      String pair,
      {String interval = '1d'}) async {
    String url = '$dataBaseUrl/historical/currency/$pair';
    DateTime toDate = DateTime.now().toUtc();
    DateTime fromDate = toDate.subtract(Duration(days: 30));

    Map<String, String> params = {
      'from_date': DateFormat('yyyy-MM-dd').format(fromDate),
      'to_date': DateFormat('yyyy-MM-dd').format(toDate),
      'utc_offset': '0',
      'interval': interval,
    };

    var data = await _getData(url, params: params);
    if (data != null && data is List) {
      List<Map<String, dynamic>> standardizedData = [];
      for (var item in data) {
        var standardizedItems = _standardizeCurrencyData(item, pair);
        standardizedData.addAll(standardizedItems);
      }
      return standardizedData;
    }
    return null;
  }

  static Future<dynamic> fetchTickers() async {
    String url = '$dataBaseUrl/tb_tickers';
    return await _getData(url);
  }

  static Future<dynamic> fetchCryptocurrencies() async {
    String url = '$dataBaseUrl/cryptocurrencies';
    return await _getData(url);
  }

  static Future<dynamic> fetchCurrencyCrosses() async {
    String url = '$dataBaseUrl/currency_crosses';
    return await _getData(url);
  }

  static Future<Map<String, dynamic>?> fetchCurrentStock(String ticker) async {
    String url = '$dataBaseUrl/tb_current/$ticker';
    var data = await _getData(url);
    if (data != null) {
      return {
        'open': data['open']?.toDouble() ?? 0.0,
        'high': data['high']?.toDouble() ?? 0.0,
        'low': data['low']?.toDouble() ?? 0.0,
        'close': data['close']?.toDouble() ?? 0.0,
        'volume': data['volume']?.toDouble() ?? 0.0,
        'info': data['info'] ?? {},
      };
    }
    return null;
  }

  static Future<Map<String, dynamic>?> fetchCurrentCrypto(String symbol) async {
    String url = '$dataBaseUrl/current/crypto/$symbol';
    var data = await _getData(url);
    if (data != null) {
      return {
        'open': data['Open']?.toDouble() ?? 0.0,
        'high': data['High']?.toDouble() ?? 0.0,
        'low': data['Low']?.toDouble() ?? 0.0,
        'close': data['Close']?.toDouble() ?? 0.0,
        'volume': data['Volume']?.toDouble() ?? 0.0,
        'dividends': data['Dividends']?.toDouble() ?? 0.0,
        'stock_splits': data['Stock Splits']?.toDouble() ?? 0.0,
        'info': data['info'] ?? {},
      };
    }
    return null;
  }
}
