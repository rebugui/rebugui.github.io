---
title: "🧬 Spatial Proteomics: 간 Zonation 패턴 매핑과 조직 손상 분석"
date: 2026-04-19T08:06:06+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

인간의 간(Liver)은 단순한 해독 기관을 넘어, 놀라운 재생 능력과 대장 내 세균 및 영양소 처리를 담당하는 복잡한 생화학 공장입니다. 그러나 만성 간 질환, 간경변, 또는 화학적 손상이 발생했을 때, 의학계가 가장 먼저 직면하는 난관은 **"조직 구조(Tissue Architecture)의 붕괴"**입니다. 간세포들이 제 기능을 잃는 것도 문제지만, 그들이 정교하게 배치된 공간적 질서(Zonation)가 무너지는 현상은 질병의 진행을 예측하고 치료 전략을 세우는 데 있어 결정적인 키가 됩니다.

전통적인 생물학 연구는 조직을 갈아서 분석(Bulk analysis)하거나, 단일 세포 수준에서 유전자를 분석(scRNA-seq)하는 데 집중해 왔습니다. 하지만 이 방식들은 세포가 **"어디에 위치해 있었는가(Where)"**라는 필수적인 맥락을 소거해 버리는 치명적인 단점이 있습니다. 문맥이 없는 세포는 해외에서 표류하는 여행자와 같습니다. 그래서 최근 AI/ML 바이오인포매틱스 분야에서는 단백질 수준에서 세포의 위치와 발현 정보를 동시에 포착하는 **Spatial Proteomics(공간 단백체학)**가 뜨거운 감자로 떠오르고 있습니다. 본 글에서는 최신 Nature 논문에서 제시된 Single-cell Spatial Proteomics 기술을 활용하여 간의 Zonation 패턴을 매핑하고, 조직 손상 시 발생하는 취약성을 분석하는 과정을 기술적 관점에서 심도 있게 다루고자 합니다.

## 본론: 공간 정보가 융합된 단백체학 분석

### 기술적 원리: Imaging Mass Cytometry (IMC)와 딥러닝

이 연구의 핵심은 **Imaging Mass Cytometry (IMC)** 기술입니다. 기존의 형광 현미경이 색깔의 조합으로 단백질을 식별하는 것과 달리, IMC는 금속 동위원소로 표지된 항체를 사용합니다. 이를 통해 채널 간 간섭(Spectral overlap) 없이 40개 이상의 단백질 마커를 동시에 검출할 수 있습니다.

여기에 컴퓨터 비전(Computer Vision)과 딥러닝 기반의 **세포 분할(Segmentation)** 알고리즘이 결합됩니다. 고해상도 이미지에서 개별 세포의 경계를 식별하고, 각 세포 내 단백질의 발현 강도를 정량화하여 `(Cell_ID, X_Coord, Y_Coord, Protein_Values)` 형태의 구조화된 데이터를 생성합니다. 이 데이터는 마치 픽셀이 세포로 대체된 '고해상도 디지털 맵'과 같습니다.

### 데이터 분석 파이프라인

공간 단백체학 분석은 단순한 이미지 처리가 아닌, 고차원 데이터의 차원 축소와 공간 통계학이 결합된 복잡한 파이프라인을 따릅니다. 아래 다이어그램은 조직 샘플부터 Zonation 패턴 도출까지의 전체 과정을 요약한 것입니다.

```javascript
graph TD
    A[조직 샘플 채취] --> B[금속 동위원소 항체 staining]
    B --> C[IMC 스캐닝]
    C --> D[딥러닝 기반 세포 분할]
    D --> E[단백질 발현 행렬 추출]
    E --> F[차원 축소 및 정규화]
    F --> G[Leiden Clustering]
    G --> H[세포 유형 주석]
    H --> I[공간 좌표 매핑]
    I --> J[Zonation Gradient 분석]
    J --> K[조직 손상 패턴 발견]
```

