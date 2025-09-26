import json
import os
import sys
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix
from collections import defaultdict,Counter
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from seqeval.metrics import precision_score, recall_score, f1_score, classification_report

 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from scripts.config import LABEL_LIST, ID2LABEL

#step 1 entity score

def __plot_entity_scores_bars_comparison_ner_data(entity_scores, show_values=False):

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
    support_counts = [entity_scores[e]["support"] for e in entities]

    x = np.arange(len(entities))
    width = 0.25

    def colorize(values):
        colors = []
        for v in values:
            if v >= 0.7:
                colors.append("green")
            elif v >= 0.4:
                colors.append("orange")
            else:
                colors.append("red")
        return colors

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)  # smaller height

    # --- Subplot 1: Plain chart ---
    rects1 = axes[0].bar(x - width, precision, width, label="Precision", color="C0")
    rects2 = axes[0].bar(x, recall, width, label="Recall", color="C1")
    rects3 = axes[0].bar(x + width, f1, width, label="F1", color="C2")

    axes[0].set_ylabel("Score")
    axes[0].set_title("Per-Entity NER Evaluation (Plain)")
    axes[0].set_ylim(0, 1.15)  # more space on top
    axes[0].legend(loc="upper right")

    # Add support counts above middle bar only (recall)
    for i, sup in enumerate(support_counts):
        axes[0].text(x[i], recall[i] + 0.05, f"{sup}",
                     ha="center", va="bottom", fontsize=8)

    # --- Subplot 2: Color-coded chart ---
    cols_p = colorize(precision)
    cols_r = colorize(recall)
    cols_f = colorize(f1)

    rects1b = axes[1].bar(x - width, precision, width, color=cols_p)
    rects2b = axes[1].bar(x, recall, width, color=cols_r)
    rects3b = axes[1].bar(x + width, f1, width, color=cols_f)

    axes[1].set_ylabel("Score")
    axes[1].set_title("Per-Entity NER Evaluation (Colored by Performance)")
    axes[1].set_ylim(0, 1.15)  # more space
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(entities, rotation=45, ha="right")

    # Add support counts above recall bar only
    for i, sup in enumerate(support_counts):
        axes[1].text(x[i], recall[i] + 0.05, f"{sup}",
                     ha="center", va="bottom", fontsize=8)

    # Legend for performance bands
    color_handles = [
        Patch(facecolor="green", label="Good (≥ 0.7)"),
        Patch(facecolor="orange", label="Moderate (0.4–0.7)"),
        Patch(facecolor="red", label="Weak (< 0.4)")
    ]
    axes[1].legend(handles=color_handles, title="Performance band", loc="upper right")

    # Optional numeric labels
    if show_values:
        def autolabel(ax, rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f"{height:.2f}",
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8)
        autolabel(axes[0], rects1)
        autolabel(axes[0], rects2)
        autolabel(axes[0], rects3)
        autolabel(axes[1], rects1b)
        autolabel(axes[1], rects2b)
        autolabel(axes[1], rects3b)

    plt.tight_layout()
    plt.show()


def calculate_entity_score_for_ner_data_predicted(expected_file, predicted_file):

    # Load JSON files
    with open(expected_file) as f:
        expected_data = json.load(f)
    with open(predicted_file) as f:
        predicted_data = json.load(f)

    # Check number of sentences
    if len(expected_data) != len(predicted_data):
        raise ValueError(f"Number of sentences mismatch: {len(expected_data)} vs {len(predicted_data)}")

    # Convert numeric tags to string labels and check token alignment
    true_labels, pred_labels = [], []
    for i, (exp, pred) in enumerate(zip(expected_data, predicted_data)):
        if len(exp["ner_tags"]) != len(pred["ner_tags"]):
            raise ValueError(f"Sentence {i} token length mismatch: {len(exp['ner_tags'])} vs {len(pred['ner_tags'])}")
        true_labels.append([ID2LABEL[t] for t in exp["ner_tags"]])
        pred_labels.append([ID2LABEL[p] for p in pred["ner_tags"]])

    # Identify all entity types
    all_entities = set()
    entity_support = {}  
    for sent in true_labels:
        for label in sent:
            if label != "O":
                ent_type = label.split("-")[-1]
                all_entities.add(ent_type)
                entity_support[ent_type] = entity_support.get(ent_type, 0) + 1

    # Compute per-entity metrics
    entity_scores = {}
    for ent in all_entities:
        # Mask other entities as "O"
        true_masked = [[l if l.endswith(ent) else "O" for l in sent] for sent in true_labels]
        pred_masked = [[l if l.endswith(ent) else "O" for l in sent] for sent in pred_labels]

        # Compute precision, recall, F1
        entity_prec = precision_score(true_masked, pred_masked) if any(l != "O" for sent in pred_masked for l in sent) else 0.0
        entity_rec = recall_score(true_masked, pred_masked)
        entity_f1 = f1_score(true_masked, pred_masked)

        entity_scores[ent] = {
            "precision": entity_prec,
            "recall": entity_rec,
            "f1": entity_f1,
            "support": entity_support.get(ent, 0)  
        }

    # Compute overall micro-averaged metrics across all entities
    overall_prec = precision_score(true_labels, pred_labels)
    overall_rec = recall_score(true_labels, pred_labels)
    overall_f1 = f1_score(true_labels, pred_labels)
    overall_support = sum(entity_support.values())
    entity_scores["OVERALL"] = {
        "precision": overall_prec,
        "recall": overall_rec,
        "f1": overall_f1,
        "support": overall_support 
    }

    __plot_entity_scores_bars_comparison_ner_data(entity_scores=entity_scores)


