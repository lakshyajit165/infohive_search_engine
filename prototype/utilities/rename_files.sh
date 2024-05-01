#!/bin/bash

# Change to the directory containing the .txt files
cd "$(dirname "$0")"

# Loop through each .txt file in the directory
for file in *.txt; do
    # Remove the numbers and dash from the beginning of the filename
    new_name=$(echo "$file" | sed 's/^[0-9]* - //')

    # Rename the file
    mv "$file" "$new_name"
done

echo "File renaming complete."
