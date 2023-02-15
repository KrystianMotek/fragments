import argparse
import logging
import numpy as np
from model import DecoderLoader
from features import LabelMLP
from statistical import Output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-aa", type=str, help="amino acids sequence")
    parser.add_argument("-ss", type=str, help="secondary structure")
    parser.add_argument("-s", "--span", type=float, help="distance from first atom to the last one")
    parser.add_argument("-p", "--population", type=int, help="number of fragments generated to select one with the most relevant distance")
    parser.add_argument("-m", "--model", type=str, help="model to be used")
    args = parser.parse_args()

    logging.getLogger("tensorflow").disabled=True
    logging.getLogger("h5py._conv").disabled=True

    aa = args.aa 
    ss = args.ss 
    span = args.span
    model = args.model 

    if args.population:
        population = args.population
    else:
        population = 10

    decoder = f"{model}/decoder.pb"
    latent = f"{model}/latent.npy"

    label = LabelMLP(aa=aa, ss=ss, r1n=span)

    loader = DecoderLoader(decoder=decoder, latent=latent)

    # obtained results
    vectors = [loader.predict(label.format())[0] for _ in range(population)]
    outputs = [Output(vector=vector, bond_length=3.8) for vector in vectors]

    # differences between predicted and expected spanning norms
    errors = [np.abs(output.compute_r1n() - span) for output in outputs]

    # output with the smallest error
    matching_output = outputs[errors.index(np.min(errors))]

    # change to PDB format
    lines = matching_output.to_pdb()
    for line in lines:
        print(line)

    print(f"{matching_output.compute_r1n():.2f}")