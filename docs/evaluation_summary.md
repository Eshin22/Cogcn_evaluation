# CoGCN Architectural Benchmark Evaluation Summary Report

## Executive Summary
This document presents a comprehensive evaluation of **Collaborative Graph Convolutional Networks with Outlier Dilution (CoGCN)** applied to the problem of monolithic software decomposition into microservices.

CoGCN optimizes an objective function with structural reconstruction, semantic attribute reconstruction, and cluster centroid distance, combined with analytical closed-form outlier weight updates ($O_1, O_2$) to prevent cross-cutting concerns and utility classes from corrupting cluster boundaries.

---

## The 7 Benchmark Evaluation Metrics (Strict Order)

1. **SM (Structural Modularity)** [$\uparrow$ Higher is better]: Measures the ratio of intra-service call density versus inter-service coupling penalty.
2. **ICP (Inter-Call Pair / Coupling Density)** [$\downarrow$ Lower is better]: Quantifies the normalized inter-service dependency edges.
3. **BCP (Business Use Case / Package Entropy)** [$\downarrow$ Lower is better]: Measures the domain purity of classes assigned to each microservice.
4. **IFN (Interface Number)** [$\downarrow$ Lower is better]: Average number of externally published service entrypoint interfaces.
5. **NED (Non-Extreme Distribution, $5 \le |C| \le 20$)** [$\uparrow$ Higher is better / $1-\text{NED}\downarrow$]: Percentage of system classes placed in maintainably sized microservices.
6. **CHD (Cohesion at Domain Level)** [$\uparrow$ Higher is better]: Average semantic Jaccard similarity across operation domain terms.
7. **CHM (Cohesion at Message Level)** [$\uparrow$ Higher is better]: Average Jaccard similarity across return types and parameter types.

---

## 10-Run Dynamic $K$ Metrics Summary Table across All Datasets

| Order | Metric Code | Metric Name | Spring PetClinic ($K=8$) | JPetStore-6 ($K=5$) | AcmeAir ($K=15$) | PlantsByWebSphere ($K=5$) | DayTrader 7 ($K=16$) | JForum ($K=19$) | JavaFX Point-of-Sales ($K=3$) | SpringBlog ($K=8$) | Apache Roller ($K=19$) | Bear Board ($K=5$) | Train Ticket ($K=18$) | DietApp ($K=8$) | IBM CICS GenApp ($K=13$) | AutoCare Nepal ($K=9$) | Pharmacy Management System ($K=11$) | Favorable Direction |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **SM** | Structural Modularity | **`0.022459`** | **`0.194863`** | **`0.088446`** | **`0.043116`** | **`0.028411`** | **`0.136679`** | **`0.097203`** | **`0.135779`** | **`0.104670`** | **`0.114975`** | **`0.074897`** | **`0.228221`** | **`0.013029`** | **`0.094460`** | **`0.090299`** | Higher is better |
| **2** | **ICP** | Inter-Call Pair / Coupling | **`0.086747`** | **`0.057539`** | **`0.081034`** | **`0.112823`** | **`0.119196`** | **`0.001639`** | **`0.017347`** | **`0.035505`** | **`0.000352`** | **`0.022071`** | **`0.000931`** | **`0.013115`** | **`0.010090`** | **`0.005012`** | **`0.022006`** | Lower is better |
| **3** | **BCP** | Business Use Case Entropy | **`1.045257`** | **`1.423184`** | **`1.176342`** | **`1.301031`** | **`1.428384`** | **`1.104741`** | **`1.784612`** | **`1.786906`** | **`0.991223`** | **`1.769419`** | **`1.341427`** | **`0.907923`** | **`0.416743`** | **`0.985789`** | **`1.127462`** | Lower is better |
| **4** | **IFN** | Interface Number | **`2.362500`** | **`3.080000`** | **`3.593333`** | **`5.340000`** | **`3.268750`** | **`4.152632`** | **`1.066667`** | **`2.762500`** | **`3.631579`** | **`2.240000`** | **`3.966667`** | **`1.850000`** | **`0.784615`** | **`0.900000`** | **`1.927273`** | Lower is better |
| **5** | **NED** | Non-Extreme Distribution | **`0.839535`** | **`0.950000`** | **`0.791011`** | **`0.925000`** | **`0.880153`** | **`0.108579`** | **`0.944118`** | **`0.866667`** | **`0.112348`** | **`0.948718`** | **`0.057729`** | **`0.846296`** | **`0.547727`** | **`0.812245`** | **`0.859322`** | Lower $1-\text{NED}$ |
| **6** | **CHD** | Cohesion at Domain Level | **`0.292898`** | **`0.211024`** | **`0.177063`** | **`0.348738`** | **`0.200535`** | **`0.314125`** | **`0.137681`** | **`0.307519`** | **`0.151989`** | **`0.337501`** | **`0.207772`** | **`0.359620`** | **`0.285749`** | **`0.271451`** | **`0.290528`** | Higher is better |
| **7** | **CHM** | Cohesion at Message Level | **`0.412571`** | **`0.294669`** | **`0.303102`** | **`0.445328`** | **`0.340841`** | **`0.490865`** | **`0.439458`** | **`0.382475`** | **`0.285331`** | **`0.455889`** | **`0.314477`** | **`0.461536`** | **`0.482201`** | **`0.401065`** | **`0.324738`** | Higher is better |

