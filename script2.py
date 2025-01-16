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
print("Step 2: Level of conservation")
print("-".center(100,"-"))

## Align
# Output directory from step 1
directory1 = "output1_sequence"
# Define input/output filename
basename = os.listdir(directory1)[0].replace(".fasta","") # get the filename for subsequent rename
clustalo_in = f"{directory1}/*.fasta"
clustalo_out = f"output2_conservation/"+basename+"_aligned.fasta"
# Run clustalo
print("Aligning...")
command_clustalo = f"clustalo -i {clustalo_in} -o {clustalo_out} --outfmt=fasta --threads=30 --seqtype=protein "
clustalo_out, clustalo_error = bash_command(command_clustalo)
if clustalo_error:
    print(clustalo_error)
else:
    print("Alignment done.")

## Show conservation plot on screen
input("Press any key to show the conservation plot (close the plot window to continue next step):")
plotcon_screen = f"plotcon -sequence output2_conservation/*.fasta -winsize 10 -graph x11 -scorefile EBLOSUM62"
# Start a subprocess for the plot display
subprocess.run(plotcon_screen, shell=True, stderr=subprocess.DEVNULL)

## Save conservation plot
plotcon_png = f"plotcon -sequence output2_conservation/*.fasta -gdirectory output2_conservation -winsize 10 -graph png -goutfile {basename} -scorefile EBLOSUM62"
plotcon_out, plotcon_error = bash_command(plotcon_png)
if plotcon_error and "Plot conservation of a sequence alignment" not in plotcon_error:
    # Print the error only if plotcon_error is not an empty string and doesn't contain the standard output message
    print(plotcon_error)
else:
    print(f"The alignment fasta file and conservation plot in PNG format has been saved to output2_conservation/")
