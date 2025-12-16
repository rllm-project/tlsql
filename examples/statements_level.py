"""Three-Level Logic Demo in TLSQL

"""


def level_I():
    """Demonstrate Level I: PREDICT Statement Logic"""
    print("Level I: Only PREDICT")
    predict_sql = """
    PREDICT VALUE(users.Age, CLF)
    FROM users
    WHERE users.Gender='F'
    """

    train_sql = None
    validate_sql = None

    print("PREDICT:")
    print(predict_sql.strip())
    print("\nTRAIN:None")
    print("Uses all data except PREDICT data")
    print("\nVALIDATE:None")
    print("Uses k=5 fold cross validation on train data")
    print()


def level_II():
    """Demonstrate Level II: TRAIN Statement Logic"""
    print("Level II: PREDICT and TRAIN")

    predict_sql = """
    PREDICT VALUE(users.Age, CLF)
    FROM users
    WHERE users.Gender='F'
    """

    train_sql = """
    TRAIN WITH (users.*, movies.title, ratings.*)
    FROM users, movies, ratings
    WHERE users.Age > 25 AND movies.Year > 2000 AND ratings.Rating >= 4
    """

    validate_sql = None

    print("PREDICT:")
    print(predict_sql.strip())
    print("\nTRAIN:")
    print(train_sql.strip())
    print("\nVALIDATE:None")
    print("Uses k=5 fold cross validation on train data")
    print()


def level_III():
    """Demonstrate Level III: VALIDATE Statement Logic"""
    print("Level III: PREDICT, TRAIN and VALIDATE")

    predict_sql = """
    PREDICT VALUE(users.Age, CLF)
    FROM users
    WHERE users.Gender='F'
    """

    train_sql = """
    TRAIN WITH (users.*, movies.title, ratings.*)
    FROM users, movies, ratings
    WHERE users.Age > 25 AND movies.Year > 2000 AND ratings.Rating >= 4
    """

    validate_sql = """
    VALIDATE WITH (users.*, movies.*)
    FROM users, movies
    WHERE users.Age BETWEEN 30 AND 50
    """

    print("PREDICT:")
    print(predict_sql.strip())
    print("\nTRAIN:")
    print(train_sql.strip())
    print("\nVALIDATE:")
    print(validate_sql.strip())
    print()


def main():
    """Main function demonstrating three-level logic"""
    level_I()
    level_II()
    level_III()

    print("Summary:")
    print("PREDICT - REQUIRED")
    print("TRAIN - OPTIONAL, defaults to all data except PREDICT")
    print("VALIDATE - OPTIONAL, defaults to k=5 fold cross validation")


if __name__ == "__main__":
    main()