---

## Dataset-by-Dataset Decomposition Analysis

### 1. Spring PetClinic ($K=8$, $V=43$)
- **System Overview**: Classic Java Spring enterprise monolithic benchmark application for microservice decomposition, architecture recovery, and refactoring studies.
- **Dynamic Optimal Cluster Count**: $K=8$ (Score = `0.2510`)
- **Structural Modularity (SM)**: `0.022459 ± 0.011743`
- **Inter-Service Coupling (ICP)**: `0.086747 ± 0.014362`
- **Business Use Case Entropy (BCP)**: `1.045257 ± 0.099705`
- **Interface Complexity (IFN)**: `2.362500 ± 0.130504`
- **Non-Extreme Distribution (NED)**: `0.839535` *(1-NED: `0.160465`)*
- **Domain Cohesion (CHD)**: `0.292898 ± 0.015725`
- **Message Cohesion (CHM)**: `0.412571 ± 0.033695`
- **Links**: [`dataset/spring-petclinic/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/spring-petclinic) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/spring-petclinic/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/spring-petclinic/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/spring-petclinic/decomposition.json))

### 2. JPetStore-6 ($K=5$, $V=42$)
- **System Overview**: Reference e-commerce sample web application built with MyBatis, Spring, and JavaServer Pages.
- **Dynamic Optimal Cluster Count**: $K=5$ (Score = `0.4700`)
- **Structural Modularity (SM)**: `0.194863 ± 0.010931`
- **Inter-Service Coupling (ICP)**: `0.057539 ± 0.006234`
- **Business Use Case Entropy (BCP)**: `1.423184 ± 0.083973`
- **Interface Complexity (IFN)**: `3.080000 ± 0.160000`
- **Non-Extreme Distribution (NED)**: `0.950000` *(1-NED: `0.050000`)*
- **Domain Cohesion (CHD)**: `0.211024 ± 0.006504`
- **Message Cohesion (CHM)**: `0.294669 ± 0.021078`
- **Links**: [`dataset/jpetstore-6/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jpetstore-6) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jpetstore-6/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jpetstore-6/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jpetstore-6/decomposition.json))

