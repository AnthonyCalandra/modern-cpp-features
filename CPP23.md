# C++23

## Overview
Many of these descriptions and examples are taken from various resources (see [Acknowledgements](#acknowledgements) section) and summarized in my own words.

C++23 includes the following new language features:
- [consteval if](#consteval-if)
- [deducing `this`](#deducing-this)
- [multidimensional subscript operator](#multidimensional-subscript-operator)
- [increasing range-based `for` safety](#increasing-range-based-for-safety)

C++23 includes the following new library features:
- [stacktrace library](#stacktrace-library)
- [contains for strings and string views](#contains-for-strings-and-string-views)
- [std::to_underlying](#stdto_underlying)
- [`spanstream`](#spanstream)
- [input/output pointers](#inputoutput-pointers)
- [monadic operations for `std::optional`](monadic-operations-for-stdoptional)
- [`std::expected`](#stdexpected)
- [`std::unreachable`](#stdunreachable)

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

### `std::to_underlying`
Supports the common utility of converting an enumeration to its underlying type:
```c++
enum class MyEnum : int { A = 1, B, C };
std::to_underlying(MyEnum::A); // == 1
std::to_underlying(MyEnum::C); // == 3
```

### `spanstream`
A `strstream` replacement using a character span as an externally-provided buffer. No ownership or re-allocation on the buffer.
```c++
char input[] = "10 20 30";
std::ispanstream is{std::span<char>{input}};
int i;
is >> i; // i == 10
is >> i; // i == 20
is >> i; // i == 30
```
```c++
char output[30]{}; // zero-initialize array
std::ospanstream os{std::span<char>{output}};
os << 10 << 20 << 30;
std::span<char> sp = os.span();
```

### Input/output pointers
`std::out_ptr` and `std::inout_ptr` are abstractions to support both C APIs and smart pointers by creating a temporary pointer-to-pointer that updates the smart pointer when it destructs. In short: it's a thing convertible to a `T**` that updates (with a `reset` call or semantically equivalent behavior) the smart pointer it is created with when it goes out of scope.

This abstraction also safely manages the lifetime of the associated memory when exceptions are thrown.
```c++
// p_handle is written (out) to.
int c_api_create_handle(MyHandle** p_handle);
// p_handle is both read (in) and written (out) to.
int c_api_recreate_handle(MyHandle** p_handle);
void c_api_delete_handle(MyHandle* handle);

struct resource_deleter {
	void operator()(MyHandle* handle) {
		c_api_delete_handle(handle);
	}
};
```
```c++
std::unique_ptr<MyHandle, resource_deleter> resource(nullptr);
int err = c_api_create_handle(std::out_ptr(resource));
// `resource` now owns the memory allocated within `c_api_create_handle`.
```
```c++
std::shared_ptr<MyHandle> resource(nullptr);
int err = c_api_recreate_handle(std::inout_ptr(resource), resource_deleter{});
// `resource` now shares the memory allocated within `c_api_recreate_handle`.
```

Both inout/out pointers support casts to `void**` (implicitly), and explicitly to user-specified types.

### Monadic operations for `std::optional`
Support various `and_then`, `transform`, and `or_else` operations for `std::optional`.
```c++
std::optional<int> parse_int(const std::string&);
std::optional<int> ensure_non_negative(int);
std::optional<double> default_value_or_empty(double);

std::optional<double> stringToSqrtDouble(const std::string& input) {
  return parse_int(input)
    .and_then(ensure_non_negative)
    .transform([](int x) {
      return std::sqrt(x);
    })
    .or_else(default_value_or_empty);
}
```

### `std::expected`
`std::expected` provides a way to represent a value and a potential error value, both contained in one type. Also supports a variety of monadic operations on both the expected and unexpected (i.e. error) values.

Use `std::unexpected` to store an unexpected (i.e. error) value.
```c++
enum class StringToSqrtDoubleError {
    ParseError, NegativeNumber
};

std::expected<int, StringToSqrtDoubleError> parse_int(const std::string&);

std::expected<double, StringToSqrtDoubleError> stringToSqrtDouble(const std::string& input) {
    auto parsed = parse_int(input);
    if (!parsed) return parsed;

    auto parsedInt = *parsed;
    if (parsedInt < 0) return std::unexpected(StringToSqrtDoubleError::NegativeNumber);

    return std::sqrt(parsedInt);
}
```

### `std::unreachable`
Provides a way to explicitly mark a code path as unreachable. May exhibit undefined behavior if the code path is reached.
```c++
enum class MyEnum { A, B, C };

int convertMyEnumToInt(MyEnum e) {
    switch (e) {
        case MyEnum::A: return 0;
        case MyEnum::B: return 1;
        case MyEnum::C: return 2;
        default: std::unreachable(); 
    }
}
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
