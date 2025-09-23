import json
import os
import sys
from sklearn.metrics import precision_recall_fscore_support
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix
 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.config import LABEL_LIST, ID2LABEL


#step 1 entity score
def calculate_entity_score_for_ner_data_predicted(expected_file,predicted_file):
    # Load JSON files
    with open(expected_file) as f:
        expected_file = json.load(f)
    with open(predicted_file) as f:
        predicted = json.load(f)
    # Extract true and predicted labels
    true_labels, pred_labels = [], []
    for exp, pred in zip(expected_file, predicted):
        # align by token
        for t, p in zip(exp["ner_tags"], pred["ner_tags"]):
            true_labels.append(t)
            pred_labels.append(p)

    # Compute per-class metrics
    labels = sorted(set(true_labels) | set(pred_labels))
    #sklearn.metrics.precision_recall_fscore_support to compute per-label precision/recall/f1. 
    # (https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)
    #The precision is the ratio tp / (tp + fp) where tp is the number of true positives and fp the number of false positives. 
    #The precision is intuitively the ability of the classifier not to label a negative sample as positive.
    
    #The recall is the ratio tp / (tp + fn) where tp is the number of true positives and fn the number of false negatives. 
    #The recall is intuitively the ability of the classifier to find all the positive samples.
    #The F-beta score can be interpreted as a weighted harmonic mean of the precision and recall, 
    # where an F-beta score reaches its best value at 1 and worst score at 0.

    # zero_division=0 sets metric=0 when denominator is zero (avoids exceptions).
    prec, rec, f1, _ = precision_recall_fscore_support(true_labels, pred_labels, labels=labels, zero_division=0)

    # Collect results
    results = {ID2LABEL[label]: {"precision": p, "recall": r, "f1": f}
            for label, p, r, f in zip(labels, prec, rec, f1)}


    entity_metrics = defaultdict(lambda: {"precision": [], "recall": [], "f1": []})

    for label, metrics in results.items():
        if label == "O":  # skip non-entities
            continue
        entity = label.split("-")[-1]  # e.g. "ORG" from "B-ORG"
        for m in ["precision", "recall", "f1"]:
            entity_metrics[entity][m].append(metrics[m])

    # Average over B-/I-
    entity_scores = {}
    for ent, metrics in entity_metrics.items():
        entity_scores[ent] = {
            m: (sum(values) / len(values)) if values else 0.0
            for m, values in metrics.items()
        }
    print(entity_scores)
    plot_entity_scores_bars_comparison(entity_scores=entity_scores)



def evaluate_multiple_ner(expected_list, predicted_list, id2label):
    """
    Evaluate multiple NER JSONs in BIO format.
    expected_list: list of expected JSON objects (tokens + ner_tags)
    predicted_list: list of predicted JSON objects (tokens + ner_tags)
    id2label: mapping from tag ids to string labels
    """
    true_labels, pred_labels = [], []

    # Aggregate labels across all documents
    for exp, pred in zip(expected_list, predicted_list):
        for t, p in zip(exp["ner_tags"], pred["ner_tags"]):
            true_labels.append(t)
            pred_labels.append(p)

    # Compute per-class metrics
    labels = sorted(set(true_labels) | set(pred_labels))
    prec, rec, f1, _ = precision_recall_fscore_support(
        true_labels, pred_labels, labels=labels, zero_division=0
    )

    # Convert to readable entity-level metrics
    results = {id2label[label]: {"precision": p, "recall": r, "f1": f}
               for label, p, r, f in zip(labels, prec, rec, f1)}

    # Aggregate B-/I- metrics to entities
    entity_metrics = defaultdict(lambda: {"precision": [], "recall": [], "f1": []})
    for label, metrics in results.items():
        if label == "O":
            continue
        entity = label.split("-")[-1]  # e.g., "ORG" from "B-ORG"
        for m in ["precision", "recall", "f1"]:
            entity_metrics[entity][m].append(metrics[m])

    # Average over B-/I- prefixes
    entity_scores = {}
    for ent, metrics in entity_metrics.items():
        entity_scores[ent] = {m: (sum(vals)/len(vals) if vals else 0.0)
                               for m, vals in metrics.items()}

    print("=== Entity Scores ===")
    for ent, scores in entity_scores.items():
        print(f"{ent}: {scores}")

    return true_labels, pred_labels, entity_scores