### 3. AcmeAir ($K=15$, $V=89$)
- **System Overview**: Fictitious airline flight booking system benchmark originally created by IBM for cloud, monolithic, and microservice refactoring benchmarks.
- **Dynamic Optimal Cluster Count**: $K=15$ (Score = `0.2853`)
- **Structural Modularity (SM)**: `0.088446 ± 0.020269`
- **Inter-Service Coupling (ICP)**: `0.081034 ± 0.015588`
- **Business Use Case Entropy (BCP)**: `1.176342 ± 0.124866`
- **Interface Complexity (IFN)**: `3.593333 ± 0.222011`
- **Non-Extreme Distribution (NED)**: `0.791011` *(1-NED: `0.208989`)*
- **Domain Cohesion (CHD)**: `0.177063 ± 0.009572`
- **Message Cohesion (CHM)**: `0.303102 ± 0.018934`
- **Links**: [`dataset/acmeair/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/acmeair) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/acmeair/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/acmeair/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/acmeair/decomposition.json))

### 4. PlantsByWebSphere ($K=5$, $V=48$)
- **System Overview**: IBM sample enterprise e-commerce application demonstrating Java EE / WebSphere enterprise computing patterns.
- **Dynamic Optimal Cluster Count**: $K=5$ (Score = `0.2627`)
- **Structural Modularity (SM)**: `0.043116 ± 0.032918`
- **Inter-Service Coupling (ICP)**: `0.112823 ± 0.018323`
- **Business Use Case Entropy (BCP)**: `1.301031 ± 0.026644`
- **Interface Complexity (IFN)**: `5.340000 ± 0.200998`
- **Non-Extreme Distribution (NED)**: `0.925000` *(1-NED: `0.075000`)*
- **Domain Cohesion (CHD)**: `0.348738 ± 0.012231`
- **Message Cohesion (CHM)**: `0.445328 ± 0.013232`
- **Links**: [`dataset/plantsbywebsphere/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/plantsbywebsphere) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/plantsbywebsphere/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/plantsbywebsphere/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/plantsbywebsphere/decomposition.json))

### 5. DayTrader 7 ($K=16$, $V=131$)
- **System Overview**: Large-scale financial stock trading application based on the Apache Geronimo DayTrader benchmark suite.
- **Dynamic Optimal Cluster Count**: $K=16$ (Score = `0.2065`)
- **Structural Modularity (SM)**: `0.028411 ± 0.020788`
- **Inter-Service Coupling (ICP)**: `0.119196 ± 0.024768`
- **Business Use Case Entropy (BCP)**: `1.428384 ± 0.068982`
- **Interface Complexity (IFN)**: `3.268750 ± 0.176887`
- **Non-Extreme Distribution (NED)**: `0.880153` *(1-NED: `0.119847`)*
- **Domain Cohesion (CHD)**: `0.200535 ± 0.021257`
- **Message Cohesion (CHM)**: `0.340841 ± 0.023797`
- **Links**: [`dataset/daytrader7/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/daytrader7) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/daytrader7/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/daytrader7/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/daytrader7/decomposition.json))

### 6. JForum ($K=19$, $V=373$)
- **System Overview**: Full-featured, high-traffic discussion board / bulletin board system written in Java.
- **Dynamic Optimal Cluster Count**: $K=19$ (Score = `0.0789`)
- **Structural Modularity (SM)**: `0.136679 ± 0.007760`
- **Inter-Service Coupling (ICP)**: `0.001639 ± 0.000143`
- **Business Use Case Entropy (BCP)**: `1.104741 ± 0.078155`
- **Interface Complexity (IFN)**: `4.152632 ± 0.209801`
- **Non-Extreme Distribution (NED)**: `0.108579` *(1-NED: `0.891421`)*
- **Domain Cohesion (CHD)**: `0.314125 ± 0.019064`
- **Message Cohesion (CHM)**: `0.490865 ± 0.032527`
- **Links**: [`dataset/jforum/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jforum) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jforum/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jforum/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/jforum/decomposition.json))

