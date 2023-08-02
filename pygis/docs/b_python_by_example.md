---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
 
(python_by_example)=

# An Introductory Example

## Overview

We\'re now ready to start learning the Python language itself.

In this lecture, we will write and then pick apart small Python
programs.

The objective is to introduce you to basic Python syntax and data
structures.

Deeper concepts will be covered in later lectures.

You should have read the {ref}`lecture <getting_started>` on getting started with Python before beginning this one.

## Understanding Data Structures

In computer science, data structures are a way of organizing and storing data to perform operations efficiently. In Python, data structures come in various types, such as lists, tuples, sets, dictionaries, and more. Each data structure has its own characteristics and use cases.

For example, lists are mutable sequences of elements, and you can add, remove, or modify elements easily. Dictionaries, on the other hand, use key-value pairs to store data, making it easy to retrieve values based on their corresponding keys.

Throughout this course, we'll use data structures to represent and manipulate data in various Python programs.

## Indentation in Python

In Python, indentation is crucial for defining the structure of the code. Unlike many other programming languages that use braces ({}) to delimit code blocks, Python uses indentation. The number of spaces or tabs at the beginning of a line determines which code block the line belongs to.

For example, in a `for` loop or `if` statement, the indented block of code represents what will be executed if the condition is met. Indentation must be consistent and usually follows the standard of four spaces.

Now that we have an understanding of data structures and indentation, let's move on to writing some Python code examples.

## The Task: Plotting a White Noise Process

Suppose we want to simulate and plot the white noise process
$\epsilon_0, \epsilon_1, \ldots, \epsilon_T$, where each draw
$\epsilon_t$ is independent standard normal.

In other words, we want to generate figures that look something like
this:


```{figure} /_static/lecture_specific/python_by_example/test_program_1_updated.png
:name: white_noise_plot
:alt: White Noise Process Plot 
:caption: White Noise Process Plot
```


(Here $t$ is on the horizontal axis and $\epsilon_t$ is on the vertical
axis.)

We\'ll do this in several different ways, each time learning something
more about Python.

We run the following command first, which helps ensure that plots appear
in the notebook if you run it on your own machine.

```{code-cell} python3
%matplotlib inline
```

## Version 1

(ourfirstprog)=

Here are a few lines of code that perform the task we set

```{code-cell} ipython3
import numpy as np
import matplotlib.pyplot as plt

ϵ_values = np.random.randn(100)
plt.plot(ϵ_values)
plt.show()
```

Let\'s break this program down and see how it works.

(import)=

### Imports

The first two lines of the program import functionality from external
code libraries.

The first line imports NumPy, a
favorite Python package for tasks like

-   working with arrays (vectors and matrices)
-   common mathematical functions like `cos` and `sqrt`
-   generating random numbers
-   linear algebra, etc.

After `import numpy as np` we have access to these attributes via the
syntax `np.attribute`.

Here\'s two more examples

```{code-cell} python3
np.sqrt(4)
```

```{code-cell} python3
np.log(4)
```

We could also use the following syntax:

```{code-cell} python3
import numpy

numpy.sqrt(4)
```

But the former method (using the short name `np`) is convenient and more
standard.

#### Why So Many Imports?

Python programs typically require several import statements.

The reason is that the core language is deliberately kept small, so that
it\'s easy to learn and maintain.

When you want to do something interesting with Python, you almost always
need to import additional functionality.

#### Packages

As stated above, NumPy is a Python *package*.

Packages are used by developers to organize code they wish to share.

In fact, a package is just a directory containing

1.  files with Python code --- called **modules** in Python speak
2.  possibly some compiled code that can be accessed by Python (e.g.,
    functions compiled from C or FORTRAN code)
3.  a file called `__init__.py` that specifies what will be executed
    when we type `import package_name`

In fact, you can find and explore the directory for NumPy on your
computer easily enough if you look around.

On this machine, it\'s located in

