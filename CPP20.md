# C++20

## Overview
Many of these descriptions and examples come from various resources (see [Acknowledgements](#acknowledgements) section), summarized in my own words.

Also, there are now dedicated readme pages for each major C++ version.

C++20 includes the following new language features:
- [concepts](#concepts)
- [lambda templates](#lambda-templates)
- [nested inline namespaces](#nested-inline-namespaces)
- [pack expansion in lambda init-capture](#pack-expansion-in-lambda-init-capture)
- [range-based for statements with initializer](#range-based-for-statements-with-initializer)

C++20 includes the following new library features:
- [concepts library](#concepts-library)
- [ranges library](#ranges-library)
- [std::bind_front](#stdbind_front)
- [std::remove_cvref](#stdremove_cvref)
- [std::type_identity](#stdtype_identity)

## C++20 Language Features

### Concepts
*Class templates, function templates, and non-template functions (typically members of class templates) may be associated with a constraint,
which specifies requirements on template arguments, which can be used to select the most appropriate function overloads and template specializations.*

Named sets of such requirements are called concepts. Each concept is a predicate, evaluated at compile time,
and becomes a part of the interface of a template where it is used as a constraint.

```c++
#include <string>
#include <cstddef>
using namespace std::literals;

// Declaration of the concept "Hashable", which is satisfied by
// any type T such that for values a of type T,
// the expression std::hash<T>{}(a) compiles and its result is convertible to std::size_t
template <typename T>
concept Hashable = requires(T a) {
    { std::hash<T>{}(a) } -> std::size_t;
};

struct foo {};

template <Hashable T>
void f(T); // constrained C++20 function template

// Alternative ways to apply the same constraint:
// template <typename T>
// requires Hashable<T>
// void f(T);
//
// template <typename T>
// void f(T) requires Hashable<T>;

int main() {
  f("abc"s); // OK, std::string satisfies Hashable
  f(foo{}); // Error: foo does not satisfy Hashable
}
```

The intent of concepts is to model semantic categories (Number, Range, RegularFunction) rather than syntactic restrictions (HasPlus, Array).
The definition of a concept must appear at namespace scope and has the form:  
`
template <template-parameter-list>
concept concept-name = constraint-expression;
`
```c++
template <typename T, typename U>
concept Derived = std::is_base_of<U, T>::value;
template <typename T>
concept Integral = std::is_integral<T>::value;
template <typename T>
concept SignedIntegral = Integral<T> && std::is_signed<T>::value;
template <typename T>
concept UnsignedIntegral = Integral<T> && !SignedIntegral<T>;

template <typename T>
using Ref = T&;

template <typename T>
concept C = requires {
    typename T::inner; // required nested member name
    typename S<T>;     // required class template specialization
    typename Ref<T>;   // required alias template substitution
};

template <typename T, typename U>
using CommonType = std::common_type_t<T, U>;

template <typename T, typename U>
concept Common = requires (T t, U u) {
    typename CommonType<T, U>; // CommonType<T, U> is valid and names a type
    { CommonType<T, U>{std::forward<T>(t)} };
    { CommonType<T, U>{std::forward<U>(u)} };
};

```

```c++
template <Incrementable T>
void f(T) requires Decrementable<T>;

template <typename T>
constexpr bool get_value() { return T::value; }

template <typename T>
requires (sizeof(T) > 1 && get_value<T>())
void f(T);

template <typename T = std::void_t<>>
requires EqualityComparable<T> || Same<T, void>
struct equal_to;
```

### Lambda templates
Lambdas can now accept template parameters like regular functions.
```c++
auto f = []<typename T>(std::vector<T>& v){
// ...
};

auto g = []<typename T, size_t N>(){
       std::array<T, N> array;
// ...
};

auto h = []<typename T, auto... indices>(const std::index_sequence<indices...>&, auto&&... Args){
// ...
}
```

### Nested inline namespaces
```c++
namespace A::inline B::C {
    class X{};
}
// vs 
namespace A {
inline namespace B {
namespace C {
    class X{};
}
}
}
```

### Pack expansion in lambda init-capture
Generate a pack of closure data members by placing an ellipsis (...) before a pack expansion as part of a lambda capture.
```c++
template <typename... Args>
auto delay_invoke_foo(Args... args) {
    return [...args = std::move(args)]() -> decltype(auto) {
        return foo(args...);
    };
}
```

### Range-based for statements with initializer
A new versions of the range-based for statement for C++: `for (init; decl : expr)`  
which simplifies common code patterns, can help users keep scopes tight and offers an elegant solution to a common lifetime problem.
```c++
for (T thing = f(); auto& x : thing.items()) {
    mutate(&x);
    log(x);
}

for (std::size_t i = 0; const auto& x : foo()) {
    bar(x, i++);
}
```

## C++20 Library Features

### Concepts library
The concepts library provides definitions of fundamental library concepts that can be used to perform
compile-time validation of template arguments and perform function dispatch based on properties of types.

**Core language concepts**
- Same - specifies two types are the same
- DerivedFrom - specifies that a type is derived from another type
- ConvertibleTo - specifies that a type is implicitly convertible to another type
- Common - specifies that two types share a common type
- Integral - specifies that a type is an integral type

**Comparison concepts**
- Boolean - specifies that a type can be used in Boolean contexts
- EqualityComparable - specifies that operator == is an equivalence relation

**Object concepts**
- Movable - specifies that an object of a type can be moved and swapped
- Copyable - pecifies that an object of a type can be copied, moved, and swapped

**Callable concepts**
- Invocable - specifies that a callable type can be invoked with a given set of argument types
- Predicate - specifies that a callable type is a Boolean predicate

### Ranges library
Ranges are an extension of the Standard Template Library and an abstration layer on top of iterators
that makes its iterators and algorithms more powerful by making them composable.

Filter a container using a predicate and transform it.
```c++
using namespace std::ranges;
std::vector<int> vi {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
auto rng = vi | view::remove_if([](int i){ return i % 2 == 1; })
              | view::transform([](int i){ return std::to_string(i); });
// rng == {"2", "4", "6", "8", "10"};
```

Generate an infinite list of integers starting at 1, square them, take the first 10, and sum them.
```c++
using namespace std::ranges;
int sum = accumulate(view::ints(1)
              | view::transform([](int i){ return i * i; })
              | view::take(10), 0);
```

Generate a sequence on the fly with a range comprehension and initialize a vector with it.
```c++
using namespace std::ranges;
std::vector<int> vi = view::for_each(view::ints(1, 10), [](int i){
        return yield_from(view::repeat_n(i, i));
    });
// vi == {1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5,...}
```

Read data into a vector, sort it, and make it unique.
```c++
extern std::vector<int> read_data();
using namespace std::ranges;
std::vector<int> vi = read_data() | action::sort | action::unique;
vi |= action::sort | action::unique; // Mutate the container in-place
```

### std::bind_front
Generates a forwarding call wrapper for a callable object f with parameters `Args&&... args`.
Calling this wrapper is equivalent to invoking f with its first sizeof...(Args) parameters bound to args.
```c++
std::bind_front(f, bound_args...)(call_args...);
```
is equivalent to
```c++
std::invoke(f, bound_args..., call_args....);
```

### std::remove_cvref
If the type T is a reference type, provides the member typedef type which is the type referred to
by T with its topmost cv-qualifiers removed. Otherwise type is T with its topmost cv-qualifiers removed.
```c++
std::is_same_v<std::remove_cvref_t<int>, int>; // true
std::is_same_v<std::remove_cvref_t<int&>, int>; // true
std::is_same_v<std::remove_cvref_t<int&&>, int>; // true
std::is_same_v<std::remove_cvref_t<const int&>, int>; // true
std::is_same_v<std::remove_cvref_t<const int(&)[2]>, int[2]>; // true
```

### std::type_identity
Provides the member typedef type that names T (i.e., the identity transformation).  
type_identity can be used to block template argument deduction:
```c++
template <typename T>
void f(T, T);

template <typename T>
void g(T, std::type_identity_t<T>);

f(4.2, 0); // error, deduced conflicting types for 'T'
g(4.2, 0); // OK, calls g<double>
```