#step2 confusion map  to be checked

def plot_confusion_heatmap_top_entities_ner_data(file_all_expected, file_all_predicted, id2label, top_n=30, print_error= False):
    """
    Plot confusion heatmap for the top-N most confused entities + show TP/FP/FN counts.

    Args:
        file_all_expected: path to JSON with gold labels
        file_all_predicted: path to JSON with predicted labels
        id2label: dictionary mapping tag ids to tag names
        top_n: number of most confused entities to display
    """
    def simplify_label(label):
        return "O" if label == "O" else label.split("-", 1)[-1]

    # Load data
    with open(file_all_expected) as f:
        all_expected = json.load(f)
    with open(file_all_predicted) as f:
        all_predicted = json.load(f)

    # Collect true and predicted labels
    true_labels, pred_labels = [], []
    for exp, pred in zip(all_expected, all_predicted):
        for t, p in zip(exp["ner_tags"], pred["ner_tags"]):
            true_labels.append(simplify_label(id2label[t]))
            pred_labels.append(simplify_label(id2label[p]))

    # Build confusion matrix
    labels = sorted(list(set(true_labels) | set(pred_labels)))
    cm = confusion_matrix(true_labels, pred_labels, labels=labels)

    # Rank entities by confusion (off-diagonal errors)
    confusion_scores = {
        label: (cm[i].sum() - cm[i, i]) + (cm[:, i].sum() - cm[i, i])
        for i, label in enumerate(labels) if label != "O"
    }
    top_entities = sorted(confusion_scores, key=confusion_scores.get, reverse=True)[:top_n]

    # Restrict to top entities (+O if exists)
    selected_labels = top_entities# + (["O"] if "O" in labels else [])
    idx = [labels.index(l) for l in selected_labels]
    sub_cm = cm[np.ix_(idx, idx)]

    # Normalize for heatmap
    sub_cm_normalized = sub_cm.astype("float") / sub_cm.sum(axis=1, keepdims=True)
    sub_cm_normalized = np.nan_to_num(sub_cm_normalized)

    # --- Plot ---
    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(
        sub_cm_normalized,
        annot=True,
        fmt=".2f",
        xticklabels=selected_labels,
        yticklabels=selected_labels,
        cmap="YlGnBu",            # soft blue for readability
        cbar_kws={'label': 'Proportion'},
    )
   # Draw thicker borders only for non-zero cells
    for i in range(sub_cm_normalized.shape[0]):
        for j in range(sub_cm_normalized.shape[1]):
            if sub_cm_normalized[i, j] > 0.009:
                ax.add_patch(plt.Rectangle(
                    (j, i), 1, 1, fill=False, edgecolor="#E93F0C", lw=1.2
                ))

    plt.title(f"NER Confusion Matrix – Top {top_n} Confused Entities")
    plt.xlabel("Predicted")
    plt.ylabel("Expected")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

    if print_error:
        # --- TP/FP/FN per entity ---
        print("\nEntity-level error analysis:")
        prec, rec, f1, support = precision_recall_fscore_support(
            true_labels, pred_labels, labels=labels, zero_division=0
        )
        for lbl, p, r, f, s in zip(labels, prec, rec, f1, support):
            tp = int(round(r * s))   # true positives = recall * support
            fn = s - tp              # false negatives
            fp = int(round(tp * (1/p - 1))) if p > 0 else 0  # false positives
            print(f"{lbl:10s} | TP={tp:4d}  FP={fp:4d}  FN={fn:4d}  "
                f"Prec={p:.2f}  Rec={r:.2f}  F1={f:.2f}")