### 7. JavaFX Point-of-Sales ($K=3$, $V=34$)
- **System Overview**: Interactive desktop point-of-sale management system built with JavaFX and SQLite.
- **Dynamic Optimal Cluster Count**: $K=3$ (Score = `0.3735`)
- **Structural Modularity (SM)**: `0.097203 ± 0.042354`
- **Inter-Service Coupling (ICP)**: `0.017347 ± 0.012156`
- **Business Use Case Entropy (BCP)**: `1.784612 ± 0.334619`
- **Interface Complexity (IFN)**: `1.066667 ± 0.133333`
- **Non-Extreme Distribution (NED)**: `0.944118` *(1-NED: `0.055882`)*
- **Domain Cohesion (CHD)**: `0.137681 ± 0.028785`
- **Message Cohesion (CHM)**: `0.439458 ± 0.080075`
- **Links**: [`dataset/javafx-pos/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/javafx-pos) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/javafx-pos/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/javafx-pos/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/javafx-pos/decomposition.json))

### 8. SpringBlog ($K=8$, $V=51$)
- **System Overview**: Modern blogging web application platform built on Spring Boot, Thymeleaf, and Spring Security.
- **Dynamic Optimal Cluster Count**: $K=8$ (Score = `0.3549`)
- **Structural Modularity (SM)**: `0.135779 ± 0.012892`
- **Inter-Service Coupling (ICP)**: `0.035505 ± 0.003026`
- **Business Use Case Entropy (BCP)**: `1.786906 ± 0.134089`
- **Interface Complexity (IFN)**: `2.762500 ± 0.162500`
- **Non-Extreme Distribution (NED)**: `0.866667` *(1-NED: `0.133333`)*
- **Domain Cohesion (CHD)**: `0.307519 ± 0.053975`
- **Message Cohesion (CHM)**: `0.382475 ± 0.049731`
- **Links**: [`dataset/springblog/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/springblog) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/springblog/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/springblog/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/springblog/decomposition.json))

### 9. Apache Roller ($K=19$, $V=575$)
- **System Overview**: Industrial-scale enterprise Java blog server powering large-scale production multi-user blogs.
- **Dynamic Optimal Cluster Count**: $K=19$ (Score = `0.0614`)
- **Structural Modularity (SM)**: `0.104670 ± 0.008873`
- **Inter-Service Coupling (ICP)**: `0.000352 ± 0.000109`
- **Business Use Case Entropy (BCP)**: `0.991223 ± 0.107783`
- **Interface Complexity (IFN)**: `3.631579 ± 0.471339`
- **Non-Extreme Distribution (NED)**: `0.112348` *(1-NED: `0.887652`)*
- **Domain Cohesion (CHD)**: `0.151989 ± 0.026595`
- **Message Cohesion (CHM)**: `0.285331 ± 0.028558`
- **Links**: [`dataset/roller/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/roller) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/roller/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/roller/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/roller/decomposition.json))

### 10. Bear Board ($K=5$, $V=39$)
- **System Overview**: Microblogging and social timeline collaboration service built on Spring MVC, Spring Data, and Redis.
- **Dynamic Optimal Cluster Count**: $K=5$ (Score = `0.3903`)
- **Structural Modularity (SM)**: `0.114975 ± 0.013992`
- **Inter-Service Coupling (ICP)**: `0.022071 ± 0.001347`
- **Business Use Case Entropy (BCP)**: `1.769419 ± 0.102146`
- **Interface Complexity (IFN)**: `2.240000 ± 0.080000`
- **Non-Extreme Distribution (NED)**: `0.948718` *(1-NED: `0.051282`)*
- **Domain Cohesion (CHD)**: `0.337501 ± 0.013226`
- **Message Cohesion (CHM)**: `0.455889 ± 0.002889`
- **Links**: [`dataset/bear-board/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/bear-board) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/bear-board/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/bear-board/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/bear-board/decomposition.json))

### 11. Train Ticket ($K=18$, $V=634$)
- **System Overview**: Comprehensive industrial-scale benchmark suite for railway ticket booking, payment, routing, and passenger management.
- **Dynamic Optimal Cluster Count**: $K=18$ (Score = `-0.0313`)
- **Structural Modularity (SM)**: `0.074897 ± 0.004745`
- **Inter-Service Coupling (ICP)**: `0.000931 ± 0.000188`
- **Business Use Case Entropy (BCP)**: `1.341427 ± 0.129017`
- **Interface Complexity (IFN)**: `3.966667 ± 0.470225`
- **Non-Extreme Distribution (NED)**: `0.057729` *(1-NED: `0.942271`)*
- **Domain Cohesion (CHD)**: `0.207772 ± 0.033057`
- **Message Cohesion (CHM)**: `0.314477 ± 0.028792`
- **Links**: [`dataset/train-ticket/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/train-ticket) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/train-ticket/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/train-ticket/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/train-ticket/decomposition.json))

### 12. DietApp ($K=8$, $V=54$)
- **System Overview**: Nutritional intake and health goal tracking application built with C# ASP.NET MVC and Entity Framework.
- **Dynamic Optimal Cluster Count**: $K=8$ (Score = `0.5475`)
- **Structural Modularity (SM)**: `0.228221 ± 0.023673`
- **Inter-Service Coupling (ICP)**: `0.013115 ± 0.004491`
- **Business Use Case Entropy (BCP)**: `0.907923 ± 0.117444`
- **Interface Complexity (IFN)**: `1.850000 ± 0.235850`
- **Non-Extreme Distribution (NED)**: `0.846296` *(1-NED: `0.153704`)*
- **Domain Cohesion (CHD)**: `0.359620 ± 0.050478`
- **Message Cohesion (CHM)**: `0.461536 ± 0.049761`
- **Links**: [`dataset/dietapp/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/dietapp) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/dietapp/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/dietapp/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/dietapp/decomposition.json))

