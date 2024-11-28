import 'package:flutter/material.dart';

class CurrencyListItem extends StatelessWidget {
  final String currencyCode;
  final bool isSelected;
  final VoidCallback onTap;

  const CurrencyListItem({
    Key? key,
    required this.currencyCode,
    required this.isSelected,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 16.0),
      padding: const EdgeInsets.all(2.0),
      decoration: BoxDecoration(
        color: isSelected
            ? Theme.of(context).primaryColor.withOpacity(0.2)
            : const Color.fromARGB(255, 22, 22, 22),
        borderRadius: BorderRadius.circular(12.0),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 6.0,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ListTile(
        title: Text(
          currencyCode,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18.0,
            fontWeight: FontWeight.bold,
          ),
        ),
        trailing: isSelected
            ? const Icon(Icons.check_circle, color: Colors.greenAccent)
            : null,
        onTap: onTap,
      ),
    );
  }
}
