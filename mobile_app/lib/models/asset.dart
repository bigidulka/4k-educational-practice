class Asset {
  final int id;
  final String assetType;
  final String assetIdentifier;
  final String name;
  double? currentPrice;

  Asset({
    required this.id,
    required this.assetType,
    required this.assetIdentifier,
    required this.name,
    this.currentPrice,
  });

  factory Asset.fromJson(Map<String, dynamic> json) {
    return Asset(
      id: json['id'],
      assetType: json['asset_type'],
      assetIdentifier: json['asset_identifier'],
      name: json['name'],
      currentPrice: json['current_price'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'asset_type': assetType,
      'asset_identifier': assetIdentifier,
      'name': name,
      'current_price': currentPrice,
    };
  }
}
