import '../../core/config/app_config.dart';

class ApiService {
  ApiService({
    String? baseUrl,
  }) : baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  final String baseUrl;

  Future<void> initialize() async {
    // API client initialization will be implemented in a later phase.
  }
}
