"""BRIDGE Model Demo with TLSQL

This example demonstrates how to use TLSQL to train a BRIDGE model.

"""

import argparse
import numpy as np
import torch
import sys

sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")

from tlsql.examples.bridge.train_with_tlsql import (
    prepare_data_from_tlsql,
    build_bridge_model,
    train_bridge_model,
)


def main():
    """Main demo function """
    parser = argparse.ArgumentParser(
        description="BRIDGE Model Demo with TLSQL"
    )
    parser.add_argument("--epochs", type=int, default=10,
                        help="Training epochs")
    parser.add_argument("--lr", type=float, default=0.001,
                        help="Learning rate")
    parser.add_argument("--wd", type=float, default=1e-4,
                        help="Weight decay")

    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Change to local config
    db_config = {
        'db_type': 'mysql',
        'host': 'localhost',
        'port': 3306,
        'database': 'tml1m',
        'username': 'root',
        'password': 'cfy1007'
    }

    predict_sql = """
    PREDICT VALUE(Age, CLF)
    FROM users
    WHERE users.Gender='F' OR users.userID IN (1,2,3,4,5,6,7)
    """

    train_sql = None
    # train_sql = """
    # TRAIN WITH (users.*, movies.*, ratings.*)
    # FROM Tables(users, movies, ratings)
    # WHERE users.Gender='M' and movies.Year >=2000  and ratings.rating >4
    # """
    validate_sql = None
    # validate_sql="""
    # VALIDATE WITH (users.*,movies.*,ratings.userID)
    # FROM Tables(users,movies,ratings)
    # WHERE users.Gender='F' and movies.Year < 2000 and ratings.rating<4
    # """

    target_table, non_table_embeddings, adj, emb_size, use_kfold = prepare_data_from_tlsql(
        train_sql=train_sql,
        validate_sql=validate_sql,
        predict_sql=predict_sql,
        db_config=db_config,
        device=device
    )

    print("Data loaded successfully")
    print(f"Target table size: {len(target_table)}")
    print(f"Number of classes: {target_table.num_classes}")
    print(f"Use k-fold: {use_kfold}")

    print("\nBRIDGE Model")
    bridge_model = build_bridge_model(
        target_table.num_classes,
        target_table.metadata,
        emb_size
    ).to(device)

    if use_kfold:
        print("Training with k-fold cross-validation")
        fold_results = train_bridge_model(
            bridge_model, target_table, non_table_embeddings, adj,
            args.epochs, args.lr, args.wd, k_folds=5
        )
        # Extract average accuracy from k-fold results
        val_accs = [r['best_val_acc'] for r in fold_results]
        test_accs = [r['test_acc'] for r in fold_results]
        val_acc_bridge = np.mean(val_accs)
        test_acc_bridge = np.mean(test_accs)
        print("K-fold Results:")
        print(f"Validation Accuracy - Mean: {val_acc_bridge:.4f}, Std: {np.std(val_accs):.4f}")
        print(f"Test Accuracy - Mean: {test_acc_bridge:.4f}, Std: {np.std(test_accs):.4f}")
    else:
        _, val_acc_bridge, test_acc_bridge = train_bridge_model(
            bridge_model, target_table, non_table_embeddings, adj,
            args.epochs, args.lr, args.wd
        )
        print(f"Validation Accuracy: {val_acc_bridge:.4f}")
        print(f"Test Accuracy: {test_acc_bridge:.4f}")


if __name__ == "__main__":
    main()
