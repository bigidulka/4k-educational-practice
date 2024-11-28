import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:io';
import '../services/api_service.dart';
import '../models/asset.dart';
import '../widgets/custom_dialog.dart';
import '../services/platform_service.dart';

class Recommendation {
  final String symbol;
  final String name;
  final String recommendation;
  final String message;
  final String market;

  Recommendation({
    required this.symbol,
    required this.name,
    required this.recommendation,
    required this.message,
    required this.market,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      symbol: json['symbol'] ?? '',
      name: json['name'] ?? '',
      recommendation: json['recommendation'] ?? '',
      message: json['message'] ?? '',
      market: json['market'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'symbol': symbol,
      'name': name,
      'recommendation': recommendation,
      'message': message,
      'market': market,
    };
  }
}

class RecommendationsScreen extends StatefulWidget {
  final int userId;

  RecommendationsScreen({required this.userId});

  @override
  _RecommendationsScreenState createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  List<Recommendation> _recommendations = [];
  bool _isLoading = true;
  bool _isFetching = false;
  String _error = '';
  late String _cacheFilePath;

  @override
  void initState() {
    super.initState();
    _initializeCache();
  }

  Future<void> _initializeCache() async {
    try {
      String documentsDirectory = await PlatformService.getDocumentsDirectory();
      _cacheFilePath = '$documentsDirectory/cached_recommendations.json';

      await _loadCachedRecommendations();

      _fetchRecommendations();
    } catch (e) {
      print('Ошибка инициализации кэша: $e');
      setState(() {
        _isLoading = false;
        _error = 'Ошибка инициализации кэша: $e';
      });
    }
  }

