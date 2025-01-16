#!/usr/bin/python3

### Import modules ###
import os
import subprocess

### Define Functions ###

## Function for bash commands
def bash_command(str):
    result = subprocess.run(str, shell = True,capture_output = True,text = True)
    return result.stdout, result.stderr

### Main Module ###
print("=".center(100,"="))
print("Step 3: Scan motifs")
print("-".center(100,"-"))

directory1 = "output1_sequence"
directory2 = "output2_conservation"
directory3 = "output3_motifs"

## Extract each sequence from fasta file
# Get the base filename for subsequent rename
matching_files = [file for file in os.listdir(directory1) if file.endswith(".fasta")]
if matching_files:
    basename = matching_files[0].replace(".fasta", "") 

# Split the fasta file
fas = f"{directory2}/{basename}_aligned.fasta"
with open(fas, "r") as file:
    fasta_data = file.read()
seq_list = fasta_data.split(">")[1:] # remove first element
for seq in seq_list:
    lines = seq.strip().split('\n')  # split each sequence
    seq_id = lines[0].split()[0] # extract sequence id
    seq_info = lines[0]
    seq_data = '\n'.join(lines[1:])  # extract the sequence
    with open(f"{directory3}/{seq_id}.fasta", "w") as f:
        f.write(f">{seq_info}\n{seq_data}")
print("Sequences extracted from fasta file.")

## Run patmatmotifs for each extracted sequence
fas_list = os.listdir(directory3)
for fas in fas_list:
    motifs_in = directory3+"/"+fas
    motifs_out = directory3+"/"+fas.replace(".fasta","_motifs.txt")
    patmatmotifs_command = f"patmatmotifs -sequence {motifs_in} -outfile {motifs_out} -full "
    patmatdb_out, patmat_error = bash_command(patmatmotifs_command)
print(f"Motif scan for all sequences done.")

## Process motif scan results
output_list = os.path.join(directory3, f"{basename}_motifs_list.txt")
with open(output_list, 'w') as output:
    output.write("Sequence_ID\tMotif\tHitCount\n")  # Write header to the output file

    for filename in os.listdir(directory3):
        if filename.endswith('_motifs.txt'):
            sequence_id = filename.replace("_motifs.txt", "")

            # Variables to store HitCount and Motif information
            hit_count = None
            motifs = []

            with open(os.path.join(directory3, filename), 'r') as file:
                for line in file:
                    if 'HitCount' in line:
                        hit_count = line.split()[-1]
                    elif line.startswith('Motif'):
                        motifs.append(line.split()[-1])

            # Write the information to the output file
            output.write(f"{sequence_id}\t")
            if motifs:
                output.write(f"{', '.join(motifs)}\t")
            else:
                output.write("/\t")
            if hit_count:
                output.write(f"{hit_count}\n")
            else:
                output.write("/\n")

print(f"List of motifs found in each sequence saved to {directory3}/")

## Remove unnecessary files from previous substeps
files = os.listdir(directory3)
for item in files:
    if item.endswith(".fasta") or item.endswith("_motifs.txt"):
        os.remove(os.path.join(directory3, item))
