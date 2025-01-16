#!/usr/bin/python3

### Import modules ###
import subprocess

### Define Functions ###

## Function for bash commands
def bash_command(str):
    result = subprocess.run(str, shell = True,capture_output = True,text = True)
    return result.stdout, result.stderr

## Specify protein family and taxonomic group
def specify_protein() :
    protein_family = ""
    taxonomic_group = ""

    while True :
        choice = input(f'''Choose your protein of interest: 
                t : Default test set (glucose-6-phosphatase in Aves (birds))
                t2: Test set 2 (ABC transporter in mammals)
                n : Input [protein name] and [taxonomic group] manually
                ''')
        if choice == "t" :
            protein_family  = "glucose-6-phosphatase"
            taxonomic_group = "aves"
            break

        if choice == "t2" :
            protein_family  = "ABC transporter"
            taxonomic_group = "mammals"
            break

        if choice == "n" :
            protein_family = input("Enter the protein family of interest:   ")
            taxonomic_group = input("Enter the taxonomic group:   ")

            choice_confirm = input(f'''Confirm your selection (y/n):
                    Protein family  : {protein_family}
                    Taxonomic group : {taxonomic_group}                                  
                y : yes 
                n : input again
                '''
            )
            print("-".center(100, '-'))
            if choice_confirm == "y":
                break
        
        else :
            print("Invalid input, try again!")

    return protein_family, taxonomic_group

## Construct search query
def search_query(query):
    print(f"Searching against NCBI database with query: {query}")
    esearch_command = f"esearch -db protein -query '{query}' | efetch -format fasta"
    search_out, search_errors = bash_command(esearch_command)
    return search_out, search_errors

## Analyse fasta data
def fasta_analysis(fasta):
    fasta_list = fasta.split("\n")
    seq_header = {} # id_number , value : (partial_State, Species) 
    species_list = set()
    for line in fasta_list:
        if line.startswith(">"):# e.g. >KFM01312.1 Glucose-6-phosphatase, partial [Aptenodytes forsteri]
            id = line.split()[0][1:]  # remove '>'
            partial = "partial" in line.lower()
            species_name = line.split('[')[-1].split(']')[0] # get species names
            seq_header[id] = (partial,species_name)
            species_list.add(species_name)
    # show results
    print(f"There are {len(seq_header)} sequences from {len(species_list)} species.")
    return len(seq_header)

## If no search result
def help():
    print("Found 0 result in your search")
    print(f'''Suggestions: 
                1 : Check if there are any misspellings in your query
                    NB: the protein input is case-sensitive and should not contain plurals (e.g. kinases x  kinase √)
                2 : Check the query on NCBI website to see if there is connection error between server and NCBI
    ''')

### Main Module ###
print("=".center(100,"="))
print("Step 1: Specify protein of interest and get the sequences from NCBI")
print("-".center(100,"-"))

## Main loop
import os
while True:
    loop_flag = True

    # Input protein of interest
    protein_family, taxonomic_group = specify_protein()
    
    query_not_partial   = f"({protein_family}[Protein name]) AND ({taxonomic_group}[Organism]) NOT PARTIAL"
    query_all           = f"({protein_family}[Protein name]) AND ({taxonomic_group}[Organism])"

    # Make query in NCBI
    search_out_all, search_error_all                 = search_query(query_all)
    search_out_not_partial, search_error_not_partial = search_query(query_not_partial)

    # Analyse fasta data
    print("Search Results".center(100, '-'))
    print("Complete & Partial Sequences")
    count_all = fasta_analysis(search_out_all)
    print()
    print("Complete Sequences")
    count_not_partial = fasta_analysis(search_out_not_partial)
    print("-".center(100, '-'))

    # Help user when no results
    if (count_all == 0 or count_not_partial == 0) :
        help()
        print(f'''Your input query:
                {query_all}
                {query_not_partial}
''')
        input("Press any key to continue".center(100, '-'))

    # output data
    while True:
        next_step = input(f'''What next?
                a : Search again 
                b : Save both partial & complete sequences
                c : Only save complete sequences                            
        ''')
        if next_step == "a":
            break

        if next_step == "b":
            outpath = "output1_sequence"
            protein_family = protein_family.strip().replace(" ", "_")
            taxonomic_group = taxonomic_group.strip().replace(" ", "_")
            output_path = f"{outpath}/{protein_family}_in_{taxonomic_group}.fasta" 
            with open(output_path, 'w') as file:
                file.write(str(search_out_all))
            loop_flag = False
            break

        if next_step == "c":
            outpath = "output1_sequence"
            protein_family = protein_family.strip().replace(" ", "_")
            taxonomic_group = taxonomic_group.strip().replace(" ", "_")
            output_path = f"{outpath}/{protein_family}_in_{taxonomic_group}.fasta" 
            with open(output_path, 'w') as file:
                file.write(str(search_out_not_partial))
            loop_flag = False
            break

        else :
            print("Invalid input, try again!")

    # Quit
    if loop_flag == False:
        print("Fasta file saved to output1_sequence/")
        print("NB: You will be able to select final output directory at the end of the programme.")
        break 
