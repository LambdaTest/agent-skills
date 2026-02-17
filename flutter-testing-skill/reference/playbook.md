# Flutter Testing — Advanced Implementation Playbook

## §1 Project Setup & Configuration

### pubspec.yaml — Test Dependencies
```yaml
dev_dependencies:
  test: ^1.24.0
  flutter_test:
    sdk: flutter
  integration_test:
    sdk: flutter
  mockito: ^5.4.0
  build_runner: ^2.4.0
  bloc_test: ^9.1.0          # if using Bloc
  mocktail: ^1.0.0            # alternative no-codegen mocks
  golden_toolkit: ^0.15.0     # enhanced golden tests
  network_image_mock: ^2.1.0  # mock network images in tests
  fake_async: ^1.3.0          # time-travel in async tests

flutter:
  fonts:
    - family: Roboto
      fonts:
        - asset: assets/fonts/Roboto-Regular.ttf
```

### dart_test.yaml — Test Runner Config
```yaml
platforms: [vm]
concurrency: 4
timeout: 30s
retry: 1
tags:
  slow:
    timeout: 120s
  integration:
    timeout: 300s
```

---

## §2 Unit Tests — Advanced Patterns

### Testing with Mockito (Code Generation)
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([ApiClient, AuthRepository, CacheManager])
import 'user_service_test.mocks.dart';

void main() {
  late MockApiClient mockApi;
  late MockCacheManager mockCache;
  late UserService service;

  setUp(() {
    mockApi = MockApiClient();
    mockCache = MockCacheManager();
    service = UserService(api: mockApi, cache: mockCache);
  });

  group('UserService.getUser', () {
    test('returns cached user when available', () async {
      when(mockCache.get('user:1'))
          .thenReturn(User(id: 1, name: 'Alice'));

      final user = await service.getUser(1);
      expect(user.name, equals('Alice'));
      verifyNever(mockApi.get(any));
    });

    test('fetches from API when cache miss', () async {
      when(mockCache.get('user:1')).thenReturn(null);
      when(mockApi.get('/users/1')).thenAnswer(
        (_) async => Response('{"id":1,"name":"Alice"}', 200),
      );

      final user = await service.getUser(1);
      expect(user.name, equals('Alice'));
      verify(mockCache.set('user:1', any)).called(1);
    });

    test('throws NetworkException on connection failure', () async {
      when(mockCache.get(any)).thenReturn(null);
      when(mockApi.get(any)).thenThrow(SocketException('No Internet'));

      expect(() => service.getUser(1), throwsA(isA<NetworkException>()));
    });
  });
}
```

### Testing with Mocktail (No Code Generation)
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockAuthRepo extends Mock implements AuthRepository {}

void main() {
  late MockAuthRepo mockAuth;

  setUpAll(() {
    registerFallbackValue(LoginRequest(email: '', password: ''));
  });

  setUp(() => mockAuth = MockAuthRepo());

  test('login returns token', () async {
    when(() => mockAuth.login(any()))
        .thenAnswer((_) async => AuthToken('abc123'));

    final token = await mockAuth.login(
      LoginRequest(email: 'user@test.com', password: 'pass'),
    );
    expect(token.value, 'abc123');
    verify(() => mockAuth.login(any())).called(1);
  });
}
```

### Stream & Async Testing
```dart
group('AuthBloc streams', () {
  test('emits states in correct order', () {
    final bloc = AuthBloc(mockAuth);
    expectLater(
      bloc.stream,
      emitsInOrder([isA<AuthLoading>(), isA<AuthAuthenticated>()]),
    );
    bloc.add(LoginEvent('user@test.com', 'password'));
  });

  test('debounced search emits after delay', () {
    fakeAsync((async) {
      final controller = SearchController();
      final results = <String>[];
      controller.results.listen((r) => results.add(r));

      controller.query('flu');
      controller.query('flutt');
      controller.query('flutter');

      async.elapse(Duration(milliseconds: 500));
      expect(results, hasLength(1));
      expect(results.first, contains('flutter'));
    });
  });
});
```

---

## §3 Widget Tests — Production Patterns

### Pump Helpers & Test Wrappers
```dart
Widget makeTestable(Widget child, {GoRouter? router}) {
  return MaterialApp.router(
    routerConfig: router ?? _defaultRouter(),
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    theme: AppTheme.light,
    home: child,
  );
}

Widget makeProviderTestable(Widget child, {
  required AuthNotifier auth,
  required CartNotifier cart,
}) {
  return MultiProvider(
    providers: [
      ChangeNotifierProvider.value(value: auth),
      ChangeNotifierProvider.value(value: cart),
    ],
    child: MaterialApp(home: child),
  );
}
```

