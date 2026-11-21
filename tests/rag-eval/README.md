# RAG 固定评测集（任务1）

## 内容

- `questions_134.json`：134 个问题，18 条案例 × 6 类 + 12 深测 + 8 干扰 + 5 鲁棒 + 2 对照。
- `results_aliyun_20261107.csv`：阿里云 text-embedding-v1 的逐题结果。
- `results_local_20261024.csv`：本地 shibing624_text2vec-base-chinese 的 36 问结果。
- `tools/build_kb_docs.py`：把 fewcases.json 生成 MaxKB 导入文件（一字段一文件）。

## 环境

| 项 | 值 |
|---|---|
| MaxKB | v2.10.3-lts，本地部署 |
| 向量模型（阿里云版） | text-embedding-v1 |
| 向量模型（本地版） | shibing624_text2vec-base-chinese |
| 相似度阈值 | 0.6 |
| 知识库 | 18 条案例 / 125 个分段 / 610 条关联问题 |

## 口径

- 通过：正确分段相似度 ≥ 0.6；
- Top3 命中：正确分段进入前三条；
- MRR：正确分段排名倒数（第1名=1，未命中=0）的平均；
- Top1 同案例：首条结果的案例编号与提问一致。

## 复跑

1. 用 `tools/build_kb_docs.py build fewcases.json --out maxkb_out --mode section` 生成导入文件；
2. 导入 MaxKB，生成关联问题，向量化；
3. 调用 `/admin/api/workspace/default/knowledge/{id}/hit_test`，参数
   `{"query_text": "...", "similarity": 0, "top_number": 20, "search_mode": "embedding"}`；
4. 按 `questions_134.json` 逐题执行，结果按 `similarity` 降序后统计。

模型、知识库或分段策略变化后需重跑本评测集。
