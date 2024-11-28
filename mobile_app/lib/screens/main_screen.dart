import 'package:flutter/material.dart';
import 'recommendations_screen.dart';
import 'favorites_screen.dart';
import 'home_screen.dart';
import 'stocks_screen.dart';
import 'currencies_screen.dart';
import 'cryptocurrencies_screen.dart';

class MainScreen extends StatefulWidget {
  final int userId;

  MainScreen({required this.userId});

  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [];

  final List<String> _tabTitles = [
    'Главная',
    'Рекомендации',
    'Избранное',
    'Акции',
    'Валюты',
    'Криптовалюты',
  ];

  @override
  void initState() {
    super.initState();
    _screens.addAll([
      HomeScreen(userId: widget.userId),
      RecommendationsScreen(userId: widget.userId),
      FavoritesScreen(userId: widget.userId),
      StocksScreen(userId: widget.userId),
      CurrenciesScreen(userId: widget.userId),
      CryptocurrenciesScreen(userId: widget.userId),
    ]);
  }

  void _onTabTapped(int index) {
    if (!mounted) return;
    setState(() {
      _currentIndex = index;
    });
  }

  BottomNavigationBarItem _buildBottomNavigationBarItem(
      IconData iconData, int index) {
    bool isSelected = _currentIndex == index;
    return BottomNavigationBarItem(
      icon: TweenAnimationBuilder<double>(
        tween: Tween<double>(begin: 24.0, end: isSelected ? 30.0 : 24.0),
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeInOut,
        builder: (context, size, child) {
          return Icon(
            iconData,
            size: size,
            color: isSelected ? Colors.deepPurpleAccent : Colors.grey,
          );
        },
      ),
      label: '',
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black54,
              offset: Offset(0, -3),
              blurRadius: 10,
              spreadRadius: 2,
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              child: Text(
                _tabTitles[_currentIndex],
                style: const TextStyle(
                  fontSize: 10.0,
                  color: Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            BottomNavigationBar(
              currentIndex: _currentIndex,
              selectedItemColor: Colors.deepPurpleAccent,
              unselectedItemColor: Colors.grey,
              onTap: _onTabTapped,
              type: BottomNavigationBarType.fixed,
              elevation: 0,
              backgroundColor: Colors.transparent,
              showSelectedLabels: false,
              showUnselectedLabels: false,
              items: [
                _buildBottomNavigationBarItem(Icons.home, 0),
                _buildBottomNavigationBarItem(Icons.star_border, 1),
                _buildBottomNavigationBarItem(Icons.favorite_border, 2),
                _buildBottomNavigationBarItem(Icons.trending_up, 3),
                _buildBottomNavigationBarItem(Icons.attach_money, 4),
                _buildBottomNavigationBarItem(Icons.monetization_on, 5),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
