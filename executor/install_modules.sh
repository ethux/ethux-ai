#!/bin/bash

# Loop through all modules
for dir in */; do
        # Install the module with pip
        echo "Installing module in $dir"
        pip install "$dir"
        if [ $? -eq 0 ]; then
            echo "Successfully installed $dir"
        else
            echo "Failed to install $dir" >&2
        fi
done