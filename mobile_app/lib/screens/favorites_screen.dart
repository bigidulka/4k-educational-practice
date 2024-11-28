import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:io';
import '../services/api_service.dart';
import '../models/asset.dart';
import '../widgets/asset_list_item.dart';
import '../widgets/custom_dialog.dart';
import '../screens/currency_summary_screen.dart';
import '../screens/cryptocurrency_summary_screen.dart';
import '../screens/stock_summary_screen.dart';
import '../services/platform_service.dart';

class FavoritesScreen extends StatefulWidget {
  final int userId;

  FavoritesScreen({required this.userId});

  @override
  _FavoritesScreenState createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  List<Asset> _favorites = [];
  final ScrollController _scrollController = ScrollController();
  String _error = '';
  bool _isLoading = true;
  bool _isFetching = false;
  late String _cacheFilePath;

  @override
  void initState() {
    super.initState();
    _initializeCache();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _initializeCache() async {
    try {
      String documentsDirectory = await PlatformService.getDocumentsDirectory();
      _cacheFilePath = '$documentsDirectory/cached_favorites.json';

      await _loadCachedFavorites();

      _fetchFavorites();
    } catch (e) {
      print('Ошибка инициализации кэша: $e');
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _error = 'Ошибка инициализации кэша: $e';
      });
    }
  }

  Future<void> _loadCachedFavorites() async {
    try {
      final file = File(_cacheFilePath);
      if (await file.exists()) {
        String cachedData = await file.readAsString();
        List<dynamic> jsonData = jsonDecode(cachedData);
        List<Asset> cachedFavorites =
            jsonData.map((item) => Asset.fromJson(item)).toList();

        if (!mounted) return;
        setState(() {
          _favorites = cachedFavorites;
          _isLoading = false;
        });
      } else {
        if (!mounted) return;
        setState(() {
          _isLoading = false;
        });
      }
    } catch (e) {
      print('Ошибка при декодировании кэшированных данных: $e');

      final file = File(_cacheFilePath);
      if (await file.exists()) {
        await file.delete();
      }
      if (!mounted) return;
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _saveFavoritesToCache(List<Asset> favorites) async {
    try {
      final file = File(_cacheFilePath);
      List<Map<String, dynamic>> jsonData =
          favorites.map((asset) => asset.toJson()).toList();
      String jsonString = jsonEncode(jsonData);
      await file.writeAsString(jsonString);
    } catch (e) {
      print('Ошибка при сохранении избранных активов в кэш: $e');
    }
  }

  void _showFavoritesDescription() {
    showDescription(
      context,
      'О разделе "Избранное"',
      'В этом разделе отображаются ваши избранные активы. Вы можете просматривать их текущую информацию и удалять из избранного.',
    );
  }

  Future<void> _fetchFavorites() async {
    if (!mounted) return;
    setState(() {
      _isFetching = true;
    });

    try {
      List<Asset> favorites = await ApiService.getFavorites(widget.userId);

      await Future.wait(favorites.map((asset) async {
        double? currentPrice = await ApiService.getCurrentPrice(asset);
        asset.currentPrice = currentPrice;
        print(currentPrice);
      }));

      if (!mounted) return;
      setState(() {
        _favorites = favorites;
        _isFetching = false;
      });

      await _saveFavoritesToCache(_favorites);
    } catch (e) {
      print('Ошибка при получении избранных активов: $e');
      if (!mounted) return;
      setState(() {
        _error = 'Ошибка при получении избранных активов: $e';
        _isFetching = false;
      });
    }
  }

  void _removeFavorite(int assetId) async {
    bool success = await ApiService.removeFavorite(widget.userId, assetId);
    if (!mounted) return;
    if (success) {
      _fetchFavorites();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Актив удален из избранного')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при удалении из избранного')),
      );
    }
  }

  void _navigateToSummary(Asset asset) {
    Widget summaryScreen;
    switch (asset.assetType.toLowerCase()) {
      case 'stock':
        summaryScreen = StockSummaryScreen(
          ticker: asset.assetIdentifier,
          userId: widget.userId,
        );
        break;
      case 'crypto':
        summaryScreen = CryptocurrencySummaryScreen(
          symbol: asset.assetIdentifier,
          userId: widget.userId,
        );
        break;
      case 'currency':
        summaryScreen = CurrencySummaryScreen(
          pair: asset.assetIdentifier,
          userId: widget.userId,
        );
        break;
      default:
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Неизвестный тип актива')),
          );
        }
        return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => summaryScreen),
    ).then((_) {
      if (mounted) {
        _fetchFavorites();
      }
    });
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
                      'Избранное',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24.0,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Row(
                      children: [
                        if (_isFetching && _favorites.isNotEmpty)
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2.0,
                            ),
                          ),
                        IconButton(
                          icon: Icon(Icons.help_outline, color: Colors.white),
                          onPressed: _showFavoritesDescription,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Expanded(
                child: _isLoading
                    ? Center(
                        child: CircularProgressIndicator(
                          color: Colors.white,
                        ),
                      )
                    : _error.isNotEmpty
                        ? Center(
                            child: Text(
                              _error,
                              style: TextStyle(color: Colors.red),
                            ),
                          )
                        : _favorites.isEmpty
                            ? (_isFetching
                                ? Center(
                                    child: CircularProgressIndicator(
                                      color: Colors.white,
                                    ),
                                  )
                                : Center(
                                    child: Text(
                                      'У вас нет избранных активов',
                                      style: TextStyle(color: Colors.white70),
                                    ),
                                  ))
                            : RefreshIndicator(
                                onRefresh: _fetchFavorites,
                                child: Theme(
                                  data: Theme.of(context).copyWith(
                                    scrollbarTheme: ScrollbarThemeData(
                                      thumbColor: MaterialStateProperty.all(
                                        Colors.white.withOpacity(0.3),
                                      ),
                                      trackColor: MaterialStateProperty.all(
                                        Colors.grey.withOpacity(0.2),
                                      ),
                                      trackBorderColor:
                                          MaterialStateProperty.all(
                                        Colors.transparent,
                                      ),
                                      radius: Radius.circular(12),
                                      thickness: MaterialStateProperty.all(4),
                                    ),
                                  ),
                                  child: Scrollbar(
                                    controller: _scrollController,
                                    thumbVisibility: true,
                                    child: ListView.builder(
                                      controller: _scrollController,
                                      padding: EdgeInsets.only(top: 16.0),
                                      itemCount: _favorites.length,
                                      itemBuilder: (context, index) {
                                        final asset = _favorites[index];
                                        return AssetListItem(
                                          asset: asset,
                                          isFavorite: true,
                                          onAddFavorite: () {},
                                          onRemoveFavorite: () =>
                                              _removeFavorite(asset.id),
                                          onTap: () =>
                                              _navigateToSummary(asset),
                                        );
                                      },
                                    ),
                                  ),
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
