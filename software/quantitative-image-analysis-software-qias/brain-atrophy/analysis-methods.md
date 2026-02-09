# Analysis Methods

## Segmentation

The anatomical segmentation is performed using FreeSurfer's default cortical and subcortical parcellation method. More information can be found here: [https://surfer.nmr.mgh.harvard.edu/fswiki](https://surfer.nmr.mgh.harvard.edu/fswiki)

The outputs include a label volume which assigns each intracranial voxel into a class, such as cortex, white matter, ventricle, hippocampus, etc, and a text file with segmentation statistics, such as the volume of each segmented structure.

## Model generation and individual patient comparison

There are models for calculating normative percentiles for total (left + right) hippocampal volume, hippocampal occupancy score (REF), and total (left + right) inferior lateral ventricle volume as a percent of total intracranial volume. These are general additive models (GAMs) created using the R package gamlss, from a total of XXX cognitively normal subjects from the ADNI phase 3 cohort. The normative percentiles calculated from these models are based on the age and sex of the patient.

## Report generation

A final report is generated using the LaTeX typesetting software, which combines patient information, representative segmentation images, patient morphometry statistics and plots into an easy-to-read and distribute PDF (see example on the introduction webpage of the Brain Atrophy software).
