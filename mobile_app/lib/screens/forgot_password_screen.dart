import 'package:flutter/material.dart';
import '../widgets/custom_text_field.dart';
import '../widgets/custom_button.dart';
import '../services/api_service.dart';

class ForgotPasswordScreen extends StatefulWidget {
  @override
  _ForgotPasswordScreenState createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final TextEditingController emailController = TextEditingController();
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController codeController = TextEditingController();
  final TextEditingController newPasswordController = TextEditingController();
  final TextEditingController newPasswordRepeatController =
      TextEditingController();

  bool _isLoading = false;
  bool _codeSent = false;
  // ignore: unused_field
  String? _receivedCode;

  void _requestReset() async {
    String? email = emailController.text.trim();
    String? username = usernameController.text.trim();

    if ((email.isEmpty) &&
        (username.isEmpty)) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Пожалуйста, укажите email или логин')),
      );
      return;
    }

    if (!mounted) return;
    setState(() {
      _isLoading = true;
    });

    var response = await ApiService.forgotPassword(
      email: email.isNotEmpty ? email : null,
      username: username.isNotEmpty ? username : null,
    );

    if (!mounted) return;
    setState(() {
      _isLoading = false;
    });

    if (response != null && response['reset_code'] != null) {
      if (!mounted) return;
      setState(() {
        _codeSent = true;
        _receivedCode = response['reset_code'];
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Код сброса пароля получен')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Не удалось отправить код сброса пароля')),
      );
    }
  }

  void _resetPassword() async {
    String? email = emailController.text.trim();
    String? username = usernameController.text.trim();
    String code = codeController.text.trim();
    String newPassword = newPasswordController.text.trim();
    String newPasswordRepeat = newPasswordRepeatController.text.trim();

    if ((email.isEmpty) &&
        (username.isEmpty)) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Пожалуйста, укажите email или логин')),
      );
      return;
    }

    if (code.isEmpty || newPassword.isEmpty || newPasswordRepeat.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Пожалуйста, заполните все поля')),
      );
      return;
    }

    if (newPassword != newPasswordRepeat) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Пароли не совпадают')),
      );
      return;
    }

    if (!mounted) return;
    setState(() {
      _isLoading = true;
    });

    var response = await ApiService.resetPassword(
      email: email.isNotEmpty ? email : null,
      username: username.isNotEmpty ? username : null,
      code: code,
      newPassword: newPassword,
      newPasswordRepeat: newPasswordRepeat,
    );
    if (!mounted) return;
    setState(() {
      _isLoading = false;
    });

    if (response != null && response['message'] != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Пароль успешно изменен')),
      );
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Не удалось изменить пароль')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.deepPurpleAccent, Colors.black],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            padding: EdgeInsets.symmetric(horizontal: 32.0, vertical: 16.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.lock_reset,
                  size: 100,
                  color: Colors.white70,
                ),
                SizedBox(height: 20),
                Text(
                  'Сброс пароля',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: 30),
                if (!_codeSent) ...[
                  CustomTextField(
                    label: 'Email',
                    controller: emailController,
                    prefixIcon: Icons.email,
                    keyboardType: TextInputType.emailAddress,
                  ),
                  SizedBox(height: 16.0),
                  CustomTextField(
                    label: 'Логин',
                    controller: usernameController,
                    prefixIcon: Icons.person,
                  ),
                  SizedBox(height: 32.0),
                  _isLoading
                      ? CircularProgressIndicator(
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        )
                      : CustomButton(
                          text: 'Запросить сброс пароля',
                          onPressed: _requestReset,
                          backgroundColor: Colors.deepPurpleAccent,
                          textColor: Colors.white,
                        ),
                ] else ...[
                  Text(
                    'Введите полученный код и новый пароль',
                    style: TextStyle(color: Colors.white70),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 20),
                  CustomTextField(
                    label: 'Код подтверждения',
                    controller: codeController,
                    prefixIcon: Icons.confirmation_number,
                  ),
                  SizedBox(height: 16.0),
                  CustomTextField(
                    label: 'Новый пароль',
                    controller: newPasswordController,
                    obscureText: true,
                    prefixIcon: Icons.lock,
                  ),
                  SizedBox(height: 16.0),
                  CustomTextField(
                    label: 'Повторите пароль',
                    controller: newPasswordRepeatController,
                    obscureText: true,
                    prefixIcon: Icons.lock_outline,
                  ),
                  SizedBox(height: 32.0),
                  _isLoading
                      ? CircularProgressIndicator(
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        )
                      : CustomButton(
                          text: 'Изменить пароль',
                          onPressed: _resetPassword,
                          backgroundColor: Colors.deepPurpleAccent,
                          textColor: Colors.white,
                        ),
                ],
                SizedBox(height: 20),
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  child: Text(
                    'Назад к авторизации',
                    style: TextStyle(
                      color: Colors.blueAccent,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
