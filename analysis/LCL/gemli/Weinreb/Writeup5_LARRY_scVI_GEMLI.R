rm(list=ls())

library(Seurat)
library(GEMLI)
library(HiClimR) # or else GEMLI cannot find fastCor

out_folder <- "~/kzlinlab/projects/scContrastiveLearn/out/kevin/Writeup5/"
load(paste0(out_folder, "Larry_41093_2000_norm_log_cleaned.RData"))

date_of_run <- Sys.time()
session_info <- devtools::session_info()

code_folder <- "~/kzlinlab/projects/scContrastiveLearn/git/SCSeq_LineageBarcoding_kevin/kevin/Writeup5_GEMLI/"
source(paste0(code_folder, "predict_lineages_custom.R"))
source(paste0(code_folder, "quantify_clusters_iterative_custom.R"))
source(paste0(code_folder, "test_lineages_custom.R"))

# run GEMLI
data_matrix <- read.csv(paste0(out_folder, "Larry_scvi_full_embeddings.csv"))
data_matrix <- as.matrix(data_matrix)
rownames(data_matrix) <- Seurat::Cells(seurat_obj)
colnames(data_matrix) <- paste0("scVI_", 1:ncol(data_matrix))
seurat_obj[["scVI"]] <- Seurat::CreateDimReducObject(data_matrix)

# first filter to the top 50 lineages
lineage_tab <- table(seurat_obj$clone_id)
largest_lineages <- names(lineage_tab)[order(lineage_tab, decreasing = TRUE)[1:50]]
keep_vec <- rep(FALSE, length(Seurat::Cells(seurat_obj)))
keep_vec[seurat_obj$clone_id %in% largest_lineages] <- TRUE
seurat_obj$keep <- keep_vec
seurat_obj <- subset(seurat_obj, keep == TRUE)

# run GEMLI
data_matrix <- t(seurat_obj[["scVI"]]@cell.embeddings)

GEMLI_items <- list()
GEMLI_items[['gene_expression']] <- data_matrix
GEMLI_items[['barcodes']] <- seurat_obj$clone_id

set.seed(10)
GEMLI_items <- predict_lineages_custom(GEMLI_items,
                                       bool_find_markers = FALSE,
                                       desired_cluster_size = c(50,200),
                                       verbose = 4)

save(date_of_run, session_info,
     GEMLI_items,
     file = paste0(out_folder, "Writeup5_Larry_scVI_GEMLI.RData"))

GEMLI_items <- test_lineages_custom(GEMLI_items, 
                                    valid_fam_sizes = c(50,200))
GEMLI_items$testing_results

save(date_of_run, session_info,
     GEMLI_items,
     file = paste0(out_folder, "Writeup5_Larry_scVI_GEMLI.RData"))

###############

plot_folder <- "~/kzlinlab/projects/scContrastiveLearn/git/SCSeq_LineageBarcoding_kevin/fig/kevin/Writeup5/"

total_true <- GEMLI_items$testing_results["0","TP"]
total_false <- GEMLI_items$testing_results["0","FP"]

tpr <- GEMLI_items$testing_results[,"TP"]/total_true
fpr <- GEMLI_items$testing_results[,"FP"]/total_false

png(paste0(plot_folder, "Writeup5_LARRY_scVI_GEMLI_ROC.png"),
    height = 1200, width = 1200, units = "px", res = 300)
plot(x = fpr,
     y = tpr,
     xlim = c(0,1),
     ylim = c(0,1),
     xlab = "FPR",
     ylab = "TPR",
     pch = 16)
lines(fpr, tpr)
lines(c(0,1), c(0,1), col = 2, lwd = 2, lty = 2)
graphics.off()