def plot_confusion_bars_top_entities_ner_data(file_all_expected, file_all_predicted, id2label, top_n=30, for_latex=False):
    """
    Plot top-N confusion pairs and (optionally) generate a LaTeX-ready caption.
    """

    with open(file_all_expected) as f:
        all_expected = json.load(f)
    with open(file_all_predicted) as f:
        all_predicted = json.load(f)

    true_labels, pred_labels = [], []
    for exp, pred in zip(all_expected, all_predicted):
        for t, p in zip(exp["ner_tags"], pred["ner_tags"]):
            true_labels.append(id2label[t])
            pred_labels.append(id2label[p])

    # Filter out "O"
    filtered = [(t, p) for t, p in zip(true_labels, pred_labels) if t != "O"]

    # Merge B-/I- prefixes
    filtered = [(t.split('-')[-1], p.split('-')[-1]) for t, p in filtered]

    # Count occurrences
    counter = Counter(filtered)
    top_items = counter.most_common(top_n)

    #labels = [f"{t} → {p}" for t, p in top_items]
    counts = [c for _, c in top_items]

    # Convert to percentages
    total = sum(counts)
    counts_percent = [c / total * 100 for c in counts]

    # Assign colors
    colors = []
    labels = []
    counts = []
    for (t, p), c in top_items:
        counts.append(c)
        if t == p:
            colors.append("green")   # correct
            labels.append(f"{t} ({c})")
        elif p == "O":
            colors.append("yellow")  # missed entity
            labels.append(f"{t} → {p} ({c})")
        else:
            colors.append("red")     # wrong label
            labels.append(f"{t} → {p} ({c})")

    # --- Plot ---
    plt.figure(figsize=(10, 6))
    bars = plt.barh(labels, counts_percent, color=colors)
    plt.xlabel("Percentage of errors (%)")
    plt.ylabel("True → Predicted",fontsize=8)
    plt.title(f"Top {top_n} Confusions (B/I merged, O excluded)")
    plt.gca().invert_yaxis()
    for bar, c in zip(bars, counts):
        plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                 f'{c}', va='center', fontsize=8)
    # Legend
    green_patch = mpatches.Patch(color="green", label="Correct")
    yellow_patch = mpatches.Patch(color="yellow", label="Missed (Pred=O)")
    red_patch = mpatches.Patch(color="red", label="Wrong Label")
    plt.legend(handles=[green_patch, yellow_patch, red_patch], loc="lower right")
    plt.tight_layout()
    plt.show()

    # --- LaTeX caption ---
    if for_latex:
        caption = (
            f"Figure X shows the top {top_n} confusion pairs from the NER evaluation. "
            "Bars represent the relative frequency of errors between reference and predicted entity types. "
            "Yellow bars indicate missed entities (predicted as `O`), red bars indicate label confusions "
            "(predicted as another entity type), and green bars indicate correct predictions. "
            "This analysis highlights common sources of error such as boundary ambiguity and clinically "
            "relevant misclassifications (e.g., DIAGNOSIS vs SYMPTOM)."
        )
        print("\n--- LaTeX-ready caption ---\n")
        print("\\caption{" + caption + "}")


#step 3 evaluation model trainingtrain loss