### Comprehensive Widget Test
```dart
testWidgets('LoginScreen validates input and navigates on success',
    (tester) async {
  final mockAuth = MockAuthNotifier();
  when(mockAuth.login(any, any)).thenAnswer((_) async => true);

  await tester.pumpWidget(makeProviderTestable(
    LoginScreen(), auth: mockAuth, cart: MockCartNotifier(),
  ));

  // Submit without filling — shows validation errors
  await tester.tap(find.byKey(Key('sign_in_button')));
  await tester.pump();
  expect(find.text('Email is required'), findsOneWidget);
  expect(find.text('Password is required'), findsOneWidget);

  // Enter invalid email
  await tester.enterText(find.byKey(Key('email_field')), 'invalid');
  await tester.tap(find.byKey(Key('sign_in_button')));
  await tester.pump();
  expect(find.text('Invalid email format'), findsOneWidget);

  // Enter valid credentials
  await tester.enterText(find.byKey(Key('email_field')), 'user@test.com');
  await tester.enterText(find.byKey(Key('password_field')), 'password123');
  await tester.tap(find.byKey(Key('sign_in_button')));
  await tester.pumpAndSettle();
  verify(mockAuth.login('user@test.com', 'password123')).called(1);
});

testWidgets('swipe to delete removes item', (tester) async {
  await tester.pumpWidget(makeTestable(CartScreen()));
  await tester.pumpAndSettle();

  final item = find.byKey(Key('cart_item_0'));
  expect(item, findsOneWidget);

  await tester.drag(item, Offset(-300, 0));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Delete'));
  await tester.pumpAndSettle();
  expect(find.byKey(Key('cart_item_0')), findsNothing);
});
```

---

## §4 Golden Tests (Visual Regression)

### Basic Golden Tests
```dart
testWidgets('ProductCard matches golden', (tester) async {
  await tester.pumpWidget(MaterialApp(
    theme: AppTheme.light,
    home: Scaffold(
      body: ProductCard(
        product: Product(name: 'Widget Pro', price: 29.99, rating: 4.5),
      ),
    ),
  ));
  await tester.pumpAndSettle();

  await expectLater(
    find.byType(ProductCard),
    matchesGoldenFile('goldens/product_card_light.png'),
  );
});
```

### Multi-Device Goldens with golden_toolkit
```dart
testGoldens('LoginScreen across devices', (tester) async {
  final builder = DeviceBuilder()
    ..overrideDevicesForAllScenarios(devices: [
      Device.phone, Device.iphone11, Device.tabletLandscape,
    ])
    ..addScenario(name: 'empty', widget: LoginScreen())
    ..addScenario(name: 'filled', widget: LoginScreen());

  await tester.pumpDeviceBuilder(builder,
      wrapper: materialAppWrapper(theme: AppTheme.light));
  await screenMatchesGolden(tester, 'login_screen_multidevice');
});
```

```bash
flutter test --update-goldens
flutter test --update-goldens --tags=golden
```

---

## §5 Integration Tests

```dart
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('end-to-end: purchase flow', () {
    testWidgets('login → browse → add to cart → checkout', (tester) async {
      app.main();
      await tester.pumpAndSettle(Duration(seconds: 3));

      // Login
      await tester.enterText(find.byKey(Key('email')), 'user@test.com');
      await tester.enterText(find.byKey(Key('password')), 'password');
      await tester.tap(find.byKey(Key('sign_in_button')));
      await tester.pumpAndSettle(Duration(seconds: 5));
      expect(find.text('Welcome'), findsOneWidget);

      // Add to cart
      await tester.tap(find.byKey(Key('product_0_add')));
      await tester.pumpAndSettle();
      expect(find.byKey(Key('cart_badge')), findsOneWidget);

      // Checkout
      await tester.tap(find.byKey(Key('cart_icon')));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Checkout'));
      await tester.pumpAndSettle();
      expect(find.text('Order Confirmed'), findsOneWidget);

      // Screenshot for CI
      final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
      await binding.takeScreenshot('order_confirmed');
    });
  });
}
```

```bash
# iOS simulator
flutter test integration_test/app_test.dart

# Android device
flutter test integration_test/app_test.dart -d emulator-5554

# Firebase Test Lab
gcloud firebase test android run \
  --type instrumentation \
  --app build/app/outputs/apk/debug/app-debug.apk \
  --test build/app/outputs/apk/androidTest/debug/app-debug-androidTest.apk
```

---

## §6 Bloc Testing (with bloc_test)

```dart
import 'package:bloc_test/bloc_test.dart';

void main() {
  late MockAuthRepository mockAuth;
  setUp(() => mockAuth = MockAuthRepository());

  blocTest<AuthBloc, AuthState>(
    'emits [loading, authenticated] on successful login',
    build: () {
      when(mockAuth.login(any, any))
          .thenAnswer((_) async => User(id: 1, name: 'Alice'));
      return AuthBloc(mockAuth);
    },
    act: (bloc) => bloc.add(LoginRequested('user@test.com', 'pass')),
    expect: () => [AuthLoading(), AuthAuthenticated(User(id: 1, name: 'Alice'))],
    verify: (_) => verify(mockAuth.login('user@test.com', 'pass')).called(1),
  );

  blocTest<AuthBloc, AuthState>(
    'emits [loading, error] on failed login',
    build: () {
      when(mockAuth.login(any, any)).thenThrow(AuthException('Invalid'));
      return AuthBloc(mockAuth);
    },
    act: (bloc) => bloc.add(LoginRequested('bad@test.com', 'wrong')),
    expect: () => [AuthLoading(), AuthError('Invalid')],
  );
}
```

