# C++23

## Overview
Many of these descriptions and examples are taken from various resources (see [Acknowledgements](#acknowledgements) section) and summarized in my own words.

C++23 includes the following new language features:
- [consteval if](#consteval-if)
- [deducing `this`](#deducing-this)
- [multidimensional subscript operator](#multidimensional-subscript-operator)
- [increasing range-based for safety](#increasing-range-based-for-safety)

C++23 includes the following new library features:
- [stacktrace library](#stacktrace-library)
- [contains for strings and string views](#contains-for-strings-and-string-views)

## C++23 Language Features

### consteval if
Write code that is instantiated during constant evaluation.
```c++
consteval int f(int i) { return i; }

constexpr int g(int i) {
  if consteval {
      return f(i);
  } else {
      return 42;
  }
}
```

### Deducing `this`
Using explicit object member functions introduced in C++23, deducing the object's type and value category is now possible by specifying the first parameter of a member function prefixed with the `this` keyword:
```c++
// NEW WAY USING DEDUCING THIS:
struct T {
  decltype(auto) operator[](this auto& self, std::size_t idx) { 
    return self.mVector[idx]; 
  }
};

// OLD WAY:
struct T {
  value_t& operator[](std::size_t idx) {
    return mVector[idx];
  }
  const value_t& operator[](std::size_t idx) const {
    return mVector[idx];
  }
};
```

### Multidimensional subscript operator
Specify zero or more arguments to the `operator[]` operator:
```c++
template <typename T, std::size_t Z, std::size_t Y, std::size_t X>
struct Array3d {
  std::array<T, X * Y * Z> m{};

  T& operator[](std::size_t z, std::size_t y, std::size_t x) {
      return m[z * Y * X + y * X + x];
  }
};

Array3d<int, 4, 3, 2> v;
v[3, 2, 1] = 42;
```

### Increasing range-based `for` safety
Fixes some of the notorious lifetime issues with one of the most important control structures in C++.

Some examples of code snippets that were broken pre-C++23 that are now fixed:

* `for (auto e : getTmp().getRef())`
* `for (auto e : getVector()[0])`
* `for (auto valueElem : getMap()["key"])`
* `for (auto e : get<0>(getTuple()))`
* `for (auto e : getOptionalCollection().value())`
* `for (char c : get<std::string>(getVariant()))`

## C++23 Library Features

### Stacktrace library
A stacktrace is an approximate representation of an invocation sequence and consists of stacktrace entries. A stacktrace entry (represented by `std::stacktrace_entry`) consists of information including the source file and line number, and a description field.

Example output on a Linux system:
```c++
#include <print>
#include <stacktrace>

int main() {
    std::println("{}", std::stacktrace::current());
}
```
```
  0#  main at /app/example.cpp:5 [0x5ee42e3db747]
  1#  <unknown> [0x76e76dc29d8f]
  2#  __libc_start_main [0x76e76dc29e3f]
  3#  _start [0x5ee42e3db644]
```

### `contains` for strings and string views
A simpler function for querying if a substring is contained within a string or string view:
```c++
std::string{"foobarbaz"}.contains("bar"); // == true
std::string{"foobarbaz"}.contains("bat"); // == false
```

## Acknowledgements
* [cppreference](http://en.cppreference.com/w/cpp) - especially useful for finding examples and documentation of new library features.
* [C++ Rvalue References Explained](http://web.archive.org/web/20240324121501/http://thbecker.net/articles/rvalue_references/section_01.html) - a great introduction I used to understand rvalue references, perfect forwarding, and move semantics.
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
