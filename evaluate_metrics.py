import os
os.environ["LOKY_MAX_CPU_COUNT"] = "4"
os.environ["OMP_NUM_THREADS"] = "4"
import warnings
warnings.filterwarnings("ignore")

import sys
import re
import glob
import math
import json
import argparse
import numpy as np
import scipy.sparse as sp
import torch
import torch.nn as nn
from torch import optim
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer

# Ensure networkx compatibility for official cogcn modules without modifying cogcn_repo
import networkx as nx
if not hasattr(nx, "from_numpy_matrix"):
    nx.from_numpy_matrix = nx.from_numpy_array

# Import directly from official cogcn_repo modules without modifying them
COGCN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "cogcn_repo", "cogcn"))
if COGCN_PATH not in sys.path:
    sys.path.insert(0, COGCN_PATH)

from model import GCNAE
from optimizer import compute_structure_loss, compute_attribute_loss, update_o1, update_o2
from kmeans import Clustering
from utils import preprocess_graph


DATASET_METADATA = {
    "spring-petclinic": {
        "title": "Spring PetClinic",
        "desc": "Classic Java Spring enterprise monolithic benchmark application for microservice decomposition, architecture recovery, and refactoring studies.",
        "repo": "spring-projects/spring-petclinic",
        "lang": "Java / Spring Boot"
    },
    "jpetstore-6": {
        "title": "JPetStore-6",
        "desc": "Reference e-commerce sample web application built with MyBatis, Spring, and JavaServer Pages.",
        "repo": "mybatis/jpetstore-6",
        "lang": "Java / MyBatis"
    },
    "acmeair": {
        "title": "AcmeAir",
        "desc": "Fictitious airline flight booking system benchmark originally created by IBM for cloud, monolithic, and microservice refactoring benchmarks.",
        "repo": "acmeair/acmeair",
        "lang": "Java / Java EE"
    },
    "plantsbywebsphere": {
        "title": "PlantsByWebSphere",
        "desc": "IBM sample enterprise e-commerce application demonstrating Java EE / WebSphere enterprise computing patterns.",
        "repo": "WASdev/sample.plantsbywebsphere",
        "lang": "Java / WebSphere"
    },
    "daytrader7": {
        "title": "DayTrader 7",
        "desc": "Large-scale financial stock trading application based on the Apache Geronimo DayTrader benchmark suite.",
        "repo": "WASdev/sample.daytrader7",
        "lang": "Java / Java EE 7"
    },
    "jforum": {
        "title": "JForum",
        "desc": "Full-featured, high-traffic discussion board / bulletin board system written in Java.",
        "repo": "rafaelsteil/jforum",
        "lang": "Java"
    },
    "javafx-pos": {
        "title": "JavaFX Point-of-Sales",
        "desc": "Interactive desktop point-of-sale management system built with JavaFX and SQLite.",
        "repo": "mhrimaz/JavaFX-POS",
        "lang": "Java / JavaFX"
    },
    "springblog": {
        "title": "SpringBlog",
        "desc": "Modern blogging web application platform built on Spring Boot, Thymeleaf, and Spring Security.",
        "repo": "RameshMF/spring-boot-tutorial",
        "lang": "Java / Spring Boot"
    },
    "roller": {
        "title": "Apache Roller",
        "desc": "Industrial-scale enterprise Java blog server powering large-scale production multi-user blogs.",
        "repo": "apache/roller",
        "lang": "Java / Apache Roller"
    },
    "bear-board": {
        "title": "Bear Board",
        "desc": "Microblogging and social timeline collaboration service built on Spring MVC, Spring Data, and Redis.",
        "repo": "bear-board/bear-board",
        "lang": "Java / Spring MVC"
    },
    "train-ticket": {
        "title": "Train Ticket",
        "desc": "Comprehensive industrial-scale benchmark suite for railway ticket booking, payment, routing, and passenger management.",
        "repo": "FudanSELab/train-ticket",
        "lang": "Java / Spring Cloud"
    },
    "dietapp": {
        "title": "DietApp",
        "desc": "Nutritional intake and health goal tracking application built with C# ASP.NET MVC and Entity Framework.",
        "repo": "dietapp/dietapp",
        "lang": "C# (.NET / ASP.NET MVC)"
    },
    "cics-genapp": {
        "title": "IBM CICS GenApp",
        "desc": "General Insurance Enterprise Application benchmark written in COBOL for IBM CICS transaction processing systems.",
        "repo": "IBM/cics-genapp",
        "lang": "COBOL / IBM CICS"
    },
    "autocare-nepal": {
        "title": "AutoCare Nepal",
        "desc": "Automobile maintenance, servicing, inventory, and customer invoicing workflow application.",
        "repo": "autocare/autocare-nepal",
        "lang": "Java / Spring Boot"
    },
    "pharmacy": {
        "title": "Pharmacy Management System",
        "desc": "Pharmacy inventory, prescription handling, medicine billing, and supplier supply chain software.",
        "repo": "pharmacy/pharmacy-system",
        "lang": "Java / Spring Boot"
    }
}