def plot_entity_scores_bars_comparison(entity_scores, show_values=False):
    from matplotlib.patches import Patch
    """
    Draw two stacked bar plots:
      - top: plain Precision / Recall / F1 grouped bars + metric legend
      - bottom: same grouped bars but colored by performance band, with a separate color legend
    entity_scores: dict {entity: {"precision":..., "recall":..., "f1":...}}

    General interpretation rules:
    High precision, low recall → The model is very careful. It only tags entities when it’s almost sure, but it misses many.
    Low precision, high recall → The model is over-predicting. It tags a lot, but many are wrong.
    High F1 → Balanced performance.

    Zero scores → The model never recognized that entity type in the evaluation set.

    For sensitive entities (e.g., patient IDs, phone numbers), high precision might be more important → fewer false positives.
    For clinical findings (symptoms, diagnoses), higher recall could be critical → you don’t want to miss them.
    """
    entities = list(entity_scores.keys())
    precision = [entity_scores[e]["precision"] for e in entities]
    recall = [entity_scores[e]["recall"] for e in entities]
    f1 = [entity_scores[e]["f1"] for e in entities]

    x = np.arange(len(entities))
    width = 0.25

    def colorize(values):
        colors = []
        for v in values:
            if v >= 0.7:
                colors.append("green")   # good
            elif v >= 0.4:
                colors.append("orange")  # moderate
            else:
                colors.append("red")     # weak
        return colors

    fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

    # --- Subplot 1: Plain chart with metric legend ---
    rects1 = axes[0].bar(x - width, precision, width, label="Precision", color="C0")
    rects2 = axes[0].bar(x, recall, width, label="Recall", color="C1")
    rects3 = axes[0].bar(x + width, f1, width, label="F1", color="C2")

    axes[0].set_ylabel("Score")
    axes[0].set_title("Per-Entity NER Evaluation (Plain)")
    axes[0].set_ylim(0, 1.05)
    axes[0].legend(loc="upper right")

    # --- Subplot 2: Color-coded chart with color legend ---
    cols_p = colorize(precision)
    cols_r = colorize(recall)
    cols_f = colorize(f1)

    rects1b = axes[1].bar(x - width, precision, width, color=cols_p)
    rects2b = axes[1].bar(x, recall, width, color=cols_r)
    rects3b = axes[1].bar(x + width, f1, width, color=cols_f)

    axes[1].set_ylabel("Score")
    axes[1].set_title("Per-Entity NER Evaluation (Colored by Performance)")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(entities, rotation=45, ha="right")

    # Color legend explaining green/orange/red
    color_handles = [
        Patch(facecolor="green", label="Good (≥ 0.7)"),
        Patch(facecolor="orange", label="Moderate (0.4–0.7)"),
        Patch(facecolor="red", label="Weak (< 0.4)")
    ]
    axes[1].legend(handles=color_handles, title="Performance band", loc="upper right")

    # Optional: numeric labels above bars
    if show_values:
        def autolabel(ax, rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f"{height:.2f}",
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8)
        # top
        autolabel(axes[0], rects1)
        autolabel(axes[0], rects2)
        autolabel(axes[0], rects3)
        # bottom
        autolabel(axes[1], rects1b)
        autolabel(axes[1], rects2b)
        autolabel(axes[1], rects3b)

    plt.tight_layout()
    plt.show()

#step2 confusion map

