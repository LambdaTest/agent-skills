---
name: rspec-skill
description: >
  Generates RSpec tests in Ruby with describe/context/it blocks, matchers,
  let/before hooks, and mocking. Use when user mentions "RSpec", "describe do",
  "expect().to", "Ruby test". Triggers on: "RSpec", "expect().to eq()",
  "describe do", "Ruby test", "spec file".
languages:
  - Ruby
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# RSpec Testing Skill

## Core Patterns

### Basic Test

```ruby
RSpec.describe Calculator do
  subject(:calculator) { described_class.new }

  describe '#add' do
    it 'adds two positive numbers' do
      expect(calculator.add(2, 3)).to eq(5)
    end

    it 'handles negative numbers' do
      expect(calculator.add(-1, 1)).to eq(0)
    end
  end

  describe '#divide' do
    it 'divides evenly' do
      expect(calculator.divide(10, 2)).to eq(5)
    end

    it 'raises on zero divisor' do
      expect { calculator.divide(10, 0) }.to raise_error(ZeroDivisionError)
    end
  end
end
```

### Matchers

```ruby
# Equality
expect(actual).to eq(expected)           # ==
expect(actual).to eql(expected)          # eql?
expect(actual).to equal(expected)        # equal? (same object)
expect(actual).to be(expected)           # equal?

# Comparison
expect(value).to be > 5
expect(value).to be_between(1, 10).inclusive

# Truthiness
expect(value).to be_truthy
expect(value).to be_falsey
expect(value).to be_nil

# Collections
expect(array).to include(3)
expect(array).to contain_exactly(1, 2, 3)
expect(array).to match_array([3, 1, 2])
expect(hash).to include(name: 'Alice')

# Strings
expect(str).to include('hello')
expect(str).to start_with('He')
expect(str).to match(/\d+/)

# Types
expect(obj).to be_a(String)
expect(obj).to be_an_instance_of(MyClass)

# Exceptions
expect { method }.to raise_error(StandardError)
expect { method }.to raise_error(StandardError, /message/)

# Change
expect { user.activate }.to change(user, :active).from(false).to(true)
expect { list.push(1) }.to change(list, :size).by(1)
```

### Hooks and Let

```ruby
RSpec.describe UserService do
  let(:repo) { instance_double(UserRepository) }
  let(:service) { described_class.new(repo) }

  before(:each) do
    allow(repo).to receive(:save).and_return(true)
  end

  after(:each) { cleanup }
  before(:all) { setup_database }
  after(:all) { teardown_database }

  context 'when creating a user' do
    it 'saves to repository' do
      service.create('Alice', 'alice@test.com')
      expect(repo).to have_received(:save).once
    end
  end
end
```

### Mocking and Stubbing

```ruby
# Doubles
user = double('User', name: 'Alice', email: 'alice@test.com')
user = instance_double(User, name: 'Alice')

# Stubs
allow(service).to receive(:fetch).and_return(data)
allow(service).to receive(:fetch).with('id').and_return(user)

# Expectations
expect(service).to receive(:save).once
expect(service).to receive(:notify).with('alice@test.com')
expect(service).not_to receive(:delete)
```

### Shared Examples

```ruby
RSpec.shared_examples 'a valid model' do
  it { is_expected.to be_valid }
  it { is_expected.to respond_to(:save) }
end

RSpec.describe User do
  subject { described_class.new(name: 'Alice') }
  it_behaves_like 'a valid model'
end
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `before` with heavy setup | `let` (lazy) | Only evaluates when used |
| No contexts | `context 'when...'` | Clear scenarios |
| Instance variables | `let` blocks | Cleaner, lazier |
| `should` syntax | `expect().to` | Modern RSpec |

## Setup: `gem install rspec` then `rspec --init`
## Run: `bundle exec rspec` or `rspec spec/models/user_spec.rb`
## Config: `.rspec` file with `--format documentation --color`

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