def camel_case_split(str_val):
    words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', str_val)
    return set([w.lower() for w in words if len(w) > 1])


def parse_dataset_classes(dataset_path):
    source_files = sorted(
        glob.glob(os.path.join(dataset_path, "**/*.java"), recursive=True) +
        glob.glob(os.path.join(dataset_path, "**/*.cs"), recursive=True) +
        glob.glob(os.path.join(dataset_path, "**/*.cbl"), recursive=True) +
        glob.glob(os.path.join(dataset_path, "**/*.cpy"), recursive=True)
    )
    source_files = [f for f in source_files if not f.endswith("AssemblyInfo.cs")]
    class_info = {}

    for filepath in source_files:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        filename = os.path.basename(filepath)

        if filename.endswith(".cbl") or filename.endswith(".cpy"):
            prog_match = re.search(r'PROGRAM-ID\.\s*([\w\-]+)', content, re.IGNORECASE)
            unit_name = prog_match.group(1).upper() if prog_match else filename.split('.')[0].upper()
            
            prefix = unit_name[:4]
            domain_map = {
                "LGAC": "account",
                "LGAP": "policy_add",
                "LGDP": "policy_delete",
                "LGIC": "customer_inquire",
                "LGIP": "policy_inquire",
                "LGUC": "customer_update",
                "LGUP": "policy_update",
                "LGST": "stats",
                "LGTE": "test",
                "LGWE": "web"
            }
            if unit_name.startswith("SOA") or unit_name.startswith("POL"):
                sub_pkg = "soa"
            else:
                sub_pkg = domain_map.get(prefix, "common")
            package = f"cobol.{sub_pkg}"

            cics_links = re.findall(r'EXEC\s+CICS\s+LINK\s+PROGRAM\s*\(\s*[\'"]?([\w\-]+)[\'"]?\s*\)', content, re.IGNORECASE)
            cics_xctls = re.findall(r'EXEC\s+CICS\s+XCTL\s+PROGRAM\s*\(\s*[\'"]?([\w\-]+)[\'"]?\s*\)', content, re.IGNORECASE)
            cobol_calls = re.findall(r'CALL\s+[\'"]([\w\-]+)[\'"]', content, re.IGNORECASE)
            copybooks = re.findall(r'COPY\s+([\w\-]+)', content, re.IGNORECASE)

            refs = set([c.upper() for c in cics_links + cics_xctls + cobol_calls + copybooks])
            words = re.findall(r'\b[A-Z0-9\-]{3,}\b', content.upper())
            refs |= set(words)

            data_items = re.findall(r'05\s+([A-Z0-9\-]+)', content.upper()) + re.findall(r'10\s+([A-Z0-9\-]+)', content.upper())

            methods = []
            raw_paras = re.findall(r'^\s*([A-Z0-9\-]+)\s*\.\s*$', content, re.MULTILINE)
            noise_words = {"PROCEDURE", "DATA", "WORKING-STORAGE", "LINKAGE", "ENVIRONMENT", "IDENTIFICATION", "PROGRAM-ID", "AUTHOR", "END-EXEC", "EXIT", "GOBACK"}
            paras = [p.upper() for p in raw_paras if p.upper() not in noise_words]

            for p in set(paras):
                terms = set([w.lower() for w in p.split('-') if len(w) > 1])
                for d in data_items:
                    terms |= set([w.lower() for w in d.split('-') if len(w) > 1])
                
                methods.append({
                    "name": p,
                    "return_type": "void",
                    "parameters": data_items[:3],
                    "pre_terms": terms,
                    "pre_rel": set(["void"]),
                    "pre_par": set(data_items[:3])
                })

            full_cls_name = f"{package}.{unit_name}"
            class_info[full_cls_name] = {
                "package": package,
                "short_name": unit_name,
                "methods": methods,
                "references": refs,
                "content": content,
                "filepath": filepath
            }
        else:
            pkg_match = re.search(r'(?:package|namespace)\s+([\w\.]+)', content)
            package = pkg_match.group(1) if pkg_match else ""

            cls_matches = list(re.finditer(r'(?:public|protected|private|internal)?\s*(?:partial\s+)?(?:class|interface|enum|struct)\s+(\w+)', content))
            if not cls_matches:
                continue

            for cls_match in cls_matches:
                cls_name = cls_match.group(1)
                if cls_name in ["class", "interface", "enum", "struct", "void", "string", "int", "bool"]:
                    continue
                full_cls_name = f"{package}.{cls_name}" if package else cls_name

                method_pattern = r'(?:public|protected|private|internal)\s+(?:virtual|override|async|static\s+)*([\w<>\[\]\?]+)\s+(\w+)\s*\(([^)]*)\)'
                methods = []
                for m in re.finditer(method_pattern, content):
                    ret_type, m_name, params_str = m.groups()
                    if m_name in [cls_name, "if", "for", "while", "switch"]:
                        continue

                    params = []
                    if params_str.strip():
                        for p in params_str.split(','):
                            parts = p.strip().split()
                            if parts:
                                params.append(parts[0])

                    terms = camel_case_split(m_name) | camel_case_split(ret_type)
                    for p in params:
                        terms |= camel_case_split(p)

                    methods.append({
                        "name": m_name,
                        "return_type": ret_type,
                        "parameters": params,
                        "pre_terms": terms,
                        "pre_rel": set([ret_type]),
                        "pre_par": set(params)
                    })

                referenced_identifiers = set(re.findall(r'\b[A-Z]\w+\b', content))

                class_info[full_cls_name] = {
                    "package": package,
                    "short_name": cls_name,
                    "methods": methods,
                    "references": referenced_identifiers,
                    "content": content,
                    "filepath": filepath
                }

    return class_info


