import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'currency_summary_screen.dart';
import '../widgets/currency_list_item.dart';
import '../widgets/custom_dialog.dart';

class CurrenciesScreen extends StatefulWidget {
  final int userId;

  CurrenciesScreen({required this.userId});

  @override
  _CurrenciesScreenState createState() => _CurrenciesScreenState();
}

class _CurrenciesScreenState extends State<CurrenciesScreen> {
  final ScrollController _leftScrollController = ScrollController();
  final ScrollController _rightScrollController = ScrollController();
  final TextEditingController _searchController = TextEditingController();

  // ignore: unused_field
  List<String> _currencies = [];
  List<String> _leftCurrencies = [];
  List<String> _rightCurrencies = [];
  String _baseCurrency = '';
  String _quoteCurrency = '';
  String _searchQuery = '';
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchCurrencies();
  }

  @override
  void dispose() {
    _leftScrollController.dispose();
    _rightScrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _fetchCurrencies() async {
    setState(() {
      _isLoading = true;
    });

    try {
      List<Map<String, dynamic>> currencies = await ApiService.getCurrencies();
      if (!mounted) return;
      setState(() {
        List<String> uniqueCurrencies = currencies
            .map((currency) => currency['base'] as String)
            .toSet()
            .toList();

        _leftCurrencies = [...uniqueCurrencies];
        _rightCurrencies = [...uniqueCurrencies];

        _leftCurrencies.sort();
        _rightCurrencies.sort();

        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _currencies = [];
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ошибка при загрузке валют')),
      );
    }
  }

  void _showCurrenciesDescription() {
    showDescription(
      context,
      'О разделе "Валюты"',
      'В этом разделе вы можете выбрать базовую и котируемую валюты, а также просмотреть информацию о их курсе и динамике.',
    );
  }

  void _viewInformation() {
    if (_baseCurrency.isNotEmpty && _quoteCurrency.isNotEmpty) {
      String pair = '$_baseCurrency$_quoteCurrency';
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) =>
              CurrencySummaryScreen(pair: pair, userId: widget.userId),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Выберите базовую и котируемую валюты')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    List<String> filteredLeftCurrencies = _leftCurrencies.where((currency) {
      return currency.toLowerCase().contains(_searchQuery.toLowerCase());
    }).toList();

    List<String> filteredRightCurrencies = _rightCurrencies.where((currency) {
      return currency.toLowerCase().contains(_searchQuery.toLowerCase());
    }).toList();

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
          child: Column(children: [
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Валюты',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24.0,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.help_outline, color: Colors.white),
                    onPressed: _showCurrenciesDescription,
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
                padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                child: TextField(
                  controller: _searchController,
                  onChanged: (val) {
                    setState(() {
                      _searchQuery = val;
                    });
                  },
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    labelText: 'Поиск валюты',
                    labelStyle: const TextStyle(color: Colors.white70),
                    prefixIcon: const Icon(Icons.search, color: Colors.white70),
                    filled: true,
                    fillColor: Colors.white24,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: BorderSide.none,
                    ),
                  ),
                ),
              ),
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
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
                            radius: const Radius.circular(12),
                            thickness: MaterialStateProperty.all(4),
                          ),
                        ),
                        child: Directionality(
                          textDirection: TextDirection.rtl,
                          child: Scrollbar(
                            thumbVisibility: true,
                            controller: _leftScrollController,
                            child: Directionality(
                              textDirection: TextDirection.ltr,
                              child: ListView.builder(
                                controller: _leftScrollController,
                                itemCount: filteredLeftCurrencies.length,
                                itemBuilder: (context, index) {
                                  final currency =
                                      filteredLeftCurrencies[index];
                                  return CurrencyListItem(
                                    currencyCode: currency,
                                    isSelected: currency == _baseCurrency,
                                    onTap: () {
                                      setState(() {
                                        _baseCurrency = currency;
                                      });
                                    },
                                  );
                                },
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: .0),
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
                            radius: const Radius.circular(12),
                            thickness: MaterialStateProperty.all(4),
                          ),
                        ),
                        child: Scrollbar(
                          thumbVisibility: true,
                          controller: _rightScrollController,
                          child: ListView.builder(
                            controller: _rightScrollController,
                            itemCount: filteredRightCurrencies.length,
                            itemBuilder: (context, index) {
                              final currency = filteredRightCurrencies[index];
                              return CurrencyListItem(
                                currencyCode: currency,
                                isSelected: currency == _quoteCurrency,
                                onTap: () {
                                  setState(() {
                                    _quoteCurrency = currency;
                                  });
                                },
                              );
                            },
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: (_baseCurrency.isNotEmpty &&
                        _quoteCurrency.isNotEmpty &&
                        !_isLoading)
                    ? _viewInformation
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: (_baseCurrency.isNotEmpty &&
                          _quoteCurrency.isNotEmpty &&
                          !_isLoading)
                      ? Colors.deepPurpleAccent
                      : Colors.grey,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16.0, vertical: 12.0),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                ),
                child: const Text(
                  'Просмотреть информацию',
                  style: TextStyle(fontSize: 16),
                ),
              ),
              const SizedBox(height: 12),
            ],
          ]),
        ),
      ),
    );
  }
}