def plot_confusion_heatmap_entities(expected_file, prediction_file, id2label):
    """
    Plot a confusion matrix for NER predictions, excluding 'O', with annotated numbers and a colorbar.
    """
    # Load JSON files
    with open(expected_file) as f:
        expected = json.load(f)
    with open(prediction_file) as f:
        predicted = json.load(f)

    # Extract true and predicted labels, excluding 'O'
    true_labels, pred_labels = [], []
    for exp, pred in zip(expected, predicted):
        for t, p in zip(exp["ner_tags"], pred["ner_tags"]):
            t_label = id2label[t]
            p_label = id2label[p]
            if t_label != "O":  # skip non-entities
                true_labels.append(t_label)
                pred_labels.append(p_label)

    # Determine entity labels
    labels = sorted(set(true_labels) | set(pred_labels))

    
    #Compute confusion matrix to evaluate the accuracy of a classification.
    #https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html

    #### 1-Diagonal cells
    #These are the cases where the predicted entity matches the true entity.
    #Higher values (closer to 1, dark green in our colormap) indicate better performance for that entity type.
    #Example: If ORG row vs ORG column = 0.8 → 80% of organizations were correctly predicted.
    
    #### 2-Off-diagonal cells
    #These show misclassifications, i.e., the fraction of times a true entity of type X was predicted as type Y.
    #Higher values (closer to 1, red in our colormap) indicate frequent misclassifications.
    #Example: If DOCTOR row vs ORG column = 0.2 → 20% of doctor mentions were incorrectly predicted as organization.
    
    #### 3-Row-normalization
    #Each row sums to 1.0 (100% of that true entity type).
    #This means you can see how errors distribute per true entity, regardless of class frequency.
    
    cm = confusion_matrix(true_labels, pred_labels, labels=labels, normalize='true')

    # Plot heatmap
    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(
        cm,
        annot=True,
        fmt=".2f",
        xticklabels=labels,
        yticklabels=labels,
        cmap="RdYlGn_r",   # Green = high, Red = low
        linewidths=0.5,
        linecolor='gray',
        cbar=True
    )

    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("NER Confusion Matrix (Entities Only)")
    plt.tight_layout()
    plt.show()


def plot_confusion_heatmap_entities_multiple(file_all_expected, file_all_predicted, id2label):
    """
    all_expected / all_predicted: list of JSONs like {"tokens": [...], "ner_tags": [...]}
    id2label: dictionary mapping tag ids to tag names (e.g., 0: "O", 1: "B-ORG", etc.)
    """
    # --- Collect all true and predicted labels ---
    def plot_confusion_heatmap_chunks(true_labels, pred_labels, chunk_size=12):
        # Collapse B- and I-
        def simplify(l):
            return l.split("-", 1)[-1] if l != "O" else "O"
        true_labels = [simplify(l) for l in true_labels]
        pred_labels = [simplify(l) for l in pred_labels]

        labels = sorted(list(set(true_labels) | set(pred_labels)))
        cm = confusion_matrix(true_labels, pred_labels, labels=labels, normalize='true')

        # Plot in chunks
        for i in range(0, len(labels), chunk_size):
            sub_labels = labels[i:i+chunk_size]
            sub_cm = cm[i:i+chunk_size, i:i+chunk_size]

            plt.figure(figsize=(10, 8))
            sns.heatmap(sub_cm, annot=True, fmt=".2f",
                        xticklabels=sub_labels, yticklabels=sub_labels,
                        cmap="YlGnBu", cbar_kws={'label': 'Proportion'})
            plt.title(f"NER Confusion Matrix (Entities {i+1}–{i+len(sub_labels)})")
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            plt.tight_layout()
            plt.show()

    def simplify_label(label):
        if label == "O":
            return "O"
        # remove B- or I-
        return label.split("-", 1)[-1]

    with open(file_all_expected) as f:
        all_expected = json.load(f)

    with open(file_all_predicted) as f:
        all_predicted = json.load(f)



    true_labels, pred_labels = [], []
    for exp, pred in zip(all_expected, all_predicted):
        for t, p in zip(exp["ner_tags"], pred["ner_tags"]):
            true_labels.append(id2label[t])
            pred_labels.append(id2label[p])
    true_labels = [simplify_label(l) for l in true_labels]
    pred_labels = [simplify_label(l) for l in pred_labels]    


    plot_confusion_heatmap_chunks(true_labels, pred_labels, chunk_size=20)
    return


    # --- Filter out 'O' labels ---
    filtered_true = [t for t, p in zip(true_labels, pred_labels) if t != "O"]
    filtered_pred = [p for t, p in zip(true_labels, pred_labels) if t != "O"]

    # --- Unique entity labels (excluding 'O') ---
    labels = sorted(list(set(filtered_true) | set(filtered_pred)))

    # --- Compute confusion matrix ---
    cm = confusion_matrix(filtered_true, filtered_pred, labels=labels, normalize='true')

    # --- Plot heatmap ---
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt=".2f", xticklabels=labels, yticklabels=labels,
                cmap="YlGnBu", cbar_kws={'label': 'Proportion'})
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("NER Confusion Matrix (Normalized, 'O' excluded)")
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()


