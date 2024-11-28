import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/line_chart_widget.dart';
import '../models/asset.dart';
import '../widgets/custom_dialog.dart';

class CryptocurrencySummaryScreen extends StatefulWidget {
  final String symbol;
  final int userId;

  CryptocurrencySummaryScreen({required this.symbol, required this.userId});

  @override
  _CryptocurrencySummaryScreenState createState() => _CryptocurrencySummaryScreenState();
}

class _CryptocurrencySummaryScreenState extends State<CryptocurrencySummaryScreen> {
  Map<String, dynamic>? _currentData;
  List<Map<String, dynamic>>? _historicalData;
  bool _isLoading = true;
  String _selectedInterval = '1d';

  List<String> _intervalOptions = [
    '1m',
    '5m',
    '15m',
    '30m',
    '60m',
    '90m',
    '1h',
    '1d',
    '5d',
    '1wk',
    '1mo',
    '3mo'
  ];

  bool _isFavorite = false;

  @override
  void initState() {
    super.initState();
    _fetchData();
    _checkIfFavorite();
  }

  void _fetchData() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
    });
    
    var currentData = await ApiService.fetchCurrentCrypto(widget.symbol);
    var historicalData = await ApiService.fetchHistoricalCrypto(
      widget.symbol,
      interval: _selectedInterval,
    );

    if (!mounted) return;

    setState(() {
      _currentData = currentData;
      _historicalData = historicalData;
      _isLoading = false;
    });
  }

  void _refreshData() {
    _fetchData();
  }
  
  void _checkIfFavorite() async {
    List<Asset> favorites = await ApiService.getFavorites(widget.userId);
    if (!mounted) return;
    setState(() {
      _isFavorite = favorites.any(
          (asset) => asset.assetIdentifier == widget.symbol && asset.assetType == 'crypto');
    });
  }

  void _addFavorite() async {
    Asset asset = Asset(
      id: 0,
      assetType: 'crypto',
      assetIdentifier: widget.symbol,
      name: _currentData?['info']['name'] ?? widget.symbol,
    );
    bool success = await ApiService.addFavorite(widget.userId, asset);
    if (!mounted) return;
    if (success) {
      setState(() {
        _isFavorite = true;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Актив добавлен в избранное')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при добавлении в избранное')),
      );
    }
  }

  void _removeFavorite() async {
    List<Asset> favorites = await ApiService.getFavorites(widget.userId);
    Asset? assetToRemove = favorites.firstWhere(
      (asset) => asset.assetIdentifier == widget.symbol && asset.assetType == 'crypto',
      orElse: () => Asset(id: 0, assetType: '', assetIdentifier: '', name: ''),
    );

    if (assetToRemove.id == 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Актив не найден в избранном')),
      );
      return;
    }

    bool success = await ApiService.removeFavorite(widget.userId, assetToRemove.id);
    if (!mounted) return;
    if (success) {
      setState(() {
        _isFavorite = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Актив удален из избранного')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при удалении из избранного')),
      );
    }
  }


void _showCryptoSummaryDescription() {
  showDescription(
    context,
    'О разделе "Сводка по криптовалюте"',
    'Здесь вы можете просмотреть текущую информацию о криптовалюте, её график цены, добавить или удалить из избранного, а также выбрать интервал времени для отображения графика.',
  );
}

  Widget _buildCurrentData() {
    if (_currentData == null) {
      return Text('Нет данных для отображения.', style: TextStyle(color: Colors.white70));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Цена открытия: ${_currentData!['open']}', style: TextStyle(color: Colors.white)),
        Text('Максимальная цена: ${_currentData!['high']}', style: TextStyle(color: Colors.white)),
        Text('Минимальная цена: ${_currentData!['low']}', style: TextStyle(color: Colors.white)),
        Text('Цена закрытия: ${_currentData!['close']}', style: TextStyle(color: Colors.white)),
        Text('Объем торгов: ${_currentData!['volume']}', style: TextStyle(color: Colors.white)),
        SizedBox(height: 16),
        Text('Информация:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        Text('Название: ${_currentData!['info']['name']}', style: TextStyle(color: Colors.white)),
        Text('Символ: ${_currentData!['info']['symbol']}', style: TextStyle(color: Colors.white)),
        Text('Рыночная капитализация: ${_currentData!['info']['marketCap']}', style: TextStyle(color: Colors.white)),
        Text('В обращении: ${_currentData!['info']['circulatingSupply']}', style: TextStyle(color: Colors.white)),
        Text('Валюта: ${_currentData!['info']['currency']}', style: TextStyle(color: Colors.white)),
      ],
    );
  }

  Widget _buildHistoricalChart() {
    if (_historicalData == null || _historicalData!.isEmpty) {
      return Text('Нет исторических данных для отображения.', style: TextStyle(color: Colors.white70));
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(height: 16),
        Text('График цены:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        LineChartWidget(historicalData: _historicalData!),
      ],
    );
  }

  Widget _buildIntervalSelector() {
    return DropdownButton<String>(
      value: _selectedInterval,
      items: _intervalOptions.map((String value) {
        return DropdownMenuItem<String>(
          value: value,
          child: Text(value, style: TextStyle(color: Colors.white)),
        );
      }).toList(),
      onChanged: (newInterval) {
        if (!mounted) return;
        setState(() {
          _selectedInterval = newInterval!;
          _fetchData();
        });
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.deepPurple, Colors.black],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    IconButton(
                      icon: Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                    Text(
                      widget.symbol,
                      style: TextStyle(color: Colors.white, fontSize: 24.0, fontWeight: FontWeight.bold),
                    ),
                    Row(
                      children: [
                        IconButton(
                          icon: Icon(Icons.help_outline, color: Colors.white),
                          onPressed: _showCryptoSummaryDescription,
                        ),
                        IconButton(
                          icon: Icon(Icons.refresh, color: Colors.white),
                          onPressed: _refreshData,
                        ),
                        IconButton(
                          icon: Icon(
                            _isFavorite ? Icons.favorite : Icons.favorite_border,
                            color: _isFavorite ? Colors.red : Colors.white,
                          ),
                          onPressed: _isFavorite ? _removeFavorite : _addFavorite,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              if (_isLoading)
                Expanded(
                  child: Center(
                    child: CircularProgressIndicator(color: Colors.white),
                  ),
                )
              else
                Expanded(
                  child: SingleChildScrollView(
                    padding: EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildCurrentData(),
                        SizedBox(height: 16),
                        Text('Выберите интервал:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                        _buildIntervalSelector(),
                        _buildHistoricalChart(),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
