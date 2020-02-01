# C++20

## Overview
Many of these descriptions and examples come from various resources (see [Acknowledgements](#acknowledgements) section), summarized in my own words.

C++20 includes the following new language features:
- [concepts](#concepts)
- [designated initializers](#designated-initializers)
- [template syntax for lambdas](#template-syntax-for-lambdas)
- [range-based for loop with initializer](#range-based-for-loop-with-initializer)
- [likely and unlikely attributes](#likely-and-unlikely-attributes)
- [deprecate implicit capture of this](#deprecate-implicit-capture-of-this)
- [class types in non-type template parameters](#class-types-in-non-type-template-parameters)

C++20 includes the following new library features:
- [concepts library](#concepts-library)

## C++20 Language Features

### Concepts
_Concepts_ are named compile-time predicates which constrain types. They take the following form:
```
template < template-parameter-list >
concept concept-name = constraint-expression;
```
where `constraint-expression` evaluates to a constexpr Boolean. _Constraints_ should model semantic requirements, such as whether a type is a numeric or hashable. A compiler error results if a given type does not satisfy the concept it's bound by (i.e. `constraint-expression` returns `false`). Because constraints are evaluated at compile-time, they can provide more meaningful error messages and runtime safety.
```c++
// `T` is not limited by any constraints.
template <typename T>
concept AlwaysSatisfied = true;
// Limit `T` to integrals.
template <typename T>
concept Integral = std::is_integral_v<T>;
// Limit `T` to both the `Integral` constraint and signedness.
template <typename T>
concept SignedIntegral = Integral<T> && std::is_signed_v<T>;
// Limit `T` to both the `Integral` constraint and the negation of the `SignedIntegral` constraint.
template <typename T>
concept UnsignedIntegral = Integral<T> && !SignedIntegral<T>;
```
There are a variety of syntactic forms for enforcing concepts:
```c++
// Forms for function parameters:
// `T` is a constrained type template parameter.
template <MyConcept T>
void f(T v);

// `T` is a constrained type template parameter.
template <typename T>
  requires MyConcept<T>
void f(T v);

// `T` is a constrained type template parameter.
template <typename T>
void f(T v) requires MyConcept<T>;

// `v` is a constrained deduced parameter.
void f(MyConcept auto v);

// `v` is a constrained non-type template parameter.
template <MyConcept auto v>
void g();

// Forms for auto-deduced variables:
// `foo` is a constrained auto-deduced value.
MyConcept auto foo = ...;

// Forms for lambdas:
// `T` is a constrained type template parameter.
auto f = []<MyConcept T> (T v) {
  // ...
};
// `T` is a constrained type template parameter.
auto f = []<typename T> requires MyConcept<T> (T v) {
  // ...
};
// `T` is a constrained type template parameter.
auto f = []<typename T> (T v) requires MyConcept<T> {
  // ...
};
// `v` is a constrained deduced parameter.
auto f = [](MyConcept auto v) {
  // ...
};
// `v` is a constrained non-type template parameter.
auto g = []<MyConcept auto v> () {
  // ...
};
```
The `requires` keyword is used either to start a requires clause or a requires expression:
```c++
template <typename T>
  requires MyConcept<T> // `requires` clause.
void f(T);

template <typename T>
concept Callable = requires (T f) { f(); }; // `requires` expression.

template <typename T>
  requires requires (T x) { x + x; } // `requires` clause and expression on same line.
T add(T a, T b) {
  return a + b;
}
```
Note that the parameter list in a requires expression is optional. Each requirement in a requires expression are one of the following:

* **Simple requirements** - asserts that the given expression is valid.

```c++
template <typename T>
concept Callable = requires (T f) { f(); };
```
* **Type requirements** - denoted by the `typename` keyword followed by a type name, asserts that the given type name is valid.

```c++
struct Foo {
  int foo;
};

struct Bar {
  using value = int;
  value data;
};

struct Baz {
  using value = int;
  value data;
};

// Using SFINAE, enable if `T` is a `Baz`.
template <typename T, typename = std::enable_if_t<std::is_same_v<T, Baz>>>
struct S {};

template <typename T>
using Ref = T&;

template <typename T>
concept C = requires {
                     // Requirements on type `T`:
  typename T::value; // A) has an inner member named `value`
  typename S<T>;     // B) must have a valid class template specialization for `S`
  typename Ref<T>;   // C) must be a valid alias template substitution
};

template <C T>
void g(T a);

g(Foo{}); // ERROR: Fails requirement A.
g(Bar{}); // ERROR: Fails requirement B.
g(Baz{}); // PASS.
```
* **Compound requirements** - an expression in braces followed by a trailing return type or type constraint.

```c++
template <typename T>
concept C = requires(T x) {
  {*x} -> typename T::inner; // the type of the expression `*x` is convertible to `T::inner`
  {x + 1} -> std::Same<int>; // the expression `x + 1` satisfies `std::Same<decltype((x + 1))>`
  {x * 1} -> T; // the type of the expression `x * 1` is convertible to `T`
};
```
* **Nested requirements** - denoted by the `requires` keyword, specify additional constraints (such as those on local parameter arguments).

```c++
template <typename T>
concept C = requires(T x) {
  requires std::Same<sizeof(x), size_t>;
};
```
See also: [concepts library](#concepts-library).

### Designated initializers
C-style designated initializer syntax. Any member fields that are not explicitly listed in the designated initializer list are default-initialized.
```c++
struct A {
  int x;
  int y;
  int z = 123;
};

A a {.x = 1, .z = 2}; // a.x == 1, a.y == 0, a.z == 2
```

### Template syntax for lambdas
Use familiar template syntax in lambda expressions.
```c++
auto f = []<typename T>(std::vector<T> v) {
  // ...
};
```

### Range-based for loop with initializer
This feature simplifies common code patterns, helps keep scopes tight, and offers an elegant solution to a common lifetime problem.
```c++
for (auto v = std::vector{1, 2, 3}; auto& e : v) {
  std::cout << e;
}
// prints "123"
```

### likely and unlikely attributes
Provides a hint to the optimizer that the labelled statement is likely/unlikely to have its body executed.
```c++
int random = get_random_number_between_x_and_y(0, 3);
[[likely]] if (random > 0) {
  // body of if statement
  // ...
}

[[unlikely]] while (unlikely_truthy_condition) {
  // body of while statement
  // ...
}
```

### Deprecate implicit capture of this
Implicitly capturing `this` in a lamdba capture using `[=]` is now deprecated; prefer capturing explicitly using `[=, this]` or `[=, *this]`.
```c++
struct int_value {
  int n = 0;
  auto getter_fn() {
    // BAD:
    // return [=]() { return n; };

    // GOOD:
    return [=, *this]() { return n; };
  }
};
```

### Class types in non-type template parameters
Classes can now be used in non-type template parameters. Objects passed in as template arguments have the type `const T`, where `T` is the type of the object, and has static storage duration.
```c++
struct foo {
  foo() = default;
  constexpr foo(int) {}
};

template <foo f>
auto get_foo() {
  return f;
}

get_foo(); // uses implicit constructor
get_foo<foo{123}>();
```

## C++20 Library Features

### Concepts library
Concepts are also provided by the standard library for building more complicated concepts. Some of these include:

**Core language concepts:**
- `Same` - specifies two types are the same.
- `DerivedFrom` - specifies that a type is derived from another type.
- `ConvertibleTo` - specifies that a type is implicitly convertible to another type.
- `Common` - specifies that two types share a common type.
- `Integral` - specifies that a type is an integral type.
- `DefaultConstructible` - specifies that an object of a type can be default-constructed.

 **Comparison concepts:**
- `Boolean` - specifies that a type can be used in Boolean contexts.
- `EqualityComparable` - specifies that `operator==` is an equivalence relation.

 **Object concepts:**
- `Movable` - specifies that an object of a type can be moved and swapped.
- `Copyable` - specifies that an object of a type can be copied, moved, and swapped.
- `Semiregular` - specifies that an object of a type can be copied, moved, swapped, and default constructed.
- `Regular` - specifies that a type is _regular_, that is, it is both `Semiregular` and `EqualityComparable`.

 **Callable concepts:**
- `Invocable` - specifies that a callable type can be invoked with a given set of argument types.
- `Predicate` - specifies that a callable type is a Boolean predicate.

See also: [concepts](#concepts).

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
