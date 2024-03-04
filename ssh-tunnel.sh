#!/bin/bash
# Autor: Gabriel Goes
# Date: 2024-02-14
# Version: 0.1
# ~/projetos/map_dir/ssh-tunnel.sh
# Description: This script creates an SSH tunnel to the sismo.ipt.br server
#             using the user's private key. The user must enter the ID of the
#             computer to which the tunnel will be created (MC, IT, SP, PB, BC).
#             The ID is used to determine the port number to be used in the tunnel.
#             The user must have the private key in the ~/.ssh/id_rsa file.
#             The user must have the public key in the ~/.ssh/authorized_keys file
#             on the sismo.ipt.br server.

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
    echo "!Conexão encerrada!"
else
    echo "Invalid ID. Please enter MC, IT, SP, PB, or BC."
fi
