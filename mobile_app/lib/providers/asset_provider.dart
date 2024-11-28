import 'package:flutter/material.dart';
import '../models/asset_current.dart';
import '../services/api_service.dart';

class AssetProvider with ChangeNotifier {
  final Map<String, AssetCurrent> _currentData = {};
  final Map<String, bool> _isLoading = {};
  final Map<String, bool> _hasError = {};

  AssetCurrent? getCurrentData(String ticker) => _currentData[ticker];
  bool isLoading(String ticker) => _isLoading[ticker] ?? false;
  bool hasError(String ticker) => _hasError[ticker] ?? false;

  Future<void> fetchCurrentData(String ticker, String assetType) async {
    if (_currentData.containsKey(ticker) || _isLoading[ticker] == true) {
      print('Данные для $ticker уже загружены или загружаются.');
      return;
    }

    print('Загружаем данные для $ticker');
    _isLoading[ticker] = true;
    _hasError[ticker] = false;
    notifyListeners();

    try {
      AssetCurrent? data;

      if (assetType.toLowerCase() == 'stock') {
        data = await ApiService.getCurrentAsset(ticker);
      } else if (assetType.toLowerCase() == 'crypto') {
        data = await ApiService.getCurrentCrypto(ticker);
      } else if (assetType.toLowerCase() == 'currency') {
        data = await ApiService.fetchCurrentCurrency(ticker);
      }

      if (data != null) {
        _currentData[ticker] = data;
        print('Данные для $ticker успешно загружены.');
      } else {
        _hasError[ticker] = true;
        print('Не удалось загрузить данные для $ticker.');
      }
    } catch (e) {
      _hasError[ticker] = true;
      print('Ошибка при загрузке данных для $ticker: $e');
    } finally {
      _isLoading[ticker] = false;
      notifyListeners();
    }
  }
}
