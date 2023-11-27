#!/bin/bash

# Define the ID_dict dictionary
declare -A ID_dict
ID_dict["MC"]="8091"
ID_dict["IT"]="8091"
ID_dict["SP"]="8085"
ID_dict["PB"]="8093"
ID_dict["BC"]="8089"

# Read the ID as a variable
read -p "Enter the ID (MC, IT, SP, PB, BC): " ID

# Check if the ID is in the dictionary
if [ -n "${ID_dict[$ID]}" ]; then
    # Use the ID to determine the port number
    PORT="${ID_dict[$ID]}"
    
    # Create an SSH tunnel
    ssh -L "$PORT:localhost:$PORT" gabrielgoes@sismo.ipt.br -i ~/.ssh/id_rsa -N
else
    echo "Invalid ID. Please enter MC, IT, SP, PB, or BC."
fi
