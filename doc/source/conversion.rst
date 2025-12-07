TLSQL to SQL Conversion
========================

This section shows the conversion process of a TLSQL statement to standard SQL, using a PREDICT VALUE statement as an example.

Example: PREDICT VALUE Statement
---------------------------------

**TLSQL:**

.. code-block:: sql

    PREDICT VALUE(users.Age, CLF)
    FROM users
    WHERE users.Gender = 'M' AND users.Occupation IN (1,2,4)

Conversion Process
------------------

The conversion process consists of four main steps:

1. **Lexical Analysis (Tokenization)**
   
   **Used Class:** :class:`Lexer`
   
   The TLSQL text is tokenized into a stream of tokens using the ``Lexer`` class.

   **Tokens Stream:**
   
   - ``PREDICT`` (keyword)
   - ``VALUE`` (keyword)
   - ``(`` (left parenthesis)
   - ``users`` (identifier)
   - ``.`` (dot)
   - ``Age`` (identifier)
   - ``,`` (comma)
   - ``CLF`` (keyword)
   - ``)`` (right parenthesis)
   - ``FROM`` (keyword)
   - ``users`` (identifier)
   - ``WHERE`` (keyword)
   - ``users`` (identifier)
   - ``.`` (dot)
   - ``Gender`` (identifier)
   ...

2. **Syntax Analysis (Parsing)**
   
   **Used Class:** :class:`Parser`
   
   The token stream is parsed into an Abstract Syntax Tree (AST) using the ``Parser`` class.

   **AST Structure:**
   
   .. code-block:: python

       PredictStatement(
         value=ValueClause(
           target=ColumnReference(table='users', column='Age'),
           predict_type=PredictType(type_name='CLF')
         ),
         from_table=FromClause(table='users'),
         where=WhereClause(
           condition=BinaryExpr(
             op='AND',
             left=BinaryExpr(
               op='=',
               left=ColumnExpr(column=ColumnReference(table='users', column='Gender')),
               right=LiteralExpr(value='M')
             ),
             right=InExpr(
               column=ColumnReference(table='users', column='Occupation'),
               values=[LiteralExpr(value=1), LiteralExpr(value=2), LiteralExpr(value=4)]
             )
           )
         )
       )

3. **SQL Generation**
   
   **Used Class:** :class:`SQLGenerator`
   
   The AST is traversed to generate standard SQL components using the ``SQLGenerator`` class.

   **Extracted Information:**
   
   - Target Table: ``users``
   - Target Column: ``users.Age``
   - Task Type: ``CLF`` (Classification)
   - WHERE Condition: ``Gender = 'M' AND Occupation IN (1,2,4)``

4. **Result Assembly**
   
   **Used Class:** :class:`ConversionResult`
   
   The final standard SQL statement is constructed and wrapped in a ``ConversionResult`` object, which contains all extracted metadata.

**Standard SQL:**

.. code-block:: sql

    SELECT * FROM users WHERE Gender = 'M' AND Occupation IN (1,2,4)

**Conversion Result:**

The conversion returns a ``ConversionResult`` object containing:

- ``statement_type``: ``'PREDICT'``
- ``target_column``: ``'users.Age'``
- ``task_type``: ``'CLF'``
- ``target_table``: ``'users'``
- ``where_condition``: ``"Gender = 'M' AND Occupation IN (1,2,4)"``
- ``filter_condition``: ``FilterCondition(table='users', condition="Gender = 'M' AND Occupation IN (1,2,4)")``

