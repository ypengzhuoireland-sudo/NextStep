In this project, a Knowledge Component (KC) is a skill point that students need to master during programming. An adaptive tutor system can observe this skill point through students' answers, code submissions, and errors.

A KC includes what students need to understand, what mistakes students may make, and how the tutor system can evaluate whether students have mastered the skill.

Each exercise in the question bank can be tagged with one or more KCs. After a student completes an exercise, the knowledge model can update its estimate of the student's mastery of the relevant KCs. Then, the exercise selection strategy can choose more exercises for the student, especially exercises related to KCs where the student appears less confident.

## KC1: Variables and Assignment

In this KC, students should learn how variables are created, named, assigned, and updated in Python. Students should understand that a variable refers to a container where they can place integers, floating-point numbers, strings, Boolean values, lists, dictionaries, or other objects. Students should also understand the concept of reassignment. For example, after running `x = 5`, if `x = x + 1` is run, the value of `x` becomes `6`.

Common mistakes include confusing `=` with "equals" in mathematics, using a variable before assigning a value to it, choosing unclear variable names, or accidentally overwriting a value that will be needed later.

The tutor system can evaluate this KC by asking students to create variables, identify the types of stored values, predict the final value after multiple assignments, or fix code with variable update errors.

## KC2: Data Types and Type Conversion

In this KC, students should understand the basic data types in Python, such as integers, floating-point numbers, strings, Boolean values, lists, and dictionaries. Students should know that Python variables do not need to have their type declared in advance. Students also need to understand type conversion. For example, the value returned by `input()` is treated as a string, so students may need to use `int()` or `float()` to convert it into a number before doing mathematical calculations.

Common mistakes include directly adding strings and integers, forgetting to convert user input, assuming that `"5"` and `5` behave in the same way, or converting data without checking whether the data can be converted.

The tutor system can evaluate this KC by asking students to identify data types, convert data, fix type errors, or explain why two expressions that look similar produce different results.

## KC3: Expressions and Operators

In this KC, students should be able to use operators to build and evaluate expressions. Students should understand arithmetic operators such as `+`, `-`, `*`, `/`, `//`, and `%`; comparison operators such as `==` and `>`; and logical operators such as `and`, `or`, and `not`. Students should know that expressions are evaluated and produce values, and that operator precedence affects the final result. They should also understand that some operators behave differently depending on data type. For example, `+` can be used for both numeric addition and string concatenation.

Common mistakes include confusing `=` and `==`, misunderstanding the order of operations, writing invalid conditions such as `x > 1 and < 10`, or using logical operators without thinking about the resulting `true` or `false` value.

The tutor system can evaluate this KC by asking students to predict expression results, complete missing operators, modify invalid expressions, or explain why a condition evaluates to `true` or `false`.

## KC4: Conditional Branching

In this KC, students need to understand how to use `if`, `elif`, and `else`, as well as `match`/`case` when appropriate. Students should know that conditions are evaluated as `true` or `false`, and then the program executes the branch whose condition is satisfied.

This KC is important because beginners often write conditions that are too broad, put branches in the wrong order, or misunderstand comparison operators and logical operators inside conditions. For example, students may write several independent `if` statements when an `if`/`elif` structure is needed, causing multiple branches to be executed. Common mistakes include forgetting the colon after a condition, using assignment as comparison, putting `else` in the wrong place, or writing overlapping conditions that lead to unexpected behavior.

The tutor system can evaluate this KC by asking students to classify input, write decision rules, predict which branch will be executed, or debug code with conditional logic errors.

## KC5: Iteration and Loop Control

In this KC, students need to understand how to use `for` and `while` loops to repeat code. Students should be able to use loops to process multiple values, repeat calculations, count items, or build results step by step. The core idea is that loops are not only about repetition; they also involve program state changing over time. Students need to know where to initialize counters or accumulators, how they change inside the loop, and when the loop should stop.

Common mistakes include off-by-one errors, forgetting to update the loop variable, incorrectly putting initialization inside the loop, using the wrong `range`, or writing a loop that never ends.

The tutor system can evaluate this KC through tasks such as asking students to sum a group of numbers, count items that meet a condition, trace loop output, use `break` or `continue`, or fix a loop with an incorrect stopping condition.

## KC6: Functions and Return Values

