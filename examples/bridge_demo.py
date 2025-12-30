"""BRIDGE Model Demo with TLSQL.

This work is conducted on the TML1M dataset from SJTUTables, a dataset of users, movies, and ratings.
"""

import time

import torch
import torch.nn.functional as F

from tlsql.examples.bridge.data_loader import prepare_data_from_tlsql
from tlsql.examples.bridge.model import build_bridge
from tlsql.examples.bridge.baselines import run_random, run_mlp


def train_bridge(model, optimizer, target_table, non_table_embeddings, adj, y, train_mask):
    """Train BRIDGE model for one epoch"""
    model.train()
    optimizer.zero_grad()
    logits = model(table=target_table, non_table=non_table_embeddings, adj=adj)
    loss = F.cross_entropy(logits[train_mask].squeeze(), y[train_mask])
    loss.backward()
    optimizer.step()
    return loss.item()


@torch.no_grad()
def test_bridge(model, target_table, non_table_embeddings, adj, y, masks):
    """Test BRIDGE model"""
    model.eval()
    logits = model(table=target_table, non_table=non_table_embeddings, adj=adj)
    preds = logits.argmax(dim=1)
    accs = []
    for mask in masks:
        correct = float(preds[mask].eq(y[mask]).sum().item())
        accs.append(correct / int(mask.sum()))
    return accs


def train_bridge_model(target_table, non_table_embeddings, adj, emb_size, epochs=10, lr=0.005, wd=1e-4, device=None):
    """Train BRIDGE model

    Args:
        target_table: Target table data
        non_table_embeddings: Non-table embeddings
        adj: Adjacency matrix
        emb_size: Embedding size
        epochs: Number of training epochs
        lr: Learning rate
        wd: Weight decay
        device: Device (CPU/GPU)

    Returns:
        tuple: (final_train_acc, best_val_acc, test_acc)
    """
    if device is None:
        device = target_table.y.device
    
    model = build_bridge(
        target_table.num_classes,
        target_table.metadata,
        emb_size
    ).to(device)
    
    y = target_table.y.long() if target_table.y.dtype != torch.long else target_table.y
    train_mask, val_mask, test_mask = (
        target_table.train_mask,
        target_table.val_mask,
        target_table.test_mask,
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)

    metric = "Acc"
    best_val_acc = test_acc = 0
    times = []

    for epoch in range(1, epochs + 1):
        start = time.time()
        train_loss = train_bridge(model, optimizer, target_table, non_table_embeddings, adj, y, train_mask)
        train_acc, val_acc, tmp_test_acc = test_bridge(
            model, target_table, non_table_embeddings, adj, y,
            [train_mask, val_mask, test_mask]
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            test_acc = tmp_test_acc

        times.append(time.time() - start)
        print(
            f"BRIDGE Epoch: [{epoch}/{epochs}] "
            f"Train Loss: {train_loss:.4f} Train {metric}: {train_acc:.4f} "
            f"Val {metric}: {val_acc:.4f}, Test {metric}: {tmp_test_acc:.4f} "
        )

    print(f"BRIDGE Mean time per epoch: {torch.tensor(times).mean():.4f}s")
    print(f"BRIDGE Total time: {sum(times):.4f}s")
    
    # Calculate final train accuracy
    model.eval()
    with torch.no_grad():
        logits = model(table=target_table, non_table=non_table_embeddings, adj=adj)
        preds = logits.argmax(dim=1)
        final_train_acc = float(preds[train_mask].eq(y[train_mask]).sum().item()) / int(train_mask.sum())
    
    print(f"BRIDGE Final - Train Acc: {final_train_acc:.4f}, Val Acc: {best_val_acc:.4f}, Test Acc: {test_acc:.4f}")
    return final_train_acc, best_val_acc, test_acc


def main():
    """Main demo function for tml1m dataset"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    db_config = {
        'db_type': 'mysql',
        'host': 'localhost',
        'port': 3306,
        'database': 'tml1m',
        'username': 'root',
        'password': 'cfy1007'
    }
    train_tlsql = """
    TRAIN WITH (users.*, movies.*, ratings.*)
    FROM users, movies, ratings
    WHERE users.Gender='M' and users.userID BETWEEN 1 AND 3000
    """

    validate_tlsql = """
    VALIDATE WITH (users.*)
    FROM users
    WHERE users.Gender='M' and users.userID>3000
    """

    predict_tlsql = """
    PREDICT VALUE(users.Age, CLF)
    FROM users
    WHERE users.Gender='F'
    """

    target_table, non_table_embeddings, adj, emb_size = prepare_data_from_tlsql(
        train_tlsql=train_tlsql,
        validate_tlsql=validate_tlsql,
        predict_tlsql=predict_tlsql,
        db_config=db_config,
        device=device
    )

    print(f"Data loaded: {len(target_table)} samples, {target_table.num_classes} classes")
    print(f"Training samples: {target_table.train_mask.sum().item()}")
    print(f"Validation samples: {target_table.val_mask.sum().item()}")
    print(f"Test samples: {target_table.test_mask.sum().item()}")

    # Random Guess
    print("\nRunning Random Guess...")
    train_mask, val_mask, test_mask = (
        target_table.train_mask,
        target_table.val_mask,
        target_table.test_mask,
    )
    random_train_acc, random_val_acc, random_test_acc = run_random(
        target_table.y, train_mask, val_mask, test_mask
    )

    # MLP
    print("\nRunning MLP...")
    mlp_train_acc, mlp_val_acc, mlp_test_acc = run_mlp(target_table, device=device)

    # BRIDGE Model
    print("\nRunning BRIDGE Model...")
    bridge_train_acc, bridge_val_acc, bridge_test_acc = train_bridge_model(
        target_table, non_table_embeddings, adj, emb_size, device=device
    )

    # Final comparison table
    print(f"\n{'Method':<20} {'Train Acc':<15} {'Val Acc':<15} {'Test Acc':<15}")
    print(f"{'='*65}")
    print(f"{'Random Guess':<20} {random_train_acc:<15.4f} {random_val_acc:<15.4f} {random_test_acc:<15.4f}")
    print(f"{'MLP':<20} {mlp_train_acc:<15.4f} {mlp_val_acc:<15.4f} {mlp_test_acc:<15.4f}")
    print(f"{'BRIDGE':<20} {bridge_train_acc:<15.4f} {bridge_val_acc:<15.4f} {bridge_test_acc:<15.4f}")


if __name__ == "__main__":
    main()
