# C++23

## Overview
Many of these descriptions and examples are taken from various resources (see [Acknowledgements](#acknowledgements) section) and summarized in my own words.

C++23 includes the following new language features:
- [consteval if](#consteval-if)
- [deducing `this`](#deducing-this)

C++23 includes the following new library features:

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

## C++23 Library Features

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