In this KC, students need to understand how to organize code into functions with clear inputs and outputs. Students should understand that parameters receive input values, the function body performs a task, and `return` sends the result back to the caller. Students should know that functions can turn code into reusable tools that can be called when needed instead of being written repeatedly.

Common mistakes include confusing `print()` and `return`, forgetting to pass arguments, returning a result too early, writing functions that depend on unrelated global variables, or not understanding where the return value goes.

The tutor system can evaluate this KC by asking students to write small functions, choose appropriate parameters, predict function return values, or fix code where a function only prints the result but does not return it.

## KC7: Lists and Index-Based Access

In this KC, students should be able to use lists to store and process ordered collections of data. Students should understand that a list can store multiple values, that each element has an index, and that Python indexing starts from `0`. Students should be able to create lists, access elements by index, update values in a list, use list methods, slice lists, and iterate through list elements. This KC is different from ordinary variables because students need to think about both the whole collection and the individual elements inside the collection.

Common mistakes include using the wrong index, forgetting that the last valid index is the length of the list minus one, confusing a single element with the whole list, or modifying a list in a way that unexpectedly affects later code.

The tutor system can evaluate this KC by asking students to get list elements, update a value, find the largest number in a list, calculate an average, or debug index errors.

## KC8: Dictionaries and Key-Value Data

In this KC, students need to understand the relationship between keys and values in dictionaries. Students should understand that dictionaries are not accessed by position like lists; they are accessed by key. Students should be able to create dictionaries, use keys to get values, update entries, check whether a key exists, and iterate through keys or values. This KC is useful for data tasks with labels, such as usernames, scores, word-frequency counts, or product prices.

Common mistakes include using list indexes when dictionary keys are needed, accessing a key that does not exist, confusing keys and values, or assuming that dictionaries and lists are used in the same way.

The tutor system can evaluate this KC by asking students to get a student's score from a dictionary, update a value, count word frequency, or fix a `KeyError`.

## KC9: String Processing

In this KC, students should be able to process text data in Python. Students should understand that a string is a sequence of characters. It can be indexed, sliced, concatenated, compared, and processed with string methods. Students need to understand common string methods such as `lower()`, `upper()`, `strip()`, and `split()`, as well as string formatting.

Common mistakes include forgetting that strings are immutable, mixing string and number operations, using the wrong index when accessing characters, or not removing extra spaces before comparing input.

The tutor system can evaluate this KC by asking students to format messages, check whether input meets a condition, split a sentence into words, count characters, or correct mistakes in the use of string methods.

## KC10: Debugging and Error Interpretation

In this KC, students should be able to read, understand, and handle errors in Python. Students should learn how to solve errors by using clues about where the program stopped and why it stopped. Students should be able to identify common error types such as `SyntaxError`, `NameError`, `TypeError`, `IndexError`, and `KeyError`.

Common mistakes include reading only the last line of an error message, randomly changing code without understanding the problem, ignoring the actual values of variables, or thinking that every error means the whole program is wrong.

The tutor system can evaluate this KC by giving students faulty code to fix, asking students to explain error messages, or asking students to choose the most likely cause of a bug.

## KC11: Recursion and Base Cases

In this KC, students should understand how a function can solve a problem by calling itself. Students should know that recursion needs a base case to stop and a recursive case that moves the problem closer to the base case. Recursion is difficult for many beginners because it requires students to think about a chain of function calls instead of a simple sequence of statements. The tutor system should provide exercises that gradually increase in difficulty.

Common mistakes include forgetting the base case, writing a recursive call that does not move the problem closer to the end, returning the wrong value, or confusing recursion with ordinary loops.

The tutor system can evaluate this KC by asking students to trace recursive output, fix a missing base case, write a recursive factorial function or summation function, or explain why a recursive function never stops.

## KC12: Object-Oriented Programming Basics

In this KC, students should understand the basic idea of using classes and objects to organize code. Students should know that a class defines a general structure, while an object is a specific instance created from that class. Students should be able to define simple classes, create objects, use attributes to store object state, and write methods to operate on that state.

Common mistakes include confusing classes and objects, forgetting `self`, using an attribute before setting it, or not understanding why a piece of code should be placed inside a class.

The tutor system can evaluate this KC by asking students to create a simple `Student` or `BankAccount` class, set and read attributes, call methods, or fix code with incorrect use of `self`.
