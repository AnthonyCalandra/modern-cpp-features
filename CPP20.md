# C++20

## Overview
Many of these descriptions and examples come from various resources (see [Acknowledgements](#acknowledgements) section), summarized in my own words.

Also, there are now dedicated readme pages for each major C++ version.

C++20 includes the following new language features:
- [concepts](#concepts)
- [lambda templates](#lambda-templates)

C++20 includes the following new library features:
- [std::ranges](#stdranges)

## C++20 Language Features

### concepts
Class templates, function templates, and non-template functions (typically members of class templates) may be associated with a constraint,
which specifies the requirements on template arguments, which can be used to select the most appropriate function overloads and template specializations.  

Named sets of such requirements are called concepts. Each concept is a predicate, evaluated at compile time,
and becomes a part of the interface of a template where it is used as a constraint.

```c++
#include <string>
#include <cstddef>
using namespace std::literals;

// Declaration of the concept "Hashable", which is satisfied by
// any type T such that for values a of type T,
// the expression std::hash<T>{}(a) compiles and its result is convertible to std::size_t
template<typename T>
concept Hashable = requires(T a) {
    { std::hash<T>{}(a) } -> std::size_t;
};

struct meow {};

template<Hashable T>
void f(T); // constrained C++20 function template

// Alternative ways to apply the same constraint:
// template<typename T>
//    requires Hashable<T>
// void f(T);
//
// template<typename T>
// void f(T) requires Hashable<T>;

int main() {
  f("abc"s); // OK, std::string satisfies Hashable
  f(meow{}); // Error: meow does not satisfy Hashable
}
```

Violations of constraints are detected at compile time, early in the template instantiation process, which leads to easy to follow error messages.
```c++
std::list<int> l = {3,-1,10};
std::sort(l.begin(), l.end());
//Typical compiler diagnostic without concepts:
//  invalid operands to binary expression ('std::_List_iterator<int>' and
//  'std::_List_iterator<int>')
//                           std::__lg(__last - __first) * 2);
//                                     ~~~~~~ ^ ~~~~~~~
// ... 50 lines of output ...
//
//Typical compiler diagnostic with concepts:
//  error: cannot call std::sort with std::_List_iterator<int>
//  note:  concept RandomAccessIterator<std::_List_iterator<int>> was not satisfied
```
The intent of concepts is to model semantic categories (Number, Range, RegularFunction) rather than syntactic restrictions (HasPlus, Array).

A concept is a named set of requirements. The definition of a concept must appear at namespace scope.
The definition of a concept has the form:
`
template < template-parameter-list >
concept concept-name = constraint-expression;
`
```c++
template <class T, class U>
concept Derived = std::is_base_of<U, T>::value;
template <class T>
concept Integral = std::is_integral<T>::value;
template <class T>
concept SignedIntegral = Integral<T> && std::is_signed<T>::value;
template <class T>
concept UnsignedIntegral = Integral<T> && !SignedIntegral<T>;

template<typename T> using Ref = T&;
template<typename T> concept C =
requires {
    typename T::inner; // required nested member name
    typename S<T>;     // required class template specialization
    typename Ref<T>;   // required alias template substitution
};

template <class T, class U> using CommonType = std::common_type_t<T, U>;
template <class T, class U> concept Common =
requires (T t, U u) {
    typename CommonType<T, U>; // CommonType<T, U> is valid and names a type
    { CommonType<T, U>{std::forward<T>(t)} };
    { CommonType<T, U>{std::forward<U>(u)} };
};

template <class T>
concept Semiregular = DefaultConstructible<T> &&
    CopyConstructible<T> && Destructible<T> && CopyAssignable<T> &&
requires(T a, size_t n) {
    requires Same<T*, decltype(&a)>;  // nested: "Same<...> evaluates to true"
    { a.~T() } noexcept;  // compound: "a.~T()" is a valid expression that doesn't throw
    requires Same<T*, decltype(new T)>; // nested: "Same<...> evaluates to true"
    requires Same<T*, decltype(new T[n])>; // nested
    { delete new T };  // compound
    { delete new T[n] }; // compound
};
```

A constraint is a sequence of logical operations and operands that specifies requirements on template arguments.
They can appear within requires-expressions and directly as bodies of concepts.
```c++
template<Incrementable T>
void f(T) requires Decrementable<T>;

template<typename T>
constexpr bool get_value() { return T::value; }

template<typename T>
    requires (sizeof(T) > 1 && get_value<T>())
void f(T);

template <class T = void>
    requires EqualityComparable<T> || Same<T, void>
struct equal_to;
```

### lambda templates
with templated lambda, template parameters is easily accessible in the body of the lambda.
```c++
auto f = []<typename T>(std::vector<T>& v) {
// ...
};
```
```c++
auto l = []<typename T>(){
     std::cout << typeid(T).name() << std::endl;
};

l.template operator()<int>();
```
## C++20 Library Features

### std::ranges
Ranges are an abstration layer on top of iterators. 
Ranges are an extension of the Standard Template Library that makes its iterators and algorithms more powerful by making them composable. 

Filter a container using a predicate and transform it.
```c++
using namespace std::ranges;
std::vector<int> vi{1,2,3,4,5,6,7,8,9,10};
auto rng = vi | view::remove_if([](int i){return i % 2 == 1;})
              | view::transform([](int i){return std::to_string(i);});
// rng == {"2","4","6","8","10"};
```
 
Generate an infinite list of integers starting at 1, square them, take the first 10, and sum them.
```c++
using namespace std::ranges;
int sum = accumulate(view::ints(1)
                   | view::transform([](int i){return i*i;})
                   | view::take(10), 0);
```

Generate a sequence on the fly with a range comprehension and initialize a vector with it.
```c++
using namespace std::ranges;
std::vector<int> vi =
    view::for_each(view::ints(1,10), [](int i){
        return yield_from(view::repeat_n(i,i));
    });
// vi == {1,2,2,3,3,3,4,4,4,4,5,5,5,5,5,...}
```

Read data into a vector, sort it, and make it unique.
```c++
extern std::vector<int> read_data();
using namespace std::ranges;
std::vector<int> vi = read_data() | action::sort | action::unique;
vi |= action::sort | action::unique; // Mutate the container in-place
```