def plot_model_training_summary(history_file):
    """
    Model Training & Evaluation Metrics

    1. Training Loss (train_loss) Measures how well the model is fitting the training data. Lower is better.
    - Definition: Error on the training dataset.
    - Y-axis: Loss value (lower is better).
    - X-axis: Epochs.
    - Interpretation:
        * If loss decreases steadily → the model is learning.
        * If loss plateaus → model has reached its capacity for this setup.
        * If loss increases → possible instability (learning rate too high) 
            or severe overfitting.

    2. Evaluation Loss (eval_loss)
    - Definition: Error on the validation dataset (unseen data).
    - Y-axis: Loss value (lower is better).
    - Interpretation:
        * Decreasing eval_loss → the model generalizes better.
        * Plateauing eval_loss → model may not improve further.
        * Increasing eval_loss while train_loss decreases → overfitting risk.

    3. Evaluation F1 (eval_f1). Higher is better.
    - Definition: Harmonic mean of precision & recall on validation data.
    - Y-axis: Score from 0–1 (higher is better).
    - Interpretation:
        * Increasing F1 → better entity recognition.
        * Plateauing F1 → more epochs unlikely to help.
        * Decreasing F1 while train_loss decreases → overfitting.

    4. Comparing the curves
    - Ideal case: 
        train_loss ↓, eval_loss ↓, eval_f1 ↑
    - Signs of overfitting:
        train_loss ↓, eval_loss ↑, eval_f1 ↓
    - Good generalization:
        small gap between train_loss and eval_loss + steadily increasing eval_f1.
    - Early stopping:
        if eval_f1 stops improving or starts dropping, training should stop.

    5. Practical example
    Epoch 1 → train_loss=0.8, eval_loss=0.9, eval_f1=0.55
    Epoch 2 → train_loss=0.4, eval_loss=0.6, eval_f1=0.65
    Epoch 3 → train_loss=0.3, eval_loss=0.58, eval_f1=0.66
    Interpretation: the model is learning, eval_loss is stable, and F1 is improving.
    Training could stop if F1 does not improve further.
    """


    with open(history_file) as f:
        history = json.load(f)

    # --- Training loss ---

    train_by_epoch = defaultdict(list)

    for log in history:
        if 'loss' in log and 'eval_loss' not in log:  # only training logs
            train_by_epoch[log['epoch']].append(log['loss'])

    # Take the average (or the last) loss per epoch
    train_epochs = sorted(train_by_epoch.keys())
    train_loss = [sum(v)/len(v) for v in train_by_epoch.values()]  # average per epoch


    # --- Deduplicate evaluation logs (keep last per epoch) ---
    eval_by_epoch = defaultdict(dict)
    for log in history:
        if 'eval_f1' in log:
            eval_by_epoch[log['epoch']] = log  # keep last per epoch

    eval_epochs = sorted(eval_by_epoch.keys())
    eval_loss = [eval_by_epoch[e]['eval_loss'] for e in eval_epochs]
    eval_f1 = [eval_by_epoch[e]['eval_f1'] for e in eval_epochs]

    # --- Plot ---
    fig, ax1 = plt.subplots(figsize=(10,6))

    # Train loss
    ax1.plot(train_epochs, train_loss, marker='o', color='blue', label='Train Loss')
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Train Loss", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Eval metrics
    ax2 = ax1.twinx()
    ax2.plot(eval_epochs, eval_loss, marker='d', color='purple', label='Eval Loss')
    ax2.plot(eval_epochs, eval_f1, marker='^', color='orange', label='Eval F1')

    ax2.set_ylabel("Eval Metrics", color='black')
    ax2.tick_params(axis='y', labelcolor='black')

    # Legend
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='center right')

    plt.title("Training Summary: Loss & F1 per Epoch")
    plt.grid(True)

    # --- Table with values ---
    cell_text = []
    for e, tl, el, f1 in zip(eval_epochs, train_loss[:len(eval_epochs)], eval_loss, eval_f1):
        cell_text.append([f"{e:.0f}", f"{tl:.4f}", f"{el:.4f}", f"{f1:.3f}"])

    columns = ["Epoch", "Train Loss", "Eval Loss", "Eval F1"]
    plt.table(cellText=cell_text, colLabels=columns, cellLoc="center", 
              loc="bottom", bbox=[0, -0.35, 1, 0.25])

    plt.subplots_adjust(bottom=0.3)  # space for table
    
    #plt.savefig("training_summary.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":

    expected_file = './data/all_data.json'
    pred_file = './output/ner_predictions.json'
    history_file = './models/gbert-base/training_history.json'

    #1 entity score
    #calculate_entity_score_for_ner_data_predicted(expected_file=expected_file, predicted_file=pred_file)

    #2 confusion matrix
    plot_confusion_heatmap_top_entities_ner_data(file_all_expected = expected_file, file_all_predicted = pred_file, id2label = ID2LABEL, top_n = 30)
    plot_confusion_bars_top_entities_ner_data(file_all_expected = expected_file, file_all_predicted = pred_file, id2label = ID2LABEL, top_n = None, for_latex=False)

    #3 evaluate model, training_loss
    plot_model_training_summary(history_file)