이 파이프라인에서 가장 중요한 단계는 **Clustering**과 **Spatial Mapping**입니다. 수만 개의 세포를 UMAP(Uniform Manifold Approximation and Projection) 등의 알고리즘으로 차원 축소한 뒤, Leiden 알고리즘을 통해 군집화합니다. 이후 각 세포의 원래 `(x, y)` 좌표를 복원하여, 특정 세포군이 간 소엽(Lobule) 내에서 어떤 위치를 차지하는지 시각화합니다.

### 기술 비교: Spatial Proteomics vs. scRNA-seq

연구자들이 Spatial Proteomics를 선택하는 이유는 명확합니다. 아래 표는 기존 단일 세포 RNA 시퀀싱과 공간 단백체학 기술의 차이점을 비교한 것입니다.

| 비교 항목 | scRNA-seq (단일 세포 RNA 시퀀싱) | Spatial Proteomics (IMC/MIBI) |
| :--- | :--- | :--- |
| **측정 대상** | mRNA (전사체 수준) | Protein (번역체 수준) |
| **공간 정보 보존** | ❌ 원래 위치 파괴됨 (Dissociated) | ✅ 조직 내 위치 정보 보존 |
| **데이터 특성** | 유전자 발현 벡터 (High dropout) | 단백질 발현 벡터 (Clean signal) |
| **세포 간 상호작용** | 추론(Inference)에 의존 | 직접 관찰 가능 |
| **주요 활용 분야** | 새로운 세포 유형 발견 | Tissue Microenvironment 분석 |

### Python을 활용한 공간 Zonation 분석 구현

실제 연구 환경에서는 `Scanpy`나 `Squidpy` 같은 Python 라이브러리를 사용하여 분석을 수행합니다. 아래 코드는 IMC 데이터를 로드하여 차원 축소를 수행하고, 공간 좌표를 기반으로 Zonation 패턴을 시각화하는 간단한 예시입니다.

```python
import scanpy as sc
import squidpy as sq
import numpy as np
import matplotlib.pyplot as plt

# 1. 가상의 IMC 데이터 생성 (실제로는 .mcd 파일에서 추출)
# n_obs: 세포 수, n_vars: 단백질 마커 수 (예: 40개)
n_cells = 5000
n_proteins = 40
adata = sc.AnnData(X=np.random.negative_binomial(5, 0.3, size=(n_cells, n_proteins)))
adata.var_names = [f"Protein_{i}" for i in range(n_proteins)]

# 2. 공간 좌표 (Spatial Coordinates) 설정
# 간 소엽 구조를 모방하기 위해 원형 분포 가정
r = np.sqrt(np.random.uniform(0, 1, n_cells))
theta = np.random.uniform(0, 2*np.pi, n_cells)
x = r * np.cos(theta) * 100
y = r * np.sin(theta) * 100
adata.obsm["spatial"] = np.column_stack((x, y))

# 3. 데이터 전처리 및 정규화
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=20)

# 4. 차원 축소 (PCA -> UMAP)
sc.tl.pca(adata)
sc.pp.neighbors(adata, n_pcs=10)
sc.tl.umap(adata)

# 5. Clustering (Leiden Algorithm)
sc.tl.leiden(adata, resolution=0.5)

# 6. 공간 Zonation 시각화
# 중심(Central Vein)에서 주변(Portal Triad)으로 퍼지는 패턴 확인
plt.figure(figsize=(10, 8))
sc.pl.spatial(
    adata, 
    color=["leiden", "Protein_0", "Protein_1"], 
    size=20, 
    img_key=None, 
    show=False
)
plt.title("Spatial Zonation Map of Liver Tissue")
plt.show()

# 7. 공간 통계 분석 (Spatial Autocorrelation)
# 특정 단백질이 공간적으로 군집을 이루는지 Moran's I 계수로 확인
sq.gr.spatial_autocorr(
    adata, 
    mode="moran", 
    n_perms=100, 
    n_jobs=1
)
print(adata.uns["moranI"].head())
```

이 코드는 각 세포가 단순히 분류되는 것을 넘어, **"어떤 단백질이 공간적으로 서로 인접해 발현하는가"**를 분석합니다. 예를 들어, 건강한 간에서는 특정 효소 중앙 정맥(Central Vein) 근처에만 집중되어야 하는데, 손상된 조직에서는 이 패턴이 무작위(Random noise)로 변질되는 것을 포착할 수 있습니다.