---

## §7 HTTP Mocking & Provider Testing

### Mock HTTP Client
```dart
import 'package:http/testing.dart';

test('ApiClient parses user list', () async {
  final mockClient = MockClient((request) async {
    if (request.url.path == '/api/users') {
      return Response(
        '[{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]', 200,
        headers: {'content-type': 'application/json'},
      );
    }
    return Response('Not Found', 404);
  });

  final api = ApiClient(client: mockClient);
  final users = await api.fetchUsers();
  expect(users, hasLength(2));
  expect(users.first.name, 'Alice');
});
```

### Riverpod Provider Testing
```dart
testWidgets('CounterScreen shows incremented value', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        counterProvider.overrideWith((ref) => CounterNotifier()..state = 5),
      ],
      child: MaterialApp(home: CounterScreen()),
    ),
  );

  expect(find.text('5'), findsOneWidget);
  await tester.tap(find.byIcon(Icons.add));
  await tester.pump();
  expect(find.text('6'), findsOneWidget);
});
```

---

## §8 CI/CD Integration

```yaml
name: Flutter CI
on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.19.0', cache: true }
      - run: flutter pub get
      - run: dart run build_runner build --delete-conflicting-outputs
      - run: flutter analyze --no-fatal-infos
      - run: flutter test --coverage --reporter=github
      - uses: codecov/codecov-action@v4
        with: { file: coverage/lcov.info }

  golden:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.19.0', cache: true }
      - run: flutter pub get
      - run: dart run build_runner build --delete-conflicting-outputs
      - run: flutter test --tags=golden
      - uses: actions/upload-artifact@v4
        if: failure()
        with: { name: golden-failures, path: test/failures/ }

  integration:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.19.0', cache: true }
      - run: flutter pub get
      - name: Integration tests (iOS Simulator)
        run: flutter test integration_test/
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `MissingPluginException` in test | Plugin not mocked | Use `setMockMethodCallHandler` or `mocktail` to stub platform channels |
| 2 | `pumpAndSettle` times out | Infinite animation (e.g. `CircularProgressIndicator`) | Use `pump(Duration)` instead; or hide animated widget in test mode |
| 3 | Golden test fails on CI | Different OS font rendering | Run golden tests on macOS only; use `golden_toolkit` for font loading |
| 4 | `No MediaQuery widget ancestor` | Missing `MaterialApp` wrapper | Wrap widget in `MaterialApp` or use `makeTestable()` helper |
| 5 | Mock not generating `.mocks.dart` | Missing `build_runner` step | Run `dart run build_runner build --delete-conflicting-outputs` |
| 6 | `A Timer is still pending` | Unawaited timer/debounce | Use `fakeAsync` + `async.elapse()` or `tester.pump(duration)` |
| 7 | `setState() called after dispose` | Async callback fires after widget removed | Check `mounted` before `setState`; cancel subscriptions in `dispose` |
| 8 | Integration test finds no widgets | App not fully loaded | Increase timeout: `pumpAndSettle(Duration(seconds: 10))` |
| 9 | `HTTP request failed` in widget test | Real HTTP calls in test | Inject `MockClient` from `package:http/testing.dart` |
| 10 | `find.byKey` returns nothing | Key not set on widget | Add `Key('identifier')` to widget; prefer `testID`-style naming |
| 11 | Bloc test expects wrong state order | Missing intermediate states | Use `blocTest` with exact emission sequence in `expect` |
| 12 | Riverpod override not applied | Provider created before override | Use `ProviderScope(overrides: [...])` as root widget in test |

---

## §10 Best Practices Checklist

1. ✅ Use `Key` widgets on all interactive/assertable elements for stable finders
2. ✅ Generate mocks with `build_runner` — run before every test suite
3. ✅ Use `pumpAndSettle()` after interactions; `pump(duration)` for animations
4. ✅ Wrap widgets in `MaterialApp` + providers via a `makeTestable()` helper
5. ✅ Run golden tests on a single OS (macOS) for font consistency
6. ✅ Use `mocktail` for simpler mocking without code generation
7. ✅ Test Bloc/Cubit with `bloc_test` — verify state emission sequences
8. ✅ Mock HTTP via `MockClient` — never make real network calls in unit/widget tests
9. ✅ Use `fakeAsync` for time-dependent logic (debounce, timers, polling)
10. ✅ Tag slow/integration tests and run separately: `flutter test --tags=integration`
11. ✅ Use `integration_test` package with `takeScreenshot()` for CI evidence
12. ✅ Set coverage thresholds: `flutter test --coverage` + `lcov` reporting
13. ✅ Keep test files adjacent: `lib/src/auth/` → `test/src/auth/`
14. ✅ Use `setUp` / `tearDown` for clean state — never share mutable state between tests
