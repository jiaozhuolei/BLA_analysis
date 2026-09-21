suppressPackageStartupMessages(library(ComplexHeatmap))
suppressPackageStartupMessages(library(circlize))

# ===============================
# 1️⃣ 颜色函数
# ===============================
col_fun = colorRamp2(c(0, 2000), c("white", "red"))

# ===============================
# 2️⃣ 读取主数据
# ===============================
dfdata = read.table(
  "POA_top71.csv",
  row.names = "X",
  header = TRUE,
  sep = ",",
  stringsAsFactors = FALSE
)

# ===============================
# 3️⃣ 读取 x轴分组 label 表
# ===============================
dfindex = read.table(
  "mPOA_neurons_label.csv",
  row.names = "X",
  header = TRUE,
  sep = ",",
  stringsAsFactors = FALSE
)

# ===============================
# 4️⃣ 按 dfdata 列顺序对齐（关键步骤）
# ===============================
dfindex = dfindex[colnames(dfdata), , drop = FALSE]

# 一致性检查（建议保留）
stopifnot(all(rownames(dfindex) == colnames(dfdata)))

# ===============================
# 5️⃣ 构建列分组（1 / 2 / 3）
# ===============================
column_group = factor(
  dfindex$label,
  levels = c(1, 2, 3),
  labels = c("Group1", "Group2", "Group3")
)

# 可选：顶部 annotation
ha = HeatmapAnnotation(
  Group = column_group,
  col = list(Group = c(
    "Group1" = "#4DBBD5",
    "Group2" = "#E64B35",
    "Group3" = "#00A087"
  ))
)

# ===============================
# 6️⃣ 画热图
# ===============================
pdf("Fig1f_final.pdf", width = 16, height = 8)

ht = Heatmap(
  dfdata,
  col = col_fun,
  cluster_rows = FALSE,
  cluster_columns = FALSE,
  column_split = column_group,
  show_column_names = FALSE,
  column_gap = unit(1, "mm"),
  border = TRUE,
  top_annotation = ha
)

draw(ht)
dev.off()