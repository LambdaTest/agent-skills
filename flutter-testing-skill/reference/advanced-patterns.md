# Flutter Testing — Advanced Patterns & Playbook

## Widget Testing with Mocks

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([UserRepository, AuthService])
void main() {
  late MockUserRepository mockRepo;
  late MockAuthService mockAuth;

  setUp(() {
    mockRepo = MockUserRepository();
    mockAuth = MockAuthService();
  });

  testWidgets('displays user list', (WidgetTester tester) async {
    when(mockRepo.getUsers()).thenAnswer((_) async => [
      User(id: 1, name: 'Alice'),
      User(id: 2, name: 'Bob'),
    ]);

    await tester.pumpWidget(MaterialApp(
      home: ProviderScope(
        overrides: [userRepoProvider.overrideWithValue(mockRepo)],
        child: const UserListScreen(),
      ),
    ));

    await tester.pumpAndSettle();

    expect(find.text('Alice'), findsOneWidget);
    expect(find.text('Bob'), findsOneWidget);
    expect(find.byType(ListTile), findsNWidgets(2));
  });

  testWidgets('handles error state', (tester) async {
    when(mockRepo.getUsers()).thenThrow(Exception('Network error'));
    await tester.pumpWidget(/* ... */);
    await tester.pumpAndSettle();
    expect(find.text('Something went wrong'), findsOneWidget);
    expect(find.byIcon(Icons.refresh), findsOneWidget);
  });
}
```

## Golden Tests (Visual Regression)

```dart
testWidgets('matches golden file', (tester) async {
  await tester.pumpWidget(MaterialApp(
    home: Scaffold(body: ProductCard(product: testProduct)),
  ));
  await expectLater(
    find.byType(ProductCard),
    matchesGoldenFile('goldens/product_card.png'),
  );
});

// Update goldens: flutter test --update-goldens
```

## Integration Testing

```dart
// integration_test/app_test.dart
import 'package:integration_test/integration_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('full login flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(Key('email')), 'user@test.com');
    await tester.enterText(find.byKey(Key('password')), 'password');
    await tester.tap(find.byKey(Key('login-btn')));
    await tester.pumpAndSettle(const Duration(seconds: 3));

    expect(find.text('Welcome'), findsOneWidget);

    // Scroll and interact
    await tester.drag(find.byType(ListView), const Offset(0, -500));
    await tester.pumpAndSettle();
    expect(find.text('Product 10'), findsOneWidget);
  });
}
```

## Bloc Testing

```dart
import 'package:bloc_test/bloc_test.dart';

blocTest<UserBloc, UserState>(
  'emits [loading, loaded] when FetchUsers is added',
  build: () {
    when(() => mockRepo.getUsers()).thenAnswer((_) async => [User(name: 'Alice')]);
    return UserBloc(mockRepo);
  },
  act: (bloc) => bloc.add(FetchUsers()),
  expect: () => [
    const UserState.loading(),
    isA<UserLoaded>().having((s) => s.users.length, 'user count', 1),
  ],
  verify: (_) { verify(() => mockRepo.getUsers()).called(1); },
);
```

## Anti-Patterns

- ❌ `await tester.pump()` without `pumpAndSettle()` for animations — incomplete renders
- ❌ `find.text()` for dynamic/localized strings — use `find.byKey(Key('...'))`
- ❌ Missing `setUp`/`tearDown` for mocks — stale state between tests
- ❌ Integration tests without `IntegrationTestWidgetsFlutterBinding.ensureInitialized()`
