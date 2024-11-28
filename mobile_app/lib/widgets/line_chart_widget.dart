import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class LineChartWidget extends StatelessWidget {
  final List<Map<String, dynamic>> historicalData;

  LineChartWidget({required this.historicalData});

  @override
  Widget build(BuildContext context) {
    if (historicalData.isEmpty) {
      return Center(
        child: Text(
          'Нет исторических данных для отображения.',
          style: TextStyle(color: Colors.white70),
        ),
      );
    }

    List<FlSpot> priceSpots = [];
    List<FlSpot> volumeSpots = [];
    List<String> dates = [];

    for (int i = 0; i < historicalData.length; i++) {
      var dataPoint = historicalData[i];
      double price = (dataPoint['close'] as num).toDouble();
      double volume = (dataPoint['volume'] as num).toDouble();
      priceSpots.add(FlSpot(i.toDouble(), price));
      volumeSpots.add(FlSpot(i.toDouble(), volume));
      dates.add(dataPoint['date']);
    }

    double minYPrice =
        priceSpots.map((e) => e.y).reduce((a, b) => a < b ? a : b);
    double maxYPrice =
        priceSpots.map((e) => e.y).reduce((a, b) => a > b ? a : b);

    double maxVolume =
        volumeSpots.map((e) => e.y).reduce((a, b) => a > b ? a : b);

    double priceInterval = (maxYPrice - minYPrice) / 5;
    if (priceInterval == 0) priceInterval = 1;

    double xInterval = (priceSpots.length / 5).ceilToDouble();
    if (xInterval == 0) xInterval = 1;

    double volumeInterval = maxVolume / 5;
    if (volumeInterval == 0) volumeInterval = 1;

    return Container(
      height: 600,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        children: [
          Expanded(
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: priceInterval,
                  getDrawingHorizontalLine: (value) {
                    return FlLine(
                      color: Colors.white24,
                      strokeWidth: 1,
                    );
                  },
                ),
                minY: minYPrice - (priceInterval * 0.5),
                maxY: maxYPrice + (priceInterval * 0.5),
                titlesData: FlTitlesData(
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: xInterval,
                      getTitlesWidget: (value, meta) {
                        int index = value.toInt();
                        if (index >= 0 && index < dates.length) {
                          DateTime date = DateTime.parse(dates[index]);
                          String displayDate = "${date.month}/${date.day}";
                          return Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(
                              displayDate,
                              style: TextStyle(
                                  fontSize: 10, color: Colors.white70),
                            ),
                          );
                        } else {
                          return const SizedBox.shrink();
                        }
                      },
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: priceInterval,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          value.toStringAsFixed(2),
                          style: TextStyle(fontSize: 10, color: Colors.white70),
                        );
                      },
                    ),
                  ),
                  topTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  rightTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                ),
                lineBarsData: [
                  LineChartBarData(
                    spots: priceSpots,
                    isCurved: true,
                    color: Colors.blue,
                    barWidth: 2,
                    dotData: FlDotData(show: false),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: BarChart(
              BarChartData(
                gridData: FlGridData(
                  show: false,
                ),
                titlesData: FlTitlesData(
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: volumeInterval,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          value.toStringAsFixed(0),
                          style: TextStyle(fontSize: 10, color: Colors.white70),
                        );
                      },
                    ),
                  ),
                  topTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  rightTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                ),
                barGroups: volumeSpots.map((spot) {
                  return BarChartGroupData(
                    x: spot.x.toInt(),
                    barRods: [
                      BarChartRodData(
                        toY: spot.y,
                        color: Colors.grey.withOpacity(0.5),
                        width: 4,
                      ),
                    ],
                  );
                }).toList(),
                barTouchData: BarTouchData(enabled: false),
                maxY: maxVolume + (volumeInterval * 0.5),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
