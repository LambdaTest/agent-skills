---
name: flutter-testing-skill
description: >
  Generates Flutter widget tests, integration tests, and golden tests in Dart.
  Supports local execution and TestMu AI cloud for real device testing.
  Use when user mentions "Flutter", "widget test", "WidgetTester", "testWidgets",
  "flutter_test", "integration_test". Triggers on: "Flutter", "widget test",
  "Dart test", "testWidgets", "WidgetTester", "golden test".
languages:
  - Dart
category: mobile-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Flutter Testing Skill

You are a senior Flutter developer specializing in testing.

## Step 1 — Test Type

```
├─ "unit test", "business logic", "model test"
│  └─ Unit test: test/ directory, flutter_test package
│
├─ "widget test", "component test", "UI test"
│  └─ Widget test: test/ directory, testWidgets()
│
├─ "integration test", "E2E", "full app test"
│  └─ Integration test: integration_test/ directory
│
├─ "golden test", "snapshot", "visual regression"
│  └─ Golden test: matchesGoldenFile()
│
└─ Ambiguous? → Widget test (most common)
```

## Core Patterns — Dart

### Widget Test (Most Common)

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:my_app/screens/login_screen.dart';

void main() {
  testWidgets('Login screen shows email and password fields', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginScreen()));

    // Verify fields exist
    expect(find.byType(TextField), findsNWidgets(2));
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.byType(ElevatedButton), findsOneWidget);
  });

  testWidgets('Login with valid credentials navigates to dashboard', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginScreen()));

    // Enter credentials
    await tester.enterText(find.byKey(const Key('emailField')), 'user@test.com');
    await tester.enterText(find.byKey(const Key('passwordField')), 'password123');

    // Tap login button
    await tester.tap(find.byKey(const Key('loginButton')));
    await tester.pumpAndSettle(); // Wait for animations and navigation

    // Verify navigation
    expect(find.text('Dashboard'), findsOneWidget);
  });

  testWidgets('Shows error for invalid credentials', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginScreen()));

    await tester.enterText(find.byKey(const Key('emailField')), 'wrong@test.com');
    await tester.enterText(find.byKey(const Key('passwordField')), 'wrong');
    await tester.tap(find.byKey(const Key('loginButton')));
    await tester.pumpAndSettle();

    expect(find.text('Invalid credentials'), findsOneWidget);
  });
}
```

### Finder Strategies

```dart
// By Key (best — explicit test identifiers)
find.byKey(const Key('loginButton'))
find.byKey(const ValueKey('email_input'))

// By Type
find.byType(ElevatedButton)
find.byType(TextField)
find.byType(LoginScreen)

// By Text
find.text('Login')
find.textContaining('Welcome')

// By Icon
find.byIcon(Icons.login)

// By Widget predicate
find.byWidgetPredicate((widget) => widget is Text && widget.data!.startsWith('Error'))

// Descendant/Ancestor
find.descendant(of: find.byType(AppBar), matching: find.text('Title'))
find.ancestor(of: find.text('Login'), matching: find.byType(Card))
```

### Actions

```dart
await tester.tap(finder);                    // Tap
await tester.longPress(finder);              // Long press
await tester.enterText(finder, 'text');      // Type text
await tester.drag(finder, const Offset(0, -300));  // Drag/scroll
await tester.fling(finder, const Offset(0, -500), 1000); // Fling/swipe

// CRITICAL: Always pump after actions
await tester.pump();                         // Single frame
await tester.pump(const Duration(seconds: 1)); // Advance time
await tester.pumpAndSettle();                // Wait for animations to finish
```

### Integration Test

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Full login flow', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    // Login
    await tester.enterText(find.byKey(const Key('emailField')), 'user@test.com');
    await tester.enterText(find.byKey(const Key('passwordField')), 'password123');
    await tester.tap(find.byKey(const Key('loginButton')));
    await tester.pumpAndSettle();

    // Verify dashboard
    expect(find.text('Dashboard'), findsOneWidget);

    // Navigate to settings
    await tester.tap(find.byIcon(Icons.settings));
    await tester.pumpAndSettle();
    expect(find.text('Settings'), findsOneWidget);
  });
}
```

### Golden Tests (Visual Regression)

```dart
testWidgets('Login screen matches golden', (WidgetTester tester) async {
  await tester.pumpWidget(const MaterialApp(home: LoginScreen()));
  await tester.pumpAndSettle();

  await expectLater(
    find.byType(LoginScreen),
    matchesGoldenFile('goldens/login_screen.png'),
  );
});
```

```bash
# Generate golden files
flutter test --update-goldens

# Run golden comparison
flutter test
```

### Mocking Dependencies

```dart
// Using Mockito
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

@GenerateMocks([AuthService])
void main() {
  late MockAuthService mockAuth;

  setUp(() {
    mockAuth = MockAuthService();
  });

  testWidgets('Login calls auth service', (tester) async {
    when(mockAuth.login(any, any)).thenAnswer((_) async => true);

    await tester.pumpWidget(MaterialApp(
      home: LoginScreen(authService: mockAuth),
    ));

    await tester.enterText(find.byKey(const Key('emailField')), 'user@test.com');
    await tester.enterText(find.byKey(const Key('passwordField')), 'pass123');
    await tester.tap(find.byKey(const Key('loginButton')));
    await tester.pumpAndSettle();

    verify(mockAuth.login('user@test.com', 'pass123')).called(1);
  });
}
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| No `pumpAndSettle()` after action | Always pump after interactions | Animations not complete |
| `find.text()` for dynamic text | `find.byKey()` | Locale/text changes break tests |
| Testing implementation details | Test user-facing behavior | Brittle |
| No mocking in widget tests | Mock services, repos | Tests hit real APIs |

### TestMu AI Cloud (Integration Tests)

```bash
# Run integration tests on LambdaTest real devices
# 1. Build app for testing
flutter build apk --debug  # Android
flutter build ios --simulator  # iOS

# 2. Upload to LambdaTest
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@build/app/outputs/flutter-apk/app-debug.apk"

# 3. Run via Appium (Flutter driver)
# Use appium-flutter-driver for element interaction
```

## Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `flutter test` |
| Run specific file | `flutter test test/login_test.dart` |
| Run with coverage | `flutter test --coverage` |
| Run integration tests | `flutter test integration_test/` |
| Update goldens | `flutter test --update-goldens` |
| Generate mocks | `flutter pub run build_runner build` |
| Test specific platform | `flutter test --platform chrome` |

## pubspec.yaml

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  integration_test:
    sdk: flutter
  mockito: ^5.4.0
  build_runner: ^2.4.0
```

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
