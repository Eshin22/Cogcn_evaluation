# CoGCN Microservice Decomposition & Evaluation Suite

A research evaluation framework for microservice decomposition using **CoGCN (Collaborative Graph Convolutional Networks with Outlier Dilution)** ([AAAI 2021](https://github.com/utkd/cogcn)). This repository provides automated GNN-based decomposition across **7 key software architecture benchmarks** (**SM**, **ICP**, **BCP**, **IFN**, **NED**, **CHD**, and **CHM**) evaluated on benchmark software systems.

---

## 📂 Repository Overview

- **Evaluation Engine**: [`evaluate_metrics.py`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/evaluate_metrics.py)
- **Summary Report**: [`docs/evaluation_summary.md`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/docs/evaluation_summary.md)
- **CoGCN Upstream Module**: [`cogcn_repo/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/cogcn_repo) ([GitHub: utkd/cogcn](https://github.com/utkd/cogcn))
- **Supported Monolithic Datasets**:
  - `Spring PetClinic` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/spring-petclinic/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/spring-petclinic/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/spring-petclinic/decomposition.json))
  - `JPetStore-6` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jpetstore-6/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jpetstore-6/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jpetstore-6/decomposition.json))
  - `AcmeAir` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/acmeair/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/acmeair/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/acmeair/decomposition.json))
  - `PlantsByWebSphere` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/plantsbywebsphere/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/plantsbywebsphere/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/plantsbywebsphere/decomposition.json))
  - `DayTrader 7` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/daytrader7/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/daytrader7/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/daytrader7/decomposition.json))
  - `JForum` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jforum/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jforum/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jforum/decomposition.json))
  - `JavaFX Point-of-Sales` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/javafx-pos/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/javafx-pos/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/javafx-pos/decomposition.json))
  - `SpringBlog` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/springblog/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/springblog/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/springblog/decomposition.json))
  - `Apache Roller` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/roller/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/roller/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/roller/decomposition.json))
  - `Bear Board` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/bear-board/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/bear-board/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/bear-board/decomposition.json))
  - `Train Ticket` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/train-ticket/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/train-ticket/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/train-ticket/decomposition.json))
  - `DietApp` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/dietapp/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/dietapp/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/dietapp/decomposition.json))
  - `IBM CICS GenApp` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/cics-genapp/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/cics-genapp/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/cics-genapp/decomposition.json))
  - `AutoCare Nepal` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/autocare-nepal/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/autocare-nepal/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/autocare-nepal/decomposition.json))
  - `Pharmacy Management System` ([Documentation](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/pharmacy/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/pharmacy/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/pharmacy/decomposition.json))

---

## 📊 Benchmark 10-Run Dynamic $K$ Mean Metrics Summary Table ($K < 20$)

| Order | Metric Code | Metric Name | Spring PetClinic ($K=8$) | JPetStore-6 ($K=5$) | AcmeAir ($K=15$) | PlantsByWebSphere ($K=5$) | DayTrader 7 ($K=16$) | JForum ($K=19$) | JavaFX Point-of-Sales ($K=3$) | SpringBlog ($K=8$) | Apache Roller ($K=19$) | Bear Board ($K=5$) | Train Ticket ($K=19$) | DietApp ($K=8$) | IBM CICS GenApp ($K=13$) | AutoCare Nepal ($K=9$) | Pharmacy Management System ($K=9$) | Favorable Direction |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **SM** | Structural Modularity | **`0.022459`** | **`0.194863`** | **`0.088446`** | **`0.043116`** | **`0.028411`** | **`0.026641`** | **`0.097203`** | **`0.135779`** | **`0.035508`** | **`0.114975`** | **`0.041519`** | **`0.228221`** | **`0.013029`** | **`0.094460`** | **`0.141847`** | Higher is better |
| **2** | **ICP** | Inter-Call Pair / Coupling | **`0.086747`** | **`0.057539`** | **`0.081034`** | **`0.112823`** | **`0.119196`** | **`0.048122`** | **`0.017347`** | **`0.035505`** | **`0.038236`** | **`0.022071`** | **`0.017876`** | **`0.013115`** | **`0.010090`** | **`0.005012`** | **`0.020604`** | Lower is better |
| **3** | **BCP** | Business Use Case Entropy | **`1.045257`** | **`1.423184`** | **`1.176342`** | **`1.301031`** | **`1.428384`** | **`2.713450`** | **`1.784612`** | **`1.786906`** | **`2.902296`** | **`1.769419`** | **`2.303672`** | **`0.907923`** | **`0.416743`** | **`0.985789`** | **`1.454387`** | Lower is better |
| **4** | **IFN** | Interface Number | **`2.362500`** | **`3.080000`** | **`3.593333`** | **`5.340000`** | **`3.268750`** | **`16.489474`** | **`1.066667`** | **`2.762500`** | **`21.442105`** | **`2.240000`** | **`14.094737`** | **`1.850000`** | **`0.784615`** | **`0.900000`** | **`2.333333`** | Lower is better |
| **5** | **NED** | Non-Extreme Distribution | **`0.839535`** | **`0.950000`** | **`0.791011`** | **`0.925000`** | **`0.880153`** | **`0.302069`** | **`0.944118`** | **`0.866667`** | **`0.096961`** | **`0.948718`** | **`0.064956`** | **`0.846296`** | **`0.547727`** | **`0.812245`** | **`0.888136`** | Lower $1-\text{NED}$ |
| **6** | **CHD** | Cohesion at Domain Level | **`0.292898`** | **`0.211024`** | **`0.177063`** | **`0.348738`** | **`0.200535`** | **`0.114570`** | **`0.137681`** | **`0.307519`** | **`0.129071`** | **`0.337501`** | **`0.181792`** | **`0.359620`** | **`0.285749`** | **`0.271451`** | **`0.233178`** | Higher is better |
| **7** | **CHM** | Cohesion at Message Level | **`0.412571`** | **`0.294669`** | **`0.303102`** | **`0.445328`** | **`0.340841`** | **`0.257365`** | **`0.439458`** | **`0.382475`** | **`0.268094`** | **`0.455889`** | **`0.284471`** | **`0.461536`** | **`0.482201`** | **`0.401065`** | **`0.261806`** | Higher is better |

---

## 🚀 Getting Started

```bash
pip install torch scipy numpy scikit-learn networkx pandas matplotlib

# Run full evaluation on all datasets
python evaluate_metrics.py --dataset all

# Or evaluate an individual dataset
python evaluate_metrics.py --dataset spring-petclinic
```
