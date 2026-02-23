# RSpec — Advanced Patterns & Playbook

## Shared Examples & Contexts

```ruby
RSpec.shared_examples "a paginated endpoint" do |path|
  it "returns paginated results" do
    get path, params: { page: 1, per_page: 10 }
    expect(response).to have_http_status(:ok)
    expect(json_body["data"].length).to be <= 10
    expect(json_body).to include("meta" => include("total", "page"))
  end
end

RSpec.shared_context "authenticated user" do
  let(:user) { create(:user) }
  let(:token) { generate_jwt(user) }
  before { request.headers["Authorization"] = "Bearer #{token}" }
end

describe UsersController do
  include_context "authenticated user"
  it_behaves_like "a paginated endpoint", "/api/users"
end
```

## Factory & Trait Patterns

```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    name { Faker::Name.name }
    email { Faker::Internet.unique.email }
    password { "password123" }
    confirmed_at { Time.current }

    trait :admin do
      role { :admin }
      after(:create) { |u| u.permissions.create!(level: :full) }
    end
    trait :with_orders do
      transient { orders_count { 3 } }
      after(:create) do |user, ctx|
        create_list(:order, ctx.orders_count, user: user)
      end
    end
  end
end

# Usage
let(:admin) { create(:user, :admin) }
let(:buyer) { create(:user, :with_orders, orders_count: 5) }
```

## Advanced Mocking with Doubles

```ruby
describe OrderService do
  let(:payment_gateway) { instance_double(PaymentGateway) }
  let(:notifier) { spy(NotificationService) }
  let(:service) { described_class.new(gateway: payment_gateway, notifier: notifier) }

  it "processes payment and notifies" do
    allow(payment_gateway).to receive(:charge)
      .with(amount: 100, currency: "USD")
      .and_return(OpenStruct.new(success?: true, id: "txn-123"))

    result = service.checkout(cart)

    expect(result).to be_success
    expect(notifier).to have_received(:send).with(
      hash_including(type: :order_confirmed, transaction_id: "txn-123")
    )
  end

  it "handles payment failure" do
    allow(payment_gateway).to receive(:charge).and_raise(PaymentError, "declined")
    expect { service.checkout(cart) }.to raise_error(PaymentError, /declined/)
    expect(notifier).not_to have_received(:send)
  end
end
```

## Request Specs (Rails API)

```ruby
RSpec.describe "Users API", type: :request do
  describe "POST /api/users" do
    let(:valid_params) { { user: { name: "Alice", email: "alice@test.com" } } }

    it "creates user" do
      expect { post "/api/users", params: valid_params, as: :json }
        .to change(User, :count).by(1)
      expect(response).to have_http_status(:created)
      expect(json_body["name"]).to eq("Alice")
    end

    it "returns errors for invalid data" do
      post "/api/users", params: { user: { name: "" } }, as: :json
      expect(response).to have_http_status(:unprocessable_entity)
      expect(json_body["errors"]).to include("name")
    end
  end
end
```

## Custom Matchers

```ruby
RSpec::Matchers.define :have_json_body_with do |expected|
  match do |response|
    body = JSON.parse(response.body)
    expected.all? { |k, v| body[k.to_s] == v }
  end
  failure_message { |r| "expected body to contain #{expected}, got #{r.body}" }
end

expect(response).to have_json_body_with(name: "Alice", role: "admin")
```

## Configuration

```ruby
# spec/spec_helper.rb
RSpec.configure do |config|
  config.expect_with(:rspec) { |e| e.syntax = :expect }
  config.order = :random
  config.filter_run_when_matching :focus
  config.profile_examples = 5
  config.shared_context_metadata_behavior = :apply_to_host_groups

  config.before(:suite) { DatabaseCleaner.strategy = :transaction }
  config.around(:each) { |ex| DatabaseCleaner.cleaning { ex.run } }
end
```

## Anti-Patterns

- ❌ `let!` everywhere — use lazy `let` unless setup is truly required
- ❌ `subject { described_class.new }` without named subject — prefer `subject(:service)`
- ❌ `before` blocks that define return values — use `let` for data, `before` for actions
- ❌ Testing private methods directly — test through public interface
- ❌ `allow_any_instance_of` — inject dependencies instead