### 13. IBM CICS GenApp ($K=13$, $V=44$)
- **System Overview**: General Insurance Enterprise Application benchmark written in COBOL for IBM CICS transaction processing systems.
- **Dynamic Optimal Cluster Count**: $K=13$ (Score = `0.2351`)
- **Structural Modularity (SM)**: `0.013029 ± 0.004040`
- **Inter-Service Coupling (ICP)**: `0.010090 ± 0.005302`
- **Business Use Case Entropy (BCP)**: `0.416743 ± 0.097424`
- **Interface Complexity (IFN)**: `0.784615 ± 0.219736`
- **Non-Extreme Distribution (NED)**: `0.547727` *(1-NED: `0.452273`)*
- **Domain Cohesion (CHD)**: `0.285749 ± 0.043238`
- **Message Cohesion (CHM)**: `0.482201 ± 0.060236`
- **Links**: [`dataset/cics-genapp/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/cics-genapp) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/cics-genapp/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/cics-genapp/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/cics-genapp/decomposition.json))

### 14. AutoCare Nepal ($K=9$, $V=49$)
- **System Overview**: Automobile maintenance, servicing, inventory, and customer invoicing workflow application.
- **Dynamic Optimal Cluster Count**: $K=9$ (Score = `0.3970`)
- **Structural Modularity (SM)**: `0.094460 ± 0.003452`
- **Inter-Service Coupling (ICP)**: `0.005012 ± 0.000978`
- **Business Use Case Entropy (BCP)**: `0.985789 ± 0.032680`
- **Interface Complexity (IFN)**: `0.900000 ± 0.152753`
- **Non-Extreme Distribution (NED)**: `0.812245` *(1-NED: `0.187755`)*
- **Domain Cohesion (CHD)**: `0.271451 ± 0.009920`
- **Message Cohesion (CHM)**: `0.401065 ± 0.022640`
- **Links**: [`dataset/autocare-nepal/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/autocare-nepal) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/autocare-nepal/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/autocare-nepal/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/autocare-nepal/decomposition.json))

### 15. Pharmacy Management System ($K=11$, $V=59$)
- **System Overview**: Pharmacy inventory, prescription handling, medicine billing, and supplier supply chain software.
- **Dynamic Optimal Cluster Count**: $K=11$ (Score = `0.3852`)
- **Structural Modularity (SM)**: `0.090299 ± 0.009377`
- **Inter-Service Coupling (ICP)**: `0.022006 ± 0.004053`
- **Business Use Case Entropy (BCP)**: `1.127462 ± 0.062338`
- **Interface Complexity (IFN)**: `1.927273 ± 0.145455`
- **Non-Extreme Distribution (NED)**: `0.859322` *(1-NED: `0.140678`)*
- **Domain Cohesion (CHD)**: `0.290528 ± 0.025079`
- **Message Cohesion (CHM)**: `0.324738 ± 0.024390`
- **Links**: [`dataset/pharmacy/`](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/pharmacy) ([README](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/pharmacy/README.md) | [Results JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/pharmacy/results.json) | [Decomposition JSON](file:///d:/Final%20Year%20Project/Cogcn_evalaution/dataset/pharmacy/decomposition.json))