```{code-block} none
anaconda3/lib/python3.7/site-packages/numpy
```

#### Subpackages

Consider the line `ϵ_values = np.random.randn(100)`.

Here `np` refers to the package NumPy, while `random` is a
**subpackage** of NumPy.

Subpackages are just packages that are subdirectories of another
package.

### Importing Names Directly

Recall this code that we saw above

```{code-cell} python3
import numpy as np

np.sqrt(4)
```

Here\'s another way to access NumPy\'s square root function

```{code-cell} python3
from numpy import sqrt

sqrt(4)
```

This is also fine.

The advantage is less typing if we use `sqrt` often in our code.

The disadvantage is that, in a long program, these two lines might be
separated by many other lines.

Then it\'s harder for readers to know where `sqrt` came from, should
they wish to.

### Random Draws

Returning to our program that plots white noise, the remaining three
lines after the import statements are

```{code-cell} python3
ϵ_values = np.random.randn(100)
plt.plot(ϵ_values)
plt.show()
```

The first line generates 100 (quasi) independent standard normals and
stores them in `ϵ_values`.

The next two lines generate the plot.

We can and will look at various ways to configure and improve this plot
below.

## Alternative Implementations

Let\'s try writing some alternative versions of
{ref}`our first program <ourfirstprog>`, which
plotted IID draws from the normal distribution.

The programs below are less efficient than the original one, and hence
somewhat artificial.

But they do help us illustrate some important Python syntax and
semantics in a familiar setting.


### A Version with a For Loop

Here\'s a version that illustrates `for` loops and Python lists.

(firstloopprog)=

```{code-cell} python3
ts_length = 100
ϵ_values = []   # empty list

for i in range(ts_length):
    e = np.random.randn()
    ϵ_values.append(e)

plt.plot(ϵ_values)
plt.show()
```

In brief,

-   The first line sets the desired length of the time series.
-   The next line creates an empty *list* called `ϵ_values` that will
    store the $\epsilon_t$ values as we generate them.
-   The statement `# empty list` is a *comment*, and is ignored by
    Python\'s interpreter.
-   The next three lines are the `for` loop, which repeatedly draws a
    new random number $\epsilon_t$ and appends it to the end of the list
    `ϵ_values`.
-   The last two lines generate the plot and display it to the user.

Let\'s study some parts of this program in more detail.

(lists_ref)=

### Lists

Consider the statement `ϵ_values = []`, which creates an empty list.

Lists are a *native Python data structure* used to group a collection of
objects.

For example, try

```{code-cell} python3
x = [10, 'foo', False]
type(x)
```

