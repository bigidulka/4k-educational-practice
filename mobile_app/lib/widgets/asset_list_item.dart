import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/asset.dart';
import '../providers/asset_provider.dart';

class AssetListItem extends StatefulWidget {
  final Asset asset;
  final bool isFavorite;
  final VoidCallback onAddFavorite;
  final VoidCallback onRemoveFavorite;
  final bool showAssetType;
  final VoidCallback? onTap;

  const AssetListItem({
    Key? key,
    required this.asset,
    required this.isFavorite,
    required this.onAddFavorite,
    required this.onRemoveFavorite,
    this.showAssetType = true,
    this.onTap,
  }) : super(key: key);

  @override
  _AssetListItemState createState() => _AssetListItemState();
}

class _AssetListItemState extends State<AssetListItem> {
  @override
  void initState() {
    super.initState();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<AssetProvider>(context, listen: false).fetchCurrentData(
        widget.asset.assetIdentifier,
        widget.asset.assetType,
      );
    });
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
    return Consumer<AssetProvider>(
      builder: (context, assetProvider, child) {
        final currentData =
            assetProvider.getCurrentData(widget.asset.assetIdentifier);
        final isLoading = assetProvider.isLoading(widget.asset.assetIdentifier);
        final hasError = assetProvider.hasError(widget.asset.assetIdentifier);

        return GestureDetector(
          onTap: widget.onTap,
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: const Color.fromARGB(255, 22, 22, 22),
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
              leading: Icon(
                Icons.monetization_on,
                color: Colors.white,
              ),
              title: Text(
                widget.asset.name,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.asset.assetIdentifier,
                    style: const TextStyle(color: Colors.white70),
                  ),
                  const SizedBox(height: 4.0),
                  if (widget.showAssetType) ...[
                    Text(
                      '${_translateAssetType(widget.asset.assetType)}',
                      style: const TextStyle(color: Colors.white54),
                    ),
                    const SizedBox(height: 4.0),
                  ],
                  isLoading
                      ? const SizedBox(
                          width: 16.0,
                          height: 16.0,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.0,
                            color: Colors.white,
                          ),
                        )
                      : hasError
                          ? const Text(
                              'Не удалось загрузить данные',
                              style: TextStyle(color: Colors.red),
                            )
                          : currentData != null
                              ? Text(
                                  '${currentData.close} ${currentData.info['currency']?.toUpperCase() ?? ''}',
                                  style: const TextStyle(color: Colors.green),
                                )
                              : Container(),
                ],
              ),
              trailing: IconButton(
                icon: Icon(
                  widget.isFavorite ? Icons.favorite : Icons.favorite_border,
                  color: widget.isFavorite ? Colors.red : Colors.white,
                ),
                onPressed: () {
                  if (widget.isFavorite) {
                    widget.onRemoveFavorite();
                  } else {
                    widget.onAddFavorite();
                  }
                },
              ),
            ),
          ),
        );
      },
    );
  }
}
