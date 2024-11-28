class AssetCurrent {
  final double open;
  final double high;
  final double low;
  final double close;
  final double volume;
  final double dividends;
  final double stockSplits;
  final Map<String, dynamic> info;
  final String assetType;

  AssetCurrent({
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.volume,
    required this.dividends,
    required this.stockSplits,
    required this.info,
    required this.assetType,
  });

  factory AssetCurrent.fromJson(Map<String, dynamic> json, String assetType) {
    double parseDouble(String key) {
      var value = json[key];
      if (value is num) {
        return value.toDouble();
      } else if (value is String) {
        return double.tryParse(value) ?? 0.0;
      } else {
        return 0.0;
      }
    }

    String openKey,
        highKey,
        lowKey,
        closeKey,
        volumeKey,
        dividendsKey,
        stockSplitsKey;

    if (assetType.toLowerCase() == 'stock') {
      openKey = 'open';
      highKey = 'high';
      lowKey = 'low';
      closeKey = 'close';
      volumeKey = 'volume';
      dividendsKey = 'dividends';
      stockSplitsKey = 'stock_splits';
    } else {
      openKey = 'Open';
      highKey = 'High';
      lowKey = 'Low';
      closeKey = 'Close';
      volumeKey = 'Volume';
      dividendsKey = 'Dividends';
      stockSplitsKey = 'Stock Splits';
    }

    double open = parseDouble(openKey);
    double high = parseDouble(highKey);
    double low = parseDouble(lowKey);
    double close = parseDouble(closeKey);
    double volume = parseDouble(volumeKey);
    double dividends = parseDouble(dividendsKey);
    double stockSplits = parseDouble(stockSplitsKey);

    Map<String, dynamic> info = json['info'] ?? {};

    return AssetCurrent(
      open: open,
      high: high,
      low: low,
      close: close,
      volume: volume,
      dividends: dividends,
      stockSplits: stockSplits,
      info: info,
      assetType: assetType,
    );
  }
}