### Step-by-step: 조직 손상 패턴 분석 가이드

연구자는 다음과 같은 절차를 통해 조직 손상을 정량화합니다.

1.  **ROI(Region of Interest) 정의**: 정상적인 간 소염 구조가 유지되는 영역과 섬유화(Fibrosis)나 괴사가 진행된 영역을 이미지 상에서 분할합니다.
2.  **공간 그래프 구축**: 세포 간의 물리적 거리를 기반으로 K-Nearest Neighbor 그래프를 생성합니다. 이는 세포 간 커뮤니케이션 네트워크를 의미합니다.
3.  **Zonation Score 계산**: Portal Triad에서 Central Vein으로 향하는 방향성에 따라 세포의 표현형이 점진적으로 변하는지 스코어링합니다 (예: Gradient Scoring).
4.  **이상치 탐지**: 정상 Zonation Gradient에서 벗어난 세포들을 이상치로 간주합니다. 예를 들어, 중심부에 있어야 할 세포가 말초부 특성을 보이는 경우입니다.
5.  **손상 정량화**: 정상적인 공간 질서를 잃은 비율을 백분율로 환산하여 조직 손상 지수(Damage Index)를 산출합니다.

이 방식은 단순히 "세포가 죽었는지"를 넘어, **"사회적 구조가 붕괴되었는지"**를 판단하기 때문에 질병의 조기 진단에 훨씬 강력한 도구가 됩니다.

## 결론

이번 연구는 Spatial Proteomics가 단순한 정지 화면 이상의 **역동적인 생물학적 맥락**을 제공함을 입증했습니다. 간의 Zonation 패턴은 세포의 위치와 기능이 분리될 수 없음을 보여주는 대표적인 사례입니다. AI/ML 기술, 특히 고차원 공간 데이터 분석 알고리즘은 이러한 복잡한 생물학적 패턴에서 인간의 눈으로는 식별하기 힘든 미세한 변화를 포착해 냈습니다.

전문가 관점에서 볼 때, 향후 이 기술의 핵심은 **MLOps 파이프라인의 자동화**에 있습니다. 임상 현장에서 병리 조직 분석이 실시간으로 이루어기 위해서는, IMC 스캔부터 세포 분할, Zonation 분석까지의 과정이 End-to-End로 자동화되어야 합니다. 또한, 단백질 데이터와 공간 데이터를 융합하여 조직의 3D 구조를 복원하는 생성형 AI(Generative AI) 모델의 개발도 기대해 볼 수 있습니다.

결론적으로, 우리는 이제 세포를 "읽는(Read)" 단계를 넘어, 세포가 살아가는 "공간(Context)"을 "해석(Interpret)"하는 시대에 접어들었습니다. 조직학과 딥러닝의 만남은 난치성 간 질환의 메커니즘을 규명하고, 개인화된 치료법을 설계하는 강력한 나침반이 될 것입니다.

### 참고자료
- *Nature Paper*: Single-cell spatial proteomics maps human liver zonation patterns and their vulnerability to disruption in tissue architecture.
- *Tools*: Scanpy (Single-cell analysis in Python), Squidpy (Spatial analysis), Imaging Mass Cytometry (Standard Bio-protocols).

---

**출처**: [https://news.google.com/rss/articles/CBMiX0FVX3lxTFBsMVY1azZ4dXJ1aFk4akhsWFB2VlJZa211dTdyZWxGY09RQWxrT01XdWJPMjk2RVhsQ0RlLWtOaEE0SzZRMHFDMXZNNWRNMlQ0REw4TS11YjZXVmh5ZHlB?oc=5](https://news.google.com/rss/articles/CBMiX0FVX3lxTFBsMVY1azZ4dXJ1aFk4akhsWFB2VlJZa211dTdyZWxGY09RQWxrT01XdWJPMjk2RVhsQ0RlLWtOaEE0SzZRMHFDMXZNNWRNMlQ0REw4TS11YjZXVmh5ZHlB?oc=5)