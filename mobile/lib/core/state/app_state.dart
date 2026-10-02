import 'package:flutter/foundation.dart';

class AppState extends ChangeNotifier {
  bool _isInitialized = false;

  bool get isInitialized => _isInitialized;

  void markInitialized() {
    if (_isInitialized) {
      return;
    }

    _isInitialized = true;
    notifyListeners();
  }
}
