# C++17/14/11

## Overview
Many of these descriptions and examples come from various resources (see [Acknowledgements](#acknowledgements) section), summarized in my own words.

C++17 includes the following new language features:
- [template argument deduction for class templates](#template-argument-deduction-for-class-templates)
- [declaring non-type template parameters with auto](#declaring-non-type-template-parameters-with-auto)
- [folding expressions](#folding-expressions)
- [new rules for auto deduction from braced-init-list](#new-rules-for-auto-deduction-from-braced-init-list)
- [constexpr lambda](#constexpr-lambda)
- [lambda capture this by value](#lambda-capture-this-by-value)
- [inline variables](#inline-variables)
- [nested namespaces](#nested-namespaces)
- [structured bindings](#structured-bindings)
- [selection statements with initializer](#selection-statements-with-initializer)
- [constexpr if](#constexpr-if)
- [utf-8 character literals](#utf-8-character-literals)
- [direct-list-initialization of enums](#direct-list-initialization-of-enums)

C++17 includes the following new library features:
- [std::variant](#stdvariant)
- [std::optional](#stdoptional)
- [std::any](#stdany)
- [std::string_view](#stdstring_view)
- [std::invoke](#stdinvoke)
- [std::apply](#stdapply)
- [splicing for maps and sets](#splicing-for-maps-and-sets)

C++14 includes the following new language features:
- [binary literals](#binary-literals)
- [generic lambda expressions](#generic-lambda-expressions)
- [lambda capture initializers](#lambda-capture-initializers)
- [return type deduction](#return-type-deduction)
- [decltype(auto)](#decltypeauto)
- [relaxing constraints on constexpr functions](#relaxing-constraints-on-constexpr-functions)
- [variable templates](#variable-templates)

C++14 includes the following new library features:
- [user-defined literals for standard library types](#user-defined-literals-for-standard-library-types)
- [compile-time integer sequences](#compile-time-integer-sequences)
- [std::make_unique](#stdmake_unique)

C++11 includes the following new language features:
- [move semantics](#move-semantics)
- [variadic templates](#variadic-templates)
- [rvalue references](#rvalue-references)
- [initializer lists](#initializer-lists)
- [static assertions](#static-assertions)
- [auto](#auto)
- [lambda expressions](#lambda-expressions)
- [decltype](#decltype)
- [template aliases](#template-aliases)
- [nullptr](#nullptr)
- [strongly-typed enums](#strongly-typed-enums)
- [attributes](#attributes)
- [constexpr](#constexpr)
- [delegating constructors](#delegating-constructors)
- [user-defined literals](#user-defined-literals)
- [explicit virtual overrides](#explicit-virtual-overrides)
- [final specifier](#final-specifier)
- [default functions](#default-functions)
- [deleted functions](#deleted-functions)
- [range-based for loops](#range-based-for-loops)
- [special member functions for move semantics](#special-member-functions-for-move-semantics)
- [converting constructors](#converting-constructors)
- [explicit conversion functions](#explicit-conversion-functions)
- [inline-namespaces](#inline-namespaces)
- [non-static data member initializers](#non-static-data-member-initializers)
- [right angle brackets](#right-angle-brackets)

C++11 includes the following new library features:
- [std::move](#stdmove)
- [std::forward](#stdforward)
- [std::to_string](#stdto_string)
- [type traits](#type-traits)
- [smart pointers](#smart-pointers)
- [std::chrono](#stdchrono)
- [tuples](#tuples)
- [std::tie](#stdtie)
- [std::array](#stdarray)
- [unordered containers](#unordered-containers)
- [std::make_shared](#stdmake_shared)
- [memory model](#memory-model)

## C++17 Language Features

### Template argument deduction for class templates
Automatic template argument deduction much like how it's done for functions, but now including class constructors.
```c++
template <typename T = float>
struct MyContainer {
  T val;
  MyContainer() : val() {}
  MyContainer(T val) : val(val) {}
  // ...
};
MyContainer c1{ 1 }; // OK MyContainer<int>
MyContainer c2; // OK MyContainer<float>
```

### Declaring non-type template parameters with auto
Following the deduction rules of `auto`, while respecting the non-type template parameter list of allowable types[\*], template arguments can be deduced from the types of its arguments:
```c++
template <auto ... seq>
struct my_integer_sequence {
  // Implementation here ...
};

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
logicalAnd(b, b2, true); // == true
```
```c++
template<typename... Args>
auto sum(Args... args) {
    // Unary folding.
    return (... + args);
}
sum(1.0, 2.0f, 3); // == 6.0
```

### New rules for auto deduction from braced-init-list
Changes to `auto` deduction when used with the uniform initialization syntax. Previously, `auto x{ 3 };` deduces a `std::initializer_list<int>`, which now deduces to `int`.
```c++
auto x1{ 1, 2, 3 }; // error: not a single element
auto x2 = { 1, 2, 3 }; // decltype(x2) is std::initializer_list<int>
auto x3{ 3 }; // decltype(x3) is int
auto x4{ 3.0 }; // decltype(x4) is double
```

### constexpr lambda
Compile-time lambdas using `constexpr`.
```c++
auto identity = [] (int n) constexpr { return n; };
static_assert(identity(123) == 123);
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

### Lambda capture `this` by value
Capturing `this` in a lambda's environment was previously reference-only. An example of where this is problematic is asynchronous code using callbacks that require an object to be available, potentially past its lifetime. `*this` (C++17) will now make a copy of the current object, while `this` (C++11) continues to capture by reference.
```c++
struct MyObj {
  int value{ 123 };
  auto getValueCopy() {
    return [*this] { return value; };
  }
  auto getValueRef() {
    return [this] { return value; };
  }
};
MyObj mo;
auto valueCopy = mo.getValueCopy();
auto valueRef = mo.getValueRef();
mo.value = 321;
valueCopy(); // 123
valueRef(); // 321
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
A proposal for de-structuring initialization, that would allow writing `auto [ x, y, z ] = expr;` where the type of `expr` was a tuple-like object, whose elements would be bound to the variables `x`, `y`, and `z` (which this construct declares). _Tuple-like objects_ include [`std::tuple`](#tuples), `std::pair`, [`std::array`](#stdarray), and aggregate structures.
```c++
using Coordinate = std::pair<int, int>;
Coordinate origin() {
  return Coordinate{0, 0};
}

const auto [ x, y ] = origin();
x; // == 0
y; // == 0
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

### constexpr if
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

### UTF-8 Character Literals
A character literal that begins with `u8` is a character literal of type `char`. The value of a UTF-8 character literal is equal to its ISO 10646 code point value.
```c++
char x = u8'x';
```

### Direct List Initialization of Enums
Enums can now be initialized using braced syntax.
```c++
enum byte : unsigned char {};
byte b{0}; // OK
byte c{-1}; // ERROR
byte d = byte{1}; // OK
byte e = byte{256}; // ERROR
```

## C++17 Library Features

### std::variant
The class template `std::variant` represents a type-safe `union`. An instance of `std::variant` at any given time holds a value of one of its alternative types (it's also possible for it to be valueless).
```c++
std::variant<int, double> v{ 12 };
std::get<int>(v); // == 12
std::get<0>(v); // == 12
v = 12.0;
std::get<double>(v); // == 12.0
std::get<1>(v); // == 12.0
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

create(false).value_or("empty"); // == "empty"
create(true).value(); // == "Godzilla"
// optional-returning factory functions are usable as conditions of while and if
if (auto str = create(true)) {
  // ...
}
```

### std::any
A type-safe container for single values of any type.
```c++
std::any x{ 5 };
x.has_value() // == true
std::any_cast<int>(x) // == 5
std::any_cast<int&>(x) = 10;
std::any_cast<int>(x) // == 10
```

### std::string_view
A non-owning reference to a string. Useful for providing an abstraction on top of strings (e.g. for parsing).
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
str; //  == "   trim me"
v; // == "trim me"
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
p(1, 2); // == 3
```

### std::apply
Invoke a `Callable` object with a tuple of arguments.
```c++
auto add = [] (int x, int y) {
  return x + y;
};
std::apply(add, std::make_tuple( 1, 2 )); // == 3
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

### Binary literals
Binary literals provide a convenient way to represent a base-2 number.
It is possible to separate digits with `'`.
```c++
0b110 // == 6
0b1111'1111 // == 255
```

### Generic lambda expressions
C++14 now allows the `auto` type-specifier in the parameter list, enabling polymorphic lambdas.
```c++
auto identity = [](auto x) { return x; };
int three = identity(3); // == 3
std::string foo = identity("foo"); // == "foo"
```

### Lambda capture initializers
This allows creating lambda captures initialized with arbitrary expressions. The name given to the captured value does not need to be related to any variables in the enclosing scopes and introduces a new name inside the lambda body. The initializing expression is evaluated when the lambda is _created_ (not when it is _invoked_).
```c++
int factory(int i) { return i * 10; }
auto f = [x = factory(2)] { return x; }; // returns 20

auto generator = [x = 0] () mutable {
  // this would not compile without 'mutable' as we are modifying x on each call
  return x++;
};
auto a = generator(); // == 0
auto b = generator(); // == 1
auto c = generator(); // == 2
```
Because it is now possible to _move_ (or _forward_) values into a lambda that could previously be only captured by copy or reference we can now capture move-only types in a lambda by value. Note that in the below example the `p` in the capture-list of `task2` on the left-hand-side of `=` is a new variable private to the lambda body and does not refer to the original `p`.
```c++
auto p = std::make_unique<int>(1);

auto task1 = [=] { *p = 5; }; // ERROR: std::unique_ptr cannot be copied
// vs.
auto task2 = [p = std::move(p)] { *p = 5; }; // OK: p is move-constructed into the closure object
// the original p is empty after task2 is created
```
Using this reference-captures can have different names than the referenced variable.
```c++
auto x = 1;
auto f = [&r = x, x = x * 10] {
  ++r;
  return r + x;
};
f(); // sets x to 2 and returns 12
```

### Return type deduction
Using an `auto` return type in C++14, the compiler will attempt to deduce the type for you. With lambdas, you can now deduce its return type using `auto`, which makes returning a deduced reference or rvalue reference possible.
```c++
// Deduce return type as `int`.
auto f(int i) {
 return i;
}
```
```c++
template <typename T>
auto& f(T& t) {
  return t;
}

// Returns a reference to a deduced type.
auto g = [](auto& x) -> auto& { return f(x); };
int y = 123;
int& z = g(y); // reference to `y`
```

### decltype(auto)
The `decltype(auto)` type-specifier also deduces a type like `auto` does. However, it deduces return types while keeping their references or "const-ness", while `auto` will not.
```c++
const int x = 0;
auto x1 = x; // int
decltype(auto) x2 = x; // const int
int y = 0;
int& y1 = y;
auto y2 = y1; // int
decltype(auto) y3 = y1; // int&
int&& z = 0;
auto z1 = std::move(z); // int
decltype(auto) z2 = std::move(z); // int&&
```
```c++
// Note: Especially useful for generic code!

// Return type is `int`.
auto f(const int& i) {
 return i;
}

// Return type is `const int&`.
decltype(auto) g(const int& i) {
 return i;
}

int x = 123;
static_assert(std::is_same<const int&, decltype(f(x))>::value == 0);
static_assert(std::is_same<int, decltype(f(x))>::value == 1);
static_assert(std::is_same<const int&, decltype(g(x))>::value == 1);
```

### Relaxing constraints on constexpr functions
In C++11, `constexpr` function bodies could only contain a very limited set of syntaxes, including (but not limited to): `typedef`s, `using`s, and a single `return` statement. In C++14, the set of allowable syntaxes expands greatly to include the most common syntax such as `if` statements, multiple `return`s, loops, etc.
```c++
constexpr int factorial(int n) {
  if (n <= 1) {
    return 1;
  } else {
    return n * factorial(n - 1);
  }
}
factorial(5); // == 120
```

### Variable Templates
C++14 allows variables to be templated:

```c++
template<class T>
constexpr T pi = T(3.1415926535897932385);
template<class T>
constexpr T e  = T(2.7182818284590452353);
```

## C++14 Library Features

### User-defined literals for standard library types
New user-defined literals for standard library types, including new built-in literals for `chrono` and `basic_string`. These can be `constexpr` meaning they can be used at compile-time. Some uses for these literals include compile-time integer parsing, binary literals, and imaginary number literals.
```c++
using namespace std::chrono_literals;
auto day = 24h;
day.count(); // == 24
std::chrono::duration_cast<std::chrono::minutes>(day).count(); // == 1440
```

### Compile-time integer sequences
The class template `std::integer_sequence` represents a compile-time sequence of integers. There are a few helpers built on top:
* `std::make_integer_sequence<T, N...>` - creates a sequence of `0, ..., N - 1` with type `T`.
* `std::index_sequence_for<T...>` - converts a template parameter pack into an integer sequence.

Convert an array into a tuple:
```c++
template<typename Array, std::size_t... I>
decltype(auto) a2t_impl(const Array& a, std::integer_sequence<std::size_t, I...>) {
  return std::make_tuple(a[I]...);
}

template<typename T, std::size_t N, typename Indices = std::make_index_sequence<N>>
decltype(auto) a2t(const std::array<T, N>& a) {
  return a2t_impl(a, Indices());
}
```

### std::make_unique
`std::make_unique` is the recommended way to create instances of `std::unique_ptr`s due to the following reasons:
* Avoid having to use the `new` operator.
* Prevents code repetition when specifying the underlying type the pointer shall hold.
* Most importantly, it provides exception-safety. Suppose we were calling a function `foo` like so:
```c++
foo(std::unique_ptr<T>{ new T{} }, function_that_throws(), std::unique_ptr<T>{ new T{} });
```
The compiler is free to call `new T{}`, then `function_that_throws()`, and so on... Since we have allocated data on the heap in the first construction of a `T`, we have introduced a leak here. With `std::make_unique`, we are given exception-safety:
```c++
foo(std::make_unique<T>(), function_that_throws(), std::make_unique<T>());
```

See the section on [smart pointers](#smart-pointers) for more information on `std::unique_ptr` and `std::shared_ptr`.

## C++11 Language Features

### Move semantics
Move semantics is mostly about performance optimization: the ability to move an object without the expensive overhead of copying. The difference between a copy and a move is that a copy leaves the source unchanged, and a move will leave the source either unchanged or radically different -- depending on what the source is. For plain old data, a move is the same as a copy.

To move an object means to transfer ownership of some resource it manages to another object. You could think of this as changing pointers held by the source object to be moved, or now held, by the destination object; the resource remains in its location in memory. Such an inexpensive transfer of resources is extremely useful when the source is an `rvalue`, where the potentially dangerous side-effect of changing the source after the move is redundant since the source is a temporary object that won't be accessible later.

Moves also make it possible to transfer objects such as `std::unique_ptr`s, [smart pointers](#smart-pointers) that are designed to hold a pointer to a unique object, from one scope to another.

See the sections on: [rvalue references](#rvalue-references), [defining move special member functions](#special-member-functions-for-move-semantics), [`std::move`](#stdmove), [`std::forward`](#stdforward).

### Rvalue references
C++11 introduces a new reference termed the _rvalue reference_. An rvalue reference to `A` is created with the syntax `A&&`. This enables two major features: move semantics; and _perfect forwarding_, the ability to pass arguments while maintaining information about them as lvalues/rvalues in a generic way.

`auto` type deduction with lvalues and rvalues:
```c++
int x = 0; // `x` is an lvalue of type `int`
int& xl = x; // `xl` is an lvalue of type `int&`
int&& xr = x; // compiler error -- `x` is an lvalue
int&& xr2 = 0; // `xr2` is an lvalue of type `int&&`
auto& al = x; // `al` is an lvalue of type `int&`
auto&& al2 = x; // `al2` is an lvalue of type `int&`
auto&& ar = 0; // `ar` is an lvalue of type `int&&`
```

See also: [`std::move`](#stdmove), [`std::forward`](#stdforward).

### Variadic templates
The `...` syntax creates a _parameter pack_ or expands one. A template _parameter pack_ is a template parameter that accepts zero or more template arguments (non-types, types, or templates). A template with at least one parameter pack is called a _variadic template_.
```c++
template <typename... T>
struct arity {
  constexpr static int value = sizeof...(T);
};
static_assert(arity<>::value == 0);
static_assert(arity<char, short, int>::value == 3);
```

### Initializer lists
A lightweight array-like container of elements created using a "braced list" syntax. For example, `{ 1, 2, 3 }` creates a sequences of integers, that has type `std::initializer_list<int>`. Useful as a replacement to passing a vector of objects to a function.
```c++
int sum(const std::initializer_list<int>& list) {
  int total = 0;
  for (auto& e : list) {
    total += e;
  }

  return total;
}

auto list = { 1, 2, 3 };
sum(list); // == 6
sum({ 1, 2, 3 }); // == 6
sum({}); // == 0
```

### Static assertions
Assertions that are evaluated at compile-time.
```c++
constexpr int x = 0;
constexpr int y = 1;
static_assert(x == y, "x != y");
```

### auto
`auto`-typed variables are deduced by the compiler according to the type of their initializer.
```c++
auto a = 3.14; // double
auto b = 1; // int
auto& c = b; // int&
auto d = { 0 }; // std::initializer_list<int>
auto&& e = 1; // int&&
auto&& f = b; // int&
auto g = new auto(123); // int*
const auto h = 1; // const int
auto i = 1, j = 2, k = 3; // int, int, int
auto l = 1, m = true, n = 1.61; // error -- `l` deduced to be int, `m` is bool
auto o; // error -- `o` requires initializer
```

Extremely useful for readability, especially for complicated types:
```c++
std::vector<int> v = ...;
std::vector<int>::const_iterator cit = v.cbegin();
// vs.
auto cit = v.cbegin();
```

Functions can also deduce the return type using `auto`. In C++11, a return type must be specified either explicitly, or using `decltype` like so:
```c++
template <typename X, typename Y>
auto add(X x, Y y) -> decltype(x + y) {
  return x + y;
}
add(1, 2); // == 3
add(1, 2.0); // == 3.0
add(1.5, 1.5); // == 3.0
```
The trailing return type in the above example is the _declared type_ (see section on [`decltype`](#decltype)) of the expression `x + y`. For example, if `x` is an integer and `y` is a double, `decltype(x + y)` is a double. Therefore, the above function will deduce the type depending on what type the expression `x + y` yields. Notice that the trailing return type has access to its parameters, and `this` when appropriate.

### Lambda expressions
A `lambda` is an unnamed function object capable of capturing variables in scope. It features: a _capture list_; an optional set of parameters with an optional trailing return type; and a body. Examples of capture lists:
* `[]` - captures nothing.
* `[=]` - capture local objects (local variables, parameters) in scope by value.
* `[&]` - capture local objects (local variables, parameters) in scope by reference.
* `[this]` - capture `this` pointer by value.
* `[a, &b]` - capture objects `a` by value, `b` by reference.

```c++
int x = 1;

auto getX = [=]{ return x; };
getX(); // == 1

auto addX = [=](int y) { return x + y; };
addX(1); // == 2

auto getXRef = [&]() -> int& { return x; };
getXRef(); // int& to `x`
```
By default, value-captures cannot be modified inside the lambda because the compiler-generated method is marked as `const`. The `mutable` keyword allows modifying captured variables. The keyword is placed after the parameter-list (which must be present even if it is empty).
```c++
int x = 1;

auto f1 = [&x] { x = 2; }; // OK: x is a reference and modifies the original

auto f2 = [x] { x = 2; }; // ERROR: the lambda can only perform const-operations on the captured value
// vs.
auto f3 = [x] () mutable { x = 2; }; // OK: the lambda can perform any operations on the captured value
```

### decltype
`decltype` is an operator which returns the _declared type_ of an expression passed to it. Examples of `decltype`:
```c++
int a = 1; // `a` is declared as type `int`
decltype(a) b = a; // `decltype(a)` is `int`
const int& c = a; // `c` is declared as type `const int&`
decltype(c) d = a; // `decltype(c)` is `const int&`
decltype(123) e = 123; // `decltype(123)` is `int`
int&& f = 1; // `f` is declared as type `int&&`
decltype(f) g = 1; // `decltype(f) is `int&&`
decltype((a)) h = g; // `decltype((a))` is int&
```
```c++
template <typename X, typename Y>
auto add(X x, Y y) -> decltype(x + y) {
  return x + y;
}
add(1, 2.0); // `decltype(x + y)` => `decltype(3.0)` => `double`
```

### Template aliases
Semantically similar to using a `typedef` however, template aliases with `using` are easier to read and are compatible with templates.
```c++
template <typename T>
using Vec = std::vector<T>;
Vec<int> v{}; // std::vector<int>

using String = std::string;
String s{"foo"};
```

### nullptr
C++11 introduces a new null pointer type designed to replace C's `NULL` macro. `nullptr` itself is of type `std::nullptr_t` and can be implicitly converted into pointer types, and unlike `NULL`, not convertible to integral types except `bool`.
```c++
void foo(int);
void foo(char*);
foo(NULL); // error -- ambiguous
foo(nullptr); // calls foo(char*)
```

### Strongly-typed enums
Type-safe enums that solve a variety of problems with C-style enums including: implicit conversions, inability to specify the underlying type, scope pollution.
```c++
// Specifying underlying type as `unsigned int`
enum class Color : unsigned int { Red = 0xff0000, Green = 0xff00, Blue = 0xff };
// `Red`/`Green` in `Alert` don't conflict with `Color`
enum class Alert : bool { Red, Green };
Color c = Color::Red;
```

### Attributes
Attributes provide a universal syntax over `__attribute__(...)`, `__declspec`, etc.
```c++
// `noreturn` attribute indicates `f` doesn't return.
[[ noreturn ]] void f() {
  throw "error";
}
```

### constexpr
Constant expressions are expressions evaluated by the compiler at compile-time. Only non-complex computations can be carried out in a constant expression. Use the `constexpr` specifier to indicate the variable, function, etc. is a constant expression.
```c++
constexpr int square(int x) {
  return x * x;
}

int square2(int x) {
  return x * x;
}

int a = square(2);  // mov DWORD PTR [rbp-4], 4

int b = square2(2); // mov edi, 2
                    // call square2(int)
                    // mov DWORD PTR [rbp-8], eax
```

`constexpr` values are those that the compiler can evaluate at compile-time:
```c++
const int x = 123;
constexpr const int& y = x; // error -- constexpr variable `y` must be initialized by a constant expression
```

Constant expressions with classes:
```c++
struct Complex {
  constexpr Complex(double r, double i) : re(r), im(i) { }
  constexpr double real() { return re; }
  constexpr double imag() { return im; }

private:
  double re;
  double im;
};

constexpr Complex I(0, 1);
```

### Delegating constructors
Constructors can now call other constructors in the same class using an initializer list.
```c++
struct Foo {
  int foo;
  Foo(int foo) : foo(foo) {}
  Foo() : Foo(0) {}
};

Foo foo{};
foo.foo; // == 0
```

### User-defined literals
User-defined literals allow you to extend the language and add your own syntax. To create a literal, define a `T operator "" X(...) { ... }` function that returns a type `T`, with a name `X`. Note that the name of this function defines the name of the literal. Any literal names not starting with an underscore are reserved and won't be invoked. There are rules on what parameters a user-defined literal function should accept, according to what type the literal is called on.

Converting Celsius to Fahrenheit:
```c++
// `unsigned long long` parameter required for integer literal.
long long operator "" _celsius(unsigned long long tempCelsius) {
  return std::llround(tempCelsius * 1.8 + 32);
}
24_celsius; // == 75
```

String to integer conversion:
```c++
// `const char*` and `std::size_t` required as parameters.
int operator "" _int(const char* str, std::size_t) {
  return std::stoi(str);
}

"123"_int; // == 123, with type `int`
```

### Explicit virtual overrides
Specifies that a virtual function overrides another virtual function. If the virtual function does not override a parent's virtual function, throws a compiler error.
```c++
struct A {
  virtual void foo();
  void bar();
};

struct B : A {
  void foo() override; // correct -- B::foo overrides A::foo
  void bar() override; // error -- A::bar is not virtual
  void baz() override; // error -- B::baz does not override A::baz
};
```

### Final specifier
Specifies that a virtual function cannot be overridden in a derived class or that a class cannot be inherited from.
```c++
struct A {
  virtual void foo();
};

struct B : A {
  virtual void foo() final;
};

struct C : B {
  virtual void foo(); // error -- declaration of 'foo' overrides a 'final' function
};
```

Class cannot be inherited from.
```c++
struct A final {

};

struct B : A { // error -- base 'A' is marked 'final'

};
```

### Default functions
A more elegant, efficient way to provide a default implementation of a function, such as a constructor.
```c++
struct A {
  A() = default;
  A(int x) : x(x) {}
  int x{ 1 };
};
A a{}; // a.x == 1
A a2{ 123 }; // a.x == 123
```

With inheritance:
```c++
struct B {
  B() : x(1);
  int x;
};

struct C : B {
  // Calls B::B
  C() = default;
};

C c{}; // c.x == 1
```

### Deleted functions
A more elegant, efficient way to provide a deleted implementation of a function. Useful for preventing copies on objects.
```c++
class A {
  int x;

public:
  A(int x) : x(x) {};
  A(const A&) = delete;
  A& operator=(const A&) = delete;
};

A x{ 123 };
A y = x; // error -- call to deleted copy constructor
y = x; // error -- operator= deleted
```

### Range-based for loops
Syntactic sugar for iterating over a container's elements.
```c++
std::array<int, 5> a{ 1, 2, 3, 4, 5 };
for (int& x : a) x *= 2;
// a == { 2, 4, 6, 8, 10 }
```

Note the difference when using `int` as opposed to `int&`:
```c++
std::array<int, 5> a{ 1, 2, 3, 4, 5 };
for (int x : a) x *= 2;
// a == { 1, 2, 3, 4, 5 }
```

### Special member functions for move semantics
The copy constructor and copy assignment operator are called when copies are made, and with C++11's introduction of move semantics, there is now a move constructor and move assignment operator for moves.
```c++
struct A {
  std::string s;
  A() : s("test") {}
  A(const A& o) : s(o.s) {}
  A(A&& o) : s(std::move(o.s)) {}
  A& operator=(A&& o) {
   s = std::move(o.s);
   return *this;
  }
};

A f(A a) {
  return a;
}

A a1 = f(A{}); // move-constructed from rvalue temporary
A a2 = std::move(a1); // move-constructed using std::move
A a3 = A{};
a2 = std::move(a3); // move-assignment using std::move
a1 = f(A{}); // move-assignment from rvalue temporary
```

### Converting constructors
Converting constructors will convert values of braced list syntax into constructor arguments.
```c++
struct A {
  A(int) {}
  A(int, int) {}
  A(int, int, int) {}
};

A a{0, 0}; // calls A::A(int, int)
A b(0, 0); // calls A::A(int, int)
A c = {0, 0}; // calls A::A(int, int)
A d{0, 0, 0}; // calls A::A(int, int, int)
```

Note that the braced list syntax does not allow narrowing:
```c++
struct A {
  A(int) {}
};

A a(1.1); // OK
A b{1.1}; // Error narrowing conversion from double to int
```

Note that if a constructor accepts a `std::initializer_list`, it will be called instead:
```c++
struct A {
  A(int) {}
  A(int, int) {}
  A(int, int, int) {}
  A(std::initializer_list<int>) {}
};

A a{0, 0}; // calls A::A(std::initializer_list<int>)
A b(0, 0); // calls A::A(int, int)
A c = {0, 0}; // calls A::A(std::initializer_list<int>)
A d{0, 0, 0}; // calls A::A(std::initializer_list<int>)
```

### Explicit conversion functions
Conversion functions can now be made explicit using the `explicit` specifier.
```c++
struct A {
  operator bool() const { return true; }
};

struct B {
  explicit operator bool() const { return true; }
};

A a{};
if (a); // OK calls A::operator bool()
bool ba = a; // OK copy-initialization selects A::operator bool()

B b{};
if (b); // OK calls B::operator bool()
bool bb = b; // error copy-initialization does not consider B::operator bool()
```
### Inline namespaces
All members of an inline namespace are treated as if they were part of its parent namespace, allowing specialization of functions and easing the process of versioning. This is a transitive property, if A contains B, which in turn contains C and both B and C are inline namespaces, C's members can be used as if they were on A.

```c++
namespace Program {
  namespace Version1 {
    int getVersion() { return 1; }
    bool isFirstVersion() { return true; }
  }
  inline namespace Version2 {
    int getVersion() { return 2; }
  }
}

int version {Program::getVersion()};              // Uses getVersion() from Version2
int oldVersion {Program::Version1::getVersion()}; // Uses getVersion() from Version1
bool firstVersion {Program::isFirstVersion()};    // Does not compile when Version2 is added
```

### Non-static data member initializers
Allows non-static data members to be initialized where they are declared, potentially cleaning up constructors of default initializations.

```c++
// Default initialization prior to C++11
class Human {
    Human() : age(0) {}
  private:
    unsigned age;
};
// Default initialization on C++11
class Human {
  private:
    unsigned age{0};
};
```


### Right angle Brackets
C++11 is now able to infer when a series of right angle brackets is used as an operator or as a closing statement of typedef, without having to add whitespace.

```c++
typedef std::map<int, std::map <int, std::map <int, int> > > cpp98LongTypedef;
typedef std::map<int, std::map <int, std::map <int, int>>>   cpp11LongTypedef;
```

## C++11 Library Features

### std::move
`std::move` indicates that the object passed to it may be moved, or in other words, moved from one object to another without a copy. The object passed in should not be used after the move in certain situations.

A definition of `std::move` (performing a move is nothing more than casting to an rvalue):
```c++
template <typename T>
typename remove_reference<T>::type&& move(T&& arg) {
  return static_cast<typename remove_reference<T>::type&&>(arg);
}
```

Transferring `std::unique_ptr`s:
```c++
std::unique_ptr<int> p1{ new int };
std::unique_ptr<int> p2 = p1; // error -- cannot copy unique pointers
std::unique_ptr<int> p3 = std::move(p1); // move `p1` into `p2`
                                         // now unsafe to dereference object held by `p1`
```

### std::forward
Returns the arguments passed to it as-is, either as an lvalue or rvalue references, and includes cv-qualification. Useful for generic code that need a reference (either lvalue or rvalue) when appropriate, e.g factories. Forwarding gets its power from _template argument deduction_:
* `T& &` becomes `T&`
* `T& &&` becomes `T&`
* `T&& &` becomes `T&`
* `T&& &&` becomes `T&&`

A definition of `std::forward`:
```c++
template <typename T>
T&& forward(typename remove_reference<T>::type& arg) {
  return static_cast<T&&>(arg);
}
```

An example of a function `wrapper` which just forwards other `A` objects to a new `A` object's copy or move constructor:
```c++
struct A {
  A() = default;
  A(const A& o) { std::cout << "copied" << std::endl; }
  A(A&& o) { std::cout << "moved" << std::endl; }
};

template <typename T>
A wrapper(T&& arg) {
  return A{ std::forward<T>(arg) };
}

wrapper(A{}); // moved
A a{};
wrapper(a); // copied
wrapper(std::move(a)); // moved
```

### std::to_string
Converts a numeric argument to a `std::string`.
```c++
std::to_string(1.2); // == "1.2"
std::to_string(123); // == "123"
```

### Type traits
Type traits defines a compile-time template-based interface to query or modify the properties of types.
```c++
static_assert(std::is_integral<int>::value == 1);
static_assert(std::is_same<int, int>::value == 1);
static_assert(std::is_same<std::conditional<true, int, double>::type, int>::value == 1);
```

### Smart pointers
C++11 introduces new smart(er) pointers: `std::unique_ptr`, `std::shared_ptr`, `std::weak_ptr`. `std::auto_ptr` now becomes deprecated and then eventually removed in C++17.

`std::unique_ptr` is a non-copyable, movable smart pointer that properly manages arrays and STL containers. **Note: Prefer using the `std::make_X` helper functions as opposed to using constructors. See the sections for [std::make_unique](#stdmake_unique) and [std::make_shared](#stdmake_shared).**
```c++
std::unique_ptr<Foo> p1 { new Foo{} };  // `p1` owns `Foo`
if (p1) p1->bar();

{
  std::unique_ptr<Foo> p2 { std::move(p1) };  // Now `p2` owns `Foo`
  f(*p2);

  p1 = std::move(p2);  // Ownership returns to `p1` -- `p2` gets destroyed
}

if (p1) p1->bar();
// `Foo` instance is destroyed when `p1` goes out of scope
```

A `std::shared_ptr` is a smart pointer that manages a resource that is shared across multiple owners. A shared pointer holds a _control block_ which has a few components such as the managed object and a reference counter. All control block access is thread-safe, however, manipulating the managed object itself is *not* thread-safe.
```c++
void foo(std::shared_ptr<T> t) {
  // Do something with `t`...
}

void bar(std::shared_ptr<T> t) {
  // Do something with `t`...
}

void baz(std::shared_ptr<T> t) {
  // Do something with `t`...
}

std::shared_ptr<T> p1 { new T{} };
// Perhaps these take place in another threads?
foo(p1);
bar(p1);
baz(p1);
```

### std::chrono
The chrono library contains a set of utility functions and types that deal with _durations_, _clocks_, and _time points_. One use case of this library is benchmarking code:
```c++
std::chrono::time_point<std::chrono::system_clock> start, end;
start = std::chrono::system_clock::now();
// Some computations...
end = std::chrono::system_clock::now();

std::chrono::duration<double> elapsed_seconds = end-start;

elapsed_seconds.count(); // t number of seconds, represented as a `double`
```

### Tuples
Tuples are a fixed-size collection of heterogeneous values. Access the elements of a `std::tuple` by unpacking using [`std::tie`](#stdtie), or using `std::get`.
```c++
// `playerProfile` has type `std::tuple<int, std::string, std::string>`.
auto playerProfile = std::make_tuple(51, "Frans Nielsen", "NYI");
std::get<0>(playerProfile); // 51
std::get<1>(playerProfile); // "Frans Nielsen"
std::get<2>(playerProfile); // "NYI"
```

### std::tie
Creates a tuple of lvalue references. Useful for unpacking `std::pair` and `std::tuple` objects. Use `std::ignore` as a placeholder for ignored values. In C++17, structured bindings should be used instead.
```c++
// With tuples...
std::string playerName;
std::tie(std::ignore, playerName, std::ignore) = std::make_tuple(91, "John Tavares", "NYI");

// With pairs...
std::string yes, no;
std::tie(yes, no) = std::make_pair("yes", "no");
```

### std::array
`std::array` is a container built on top of a C-style array. Supports common container operations such as sorting.
```c++
std::array<int, 3> a = {2, 1, 3};
std::sort(a.begin(), a.end()); // a == { 1, 2, 3 }
for (int& x : a) x *= 2; // a == { 2, 4, 6 }
```

### Unordered containers
These containers maintain average constant-time complexity for search, insert, and remove operations. In order to achieve constant-time complexity, sacrifices order for speed by hashing elements into buckets. There are four unordered containers:
* `unordered_set`
* `unordered_multiset`
* `unordered_map`
* `unordered_multimap`

### std::make_shared
`std::make_shared` is the recommended way to create instances of `std::shared_ptr`s due to the following reasons:
* Avoid having to use the `new` operator.
* Prevents code repetition when specifying the underlying type the pointer shall hold.
* It provides exception-safety. Suppose we were calling a function `foo` like so:
```c++
foo(std::shared_ptr<T>{ new T{} }, function_that_throws(), std::shared_ptr<T>{ new T{} });
```
The compiler is free to call `new T{}`, then `function_that_throws()`, and so on... Since we have allocated data on the heap in the first construction of a `T`, we have introduced a leak here. With `std::make_shared`, we are given exception-safety:
```c++
foo(std::make_shared<T>(), function_that_throws(), std::make_shared<T>());
```
* Prevents having to do two allocations. When calling `std::shared_ptr{ new T{} }`, we have to allocate memory for `T`, then in the shared pointer we have to allocate memory for the control block within the pointer.

See the section on [smart pointers](#smart-pointers) for more information on `std::unique_ptr` and `std::shared_ptr`.

### Memory model
C++11 introduces a memory model for C++, which means library support for threading and atomic operations. Some of these operations include (but aren't limited to) atomic loads/stores, compare-and-swap, atomic flags, promises, futures, locks, and condition variables.

## Acknowledgements
* [cppreference](http://en.cppreference.com/w/cpp) - especially useful for finding examples and documentation of new library features.
* [C++ Rvalue References Explained](http://thbecker.net/articles/rvalue_references/section_01.html) - a great introduction I used to understand rvalue references, perfect forwarding, and move semantics.
* [clang](http://clang.llvm.org/cxx_status.html) and [gcc](https://gcc.gnu.org/projects/cxx-status.html)'s standards support pages. Also included here are the proposals for language/library features that I used to help find a description of, what it's meant to fix, and some examples.
* [Compiler explorer](https://godbolt.org/)
* [Scott Meyers' Effective Modern C++](https://www.amazon.com/Effective-Modern-Specific-Ways-Improve/dp/1491903996) - highly recommended book!
* [Jason Turner's C++ Weekly](https://www.youtube.com/channel/UCxHAlbZQNFU2LgEtiqd2Maw) - nice collection of C++-related videos.
* [What can I do with a moved-from object?](http://stackoverflow.com/questions/7027523/what-can-i-do-with-a-moved-from-object)
* [What are some uses of decltype(auto)?](http://stackoverflow.com/questions/24109737/what-are-some-uses-of-decltypeauto)
* And many more SO posts I'm forgetting...

## Author
Anthony Calandra

## Content Contributors
See: https://github.com/AnthonyCalandra/modern-cpp-features/graphs/contributors

## License
MIT
