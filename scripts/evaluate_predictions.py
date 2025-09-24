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

def __plot_entity_scores_bars_comparison(entity_scores, show_values=False):
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
    __plot_entity_scores_bars_comparison(entity_scores=entity_scores)

def calculate_entity_score_for_ner_data_predicted2(expected_file, predicted_file):
    from seqeval.metrics import precision_score, recall_score, f1_score, classification_report
    import json
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
    for sent in true_labels:
        for label in sent:
            if label != "O":
                all_entities.add(label.split("-")[-1])

    # Compute per-entity metrics
    entity_scores = {}
    for ent in all_entities:
        # Mask other entities as "O"
        true_masked = [[l if l.endswith(ent) else "O" for l in sent] for sent in true_labels]
        pred_masked = [[l if l.endswith(ent) else "O" for l in sent] for sent in pred_labels]

        # Compute precision, recall, F1
        entity_prec = precision_score(true_masked, pred_masked)
        entity_rec = recall_score(true_masked, pred_masked)
        entity_f1 = f1_score(true_masked, pred_masked)

        entity_scores[ent] = {
            "precision": entity_prec,
            "recall": entity_rec,
            "f1": entity_f1
        }

    # Compute overall micro-averaged metrics across all entities
    overall_prec = precision_score(true_labels, pred_labels)
    overall_rec = recall_score(true_labels, pred_labels)
    overall_f1 = f1_score(true_labels, pred_labels)

    entity_scores["OVERALL"] = {
        "precision": overall_prec,
        "recall": overall_rec,
        "f1": overall_f1
    }

    # Print results
#    print("Entity-level scores:", entity_scores)

    # Plotting (if you have your function)
    __plot_entity_scores_bars_comparison(entity_scores=entity_scores)


#step2 confusion map  to be checked

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



#step 3 evaluation model trainingtrain loss


def plot_final_training_summary(history_file):
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
    train_epochs = [log['epoch'] for log in history if 'loss' in log and 'eval_loss' not in log]
    train_loss = [log['loss'] for log in history if 'loss' in log and 'eval_loss' not in log]

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
    # plot_train_loss_for_epoch(history_file)
    # plot_train_eval_metrics(history_file)
    # plot_train_loss_as_table(history_file)





    # evaluate model
    plot_final_training_summary(history_file)

    #evaluate prediction entity_score

    calculate_entity_score_for_ner_data_predicted2(expected_file='./data/all_data.json', predicted_file='./output/ner_predictions.json', )



    plot_confusion_heatmap_entities_multiple(file_all_expected='./data/all_data.json', file_all_predicted='./output/ner_predictions.json', id2label=ID2LABEL)
    plot_top_n_confusion_bars(file_all_expected='./data/all_data.json', file_all_predicted='./output/ner_predictions.json', id2label=ID2LABEL, top_n=40)