#!/bin/bash

# Define the zip files and their base names for zipping, splitting, and assembling
zip_files=("oct_large.zip" "ico_large.zip")
base_names=("oct_large" "ico_large")

for i in "${!zip_files[@]}"; do
  # Check if a folder with the base name exists
  if [[ -d "${base_names[i]}" ]]; then
    echo "Zipping folder ${base_names[i]}..."
    zip -r "${zip_files[i]}" "${base_names[i]}"
    echo "Deleting folder ${base_names[i]}..."
    rm -rf "${base_names[i]}"
  fi

  if [[ -f "${zip_files[i]}" ]]; then
    # If the zip file exists, split it into 100MB chunks
    echo "Splitting ${zip_files[i]} into 100MB chunks..."
    split -b 100M "${zip_files[i]}" "${base_names[i]}_part_"
  else
    # If the zip file doesn't exist, try to reassemble it from its chunks
    echo "Assembling ${zip_files[i]} from chunks..."
    cat "${base_names[i]}_part_"* > "${zip_files[i]}"
    # After assembling, unzip the file
    if [[ -f "${zip_files[i]}" ]]; then
      echo "Unpacking ${zip_files[i]}..."
      unzip "${zip_files[i]}"
    fi
  fi
done

echo "Operation completed."

