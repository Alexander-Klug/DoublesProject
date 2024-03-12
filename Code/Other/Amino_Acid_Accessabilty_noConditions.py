from itertools import product
import timeit

# Lists of DNA nucleotides and their respective sets.
DNA_Nucleotides = ['A', 'C', 'G', 'T']
DNA_Nucleotides_set = {'A', 'C', 'G', 'T'}

# Dictionary for DNA nucleotide complement mapping.
DNA_ReverseComplement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}

# Dictionary of DNA codons to corresponding amino acids.
DNA_Codons = {
    # 'M' - START, '_' - STOP
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TGT": "C", "TGC": "C",
    "GAT": "D", "GAC": "D",
    "GAA": "E", "GAG": "E",
    "TTT": "F", "TTC": "F",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
    "CAT": "H", "CAC": "H",
    "ATA": "I", "ATT": "I", "ATC": "I",
    "AAA": "K", "AAG": "K",
    "TTA": "L", "TTG": "L", "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATG": "M",
    "AAT": "N", "AAC": "N",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "CAA": "Q", "CAG": "Q",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R", "AGA": "R", "AGG": "R",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S", "AGT": "S", "AGC": "S",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TGG": "W",
    "TAT": "Y", "TAC": "Y",
    "TAA": "_", "TAG": "_", "TGA": "_"
}


def contains_dash_where_AA_does_not(AA, NewAA):
    """Check if NewAA has a stop codon where AA does not."""
    for i in range(len(AA)):
        if AA[i] != '_' and NewAA[i] == '_':
            return True
    return False


def AASequence(ntSeq):
    """Convert a nucleotide sequence to its corresponding amino acid sequence."""
    Codons = int(len(ntSeq)/3)
    AA = []
    for c in range(Codons):
        codonSeq = ''.join(ntSeq[0+3*c:3+3*c])
        AA.append(DNA_Codons[codonSeq])
    return ''.join(AA)

# Setup for analysis.
Codons = 3
print("RingCodons", Codons)

# Generate all possible DN combinations for the given number of codons.
dn_mutations = [[i, i+1] for i in range(Codons*3-1)] + [[0, Codons*3-1]]

# Initializing counters to track various mutation outcomes.
counterSN = 0
counterDN = 0
counterDNMore = 0
counterSNMore = 0
counterSNandDN = 0
counterSNsyn = 0
counterDNsyn = 0
counterSNmis = 0
counterDNmis = 0
counterSNnon = 0
counterDNnon = 0
counter_all = 0
counter_all_SN = 0
counter_all_DN = 0
counterOnlyDNacc = 0

# Main loop to iterate through all possible DNA sequences.
start = timeit.default_timer()
ci = 0
for item in product(DNA_Nucleotides, repeat=3*Codons):
    ci += 1
    if ci % 1_000_000 == 0:
        print(f"Progress: {ci}, Time: {timeit.default_timer() - start}")

    # Process single nucleotide (SN) mutations.
    AA = AASequence(item)  # Initial amino acid sequence.
    counter_all += 1
    NewAASetSN = {AA}
    for locus in range(len(item)):  # iterating through all loci
        substi = list(DNA_Nucleotides_set-{item[locus]})  # create all substitutions
        copy_item = list(item[:])
        for s in range(len(substi)):  # iterating through all substitutions
            counter_all_SN += 1
            copy_item[locus] = substi[s]
            NewAA = AASequence(copy_item)  # mutant AA
            NewAASetSN.add(NewAA)
            # Classify the mutation based on its effect.
            if AA == NewAA:
                counterSNsyn += 1
            elif contains_dash_where_AA_does_not(AA, NewAA) == True:
                counterSNnon += 1
            else:
                counterSNmis += 1
    counterSN += (len(NewAASetSN)-1)/Codons  # how many distinct mutant AA are accessible?

    # Process double nucleotide (DN) mutations.
    NewAASetDN = {AA}
    for dn_comb in range(len(dn_mutations)):  # iterating through all DN combinations
        substi0 = list(DNA_Nucleotides_set-{item[dn_mutations[dn_comb][0]]})  # create all substitutions
        substi1 = list(DNA_Nucleotides_set-{item[dn_mutations[dn_comb][1]]})  # create all substitutions
        copy_item = list(item).copy()
        for s0 in range(len(substi0)):  # iterating through all substitutions
            for s1 in range(len(substi1)):  # iterating through all substitutions
                counter_all_DN += 1
                copy_item[dn_mutations[dn_comb][0]] = substi0[s0]
                copy_item[dn_mutations[dn_comb][1]] = substi1[s1]
                NewAA = AASequence(copy_item)  # mutant AA
                NewAASetDN.add(NewAA)
                # Classify the mutation based on its effect.
                if AA == NewAA:
                    counterDNsyn += 1
                elif contains_dash_where_AA_does_not(AA, NewAA) == True:
                    counterDNnon += 1
                else:
                    counterDNmis += 1

                if NewAA not in NewAASetSN:
                    counterOnlyDNacc += 1

    counterDN += (len(NewAASetDN)-1)/Codons
    counterDNMore += (len(NewAASetDN.difference(NewAASetSN)))/Codons
    counterSNMore += (len(NewAASetSN.difference(NewAASetDN)))/Codons
    counterSNandDN += (len(NewAASetSN.intersection(NewAASetDN)))/Codons

