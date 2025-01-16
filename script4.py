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
print("Step 4: Phylogenetic tree")
print("-".center(100,"-"))

directory1 = "output1_sequence"
directory2 = "output2_conservation"
directory4 = "output4_phylogeny"

## Detect number of final result directories in current directory

current_directory = os.getcwd()
# Get the list of directories in the current directory
subdirectories = [d for d in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, d))]
# Filter subdirectories that contain "_in_" in their names
matching_directories = [dir for dir in subdirectories if "_in_" in dir]
# Get the base filename form temporary output of current session
matching_files = [file for file in os.listdir(directory1) if file.endswith(".fasta")]
if matching_files:
    basename = matching_files[0].replace(".fasta", "")
# Check if there are any directories in matching_directories with the same name as basename
basename_match_dirs = [dir_name for dir_name in matching_directories if dir_name == basename]
# Include current temporary output directory in the selection list
if not basename_match_dirs: # include directory1 only if the search query is different from previous search
    matching_directories.append(directory1)
else: # Replace the matching directory with directory1
    matching_directories = [directory1 if dir_name == basename else dir_name for dir_name in matching_directories]
# Count the number of matching subdirectories
num_matching_directories = len(matching_directories)

## Phylogenetic tree

if num_matching_directories == 1:
    # Construct phylogenetic tree for current session
    # Run ClustalW
    clustalw_input = f"4\n1\n{directory2}/{basename}_aligned.fasta\n5\n{directory4}/{basename}.phb\n100\n1000\n\nx\n"
    clustalw_command = f"clustalw"
    print("Reconstructing phylogenetic tree...")
    process = subprocess.Popen(clustalw_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(clustalw_input)
    if stderr:
        print(stderr)
    else:
        print(f"Phylogenetic tree has been saved to {directory4}/")
    print("NB: You can construct a phylogenetic tree with sequences from multiple queries by running the programme multiple times with different queries (e.g. same protein in different taxonomic groups).")
    print("    To do this, you will need to choose current working directories as final result output directory in the next step.")
    print("    You will be able to export all the results later.")

else:
    # Display matching directories and let user to choose
    print("NCBI search results saved in working directory:")
    for index, dir_name in enumerate(matching_directories, start=1):
        if dir_name == directory1:
            print(f"{index}. {basename}")
        else:
            print(f"{index}. {dir_name}")

    while True:
        user_choices = input(f"Choose the results you want to use to build the phylogenetic tree. \nEnter the numbers (1-{num_matching_directories}) separated by space: ")

        try:
            chosen_indices = [int(idx) for idx in user_choices.split()]
            chosen_directories = [matching_directories[idx - 1] for idx in chosen_indices]
            print("Chosen search results:")
            print('\n'.join([f"{idx}. {basename}" if dir_name == directory1 else f"{idx}. {dir_name}" for idx, dir_name in zip(chosen_indices, chosen_directories)]))

            for idx, dir_name in zip(chosen_indices, chosen_directories):
         
                if dir_name == directory1 and len(chosen_directories) == 1:
                    # Run ClustalW (calculate tree)
                    clustalw_input = f"4\n1\n{directory2}/{basename}_aligned.fasta\n5\n{directory4}/{basename}.phb\n100\n1000\n\nx\n"
                    clustalw_command = f"clustalw"
                    print("Reconstructing phylogenetic tree...")
                    process = subprocess.Popen(clustalw_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate(clustalw_input)
                    if stderr:
                        print(stderr)
                    else:
                        print(f"Phylogenetic tree has been saved to {directory4}/")
                    break

                if dir_name != directory1 and len(chosen_directories) == 1:
                    print("Invalid input. Please input either the results from current session or multiple results from both current and previous sessions.")
                    break

                else:
                    # Collect filenames matching the pattern from chosen directories
                    matching_filenames = []

                    for directory in chosen_directories:
                        files_in_dir = os.listdir(directory)
                        matching_files = [file for file in files_in_dir if '_in_' in file and 'fasta' in file and 'aligned' not in file]
                        if matching_files:
                            matching_filenames.extend([os.path.join(directory, file) for file in matching_files])
                
                    # Combine fasta files from chosen directories
                    # Read and append content of fasta files
                    appended_sequences = []
                    for filename in matching_filenames:
                        with open(filename, 'r') as file:
                            appended_sequences.append(file.read())
                    # Write appended sequences to a new file
                    output_append_sequences = f"{directory4}/append.fasta"
                    with open(output_append_sequences, 'w') as output_file:
                        output_file.write('\n'.join(appended_sequences))        
                    # Read the file and remove blank lines
                    with open(output_append_sequences, 'r') as file:
                        lines = file.readlines()
                        non_empty_lines = [line.strip() for line in lines if line.strip()]  # Remove blank lines
                    # Write back to the file
                    with open(output_append_sequences, 'w') as file:
                        file.write('\n'.join(non_empty_lines))

                    # ClustalO alignment
                    clustalo_in = output_append_sequences
                    clustalo_out = f"{directory4}/append_aligned.fasta"
                    # Run clustalo
                    print("Aligning...")
                    cmd_clustalo = f"clustalo -i {clustalo_in} -o {clustalo_out} --outfmt=fasta --seqtype=protein -v --force"
                    clustalo_stdout, clustalo_error = bash_command(cmd_clustalo)
                    if clustalo_error:
                        print(clustalo_error)
                    else:
                        print("Aligned chosen sequences.")

                    # Run ClustalW (calculate tree)
                    clustalw_input = f"4\n1\n{clustalo_out}\n5\n{directory4}/tree_multi.phb\n100\n1000\n\nx\n"
                    clustalw_command = f"clustalw"
                    print("Constructing phylogeny tree...")
                    process = subprocess.Popen(clustalw_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate(clustalw_input)
                    if stderr:
                        print(stderr)
                    else:
                        print(f"Phylogeny tree of chosen sequences has been saved as {directory4}/tree_multi.phb")
                    
                    break
           
            if not (dir_name != directory1 and len(chosen_directories) == 1):
                break # Make sure user return to choosing menu after 'invalid input' warning

        except (ValueError, IndexError):
            print(f"Invalid input. Enter valid numbers separated by space (1-{num_matching_directories}).")