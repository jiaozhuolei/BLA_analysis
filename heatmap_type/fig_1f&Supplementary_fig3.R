suppressPackageStartupMessages(library(ComplexHeatmap))
library(cluster)
suppressPackageStartupMessages(library(dendextend))
suppressPackageStartupMessages(library(circlize))


col_fun = colorRamp2(c(0,6000), c("white","red")) # for fig1 f

# col_fun = colorRamp2(c(0,60), c("white","red")) # for Supplementary Fig3
# col_fun = colorRamp2(c(0,1000, 2000), c( "white","yellow", "red"))
col_fun(seq(-2, 2))

#for fig1 f
dfdata = read.table("bilateral_top43.csv",row.names = "X",header = TRUE,sep = ",")

#for figs 5
# dfdata = read.table("all_neurons_terminal_terminal_number_Supplementary_fig3_sort.csv",row.names = "X",header = TRUE,sep = ",")

dfcol = read.table("BLA_3_plot_43.csv",row.names = "X",header = TRUE,sep = ",")
dflabel = read.table("BLA_geno_location2.csv",row.names = "X",header = TRUE,sep = ",")

dfdist = read.table("morphology_matrix39.csv",row.names = "X",header = TRUE,sep = ",")
d = as.dist(dfdist)
dend_rows = as.dendrogram(hclust(d,"ward.D2"))

dflabel$geno <- as.factor(dflabel$geno)
dflabel$location <- as.factor(dflabel$location)

geno_colors <- c('Crh'='red','Vglut1'='#107010','Sst'='#0000ff')
  

location_colors <- c(
   'BLAa' = 'yellow',
   'BLAp' = 'pink',
   'BLAv' = 'gray'

)


ha = HeatmapAnnotation(
  geno = dflabel$geno,
  location = dflabel$location,
  col = list(geno = geno_colors,location = location_colors),
  annotation_legend_param = list(
    geno = list(
      title = "Geno",
      at = names(geno_colors),
      labels = names(geno_colors)
)
      
    ),
    location = list(
      title = "Location",
      at = names(location_colors),
      labels = names(location_colors)
      # colors = location_colors
    )
  )

 
pdf("Fig1f6.pdf", width = 6, height = 8.6)
ht = Heatmap(t(dfdata),col = col_fun,cluster_columns = dend_rows,
             column_split = 5,show_column_names = FALSE,
             row_split = t(dfcol),row_gap = unit(0.8, "mm"),
             column_gap = unit(0.8, "mm"),border = TRUE,
             cluster_rows = FALSE,top_annotation = ha)
draw(ht)
dev.off()

