# C++20

## Overview
Many of these descriptions and examples come from various resources (see [Acknowledgements](#acknowledgements) section), summarized in my own words.

C++20 includes the following new language features:
- [concepts](#concepts)

C++20 includes the following new library features:
- [concepts library](#concepts-library)

## C++20 Language Features

### Concepts
_Concepts_ are named compile-time predicates which constrain template arguments. They take the following form:
```
template < template-parameter-list >
concept concept-name = constraint-expression;
```
where `constraint-expression` evaluates to a constexpr Boolean. Example:
```c++
// `MyConcept` is always satisfied.
template <typename T>
concept MyConcept = true;

// Three syntactic forms for constraints (same for lambdas):
template <MyConcept T>
void f(T);

template <typename T>
  requires MyConcept<T>
void f(T);

template <typename T>
void f(T) requires MyConcept<T>;
```
_Constraints_ should model semantic requirements, such as whether a type is a numeric or hashable. Because constraints are evaluated at compile-time, they can provide more meaningful error messages and runtime safety.
```c++
template <typename T>
concept Integral = std::is_integral_v<T>;
template <typename T>
concept SignedIntegral = Integral<T> && std::is_signed_v<T>;
template <typename T>
concept UnsignedIntegral = Integral<T> && !SignedIntegral<T>;
```
The `requires` keyword is used either to start a requires clause or a requires expression:
```c++
template <typename T>
  requires MyConcept<T> // requires clause
void f(T);

template <typename T>
concept Callable = requires (T f) { f(); }; // requires expression

template <typename T>
  requires requires (T x) { x + x; } // requires clause and expression on same line
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
  typename T::value; // A) required nested member name
  typename S<T>;     // B) required class template specialization
  typename Ref<T>;   // C) required alias template substitution
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
  {*x} -> typename T::inner; // the expression *x must be valid
                             // AND the type T::inner must be valid
                             // AND the result of *x must be convertible to T::inner
  {x + 1} -> std::Same<int>; // the expression x + 1 must be valid
                             // AND std::Same<decltype((x + 1)), int> must be satisfied
                             // i.e., (x + 1) must be a prvalue of type int
  {x * 1} -> T; // the expression x * 1 must be valid
                // AND its result must be convertible to T
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
