import 'package:cyberguard_mobile/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('CyberGuard app loads', (WidgetTester tester) async {
    await tester.pumpWidget(const CyberGuardApp());

    expect(find.text('CyberGuard'), findsOneWidget);
  });
}