def plot_top_n_confusion_bars(file_all_expected, file_all_predicted, id2label, top_n=20):
    """
    all_expected / all_predicted: list of JSONs like {"tokens": [...], "ner_tags": [...]}
    id2label: dictionary mapping tag ids to tag names (e.g., 0: "O", 1: "B-ORG", etc.)
    top_n: number of most frequent misclassifications to display
    """
    from collections import Counter
    import matplotlib.patches as mpatches
      
    with open(file_all_expected) as f:
        all_expected = json.load(f)

    with open(file_all_predicted) as f:
        all_predicted = json.load(f)
    true_labels, pred_labels = [], []

    for exp, pred in zip(all_expected, all_predicted):
        for t, p in zip(exp["ner_tags"], pred["ner_tags"]):
            # Map ids to labels
            true_labels.append(id2label[t])
            pred_labels.append(id2label[p])

    # Filter out O
    filtered = [(t, p) for t, p in zip(true_labels, pred_labels) if t != "O"]

    # Merge B-/I- prefixes
    filtered = [(t.split('-')[-1], p.split('-')[-1]) for t, p in filtered]

    # Count occurrences
    counter = Counter(filtered)
    top_items = counter.most_common(top_n)

    labels = [f"{t} - {p}" for t, p in top_items]
    counts = [c for _, c in top_items]
  # Assign colors
    colors = []
    for t, p in [item[0] for item in top_items]:
        if t == p:
            colors.append('green')      # correct
        elif p == 'O':
            colors.append('yellow')     # missed entity
        else:
            colors.append('red')        # wrong label
    # Plot
    plt.figure(figsize=(12,6))
    plt.bar(labels, counts, color=colors)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Count")
    plt.title(f"Top {top_n} Confusions (B/I merged, O excluded)")


        # Add legend
    green_patch = mpatches.Patch(color='green', label='Correct')
    yellow_patch = mpatches.Patch(color='yellow', label='Missed (Pred=O)')
    red_patch = mpatches.Patch(color='red', label='Wrong Label')
    plt.legend(handles=[green_patch, yellow_patch, red_patch], loc='upper right')
    plt.tight_layout()
    plt.show()

#step 3 train loss

def plot_train_loss_for_epoch(history_file):
    """
1. Training Loss (usually a downward curve)
    Y-axis: Loss value (lower is better).
    X-axis: Epochs.

    Interpretation:

    If loss decreases steadily, the model is learning and fitting the data.
    If loss plateaus, the model may have reached its learning capacity for this setup.
    If loss increases, the learning rate may be too high or the model is overfitting/unstable.

2. Evaluation F1 (usually an upward curve)
    Y-axis: F1-score (0–1, higher is better).
    X-axis: Epochs.

    Interpretation:

    Increasing F1 → the model is improving on the validation set.
    Plateauing F1 → the model may have learned as much as it can; additional epochs may not help.
    Decreasing F1 while loss decreases → overfitting (the model fits training data but generalizes poorly).

3. Comparing curves

    Ideally, training loss decreases while evaluation F1 increases.
    A gap between training loss and evaluation F1:
    Small gap → good generalization.
    Large gap → potential overfitting.
4. Practical example
    
    Suppose after 3 epochs:
    Train loss: 0.8 → 0.4 → 0.3
    Eval F1: 0.55 → 0.65 → 0.66
    Interpretation: the model is learning well, and F1 is improving. If F1 stopped increasing while loss decreased, you might stop training or adjust parameters.

    """


    with open(history_file) as f:
        history = json.load(f)
    # Extract loss and F1 per epoch
    train_epochs = [log['epoch'] for log in history if 'loss' in log and 'eval_loss' not in log]
    train_loss = [log['loss'] for log in history if 'loss' in log and 'eval_loss' not in log]

    eval_epochs = [log['epoch'] for log in history if 'eval_f1' in log]
    eval_f1 = [log['eval_f1'] for log in history if 'eval_f1' in log]

    plt.figure(figsize=(8,5))
    plt.plot(train_epochs, train_loss, label="Train Loss", color='blue', marker='o')
    plt.plot(eval_epochs, eval_f1, label="Eval F1", color='orange', marker='x')
    plt.xlabel("Epoch")
    plt.ylabel("Metric")
    plt.title("Training Loss & Evaluation F1 per Epoch")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_train_loss_as_table(history_file):

    with open(history_file) as f:
        history = json.load(f)

    # Extract per-step training loss
    train_loss = [log["loss"] for log in history if "loss" in log and "eval_loss" not in log]
    train_epoch = [log["epoch"] for log in history if "loss" in log and "eval_loss" not in log]

    # Extract per-epoch eval metrics
    eval_f1 = [h["eval_f1"] for h in history if "eval_f1" in h]
    eval_epoch = [h["epoch"] for h in history if "eval_f1" in h]
    eval_precision = [h["eval_precision"] for h in history if "eval_f1" in h]
    eval_recall = [h["eval_recall"] for h in history if "eval_f1" in h]

    # Plot
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(train_epoch, train_loss, marker='o', label="Train Loss")
    ax.plot(eval_epoch, eval_f1, marker='x', label="Eval F1")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Metric")
    ax.set_title("Training Metrics per Epoch")
    ax.grid(True)
    ax.legend()

    # Add table at the bottom
    cell_text = []
    for e, loss, f1, p, r in zip(eval_epoch, train_loss[:len(eval_epoch)], eval_f1, eval_precision, eval_recall):
        cell_text.append([f"{e:.2f}", f"{loss:.4f}", f"{p:.3f}", f"{r:.3f}", f"{f1:.3f}"])

    columns = ["Epoch", "Train Loss", "Precision", "Recall", "F1"]
    plt.table(cellText=cell_text, colLabels=columns, cellLoc="center", loc="bottom", bbox=[0, -0.35, 1, 0.25])

    plt.subplots_adjust(bottom=0.3)  # make space for table
    plt.show()