The first element of `x` is an
[integer](https://en.wikipedia.org/wiki/Integer_%28computer_science%29),
the next is a
[string](https://en.wikipedia.org/wiki/String_%28computer_science%29),
and the third is a [Boolean value](https://en.wikipedia.org/wiki/Boolean_data_type).

When adding a value to a list, we can use the syntax
`list_name.append(some_value)`

```{code-cell} python3
x
```

```{code-cell} python3
x.append(2.5)
x
```

Here `append()` is what\'s called a *method*, which is a function
\"attached to\" an object---in this case, the list `x`.

We\'ll learn all about methods later on, but just to give you some idea,

-   Python objects such as lists, strings, etc. all have methods that
    are used to manipulate the data contained in the object.
-   String objects have [string methods](https://docs.python.org/3/library/stdtypes.html#string-methods),
    list objects have [list methods](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists),
    etc.

Another useful list method is `pop()`

```{code-cell} python3
x
```

```{code-cell} python3
x.pop()
```

```{code-cell} python3
x
```

Lists in Python are zero-based (as in C, Java or Go), so the first
element is referenced by `x[0]`

```{code-cell} python3
x[0]   # first element of x
```

```{code-cell} python3
x[1]   # second element of x
```

### The For Loop

Now let\'s consider the `for` loop from
{ref}`the program above <firstloopprog>`, which
was

```{code-cell} python3
for i in range(ts_length):
    e = np.random.randn()
    ϵ_values.append(e)
```

Python executes the two indented lines `ts_length` times before moving
on.

These two lines are called a `code block`, since they comprise the
\"block\" of code that we are looping over.

Unlike most other languages, Python knows the extent of the code block
*only from indentation*.

In our program, indentation decreases after line `ϵ_values.append(e)`,
telling Python that this line marks the lower limit of the code block.

More on indentation below---for now, let\'s look at another example of
a `for` loop

```{code-cell} python3
animals = ['dog', 'cat', 'bird']
for animal in animals:
    print("The plural of " + animal + " is " + animal + "s")
```

This example helps to clarify how the `for` loop works: When we execute
a loop of the form

```{code-block}
---
class: no-execute
---

for variable_name in sequence:
    <code block>
```

The Python interpreter performs the following:

-   For each element of the `sequence`, it \"binds\" the name
    `variable_name` to that element and then executes the code block.

The `sequence` object can in fact be a very general object, as we\'ll
see soon enough.

### A Comment on Indentation

In discussing the `for` loop, we explained that the code blocks being
looped over are delimited by indentation.

In fact, in Python, **all** code blocks (i.e., those occurring inside
loops, if clauses, function definitions, etc.) are delimited by
indentation.

Thus, unlike most other languages, whitespace in Python code affects the
output of the program.

Once you get used to it, this is a good thing: It

-   forces clean, consistent indentation, improving readability
-   removes clutter, such as the brackets or end statements used in
    other languages

On the other hand, it takes a bit of care to get right, so please
remember:

-   The line before the start of a code block always ends in a colon
    -   `for i in range(10):`
    -   `if x > y:`
    -   `while x < 100:`
    -   etc., etc.
-   All lines in a code block **must have the same amount of indentation**.
-   The Python standard is 4 spaces, and that\'s what you should use.

### While Loops

The `for` loop is the most common technique for iteration in Python.

But, for the purpose of illustration, let\'s modify
{ref}`the program above <firstloopprog>` to use
a `while` loop instead.

(whileloopprog)=

```{code-cell} python3
ts_length = 100
ϵ_values = []
i = 0
while i < ts_length:
    e = np.random.randn()
    ϵ_values.append(e)
    i = i + 1
plt.plot(ϵ_values)
plt.show()
```

Note that

-   the code block for the `while` loop is again delimited only by indentation
-   the statement `i = i + 1` can be replaced by `i += 1`

## Another Application

Let\'s do one more application before we turn to exercises.

In this application, we plot the balance of a bank account over time.

There are no withdraws over the time period, the last date of which is
denoted by $T$.

The initial balance is $b_0$ and the interest rate is $r$.

The balance updates from period $t$ to $t+1$ according to

```{math}
:label: ilom
    b_{t+1} = (1 + r) b_t
```

In the code below, we generate and plot the sequence $b_0, b_1, \ldots, b_T$
generated by {eq}`ilom`.

Instead of using a Python list to store this sequence, we will use a
NumPy array.

```{code-cell} python3
r = 0.025         # interest rate
T = 50            # end date
b = np.empty(T+1) # an empty NumPy array, to store all b_t
b[0] = 10         # initial balance

for t in range(T):
    b[t+1] = (1 + r) * b[t]

plt.plot(b, label='bank balance')
plt.legend()
plt.show()
```

The statement `b = np.empty(T+1)` allocates storage in memory for `T+1`
(floating point) numbers.

These numbers are filled in by the `for` loop.

Allocating memory at the start is more efficient than using a Python
list and `append`, since the latter must repeatedly ask for storage
space from the operating system.

Notice that we added a legend to the plot.

## Attribution
The above lesson was pulled directly from work by [Thomas J. Sargent & John Stachurski](https://python-programming.quantecon.org/about_py.html)
