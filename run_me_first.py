#!/usr/bin/python3

### Import modules ###
import os
import subprocess
import shutil
import sys

### Define Functions ###

## Copy directory
def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)            

## Choose final output directory
def output_directory():
    output_directory = input('''Enter the path to your desired output directory for results in the current session (will create if not exist; press Enter for the current directory): \n''').strip()
    if output_directory:
        if not os.path.exists(os.path.join(output_directory, basename)):
            os.makedirs(os.path.join(output_directory, basename))
        files = os.listdir(os.getcwd())
        for item in files:
            if item.startswith("output"):
                copytree(item, f"{output_directory}/{basename}")
        print(f"Results copied to {output_directory}/{basename}/")
    else:
        files = os.listdir(os.getcwd())
        if not os.path.exists(basename):
            os.makedirs(basename)
        for item in files:
            if item.startswith("output"):
                copytree(item, f"{basename}")
        print(f"Outputs copied to {basename}/")

## Check and (re)create output directory
def check_directory(outpath):
    if outpath:
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        else:
            shutil.rmtree(outpath)
            os.makedirs(outpath)
    else:
        pass
    return outpath

## Function for bash commands
def bash_command(str):
    result = subprocess.run(str, shell = True,capture_output = True,text = True)
    return result.stdout, result.stderr

### Main Module ###

## Main loop
while True:
    loop_flag = True

    ## Make default output directories
    check_directory("output1_sequence")
    check_directory("output2_conservation")
    check_directory("output3_motifs")
    check_directory("output4_phylogeny")

    ## Run the scripts sequentially
    subprocess.run(["python3", "script1.py"])
    subprocess.run(["python3", "script2.py"])
    subprocess.run(["python3", "script3.py"])
    subprocess.run(["python3", "script4.py"])
    
    print("=".center(100,"="))
    print("All 4 steps done.")

    ## Output results

    directory1 = "output1_sequence"
    directory2 = "output2_conservation"
    directory3 = "output3_motifs"
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
    # Include current temporary output directory in the selection list
    matching_directories.append(directory1)
    # Count the number of matching subdirectories
    num_matching_directories = len(matching_directories)

    # Display matching directories and let user choose
    print("Outputs saved in current working directory (the last result is from current session): ")
    for index, dir_name in enumerate(matching_directories, start=1):
        if dir_name == directory1:
            print(f"{index}. {basename}")
        else:
            print(f"{index}. {dir_name}")
    
    ## Handle the outputs from current session
    if num_matching_directories > 1:
        print("Next: Step 1. Choose where to save outputs from current session;")
        print("      Step 2. Handle outputs saved in current working directories.")
        print("-".center(100,"-"))

        # Check if there are any directories in matching_directories with the same name as basename
        basename_match_dirs = [dir_name for dir_name in matching_directories if dir_name == basename]
        
        if not basename_match_dirs: 
            output_directory()
        else: 
            print("!Found previous outputs using the same query as in current session!")
            print("The new outputs will replace the old ones if you choose to save it to current working directory.")
            output_directory()

        ## Handle all the outputs saved in current working directory
        ## Detect number of final result directories currently in working directory
        current_directory = os.getcwd()
        # Get the list of directories in the current directory
        subdirectories = [d for d in os.listdir(current_directory) if os.path.isdir(os.path.join(current_directory, d))]
        saved_directories = [dir for dir in subdirectories if "_in_" in dir]
        num_saved_directories = len(saved_directories)

        # Display saved directories and let user choose
        print("-".center(100,"-"))
        print("Outputs saved in current working directory: ")
        for index, dir_name in enumerate(saved_directories, start=1):
            print(f"{index}. {dir_name}")

        # Choose the outputs to save to other directories
        user_choices1 = input(f'''Choose the outputs you want to save to another directory. \nEnter the numbers separated by space (press Enter to skip this step): ''')
        if user_choices1.strip():  # Check if the input is not empty
            while True:
                try:
                    chosen_indices = [int(idx) for idx in user_choices1.split()]
                    chosen_directories = [saved_directories[idx - 1] for idx in chosen_indices]
                    print("Chosen outputs:")
                    for idx, dir_name in zip(chosen_indices, chosen_directories):
                        print(f"{idx}. {dir_name}")
                    confirm_choice = input("Confirm your choice (y/n): ")
                    if confirm_choice.lower() == "y":
                        break
                    else:
                        print("Please re-enter your choices.")

                except (ValueError, IndexError):
                    print(f"Invalid input. Enter valid numbers separated by space (1-{num_saved_directories}).")

            # Choose output directory
            destination_directory = input("Enter the destination directory (will create if not exist) to copy the chosen outputs: ")
            # Create the destination directory if it doesn't exist
            if not os.path.exists(os.path.join(destination_directory, os.path.basename(dir_name))):
                os.makedirs(os.path.join(destination_directory, os.path.basename(dir_name)))
            # Copy chosen directories to the destination directory
            for dir_name in chosen_directories:
                # Copy the directory to the destination directory
                copytree(dir_name, os.path.join(destination_directory, os.path.basename(dir_name)))
                
            print("Chosen outputs copied to the destination directory successfully!")
   
        # Choose the outputs to keep in the current working directory (other will be deleted)
        print("-".center(100,"-"))
        while True:
            user_choices2 = input(f"Choose the outputs you want to keep in the current working directory (other will be deleted). \nEnter the numbers separated by space (press Enter to delete all): ")

            if not user_choices2.strip():
                confirm_delete = input("Are you sure you want to delete all output directories? This action cannot be undone. (yes/no): ")
                if confirm_delete.lower() == "yes":
                    # Delete all directories
                    for directory in saved_directories:
                        shutil.rmtree(directory)
                    print("All output directories have been deleted from the current working directory.")
                    break
                else:
                    print("Please re-enter your choices.")
                    continue

            try:
                chosen_indices = [int(idx) for idx in user_choices2.split()]
                chosen_directories = [saved_directories[idx - 1] for idx in chosen_indices]
                print("Chosen outputs:")
                for idx, dir_name in zip(chosen_indices, chosen_directories):
                    print(f"{idx}. {dir_name}")
                confirm_choice = input("Confirm your choice (y/n): ")
                if confirm_choice.lower() == "y":
                    # Identify directories to remove
                    directories_to_remove = [dir for dir in saved_directories if dir not in chosen_directories]
                    # Delete unchosen directories
                    for directory in directories_to_remove:
                        shutil.rmtree(directory)
                    print("Unchosen directories have been deleted from the current working directory.")
                    break
                else:
                    print("Please re-enter your choices.")
                    continue

            except (ValueError, IndexError):
                print(f"Invalid input. Enter valid numbers separated by space (1-{num_saved_directories}).")
            
            # Identify directories to remove
            directories_to_remove = [dir for dir in saved_directories if dir not in chosen_directories]
            # Delete unchosen directories
            for directory in directories_to_remove:
                shutil.rmtree(directory)
            print("Unchosen directories have been deleted from current working directory.")

    else: # When there is no existing outputs in working directory
        output_directory()

    ## Final step
    print("-".center(100,"-"))
    while True:
        next_step = input(f'''What next?
                a : Start from step 1 again 
                b : Exit                            
        ''')

        if next_step == "a":
            break

        if next_step == "b":
            sys.exit("Quit sucessfully.") 

        else :
            print("Invalid input, try again!")

    # Quit
    if loop_flag == False:
        print("Programme finished.")
        break 
