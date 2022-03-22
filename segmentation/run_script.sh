#!/bin/bash

studies="Human_Aging" #"Human_Lung_Atlas" #
subjects="AGING004 AGING038"
protocols="Expn5x5" #"Insp"

for study in $studies
do
  for subject in $subjects
  do
    for protocol in $protocols
    do
      #mkdir -p /hpc/mpag253/Torso/segmentation/Human_Aging/AGING063/Insp/Raw
      #unzip Human_Aging/AGING054/Insp/Raw/Archive.zip -d /hpc/mpag253/Torso/segmentation/Human_Aging/AGING054/Insp/Raw
      mkdir -p /hpc/mpag253/Torso/segmentation/${study}/${subject}/${protocol}/Raw
      #unzip /groups/lung/Data/${study}/${subject}/${protocol}/Raw/Archive.zip -d /hpc/mpag253/Torso/segmentation/${study}/${subject}/${protocol}/Raw
      unzip /groups/lung/Data/${study}/${subject}/${protocol}/Raw/*.zip -d /hpc/mpag253/Torso/segmentation/${study}/${subject}/${protocol}/Raw
      #echo "python surface_fit_torso.py -s ${study} -c ${subject} -p ${protocol} -t ${action}"
    done #protocol
  done #subject
done #study

# to run:
# chmod u+x run_script.sh         --- JUST ONCE
# sed -i 's/\r$//' run_script.sh  --- EVERY TIME!!!!
# bash run_script.sh