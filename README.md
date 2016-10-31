# C++11/14/17

## Overview
Many of these descriptions and examples come from their proposal papers, summarized in my own words.

C++17 includes the following new language features:
- [template argument deduction for class templates](#template-argument-deduction-for-class-templates)
- [declaring non-type template parameters with auto](#declaring-non-type-template-parameters-with-auto)
- [folding expressions](#folding-expressions)
- [new Rules for auto deduction from braced-init-list](#new-rules-for-auto-deduction---from---braced---init---list)
- [constexpr lambda](#constexpr-lambda)
- [inline variables](#inline-variables)
- [nested namespaces](#nested-namespaces)
- [structured bindings](#structured-bindings)
- [selection statements with initializer](#selection-statements-with-initializer)
- [constexpr if](#constexpr-if)

C++17 includes the following new library features:
- [std::variant](#std::variant)
- [std::optional](#std::optional)
- [std::any](#std::any)
- [std::string_view](#std::string_view)
- [std::invoke](#std::invoke)
- [std::apply](#std::apply)
- [splicing for maps and sets](#splicing-for-maps-and-sets)

## C++17 Language Features

### Template argument deduction for class templates
Automatic template argument deduction much like how it's done for functions, but now including class constructors.
```c++
template <typename T>
struct MyContainer {
  T val;
  MyContainer(T val) : val(val) {}
  // ...
};
MyContainer c1{ 1 }; // OK MyContainer<int>
MyContainer c2; // OK MyContainer<>
```

### Declaring non-type template parameters with auto
Following the deduction rules of `auto`, while respecting the non-type template parameter list of allowable types[\*], template arguments can be deduced from the types of its arguments:
```c++
// Explicitly pass type `int` as template argument.
auto seq = std::integer_sequence<int, 0, 1, 2>();
// Type is deduced to be `int`.
auto seq2 = my_integer_sequence<0, 1, 2>();
```
\* - For example, you cannot use a `double` as a template parameter type, which also makes this an invalid deduction using `auto`.

### Folding expressions
A fold expression performs a fold of a template parameter pack over a binary operator.
* An expression of the form `(... op e)` or `(e op ...)`, where `op` is a fold-operator and `e` is an unexpanded parameter pack, are called _unary folds_.
* An expression of the form `(e1 op1 ... op2 e2)`, where `op1` and `op2` are fold-operators, is called a _binary fold_. Either `e1` or `e2` are unexpanded parameter packs, but not both.
```c++
template<typename... Args>
bool logicalAnd(Args... args) {
    // Binary folding.
    return (true && ... && args);
}
bool b = true;
bool& b2 = b;
assert(logicalAnd(b, b2, true) == true);
```
```c++
template<typename... Args>
auto sum(Args... args) {
    // Unary folding.
    return (... + args);
}
assert(sum(1.0, 2.0f, 3) == 6.0);
```

### New rules for auto deduction from braced-init-list
Changes to `auto` deduction when used with the uniform initialization syntax. Previously, `auto x{ 3 };` deduces a `std::initializer_list<int>`, which now deduces to `int`.
```c++
auto x1{ 1, 2, 3 }; // error: not a single element
auto x2 = { 1, 2, 3 }; // decltype(x2) is std::initializer_list<int>
auto x3{ 3 }; // decltype(x3) is int
auto x4{ 3.0 }; // decltype(x4) is double
```

### Constexpr lambda
Compile-time lambdas using `constexpr`.
```c++
auto identity = [] (int n) constexpr { return n; };
constexpr int i = identity(123);
```
```c++
constexpr auto add = [] (int x, int y) {
  auto L = [=] { return x; };
  auto R = [=] { return y; };
  return [=] { return L() + R(); };
};
static_assert(add(1, 2)() == 3);
```
```c++
constexpr int addOne(int n) {
  return [n] { return n + 1; }();
}
static_assert(addOne(1) == 2);
```

### Inline variables
The inline specifier can be applied to variables as well as to functions. A variable declared inline has the same semantics as a function declared inline.
```c++
// Disassembly example using compiler explorer.
struct S { int x; };
inline S x1 = S{321}; // mov esi, dword ptr [x1]
                      // x1: .long 321

S x2 = S{123};        // mov eax, dword ptr [.L_ZZ4mainE2x2]
                      // mov dword ptr [rbp - 8], eax
                      // .L_ZZ4mainE2x2: .long 123
```

### Nested namespaces
Using the namespace resolution operator to create nested namespace definitions.
```c++
namespace A {
  namespace B {
    namespace C {
      int i;
    }
  }
}
// vs.
namespace A::B::C {
  int i;
}
```

### Structured bindings
A proposal for de-structuring initialization, that would allow writing `auto {x, y, z} = expr;` where the type of `expr` was a tuple-like object, whose elements would be bound to the variables `x`, `y`, and `z` (which this construct declares). _Tuple-like objects_ include `std::tuple`, `std::pair`, `std::array`, and aggregate structures.
```c++
using Coordinate = std::pair<int, int>;
Coordinate origin() {
  return Coordinate{0, 0};
}
const auto [ x, y ] = origin();
assert(x == 0);
assert(y == 0);
```

### Selection statements with initializer
New versions of the `if` and `switch` statements which simplify common code patterns and help users keep scopes tight.
```c++
{
  std::lock_guard<std::mutex> lk(mx);
  if (v.empty()) v.push_back(val);
}
// vs.
if (std::lock_guard<std::mutex> lk(mx); v.empty()) {
  v.push_back(val);
}
```
```c++
Foo gadget(args);
switch (auto s = gadget.status()) {
  case OK: gadget.zip(); break;
  case Bad: throw BadFoo(s.message());
}
// vs.
switch (Foo gadget(args); auto s = gadget.status()) {
  case OK: gadget.zip(); break;
  case Bad: throw BadFoo(s.message());
}
```

### Constexpr if
Write code that is instantiated depending on a compile-time condition.
```c++
template <typename T>
constexpr bool isIntegral() {
  if constexpr (std::is_integral<T>::value) {
    return true;
  } else {
    return false;
  }
}
static_assert(isIntegral<int>() == true);
static_assert(isIntegral<char>() == true);
static_assert(isIntegral<double>() == false);
struct S {};
static_assert(isIntegral<S>() == false);
```

## C++17 Library Features

### std::variant
The class template `std::variant` represents a type-safe `union`. An instance of `std::variant` at any given time holds a value of one of its alternative types (it's also possible for it to be valueless).
```c++
std::variant<int, double> v{ 12 };
assert(std::get<int>(v) == 12);
assert(std::get<0>(v) == 12);
v = 12.0;
assert(std::get<double>(v) == 12.0);
assert(std::get<1>(v) == 12.0);
```

### std::optional
The class template `std::optional` manages an optional contained value, i.e. a value that may or may not be present. A common use case for optional is the return value of a function that may fail.
```c++
std::optional<std::string> create(bool b) {
  if (b) {
    return "Godzilla";
  } else {
    return {};
  }
}
assert(create(false).value_or("empty") == "empty");
assert(create(true).value() == "Godzilla");
// optional-returning factory functions are usable as conditions of while and if
if (auto str = create(true)) {
  // ...
}
```

### std::any
A type-safe container for single values of any type.
```c++
std::any x{ 5 };
assert(x.has_value() == true);
assert(std::any_cast<int>(x) == 5);
std::any_cast<int&>(x) = 10;
assert(std::any_cast<int>(x) == 10);
```

### std::string_view
The class template basic_string_view describes an object that can refer to a constant contiguous sequence of `char`-like objects with the first element of the sequence at position zero. Useful for providing an abstraction on top of strings (e.g. for parsing).
```c++
// Regular strings.
std::string_view cppstr{ "foo" };
// Wide strings.
std::wstring_view wcstr_v{ L"baz" };
// Character arrays.
char array[3] = {'b', 'a', 'r'};
std::string_view array_v(array, sizeof array);
```
```c++
std::string str{ "   trim me" };
std::string_view v{ str };
v.remove_prefix(std::min(v.find_first_not_of(" "), v.size()));
assert(str == "   trim me");
assert(v == "trim me");
```

### std::invoke
Invoke a `Callable` object with parameters. Examples of `Callable` objects are `std::function` or `std::bind` where an object can be called similarly to a regular function.
```c++
template <typename Callable>
class Proxy {
    Callable c;
public:
    Proxy(Callable c): c(c) {}
    template <class... Args>
    decltype(auto) operator()(Args&&... args) {
        // ...
        return std::invoke(c, std::forward<Args>(args)...);
    }
};
auto add = [] (int x, int y) {
  return x + y;
};
Proxy<decltype(add)> p{ add };
assert(p(1, 2) == 3);
```

### std::apply
Invoke a `Callable` object with a tuple of arguments.
```c++
auto add = [] (int x, int y) {
  return x + y;
};
assert(std::apply(add, std::make_tuple( 1, 2 )) == 3);
```

### Splicing for maps and sets
Moving nodes and merging containers without the overhead of expensive copies, moves, or heap allocations/deallocations.

Moving elements from one map to another:
```c++
std::map<int, string> src{ { 1, "one" }, { 2, "two" }, { 3, "buckle my shoe" } };
std::map<int, string> dst{ { 3, "three" } };
dst.insert(src.extract(src.find(1))); // Cheap remove and insert of { 1, "one" } from `src` to `dst`.
dst.insert(src.extract(2)); // Cheap remove and insert of { 2, "two" } from `src` to `dst`.
// dst == { { 1, "one" }, { 2, "two" }, { 3, "three" } };
```

Inserting an entire set:
```c++
std::set<int> src{1, 3, 5};
std::set<int> dst{2, 4, 5};
dst.merge(src);
// src == { 5 }
// dst == { 1, 2, 3, 4, 5 }
```

Inserting elements which outlive the container:
```c++
auto elementFactory() {
  std::set<...> s;
  s.emplace(...);
  return s.extract(s.begin());
}
s2.insert(elementFactory());
```

Changing the key of a map element:
```c++
std::map<int, string> m{ { 1, "one" }, { 2, "two" }, { 3, "three" } };
auto e = m.extract(2);
e.key() = 4;
m.insert(std::move(e));
// m == { { 1, "one" }, { 3, "three" }, { 4, "two" } }
```

## C++14 Language Features
TODO

## C++14 Library Features
TODO

## C++11 Language Features
TODO

## C++11 Library Features
TODO
