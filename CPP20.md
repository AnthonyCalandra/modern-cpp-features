# C++20

## Overview
Many of these descriptions and examples come from various resources (see [Acknowledgements](#acknowledgements) section), summarized in my own words.

Also, there are now dedicated readme pages for each major C++ version.

C++20 includes the following new language features:
- [lambda templates](#lambda-templates)

C++20 includes the following new library features:
- [std::ranges](#stdranges)

## C++20 Language Features

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