def plot_train_eval_metrics(history_file):
    with open(history_file) as f:
        history = json.load(f)

    # --- Training loss ---
    train_epochs = [log['epoch'] for log in history if 'loss' in log and 'eval_loss' not in log]
    train_loss = [log['loss'] for log in history if 'loss' in log and 'eval_loss' not in log]

    # --- Deduplicate evaluation logs (keep last per epoch) ---
    eval_by_epoch = defaultdict(dict)
    for log in history:
        if 'eval_f1' in log:
            epoch = log['epoch']
            eval_by_epoch[epoch] = log  # overwrites → keeps last per epoch

    eval_epochs = sorted(eval_by_epoch.keys())
    eval_loss = [eval_by_epoch[e]['eval_loss'] for e in eval_epochs]
    eval_precision = [eval_by_epoch[e]['eval_precision'] for e in eval_epochs]
    eval_recall = [eval_by_epoch[e]['eval_recall'] for e in eval_epochs]
    eval_f1 = [eval_by_epoch[e]['eval_f1'] for e in eval_epochs]

    # --- Plot ---
    fig, ax1 = plt.subplots(figsize=(10,6))

    # Training loss
    ax1.plot(train_epochs, train_loss, 'b-o', label='Train Loss')
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Train Loss", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Evaluation metrics
    ax2 = ax1.twinx()
    ax2.plot(eval_epochs, eval_loss, color='purple', marker='d', label='Eval Loss')
    # ax2.plot(eval_epochs, eval_precision, color='green', marker='x', label='Eval Precision')
    # ax2.plot(eval_epochs, eval_recall, color='red', marker='s', label='Eval Recall')
    ax2.plot(eval_epochs, eval_f1, color='orange', marker='^', label='Eval F1')

    ax2.set_ylabel("Evaluation Metrics", color='black')
    ax2.tick_params(axis='y', labelcolor='black')

    # Legend
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='center right')

    plt.title("Training Loss & Evaluation Metrics per Epoch")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":

    expected_file = "./expected/report.json"
    pred_file = "./predictions/report.json"
    history_file = './models/gbert-base/training_history.json'
    #calculate_entity_score_for_ner_data_predicted(expected_file=expected_file, predicted_file=pred_file)
    # plot_confusion_heatmap_entities(
    # expected_file=expected_file,
    # prediction_file=pred_file, id2label=ID2LABEL
    # )
    #plot_train_loss_for_epoch(history_file)
    #plot_train_eval_metrics(history_file)

    #plot_confusion_heatmap_entities_multiple(file_all_expected='./data/all_data.json', file_all_predicted='./output/ner_predictions.json', id2label=ID2LABEL)
    plot_top_n_confusion_bars(file_all_expected='./data/all_data.json', file_all_predicted='./output/ner_predictions.json', id2label=ID2LABEL)