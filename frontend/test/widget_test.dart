import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:cross_media_engine/app.dart';
import 'package:cross_media_engine/core/realtime/realtime_bootstrap.dart';
import 'package:cross_media_engine/data/providers/core_providers.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('app renders login when logged out', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
        child: const RealtimeBootstrap(child: CrossMediaApp()),
      ),
    );

    await tester.pumpAndSettle();
    expect(find.text('CROSSMEDIA'), findsOneWidget);
  });
}
