# Lineage-aware_CL

## dependicys 

## Example Usage

An example usage file of how to LCL model is available in this repository. You can view it [here](https://github.com/SZ-yang/Lineage-aware_CL/blob/main/example_usage.ipynb).


## File Organization

```text
main/                                # Python scripts to train and run LCL

analysis/
├── data_processing/                 # Preprocessing and dataset construction
│   ├── cellTag/
│   ├── cellTagMulti/
│   ├── cellTag_cellTagMulti_Integration/
│   └── LARRY/
│
├── LCL/                             # Core LCL experiments and analyses
│   ├── train_test/                  # Train/test split: KNN & KL divergence (Sections 5.2–5.3)
│   ├── train_test_unseen_lineage/   # Supplementary unseen-lineage generalization 
│   ├── simulation/                  # Pseudo-real simulations (Section 5.1)
│   ├── gemli/                       # GEMLI comparisons and memory gene analyses (Section 5.4)
│   ├── gsea/                        # Cospar and GSEA analyses
│   └── plotting/                    # Figure generation
│
├── scVI/                            # scVI baseline experiments
├── supUMAP/                         # Supervised UMAP baseline
├── variancePartition/               # Supplementary variance analyses
│
example_usage.ipynb                  # Minimal example: training LCL on a new dataset
```