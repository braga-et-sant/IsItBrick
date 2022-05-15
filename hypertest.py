from scipy.stats import multivariate_hypergeom

if __name__ == '__main__':
    print(multivariate_hypergeom.pmf(x=[1, 1, 3], m=[3, 3, 34], n=5))