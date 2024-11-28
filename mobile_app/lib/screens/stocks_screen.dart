import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/asset.dart';
import '../widgets/asset_list_item.dart';
import 'stock_summary_screen.dart';
import '../widgets/custom_dialog.dart';

class StocksScreen extends StatefulWidget {
  final int userId;

  StocksScreen({required this.userId});

  @override
  _StocksScreenState createState() => _StocksScreenState();
}

class _StocksScreenState extends State<StocksScreen> {
  List<Asset> _allStocks = [];
  List<Asset> _filteredStocks = [];
  List<Asset> _favoriteStocks = [];
  int _currentPage = 1;
  final int _itemsPerPage = 10;

  bool _isLoading = false;
  String _searchQuery = '';

  TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchStocks();
    _fetchFavorites();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _fetchStocks() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
    });

    List<Asset> stocks = await ApiService.getStocks();

    if (!mounted) return;

    setState(() {
      _allStocks = stocks;
      _filteredStocks = stocks;
      _isLoading = false;
      _currentPage = 1;
    });
  }

  void _fetchFavorites() async {
    List<Asset> favorites = await ApiService.getFavorites(widget.userId);
    if (!mounted) return;
    setState(() {
      _favoriteStocks = favorites;
    });
  }

  void _updateFavorites(Asset asset, bool isAdded) {
    if (!mounted) return;
    setState(() {
      if (isAdded) {
        _favoriteStocks.add(asset);
      } else {
        _favoriteStocks
            .removeWhere((a) => a.assetIdentifier == asset.assetIdentifier);
      }
    });
  }

  void _onSearch(String query) {
    if (!mounted) return;
    setState(() {
      _searchQuery = query.trim().toLowerCase();
      _currentPage = 1;
      _filteredStocks = _allStocks.where((stock) {
        return stock.assetIdentifier.toLowerCase().contains(_searchQuery) ||
            stock.name.toLowerCase().contains(_searchQuery);
      }).toList();
    });
  }

  void _showStocksDescription() {
    showDescription(
      context,
      'О разделе "Акции"',
      'В этом разделе вы можете просматривать список доступных акций, искать их по названию или тикеру, а также добавлять в избранное.',
    );
  }

  List<Asset> get _currentStocks {
    int startIndex = (_currentPage - 1) * _itemsPerPage;
    int endIndex = startIndex + _itemsPerPage;
    if (startIndex >= _filteredStocks.length) {
      return [];
    }
    if (endIndex > _filteredStocks.length) {
      endIndex = _filteredStocks.length;
    }
    return _filteredStocks.sublist(startIndex, endIndex);
  }

  int get _totalPages {
    return (_filteredStocks.length / _itemsPerPage).ceil();
  }

  void _previousPage() {
    if (_currentPage > 1) {
      if (!mounted) return;
      setState(() {
        _currentPage--;
      });
    }
  }

  void _nextPage() {
    if (_currentPage < _totalPages) {
      if (!mounted) return;
      setState(() {
        _currentPage++;
      });
    }
  }

  void _addFavorite(Asset asset) async {
    bool success = await ApiService.addFavorite(widget.userId, asset);
    if (!mounted) return;
    if (success) {
      _updateFavorites(asset, true);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Актив добавлен в избранное')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при добавлении в избранное')),
      );
    }
  }

  void _removeFavorite(Asset asset) async {
    final favorite = _favoriteStocks.firstWhere(
      (a) => a.assetIdentifier == asset.assetIdentifier,
      orElse: () => Asset(id: 0, assetType: '', assetIdentifier: '', name: ''),
    );

    if (favorite.id == 0) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Актив не найден в избранном')),
      );
      return;
    }

    bool success = await ApiService.removeFavorite(widget.userId, favorite.id);
    if (!mounted) return;
    if (success) {
      _updateFavorites(asset, false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Актив удален из избранного')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при удалении из избранного')),
      );
    }
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
                    Text(
                      'Акции',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24.0,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    IconButton(
                      icon: Icon(Icons.help_outline, color: Colors.white),
                      onPressed: _showStocksDescription,
                    ),
                  ],
                ),
              ),
              if (_isLoading)
                Expanded(
                  child: Center(
                    child: CircularProgressIndicator(
                      color: Colors.white,
                    ),
                  ),
                )
              else ...[
                Padding(
                  padding:
                      EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                  child: TextField(
                    controller: _searchController,
                    onChanged: _onSearch,
                    style: TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: Colors.white24,
                      labelText: 'Поиск акций',
                      labelStyle: TextStyle(color: Colors.white70),
                      prefixIcon: Icon(Icons.search, color: Colors.white70),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8.0),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: Theme(
                    data: Theme.of(context).copyWith(
                      scrollbarTheme: ScrollbarThemeData(
                        thumbColor: MaterialStateProperty.all(
                          Colors.white.withOpacity(0.3),
                        ),
                        trackColor: MaterialStateProperty.all(
                          Colors.grey.withOpacity(0.2),
                        ),
                        trackBorderColor: MaterialStateProperty.all(
                          Colors.transparent,
                        ),
                        radius: Radius.circular(12),
                        thickness: MaterialStateProperty.all(4),
                      ),
                    ),
                    child: Scrollbar(
                      thumbVisibility: true,
                      child: RefreshIndicator(
                        onRefresh: () async {
                          _fetchStocks();
                          _fetchFavorites();
                        },
                        child: _currentStocks.isEmpty
                            ? Center(
                                child: Text(
                                  'Акции не найдены',
                                  style: TextStyle(color: Colors.white70),
                                ),
                              )
                            : ListView.builder(
                                key: ValueKey(_currentPage),
                                itemCount: _currentStocks.length,
                                itemBuilder: (context, index) {
                                  final stock = _currentStocks[index];
                                  final isFavorite = _favoriteStocks.any((a) =>
                                      a.assetIdentifier ==
                                      stock.assetIdentifier);
                                  return GestureDetector(
                                    onTap: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) =>
                                              StockSummaryScreen(
                                            ticker: stock.assetIdentifier,
                                            userId: widget.userId,
                                          ),
                                        ),
                                      );
                                    },
                                    child: AssetListItem(
                                      key: ValueKey(stock.assetIdentifier),
                                      asset: stock,
                                      isFavorite: isFavorite,
                                      onAddFavorite: () => _addFavorite(stock),
                                      onRemoveFavorite: () =>
                                          _removeFavorite(stock),
                                      showAssetType: false,
                                    ),
                                  );
                                },
                              ),
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding:
                      EdgeInsets.symmetric(vertical: 12.0, horizontal: 32.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      ElevatedButton(
                        onPressed: _currentPage > 1 ? _previousPage : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurpleAccent,
                          foregroundColor: Colors.white,
                          padding: EdgeInsets.symmetric(
                            horizontal: 16.0,
                            vertical: 12.0,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8.0),
                          ),
                        ),
                        child: Text('Предыдущая'),
                      ),
                      Text(
                        '$_currentPage из $_totalPages',
                        style: TextStyle(color: Colors.white, fontSize: 16.0),
                      ),
                      ElevatedButton(
                        onPressed:
                            _currentPage < _totalPages ? _nextPage : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurpleAccent,
                          foregroundColor: Colors.white,
                          padding: EdgeInsets.symmetric(
                            horizontal: 16.0,
                            vertical: 12.0,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8.0),
                          ),
                        ),
                        child: Text('Следующая'),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
