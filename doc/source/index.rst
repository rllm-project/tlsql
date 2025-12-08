TLSQL Documentation
===================

TLSQL is a Python library that converts custom SQL-like statements into standard SQL queries for machine learning workflows. It supports three types of statements for dataset splitting in machine learning pipelines.

Overview
--------

TLSQL uses three statements to divide your dataset into training, validation, and test sets:

- **TRAIN WITH**: Specifies the training set
- **PREDICT VALUE**: Specifies the test set, target column and task_type
- **VALIDATE WITH**: Specifies the validation set

TLSQL Syntax
------------

1. TRAIN WITH Statement
~~~~~~~~~~~~~~~~~~~~~~~~

The ``TRAIN WITH`` statement specifies which columns and tables to use for training data.

**Syntax:**

.. code-block:: sql

    TRAIN WITH (column_selectors)
    FROM Tables(table1, table2, ...)
    [WHERE conditions]

**Example:**

.. code-block:: sql

    TRAIN WITH (users.*, movies.*, ratings.*)
    FROM Tables(users, movies, ratings)
    WHERE users.Gender='M' AND movies.Year >= 2000 AND ratings.Rating > 4


2. PREDICT VALUE Statement
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``PREDICT VALUE`` statement specifies the target column for prediction and the task type. This statement defines the test set - the data for which you want to make predictions.

**Syntax:**

.. code-block:: sql

    PREDICT VALUE(table.column, TASK_TYPE)
    FROM table
    [WHERE conditions]

**Task Types:**

- ``CLF`` - Classification task (predicts discrete categories)
- ``REG`` - Regression task (predicts continuous values)

**Example:**

.. code-block:: sql

    PREDICT VALUE(users.Age, CLF)
    FROM users
    WHERE users.Gender='F' OR users.userID IN (1,2,3,4,5)

3. VALIDATE WITH Statement
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``VALIDATE WITH`` statement specifies validation data with the same syntax as ``TRAIN WITH``

**Syntax:**

.. code-block:: sql

    VALIDATE WITH (column_selectors)
    FROM Tables(table1, table2, ...)
    [WHERE conditions]

**Example:**

.. code-block:: sql

    VALIDATE WITH (users.*, movies.*, ratings.*)
    FROM Tables(users, movies, ratings)
    WHERE users.Gender='M' AND movies.Year < 2000



Quick Start
-----------

.. code-block:: python

    import tlsql
    
    result = tlsql.convert("PREDICT VALUE(users.Age, CLF) FROM users")
    print(result.statement_type)  # 'PREDICT'
    print(result.target_column)   # 'users.Age'
    print(result.task_type)       # 'CLF'

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Conversion

   conversion

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   modules/core

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
