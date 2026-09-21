* Reproduce the experimenter-demand statistics quoted in the manuscript.
version 17
args output_csv
do 00_setup.do
do "${code_folder}/Helpers/load_expdemand_data.do" "${data_folder}"
do "${code_folder}/Helpers/test_expdemand_subgroups.do" "$controls" "`output_csv'"