print("\nFinal Statistics:")
print('Total genotypes considered: {}. Out of {}'.format(counter_all, 4**(Codons*3)))
print('Total single nucleotide mutations considered: {}. Out of {}'.format(counter_all_SN, 4**(Codons*3)*Codons*3*3))
print('Total double nucleotide mutations considered: {}. Out of {}'.format(counter_all_DN, 4**(Codons*3)*(Codons*3)*3*3))

print('\nP_{inac} =', counterOnlyDNacc/counter_all_DN)

print("\nAmino acid sequences accessible by SN mutation: ", counterSN/counter_all)
print("Amino acid sequences accessible by DN mutation: ", counterDN/counter_all)
print("Amino acid sequences only accessible by DN mutation: ", counterDNMore/counter_all)
print("Amino acid sequences only accessible by SN mutation: ", counterSNMore/counter_all)
print("Amino acid sequences accessible by SN and DN mutation:: ", counterSNandDN/counter_all)

print("\nFraction of non-sense mutatione (SN)", counterSNnon/(counterSNsyn+counterSNmis+counterSNnon))
print("Fraction of non-sense mutatione (DN)", counterDNnon/(counterDNsyn+counterDNmis+counterDNnon))
print('------------------------------------------')
print("Fraction of synonymous mutations (SN)", counterSNsyn/counter_all_SN)
print("Fraction of synonymous mutations (DN)", counterDNsyn/counter_all_DN)
print('------------------------------------------')
print("Fraction of nonsynonymous mutations (SN)", (counterSNmis+counterSNnon)/(counterSNsyn+counterSNmis+counterSNnon))
print("Fraction of nonsynonymous mutations (DN)", (counterDNmis+counterDNnon)/(counterDNsyn+counterDNmis+counterDNnon))
print('------------------------------------------')
print("Fraction of missense mutations (SN)", (counterSNmis)/(counterSNsyn+counterSNmis+counterSNnon))
print("Fraction of missense mutations (DN)", (counterDNmis)/(counterDNsyn+counterDNmis+counterDNnon))
print('------------------------------------------')
print('Counter missense mutations (SN)', counterSNmis)
print('Counter nonsense mutations (SN)', counterSNnon)
print('Counter synonymous mutations (SN)', counterSNsyn)
print('------------------------------------------')
print('Sanity Check')
print('counter_all_SN: {}, counterSNsyn+counterSNmis+counterSNnon {}'.format(counter_all_SN, counterSNsyn+counterSNmis+counterSNnon))
print('counter_all_DN: {}, counterDNsyn+counterDNmis+counterDNnon {}'.format(counter_all_DN, counterDNsyn+counterDNmis+counterDNnon))
