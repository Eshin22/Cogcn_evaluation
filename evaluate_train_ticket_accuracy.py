import json
import os
import numpy as np
from collections import Counter, defaultdict
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score
from scipy.optimize import linear_sum_assignment
from evaluate_metrics import parse_dataset_classes

def evaluate_train_ticket_accuracy():
    info = parse_dataset_classes("dataset/train-ticket")
    with open("dataset/train-ticket/decomposition.json", "r", encoding="utf-8") as f:
        decomp = json.load(f)

    classes = sorted(list(info.keys()))
    class_to_cluster = {}
    for cluster in decomp:
        cid = cluster["cluster_id"]
        for c in cluster["classes"]:
            class_to_cluster[c] = cid

    gt_services = []
    pred_clusters = []

    for c in classes:
        fp = info[c]["filepath"].replace("\\", "/")
        parts = fp.split("/")
        svc = "unknown"
        for p in parts:
            if p.startswith("ts-") or p == "old-docs":
                svc = p
                break
        gt_services.append(svc)
        pred_clusters.append(class_to_cluster.get(c, -1))

    # Metrics
    nmi = normalized_mutual_info_score(gt_services, pred_clusters)
    ari = adjusted_rand_score(gt_services, pred_clusters)

    unique_gt = sorted(list(set(gt_services)))
    unique_pred = sorted(list(set(pred_clusters)))
    gt_map = {s: i for i, s in enumerate(unique_gt)}
    pred_map = {c: i for i, c in enumerate(unique_pred)}

    y_true_idx = [gt_map[s] for s in gt_services]
    y_pred_idx = [pred_map[c] for c in pred_clusters]

    cost_matrix = np.zeros((len(unique_gt), len(unique_pred)))
    for gt_i, pred_i in zip(y_true_idx, y_pred_idx):
        cost_matrix[gt_i, pred_i] -= 1

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    correct_matches = int(-cost_matrix[row_ind, col_ind].sum())
    accuracy = correct_matches / len(classes)

    # Calculate MoJoFM
    # MoJo Distance measures minimum Move/Join operations to transform predicted into ground truth
    # MoJoFM = 100 * (1 - (mno(A, B) / max(mno(A_null, B))))
    # Approximation of MoJo Reachability / Fidelity:
    total_classes = len(classes)
    mojo_moves = 0
    for gt_idx, pred_idx in zip(row_ind, col_ind):
        gt_name = unique_gt[gt_idx]
        pred_c = unique_pred[pred_idx]
        # classes in this cluster not matching gt_name
        cluster_classes = [c for c in classes if class_to_cluster.get(c) == pred_c]
        non_matching = sum(1 for c in cluster_classes if gt_services[classes.index(c)] != gt_name)
        mojo_moves += non_matching

    # Max moves = total_classes
    mojofm = max(0.0, 100.0 * (1.0 - (mojo_moves / total_classes)))

    # Cluster by Cluster breakdown
    cluster_stats = []
    for cluster in decomp:
        cid = cluster["cluster_id"]
        c_classes = cluster["classes"]
        c_svcs = [gt_services[classes.index(cls)] for cls in c_classes]
        svc_counts = Counter(c_svcs)
        top_svc, top_cnt = svc_counts.most_common(1)[0]
        purity = top_cnt / len(c_classes)
        
        cluster_stats.append({
            "cluster_id": cid,
            "size": len(c_classes),
            "dominant_service": top_svc,
            "matched_classes": top_cnt,
            "purity": purity,
            "service_composition": dict(svc_counts.most_common(4))
        })

    # Ground-truth service recovery breakdown (for top microservices)
    gt_service_stats = []
    gt_counts = Counter(gt_services)
    for svc, total_svc_classes in gt_counts.most_common(15):
        svc_cls_indices = [i for i, s in enumerate(gt_services) if s == svc]
        assigned_clusters = [pred_clusters[i] for i in svc_cls_indices]
        top_cluster, top_cluster_cnt = Counter(assigned_clusters).most_common(1)[0]
        retention = top_cluster_cnt / total_svc_classes
        gt_service_stats.append({
            "service_name": svc,
            "total_classes": total_svc_classes,
            "assigned_cluster": top_cluster,
            "retained_classes": top_cluster_cnt,
            "retention_rate": retention
        })

    output = {
        "dataset": "train-ticket",
        "total_classes": total_classes,
        "ground_truth_services_count": len(unique_gt),
        "decomposed_clusters_count": len(unique_pred),
        "accuracy_metrics": {
            "NMI": round(float(nmi), 4),
            "ARI": round(float(ari), 4),
            "Hungarian_Bipartite_Accuracy": round(float(accuracy), 4),
            "MoJoFM_Percentage": round(float(mojofm), 2)
        },
        "top_ground_truth_services_recovery": gt_service_stats,
        "decomposed_clusters_breakdown": cluster_stats
    }

    print(json.dumps(output, indent=2))
    
    with open("dataset/train-ticket/service_accuracy.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    evaluate_train_ticket_accuracy()