def run_cogcn_clustering(adj_matrix, feature_matrix, target_k, run_seed=42, preepochs=30, epochs=30):
    """
    Executes CoGCN Graph Neural Network with Outlier Dilution using the exact official GCNAE,
    loss functions, and analytical outlier updates from utkd/cogcn.
    """
    torch.manual_seed(run_seed)
    np.random.seed(run_seed)

    n_nodes = adj_matrix.shape[0]
    feat_dim = feature_matrix.shape[1]

    features = torch.FloatTensor(feature_matrix)
    adj_norm = preprocess_graph(adj_matrix)

    if sp.issparse(adj_matrix):
        adj_dense = torch.FloatTensor(adj_matrix.toarray())
    else:
        adj_dense = torch.FloatTensor(adj_matrix)

    hidden1 = min(64, max(feat_dim, 16))
    hidden2 = min(32, max(target_k * 2, 8))
    dropout = 0.1
    lr = 0.01

    model = GCNAE(feat_dim, hidden1, hidden2, dropout)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    lossfn = nn.MSELoss(reduction='none')

    # Initial uniform outlier weights summing to 1
    init_value = [1.0 / n_nodes] * n_nodes
    o_1 = torch.FloatTensor(init_value)
    o_2 = torch.FloatTensor(init_value)

    lambda1 = 0.1
    lambda2 = 0.1
    lambda3 = 0.8
    pre_l1 = lambda1 / (lambda1 + lambda2)
    pre_l2 = lambda2 / (lambda1 + lambda2)

    # Phase 1: Pre-train on structure and attribute reconstruction
    for epoch in range(preepochs):
        model.train()
        optimizer.zero_grad()

        recon, embed = model(features, adj_norm)

        structure_loss = compute_structure_loss(adj_norm, embed, o_1)
        attribute_loss = compute_attribute_loss(lossfn, features, recon, o_2)

        loss = pre_l1 * structure_loss + pre_l2 * attribute_loss
        loss.backward()
        optimizer.step()

    # Phase 2: Initialize KMeans clustering
    model.eval()
    with torch.no_grad():
        recon, embed = model(features, adj_norm)
    kmeans = Clustering(target_k)
    kmeans.cluster(embed)

    # Phase 3: Train on structure, attribute, and clustering losses with outlier updates
    for epoch in range(epochs):
        o_1 = update_o1(adj_norm, embed)
        o_2 = update_o2(features, recon)

        model.train()
        optimizer.zero_grad()

        recon, embed = model(features, adj_norm)

        if epoch % 10 == 0:
            kmeans.cluster(embed)

        structure_loss = compute_structure_loss(adj_norm, embed, o_1)
        attribute_loss = compute_attribute_loss(lossfn, features, recon, o_2)
        clustering_loss = kmeans.get_loss(embed)

        loss = (lambda1 * structure_loss) + (lambda2 * attribute_loss) + (lambda3 * clustering_loss)
        loss.backward()
        optimizer.step()

    # Phase 4: Final cluster extraction
    model.eval()
    with torch.no_grad():
        recon, embed = model(features, adj_norm)
    kmeans.cluster(embed)
    membership = kmeans.get_membership()

    return membership


