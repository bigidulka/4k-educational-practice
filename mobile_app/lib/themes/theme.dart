import 'package:flutter/material.dart';

final ThemeData darkPurpleTheme = ThemeData(
  brightness: Brightness.dark,
  primarySwatch: Colors.deepPurple,
  colorScheme: ColorScheme.fromSwatch(
    primarySwatch: Colors.deepPurple,
    brightness: Brightness.dark,
    accentColor: Colors.deepPurpleAccent,
  ),
  scaffoldBackgroundColor: const Color(0xFF121212),
  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: Colors.white),
  ),
);