  Future<void> _loadCachedRecommendations() async {
    try {
      final file = File(_cacheFilePath);
      if (await file.exists()) {
        String cachedData = await file.readAsString();
        List<dynamic> jsonData = jsonDecode(cachedData);
        List<Recommendation> cachedRecommendations =
            jsonData.map((item) => Recommendation.fromJson(item)).toList();

        if (!mounted) return;
        setState(() {
          _recommendations = cachedRecommendations;
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
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _saveRecommendationsToCache(
      List<Recommendation> recommendations) async {
    try {
      final file = File(_cacheFilePath);
      List<Map<String, dynamic>> jsonData =
          recommendations.map((rec) => rec.toJson()).toList();
      String jsonString = jsonEncode(jsonData);
      await file.writeAsString(jsonString);
    } catch (e) {
      print('Ошибка при сохранении рекомендаций в кэш: $e');
    }
  }

  void _showRecommendationsDescription(Recommendation rec) {
    showDescription(
      context,
      'Описание актива: ${rec.symbol}',
      rec.message.isNotEmpty
          ? rec.message
          : 'Нет дополнительной информации о данном активе.',
    );
  }

  Future<void> _fetchRecommendations() async {
    setState(() {
      _isFetching = true;
    });

    try {
      List<Asset> favorites = await ApiService.getFavorites(widget.userId);

      if (!mounted) return;

      if (favorites.isEmpty) {
        setState(() {
          _recommendations = [];
          _isFetching = false;
        });
        return;
      }

      List<Future<Map<String, dynamic>?>> recommendationFutures =
          favorites.map((asset) {
        return ApiService.getRecommendation(
            asset.assetType, asset.assetIdentifier);
      }).toList();

      List<Map<String, dynamic>?> recommendationsJson =
          await Future.wait(recommendationFutures);

      List<Recommendation> recommendations = [];
      for (int i = 0; i < favorites.length; i++) {
        final recommendationData = recommendationsJson[i];
        final assetType = favorites[i].assetType;
        if (recommendationData != null) {
          recommendationData['market'] = assetType;
          recommendations.add(Recommendation.fromJson(recommendationData));
        } else {
          print(
              'Не удалось получить рекомендацию для актива типа: ${favorites[i].assetType}');
          recommendations.add(Recommendation(
            symbol: favorites[i].assetIdentifier,
            name: favorites[i].name,
            market: assetType,
            recommendation: 'Нет данных',
            message: 'Не удалось получить рекомендацию.',
          ));
        }
      }

      if (!mounted) return;
      setState(() {
        _recommendations = recommendations;
        _isFetching = false;
      });

      await _saveRecommendationsToCache(_recommendations);
    } catch (e) {
      print('Ошибка при получении рекомендаций: $e');
      if (!mounted) return;
      setState(() {
        _error = 'Ошибка при получении рекомендаций: $e';
        _isFetching = false;
      });
    }
  }

  Color _getRecommendationColor(String recommendation) {
    switch (recommendation.toLowerCase()) {
      case 'покупка':
        return Colors.green;
      case 'продажа':
        return Colors.red;
      case 'удержание':
        return Colors.yellow;
      default:
        return Colors.white;
    }
  }

  String _translateAssetType(String assetType) {
    switch (assetType.toLowerCase()) {
      case 'stock':
        return 'Акция';
      case 'crypto':
        return 'Криптовалюта';
      case 'currency':
        return 'Валюта';
      default:
        return 'Неизвестный тип';
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
                padding:
                    const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Рекомендации',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24.0,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Row(
                      children: [
                        if (_isFetching && _recommendations.isNotEmpty)
                          const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2.0,
                            ),
                          ),
                        IconButton(
                          icon: const Icon(Icons.help_outline,
                              color: Colors.white),
                          onPressed: () {
                            showDescription(
                              context,
                              'О разделе "Рекомендации"',
                              'В этом разделе вы получаете рекомендации по вашим избранным активам на основе аналитических данных.',
                            );
                          },
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Expanded(
                child: _isLoading
                    ? const Center(
                        child: CircularProgressIndicator(
                          color: Colors.white,
                        ),
                      )
                    : _error.isNotEmpty
                        ? Center(
                            child: Text(
                              _error,
                              style: const TextStyle(color: Colors.red),
                            ),
                          )
                        : _recommendations.isEmpty
                            ? (_isFetching
                                ? const Center(
                                    child: CircularProgressIndicator(
                                      color: Colors.white,
                                    ),
                                  )
                                : const Center(
                                    child: Text(
                                      'У вас нет избранных активов',
                                      style: TextStyle(color: Colors.white),
                                    ),
                                  ))
                            : RefreshIndicator(
                                onRefresh: _fetchRecommendations,
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
                                      radius: const Radius.circular(12),
                                      thickness: MaterialStateProperty.all(4),
                                    ),
                                  ),
                                  child: Scrollbar(
                                    thumbVisibility: true,
                                    child: ListView.builder(
                                      padding: const EdgeInsets.all(16.0),
                                      itemCount: _recommendations.length,
                                      itemBuilder: (context, index) {
                                        final rec = _recommendations[index];
                                        return Container(
                                          margin: const EdgeInsets.symmetric(
                                              vertical: 8.0),
                                          padding: const EdgeInsets.all(12.0),
                                          decoration: BoxDecoration(
                                            color: const Color.fromARGB(
                                                255, 22, 22, 22),
                                            borderRadius:
                                                BorderRadius.circular(12.0),
                                            boxShadow: [
                                              BoxShadow(
                                                color: Colors.black
                                                    .withOpacity(0.5),
                                                blurRadius: 6.0,
                                                offset: const Offset(0, 4),
                                              ),
                                            ],
                                          ),
                                          child: ListTile(
                                            title: Text(
                                              '${rec.symbol} ${rec.name}',
                                              style: const TextStyle(
                                                  color: Colors.white),
                                            ),
                                            subtitle: Text(
                                              _translateAssetType(rec.market),
                                              style: const TextStyle(
                                                  color: Colors.grey),
                                            ),
                                            trailing: Text(
                                              rec.recommendation,
                                              style: TextStyle(
                                                color: _getRecommendationColor(
                                                    rec.recommendation),
                                                fontSize: 25,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                            onTap: () =>
                                                _showRecommendationsDescription(
                                                    rec),
                                          ),
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
