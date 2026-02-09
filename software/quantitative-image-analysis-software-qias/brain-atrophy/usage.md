# Usage

The software is a script run from the command line, currently tested on Ubuntu 18.04.&#x20;

The main script is qias\_brain\_atrophy.sh located in the qiasbrainatrophy/scripts subdirectory of the qias project. At the command line while in the scripts directory, type ./qias\_brain\_atrophy.sh and include required and any desired optional argument&#x73;_._ Use the -h or --help flag for a description of script usage.

Dependencies for the script include:

* Freesurfer, version 6.0 or greater
  * Freeview, included with Freesurfer
* DCMTK
* R
  * gamlss
* Python, version 3.0 or greater
  * numpy
  * itk
* Latex and pdfLatex

The entire program takes approximately 4 hours to run on a standard desktop computer. The majority of this run time is due to the FreeSurfer segmentation.
