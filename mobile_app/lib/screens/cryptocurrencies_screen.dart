import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/asset.dart';
import '../widgets/asset_list_item.dart';
import 'cryptocurrency_summary_screen.dart';
import '../widgets/custom_dialog.dart';

class CryptocurrenciesScreen extends StatefulWidget {
  final int userId;

  CryptocurrenciesScreen({required this.userId});

  @override
  _CryptocurrenciesScreenState createState() => _CryptocurrenciesScreenState();
}

class _CryptocurrenciesScreenState extends State<CryptocurrenciesScreen> {
  List<Asset> _allCryptos = [];
  List<Asset> _filteredCryptos = [];
  List<Asset> _favoriteCryptos = [];
  int _currentPage = 1;
  final int _itemsPerPage = 10;

  bool _isLoading = false;
  String _searchQuery = '';

  TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchCryptos();
    _fetchFavorites();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _fetchCryptos() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
    });

    List<Asset> cryptos = await ApiService.getCryptocurrencies();

    if (!mounted) return;

    setState(() {
      _allCryptos = cryptos;
      _filteredCryptos = cryptos;
      _isLoading = false;
      _currentPage = 1;
    });
  }

  void _fetchFavorites() async {
    List<Asset> favorites = await ApiService.getFavorites(widget.userId);
    if (!mounted) return;
    setState(() {
      _favoriteCryptos = favorites
          .where((asset) => asset.assetType.toLowerCase() == 'crypto')
          .toList();
    });
  }

  void _updateFavorites(Asset asset, bool isAdded) {
    if (!mounted) return;
    setState(() {
      if (isAdded) {
        _favoriteCryptos.add(asset);
      } else {
        _favoriteCryptos
            .removeWhere((a) => a.assetIdentifier == asset.assetIdentifier);
      }
    });
  }

  void _onSearch(String query) {
    if (!mounted) return;
    setState(() {
      _searchQuery = query.trim().toLowerCase();
      _currentPage = 1;
      _filteredCryptos = _allCryptos.where((crypto) {
        return crypto.assetIdentifier.toLowerCase().contains(_searchQuery) ||
            crypto.name.toLowerCase().contains(_searchQuery);
      }).toList();
    });
  }

  void _showCryptocurrenciesDescription() {
    showDescription(
      context,
      'О разделе "Криптовалюты"',
      'В этом разделе вы можете просматривать список доступных криптовалют, искать их по названию или символу, а также добавлять в избранное.',
    );
  }

  List<Asset> get _currentCryptos {
    int startIndex = (_currentPage - 1) * _itemsPerPage;
    int endIndex = startIndex + _itemsPerPage;
    if (startIndex >= _filteredCryptos.length) {
      return [];
    }
    if (endIndex > _filteredCryptos.length) {
      endIndex = _filteredCryptos.length;
    }
    return _filteredCryptos.sublist(startIndex, endIndex);
  }

  int get _totalPages {
    return (_filteredCryptos.length / _itemsPerPage).ceil();
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
    final favorite = _favoriteCryptos.firstWhere(
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
                      'Криптовалюты',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24.0,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    IconButton(
                      icon: Icon(Icons.help_outline, color: Colors.white),
                      onPressed: _showCryptocurrenciesDescription,
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
                      labelText: 'Поиск криптовалют',
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
                      thickness: 4.0,
                      radius: Radius.circular(10),
                      child: RefreshIndicator(
                        onRefresh: () async {
                          _fetchCryptos();
                          _fetchFavorites();
                        },
                        child: _currentCryptos.isEmpty
                            ? Center(
                                child: Text(
                                  'Криптовалюты не найдены',
                                  style: TextStyle(color: Colors.white70),
                                ),
                              )
                            : ListView.builder(
                                key: ValueKey(_currentPage),
                                itemCount: _currentCryptos.length,
                                itemBuilder: (context, index) {
                                  final crypto = _currentCryptos[index];
                                  final isFavorite = _favoriteCryptos.any((a) =>
                                      a.assetIdentifier ==
                                      crypto.assetIdentifier);
                                  return GestureDetector(
                                    onTap: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder: (context) =>
                                              CryptocurrencySummaryScreen(
                                            symbol: crypto.assetIdentifier,
                                            userId: widget.userId,
                                          ),
                                        ),
                                      );
                                    },
                                    child: AssetListItem(
                                      key: ValueKey(crypto.assetIdentifier),
                                      asset: crypto,
                                      isFavorite: isFavorite,
                                      onAddFavorite: () => _addFavorite(crypto),
                                      onRemoveFavorite: () =>
                                          _removeFavorite(crypto),
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
                              horizontal: 16.0, vertical: 12.0),
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
                              horizontal: 16.0, vertical: 12.0),
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
