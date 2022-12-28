import numpy as np
from coordinates import Vec3
from coordinates import z_matrix_to_cartesian


class Output:
    def __init__(self, vector):
        self.vector = vector # row data generated by decoder 
        self.n = int((len(vector) - 3) / 3) # number of amino acids 

    @staticmethod
    def compute_dihedral(sin, cos):
        k = np.sqrt(np.square(sin) + np.square(cos))
        return np.degrees(np.arctan2(sin / k, cos / k))

    def displacement(self):
        return self.vector[0:3]
    
    def alpha(self):
        START = 3
        END = START + self.n
        return [180 * alpha for alpha in self.vector[START:END]] # original alpha angles are normalized at the stage of data processing

    def sin_theta(self):
        START = 3 + self.n
        END = START + self.n
        return self.vector[START:END]
    
    def cos_theta(self):
        START = 3 + 2 * self.n
        END = START + self.n
        return self.vector[START:END]
    
    def theta(self):
        return self.compute_dihedral(self.sin_theta(), self.cos_theta())
    
    def to_original(self):
        angles = np.concatenate([[alpha, theta] for alpha, theta in zip(self.alpha(), self.theta())])
        return np.concatenate([self.displacement(), angles])

    def to_cartesian(self, bond_length=3.8):
        # angles below are given in degrees
        alpha = self.alpha()
        theta = self.theta()

        # set initial atoms 
        c_s = Vec3(x=0.0, y=0.0, z=0.0)
        c_1 = Vec3(x=bond_length, y=0.0, z=0.0)
        c_2 = Vec3(x=bond_length * (1 + np.cos(np.radians(180 - alpha[0]))), y=bond_length * np.sin(np.radians(180 - alpha[0])), z=0.0)

        atoms = [c_s, c_1, c_2] # list of reconstructed carbons   

        count = 0
        for alpha, theta in zip(alpha[1:], theta[1:]):
            c_i = Vec3(x=0.0, y=0.0, z=0.0)
            c_j = Vec3(x=atoms[-2].x, y=atoms[-2].y, z=atoms[-2].z)
            c_k = Vec3(x=atoms[-1].x, y=atoms[-1].y, z=atoms[-1].z)
            c_0 = Vec3(x=atoms[-3].x, y=atoms[-3].y, z=atoms[-3].z)
            c_new = Vec3(x=9.999, y=9.999, z=9.999)
            c_j.subtract(c_0)
            c_k.subtract(c_0)

            if count == self.n - 2:
                z_matrix_to_cartesian(c_i, c_j, c_k, np.linalg.norm(self.displacement()), np.radians(alpha), np.radians(theta), c_new)
            else:
                z_matrix_to_cartesian(c_i, c_j, c_k, bond_length, np.radians(alpha), np.radians(theta), c_new)

            c_new.add(c_0)
            atoms.append(c_new)
            count += 1

        return atoms

    def to_pdb(self, ordinal):
        pass


def one_hot_to_string(vector, codes):
    string = ""
    categories = len(codes)
    i = 0
    while i < len(vector):
        index = list(vector[i:i+categories]).index(1.0)
        string += codes[index]
        i += categories
    return string


def angles_distribution(ss, output: Output):
    # return plane and dihedral angles corresponding to secondary structure
    alpha = output.alpha()
    theta = output.theta()
    return [[ss, alpha, theta] for ss, alpha, theta in zip(ss, alpha, theta)]


def extract_ss(vector):
    # get secondary structure from label vector
    n = int(len(vector) / 23) 
    ORDINAL = 20 * n 
    return one_hot_to_string(vector[ORDINAL:], codes="HEC")


def hec_distribution(angles):
    h_angles = []
    e_angles = []
    c_angles = []
    for element in angles:
        ss = element[0]
        alpha = element[1]
        theta = element[2]
        if ss == "H": h_angles.append([alpha, theta])
        if ss == "E": e_angles.append([alpha, theta])
        if ss == "C": c_angles.append([alpha, theta])
    return h_angles, e_angles, c_angles