def compute_metrics_for_K(class_info, target_K, run_seed=42):
    class_names = sorted(list(class_info.keys()))
    N = len(class_names)
    target_K = max(2, min(target_K, N))

    class_texts = []
    for cname in class_names:
        content = class_info[cname]["content"]
        words = re.findall(r'[a-zA-Z]+', content)
        class_texts.append(' '.join(words))

    calls = np.zeros((N, N))
    for i, src_name in enumerate(class_names):
        content = class_info[src_name]["content"]
        for j, tgt_name in enumerate(class_names):
            short_name = class_info[tgt_name]["short_name"]
            if short_name in content and i != j:
                calls[i, j] += content.count(short_name)

    call_sym = calls + calls.T
    
    # Structural adjacency
    adj = (call_sym > 0).astype(float)
    np.fill_diagonal(adj, 0.0)

    # Semantic feature matrix using TF-IDF
    tfidf_mat = TfidfVectorizer(max_features=min(128, max(20, N * 2)), stop_words='english').fit_transform(class_texts).toarray()

    # Run CoGCN GNN Autoencoder with Outlier Dilution
    membership = run_cogcn_clustering(adj, tfidf_mat, target_K, run_seed=run_seed, preepochs=30, epochs=30)

    # Form partitions
    partitions_dict = defaultdict(list)
    for idx, cluster_id in enumerate(membership):
        partitions_dict[int(cluster_id)].append(class_names[idx])
    partitions = [partitions_dict[k] for k in sorted(partitions_dict.keys()) if len(partitions_dict[k]) > 0]

    K = len(partitions)
    V = N

    class_to_cluster = {c: cluster_id for cluster_id, cluster_classes in enumerate(partitions) for c in cluster_classes}
    short_to_full = {c.split('.')[-1]: c for c in class_names}

    edges = defaultdict(set)
    for c in class_names:
        info = class_info.get(c, None)
        if info:
            for ref in info["references"]:
                if ref in short_to_full:
                    tgt = short_to_full[ref]
                    if tgt != c:
                        edges[c].add(tgt)

    # 1. SM (Structural Modularity)
    u_k = defaultdict(int)
    sigma = defaultdict(int)

    for src, targets in edges.items():
        src_cluster = class_to_cluster.get(src, None)
        if src_cluster is None: continue
        for tgt in targets:
            tgt_cluster = class_to_cluster.get(tgt, None)
            if tgt_cluster is None: continue
            if src_cluster == tgt_cluster:
                u_k[src_cluster] += 1
            else:
                pair = tuple(sorted([src_cluster, tgt_cluster]))
                sigma[pair] += 1

    sm_intra = sum((u_k[k] / (len(partitions[k])**2)) for k in range(K)) / K
    num_pairs = K * (K - 1) / 2 if K > 1 else 1
    sm_inter = sum(count / (2.0 * len(partitions[k1]) * len(partitions[k2])) for (k1, k2), count in sigma.items()) / num_pairs
    SM = sm_intra - sm_inter

    # 2. ICP (Inter-Call Pair / Coupling)
    icp_sum = sum(count / (len(partitions[k1]) * len(partitions[k2])) for (k1, k2), count in sigma.items())
    ICP = icp_sum / num_pairs

    # 3. BCP (Business Use Case Entropy)
    bcp_list = []
    for k in range(K):
        tags = [c.split('.')[-2] if len(c.split('.')) > 1 else 'domain' for c in partitions[k]]
        counts = Counter(tags)
        total = sum(counts.values())
        entropy = -sum((cnt / total) * math.log2(cnt / total) for cnt in counts.values() if cnt > 0)
        bcp_list.append(entropy)
    BCP = sum(bcp_list) / K

    # 4. IFN (Interface Number)
    published_interfaces = defaultdict(set)
    for src, targets in edges.items():
        src_cluster = class_to_cluster[src]
        for tgt in targets:
            tgt_cluster = class_to_cluster[tgt]
            if src_cluster != tgt_cluster:
                published_interfaces[tgt_cluster].add(tgt)

    ifn_list = [len(published_interfaces[k]) for k in range(K)]
    IFN = sum(ifn_list) / K

    # 5. NED (Non-Extreme Distribution)
    non_extreme_count = sum(len(partitions[k]) for k in range(K) if 5 <= len(partitions[k]) <= 20)
    NED = non_extreme_count / V
    ONE_MINUS_NED = 1.0 - NED

    # 6. CHD & 7. CHM
    chd_list = []
    chm_list = []

    for k in range(K):
        pub_ifaces = published_interfaces[k]
        if not pub_ifaces:
            pub_ifaces = partitions[k]

        operations = []
        for cls in pub_ifaces:
            info = class_info.get(cls, None)
            if info:
                for m in info["methods"]:
                    operations.append(m)

        if len(operations) <= 1:
            chd_list.append(1.0 if len(operations) == 1 else 0.0)
            chm_list.append(1.0 if len(operations) == 1 else 0.0)
            continue

        if len(operations) > 50:
            step = max(1, len(operations) // 50)
            operations = operations[::step][:50]

        f_dom_sum = 0.0
        f_msg_sum = 0.0
        pair_cnt = 0
        num_ops = len(operations)

        for i in range(num_ops):
            op1 = operations[i]
            terms1 = op1["pre_terms"]
            rel1 = op1["pre_rel"]
            par1 = op1["pre_par"]

            for j in range(i + 1, num_ops):
                op2 = operations[j]
                terms2 = op2["pre_terms"]
                rel2 = op2["pre_rel"]
                par2 = op2["pre_par"]

                union_dom = terms1 | terms2
                inter_dom = terms1 & terms2
                jaccard_dom = (len(inter_dom) / len(union_dom)) if union_dom else 1.0

                union_rel = rel1 | rel2
                inter_rel = rel1 & rel2
                jaccard_rel = (len(inter_rel) / len(union_rel)) if union_rel else 1.0

                union_par = par1 | par2
                inter_par = par1 & par2
                jaccard_par = (len(inter_par) / len(union_par)) if union_par else (1.0 if not par1 and not par2 else 0.0)

                jaccard_msg = 0.5 * (jaccard_rel + jaccard_par)

                f_dom_sum += jaccard_dom
                f_msg_sum += jaccard_msg
                pair_cnt += 1

        chd_list.append(f_dom_sum / pair_cnt if pair_cnt > 0 else 1.0)
        chm_list.append(f_msg_sum / pair_cnt if pair_cnt > 0 else 1.0)

    CHD = sum(chd_list) / K
    CHM = sum(chm_list) / K

    score = SM - ICP - 0.1 * BCP + 0.5 * NED

    return {
        "K": K,
        "V": V,
        "SM": SM,
        "ICP": ICP,
        "BCP": BCP,
        "IFN": IFN,
        "NED": NED,
        "1-NED": ONE_MINUS_NED,
        "CHD": CHD,
        "CHM": CHM,
        "score": score,
        "partitions": partitions
    }


def generate_dataset_readme(dataset_name, dataset_path, summary_payload, decomp_out):
    meta = DATASET_METADATA.get(dataset_name, {
        "title": dataset_name.replace('-', ' ').title(),
        "desc": f"Benchmark monolithic software system: {dataset_name}.",
        "repo": f"{dataset_name}/{dataset_name}",
        "lang": "Java / Polyglot"
    })
    opt_k = summary_payload["optimal_K"]
    v_classes = summary_payload["V_classes"]
    m = summary_payload["optimal_metrics_orderly"]

    lines = [
        f"# Dataset Documentation: {meta['title']}",
        "",
        "## Overview",
        f"**{meta['title']}** is a standard monolithic benchmark software system evaluated using **CoGCN (Collaborative Graph Convolutional Networks with Outlier Dilution)**.",
        "",
        f"- **Repository / Baseline**: [{meta['repo']}](https://github.com/{meta['repo']})",
        f"- **Primary Language**: {meta['lang']}",
        f"- **Evaluation Model**: CoGCN GNN Autoencoder with Outlier Dilution (AAAI 2021)",
        "",
        "---",
        "",
        f"## Dataset Statistics & Optimal $K < 20$ Configuration",
        f"- **Total System Classes ($V$)**: `{v_classes}`",
        f"- **Dynamically Selected Optimal Cluster Count ($K$)**: **`{opt_k}` microservices**",
        f"- **Non-Extreme Distribution Ratio ($\\text{{NED}}$)**: `{m['NED']:.6f}` ({m['NED']*100:.1f}% of classes in balanced partitions $5 \\le |C| \\le 20$)",
        f"- **Composite Architectural Score**: `{m['score']:.6f}`",
        "",
        "---",
        "",
        f"## Stored Optimal 7 Benchmark Metrics ($K = {opt_k}$, 10-Run Mean $\\pm$ Std)",
        "",
        "| Order | Metric Code | Metric Name | Evaluated Value ($K=" + str(opt_k) + "$) | 10-Run Std Dev | Preferred Direction |",
        "| :---: | :--- | :--- | :---: | :---: | :---: |",
        f"| **1** | **SM** | Structural Modularity | **`{m['SM']:.6f}`** | `±{m['SM_std']:.6f}` | Higher is better |",
        f"| **2** | **ICP** | Inter-Call Pair / Coupling Density | **`{m['ICP']:.6f}`** | `±{m['ICP_std']:.6f}` | Lower is better |",
        f"| **3** | **BCP** | Business Use Case Entropy | **`{m['BCP']:.6f}`** | `±{m['BCP_std']:.6f}` | Lower is better |",
        f"| **4** | **IFN** | Interface Number | **`{m['IFN']:.6f}`** | `±{m['IFN_std']:.6f}` | Lower is better |",
        f"| **5** | **NED** | Non-Extreme Distribution | **`{m['NED']:.6f}`** *(1-NED: `{m['1-NED']:.6f}`)* | `±{m['NED_std']:.6f}` | Lower $1-\\text{{NED}}$ |",
        f"| **6** | **CHD** | Cohesion at Domain Level | **`{m['CHD']:.6f}`** | `±{m['CHD_std']:.6f}` | Higher is better |",
        f"| **7** | **CHM** | Cohesion at Message Level | **`{m['CHM']:.6f}`** | `±{m['CHM_std']:.6f}` | Higher is better |",
        "",
        "---",
        "",
        f"## Microservices Decomposition Breakdown ($K = {opt_k}$)",
        ""
    ]

    for cluster in decomp_out:
        cid = cluster["cluster_id"]
        csize = cluster["size"]
        classes = cluster["classes"]
        lines.append(f"### Service {cid + 1} (Size: {csize} classes)")
        for c in sorted(classes):
            short_c = c.split('.')[-1]
            lines.append(f"- `{short_c}` (`{c}`)")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Stored Artifact Files",
        f"- [decomposition.json](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{dataset_name}/decomposition.json): Class cluster assignments for all {opt_k} optimal microservices.",
        f"- [results.json](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{dataset_name}/results.json): Structured JSON payload of evaluated metrics across all candidate $K < 20$.",
        ""
    ])

    readme_path = os.path.join(dataset_path, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def update_master_docs(all_dataset_names):
    # Collect all existing results.json
    results_map = {}
    for d in all_dataset_names:
        rpath = os.path.join("dataset", d, "results.json")
        if os.path.exists(rpath):
            with open(rpath, "r", encoding="utf-8") as f:
                results_map[d] = json.load(f)

    if not results_map:
        return

    # 1. Update Root README.md
    readme_lines = [
        "# CoGCN Microservice Decomposition & Evaluation Suite",
        "",
        "A research evaluation framework for microservice decomposition using **CoGCN (Collaborative Graph Convolutional Networks with Outlier Dilution)** ([AAAI 2021](https://github.com/utkd/cogcn)). This repository provides automated GNN-based decomposition across **7 key software architecture benchmarks** (**SM**, **ICP**, **BCP**, **IFN**, **NED**, **CHD**, and **CHM**) evaluated on benchmark software systems.",
        "",
        "---",
        "",
        "## 📂 Repository Overview",
        "",
        "- **Evaluation Engine**: [`evaluate_metrics.py`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/evaluate_metrics.py)",
        "- **Summary Report**: [`docs/evaluation_summary.md`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/docs/evaluation_summary.md)",
        "- **CoGCN Upstream Module**: [`cogcn_repo/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/cogcn_repo) ([GitHub: utkd/cogcn](https://github.com/utkd/cogcn))",
        "- **Supported Monolithic Datasets**:",
    ]

    for d in all_dataset_names:
        if d in results_map:
            meta = DATASET_METADATA.get(d, {"title": d})
            readme_lines.append(f"  - `{meta['title']}` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{d}/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{d}/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{d}/decomposition.json))")

    readme_lines.extend([
        "",
        "---",
        "",
        "## 📊 Benchmark 10-Run Dynamic $K$ Mean Metrics Summary Table ($K < 20$)",
        "",
    ])

    # Construct table header
    eval_datasets = [d for d in all_dataset_names if d in results_map]
    header_cols = ["Order", "Metric Code", "Metric Name"]
    for d in eval_datasets:
        meta = DATASET_METADATA.get(d, {"title": d})
        opt_k = results_map[d]["optimal_K"]
        header_cols.append(f"{meta['title']} ($K={opt_k}$)")
    header_cols.append("Favorable Direction")

    readme_lines.append("| " + " | ".join(header_cols) + " |")
    readme_lines.append("| " + " | ".join([":---:" if i == 0 else (":---" if i in [1, 2] else ":---:") for i in range(len(header_cols))]) + " |")

    metrics_def = [
        ("1", "SM", "Structural Modularity", "Higher is better", lambda m: f"**`{m['SM']:.6f}`**"),
        ("2", "ICP", "Inter-Call Pair / Coupling", "Lower is better", lambda m: f"**`{m['ICP']:.6f}`**"),
        ("3", "BCP", "Business Use Case Entropy", "Lower is better", lambda m: f"**`{m['BCP']:.6f}`**"),
        ("4", "IFN", "Interface Number", "Lower is better", lambda m: f"**`{m['IFN']:.6f}`**"),
        ("5", "NED", "Non-Extreme Distribution", "Lower $1-\\text{NED}$", lambda m: f"**`{m['NED']:.6f}`**"),
        ("6", "CHD", "Cohesion at Domain Level", "Higher is better", lambda m: f"**`{m['CHD']:.6f}`**"),
        ("7", "CHM", "Cohesion at Message Level", "Higher is better", lambda m: f"**`{m['CHM']:.6f}`**"),
    ]

    for order, code, name, fav, fmt_fn in metrics_def:
        row = [f"**{order}**", f"**{code}**", name]
        for d in eval_datasets:
            m = results_map[d]["optimal_metrics_orderly"]
            row.append(fmt_fn(m))
        row.append(fav)
        readme_lines.append("| " + " | ".join(row) + " |")

    readme_lines.extend([
        "",
        "---",
        "",
        "## 🚀 Getting Started",
        "",
        "```bash",
        "pip install torch scipy numpy scikit-learn networkx pandas matplotlib",
        "",
        "# Run full evaluation on all datasets",
        "python evaluate_metrics.py --dataset all",
        "",
        "# Or evaluate an individual dataset",
        "python evaluate_metrics.py --dataset spring-petclinic",
        "```",
        ""
    ])

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(readme_lines))

    # 2. Update docs/evaluation_summary.md
    os.makedirs("docs", exist_ok=True)
    doc_lines = [
        "# CoGCN Architectural Benchmark Evaluation Summary Report",
        "",
        "## Executive Summary",
        "This document presents a comprehensive evaluation of **Collaborative Graph Convolutional Networks with Outlier Dilution (CoGCN)** applied to the problem of monolithic software decomposition into microservices.",
        "",
        "CoGCN optimizes an objective function with structural reconstruction, semantic attribute reconstruction, and cluster centroid distance, combined with analytical closed-form outlier weight updates ($O_1, O_2$) to prevent cross-cutting concerns and utility classes from corrupting cluster boundaries.",
        "",
        "---",
        "",
        "## The 7 Benchmark Evaluation Metrics (Strict Order)",
        "",
        "1. **SM (Structural Modularity)** [$\\uparrow$ Higher is better]: Measures the ratio of intra-service call density versus inter-service coupling penalty.",
        "2. **ICP (Inter-Call Pair / Coupling Density)** [$\\downarrow$ Lower is better]: Quantifies the normalized inter-service dependency edges.",
        "3. **BCP (Business Use Case / Package Entropy)** [$\\downarrow$ Lower is better]: Measures the domain purity of classes assigned to each microservice.",
        "4. **IFN (Interface Number)** [$\\downarrow$ Lower is better]: Average number of externally published service entrypoint interfaces.",
        "5. **NED (Non-Extreme Distribution, $5 \\le |C| \\le 20$)** [$\\uparrow$ Higher is better / $1-\\text{NED}\\downarrow$]: Percentage of system classes placed in maintainably sized microservices.",
        "6. **CHD (Cohesion at Domain Level)** [$\\uparrow$ Higher is better]: Average semantic Jaccard similarity across operation domain terms.",
        "7. **CHM (Cohesion at Message Level)** [$\\uparrow$ Higher is better]: Average Jaccard similarity across return types and parameter types.",
        "",
        "---",
        "",
        "## 10-Run Dynamic $K$ Metrics Summary Table across All Datasets",
        "",
        "| " + " | ".join(header_cols) + " |",
        "| " + " | ".join([":---:" if i == 0 else (":---" if i in [1, 2] else ":---:") for i in range(len(header_cols))]) + " |"
    ]

    for order, code, name, fav, fmt_fn in metrics_def:
        row = [f"**{order}**", f"**{code}**", name]
        for d in eval_datasets:
            m = results_map[d]["optimal_metrics_orderly"]
            row.append(fmt_fn(m))
        row.append(fav)
        doc_lines.append("| " + " | ".join(row) + " |")

    doc_lines.extend([
        "",
        "---",
        "",
        "## Dataset-by-Dataset Decomposition Analysis",
        ""
    ])

    for idx, d in enumerate(eval_datasets, 1):
        meta = DATASET_METADATA.get(d, {"title": d, "desc": ""})
        res = results_map[d]
        opt_k = res["optimal_K"]
        v_cls = res["V_classes"]
        m = res["optimal_metrics_orderly"]

        doc_lines.extend([
            f"### {idx}. {meta['title']} ($K={opt_k}$, $V={v_cls}$)",
            f"- **System Overview**: {meta['desc']}",
            f"- **Dynamic Optimal Cluster Count**: $K={opt_k}$ (Score = `{m['score']:.4f}`)",
            f"- **Structural Modularity (SM)**: `{m['SM']:.6f} ± {m['SM_std']:.6f}`",
            f"- **Inter-Service Coupling (ICP)**: `{m['ICP']:.6f} ± {m['ICP_std']:.6f}`",
            f"- **Business Use Case Entropy (BCP)**: `{m['BCP']:.6f} ± {m['BCP_std']:.6f}`",
            f"- **Interface Complexity (IFN)**: `{m['IFN']:.6f} ± {m['IFN_std']:.6f}`",
            f"- **Non-Extreme Distribution (NED)**: `{m['NED']:.6f}` *(1-NED: `{m['1-NED']:.6f}`)*",
            f"- **Domain Cohesion (CHD)**: `{m['CHD']:.6f} ± {m['CHD_std']:.6f}`",
            f"- **Message Cohesion (CHM)**: `{m['CHM']:.6f} ± {m['CHM_std']:.6f}`",
            f"- **Links**: [`dataset/{d}/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{d}) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{d}/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{d}/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/{d}/decomposition.json))",
            ""
        ])

    with open(os.path.join("docs", "evaluation_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(doc_lines))


def evaluate_dataset_10_runs(dataset_name, dataset_path, num_runs=10):
    class_info = parse_dataset_classes(dataset_path)
    V_classes = len(class_info)
    
    max_k_limit = min(20, V_classes)
    candidate_k_values = list(range(2, max_k_limit))

    k_run_results = defaultdict(list)
    k_partitions = {}

    for run_id in range(num_runs):
        seed = 42 + run_id * 13
        for k in candidate_k_values:
            res = compute_metrics_for_K(class_info, k, run_seed=seed)
            k_run_results[f"K_{k}"].append(res)
            if run_id == 0:
                k_partitions[f"K_{k}"] = res["partitions"]

    aggregated_k_results = {}
    for k_key, runs in k_run_results.items():
        sm_vals = [r["SM"] for r in runs]
        icp_vals = [r["ICP"] for r in runs]
        bcp_vals = [r["BCP"] for r in runs]
        ifn_vals = [r["IFN"] for r in runs]
        ned_vals = [r["NED"] for r in runs]
        one_minus_ned_vals = [r["1-NED"] for r in runs]
        chd_vals = [r["CHD"] for r in runs]
        chm_vals = [r["CHM"] for r in runs]
        score_vals = [r["score"] for r in runs]

        aggregated_k_results[k_key] = {
            "K": runs[0]["K"],
            "SM": float(np.mean(sm_vals)),
            "SM_std": float(np.std(sm_vals)),
            "ICP": float(np.mean(icp_vals)),
            "ICP_std": float(np.std(icp_vals)),
            "BCP": float(np.mean(bcp_vals)),
            "BCP_std": float(np.std(bcp_vals)),
            "IFN": float(np.mean(ifn_vals)),
            "IFN_std": float(np.std(ifn_vals)),
            "NED": float(np.mean(ned_vals)),
            "NED_std": float(np.std(ned_vals)),
            "1-NED": float(np.mean(one_minus_ned_vals)),
            "1-NED_std": float(np.std(one_minus_ned_vals)),
            "CHD": float(np.mean(chd_vals)),
            "CHD_std": float(np.std(chd_vals)),
            "CHM": float(np.mean(chm_vals)),
            "CHM_std": float(np.std(chm_vals)),
            "score": float(np.mean(score_vals)),
            "score_std": float(np.std(score_vals))
        }

    # Dynamically select optimal K < 20 based on highest mean score
    best_k_key = max(aggregated_k_results.keys(), key=lambda k: aggregated_k_results[k]["score"])
    optimal = aggregated_k_results[best_k_key]
    optimal_partitions = k_partitions[best_k_key]

    summary_payload = {
        "dataset": dataset_name,
        "runs_count": num_runs,
        "optimal_K": optimal["K"],
        "V_classes": V_classes,
        "optimal_metrics_orderly": {
            "SM": optimal["SM"],
            "SM_std": optimal["SM_std"],
            "ICP": optimal["ICP"],
            "ICP_std": optimal["ICP_std"],
            "BCP": optimal["BCP"],
            "BCP_std": optimal["BCP_std"],
            "IFN": optimal["IFN"],
            "IFN_std": optimal["IFN_std"],
            "NED": optimal["NED"],
            "NED_std": optimal["NED_std"],
            "1-NED": optimal["1-NED"],
            "1-NED_std": optimal["1-NED_std"],
            "CHD": optimal["CHD"],
            "CHD_std": optimal["CHD_std"],
            "CHM": optimal["CHM"],
            "CHM_std": optimal["CHM_std"],
            "score": optimal["score"],
            "score_std": optimal["score_std"]
        },
        "all_K_below_20_metrics": aggregated_k_results
    }

    out_dir = dataset_path
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=4)

    decomp_out = [{"cluster_id": i, "size": len(p), "classes": p} for i, p in enumerate(optimal_partitions)]
    with open(os.path.join(out_dir, "decomposition.json"), "w", encoding="utf-8") as f:
        json.dump(decomp_out, f, indent=4)

    # Generate individual dataset README.md
    generate_dataset_readme(dataset_name, dataset_path, summary_payload, decomp_out)

    print(f"[{dataset_name}] Evaluated successfully! Optimal K={optimal['K']}, Score={optimal['score']:.4f}, SM={optimal['SM']:.4f}, ICP={optimal['ICP']:.4f}, NED={optimal['NED']:.4f}", flush=True)

    return summary_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate CoGCN microservice decomposition on software benchmark datasets.")
    parser.add_argument("--dataset", type=str, default="all", help="Dataset name to evaluate (or 'all').")
    parser.add_argument("--runs", type=int, default=10, help="Number of independent evaluation runs.")
    args = parser.parse_args()

    all_datasets = [
        'spring-petclinic',
        'jpetstore-6',
        'acmeair',
        'plantsbywebsphere',
        'daytrader7',
        'jforum',
        'javafx-pos',
        'springblog',
        'roller',
        'bear-board',
        'train-ticket',
        'dietapp',
        'cics-genapp',
        'autocare-nepal',
        'pharmacy'
    ]

    target_datasets = all_datasets if args.dataset == "all" else [args.dataset]
    print(f"Starting CoGCN evaluation for: {target_datasets} ({args.runs} runs per dataset, dynamic K < 20)...", flush=True)

    for d in target_datasets:
        dpath = os.path.join("dataset", d)
        if not os.path.exists(dpath):
            print(f"Error: Dataset directory {dpath} does not exist. Skipping...", flush=True)
            continue
        print(f"\n---> Evaluating dataset: {d} ({args.runs} runs)...", flush=True)
        evaluate_dataset_10_runs(d, dpath, num_runs=args.runs)
        update_master_docs(all_datasets)

    print("\nCoGCN evaluation and documentation update complete!")
