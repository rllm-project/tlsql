"""BRIDGE Model Demo with TLSQL.

The TML1M dataset from SJTUTables is used in this study. The dataset comprises three tables: users, movies, and ratings.
"""

import argparse
import torch
from tlsql.examples.bridge.data_loader import prepare_data_from_tlsql
from tlsql.examples.bridge.model import build_bridge_model
from tlsql.examples.bridge.train import train_bridge_model


def main():
    """Main demo function for tml1m dataset"""
    parser = argparse.ArgumentParser(
        description="BRIDGE Model Demo with TLSQL on tml1m Dataset"
    )
    parser.add_argument("--epochs", type=int, default=10, help="Training epochs")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--wd", type=float, default=1e-4, help="Weight decay")

    args = parser.parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    db_config = {
        'db_type': 'mysql',
        'host': 'localhost',
        'port': 3306,
        'database': 'tml1m',
        'username': 'yourusername',
        'password': 'yourpassword'
    }

    train_sql = """
    TRAIN WITH (users.*, movies.title, ratings.*)
    FROM users, movies, ratings
    WHERE users.Gender='M' and users.userID BETWEEN 1 AND 3000
    """

    validate_sql = """
    VALIDATE WITH (users.*, movies.*)
    FROM users, movies
    WHERE users.Gender='M' and users.userID>3000
    """

    predict_sql = """
    PREDICT VALUE(users.Age, CLF)
    FROM users
    WHERE users.Gender='F'
    """

    target_table, non_table_embeddings, adj, emb_size = prepare_data_from_tlsql(
        train_sql=train_sql,
        validate_sql=validate_sql,
        predict_sql=predict_sql,
        db_config=db_config,
        device=device
    )

    print(f"Data loaded: {len(target_table)} samples, {target_table.num_classes} classes")
    print(f"Training samples: {target_table.train_mask.sum().item()}")
    print(f"Validation samples: {target_table.val_mask.sum().item()}")
    print(f"Test samples: {target_table.test_mask.sum().item()}")

    bridge_model = build_bridge_model(
        target_table.num_classes,
        target_table.metadata,
        emb_size
    ).to(device)

    model, best_val_acc, test_acc = train_bridge_model(
        bridge_model, target_table, non_table_embeddings, adj,
        args.epochs, args.lr, args.wd
    )

    print("Final Results:")
    print(f"Best Validation Accuracy: {best_val_acc:.4f}")
    print(f"Test Accuracy: {test_acc:.4f}")


if __name__ == "__main__":
    main()
