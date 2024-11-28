import 'package:flutter/material.dart';
import 'login_screen.dart';
import '../widgets/custom_dialog.dart';

class HomeScreen extends StatefulWidget {
  final int userId;

  HomeScreen({required this.userId});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  void _logout() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => LoginScreen()),
    );
  }

  void _showAppDescription() {
    showDescription(
      context,
      'О программе',
      'Это приложение предназначено для отслеживания и анализа различных финансовых активов, включая акции, криптовалюты и валютные пары. Вы можете добавлять активы в избранное, получать персонализированные рекомендации, просматривать текущие данные и исторические графики.\n\n'
          'Основные возможности:\n'
          '• Просмотр текущих данных активов\n'
          '• Добавление активов в избранное\n'
          '• Получение рекомендаций на основе аналитических данных\n'
          '• Просмотр подробной информации и графиков для каждого актива',
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
                    Text(
                      'Главная',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24.0,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Row(
                      children: [
                        IconButton(
                          icon: Icon(Icons.info_outline, color: Colors.white),
                          onPressed: _showAppDescription,
                        ),
                        IconButton(
                          icon: Icon(Icons.logout, color: Colors.white),
                          onPressed: _logout,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Добро пожаловать!',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 10),
                      Text(
                        'Это приложение помогает вам следить за вашими финансовыми активами, предоставляя актуальные данные, аналитические рекомендации и подробную информацию о каждом активе. Вы можете добавлять активы в избранное для быстрого доступа и получать персонализированные советы на основе ваших предпочтений.',
                        style: TextStyle(fontSize: 16, color: Colors.white70),
                      ),
                      SizedBox(height: 20),
                      Text(
                        'Основные возможности:',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 10),
                      Column(
                        children: [
                          ListTile(
                            leading: Icon(Icons.show_chart,
                                color: Colors.greenAccent),
                            title: Text(
                              'Просмотр текущих данных активов',
                              style: TextStyle(color: Colors.white),
                            ),
                          ),
                          ListTile(
                            leading: Icon(Icons.star_border,
                                color: Colors.orangeAccent),
                            title: Text(
                              'Добавление активов в избранное',
                              style: TextStyle(color: Colors.white),
                            ),
                          ),
                          ListTile(
                            leading: Icon(Icons.lightbulb_outline,
                                color: Colors.blueAccent),
                            title: Text(
                              'Получение аналитических рекомендаций',
                              style: TextStyle(color: Colors.white),
                            ),
                          ),
                          ListTile(
                            leading: Icon(Icons.timeline,
                                color: Colors.purpleAccent),
                            title: Text(
                              'Просмотр исторических графиков и трендов',
                              style: TextStyle(color: Colors.white),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 30),
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
