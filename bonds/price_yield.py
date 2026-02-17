import numpy as np
import matplotlib.pyplot as plt

from bonds.bonds import Bond


def plot_price_yield(ax: plt.Axes, bond: Bond):
    yields = np.linspace(0, 1, 100)
    prices = [bond.present_value(y) for y in yields]
    ax.plot(yields, prices)
      

if __name__ == "__main__":
    fig, ax = plt.subplots()
    bond_3y = Bond(0.1, 100, 6, 2)
    bond_10y = Bond(0.1, 100, 20, 2)
    bond_30y = Bond(0.1, 100, 60, 2)
    plot_price_yield(ax, bond_3y)
    plot_price_yield(ax, bond_10y)
    plot_price_yield(ax, bond_30y)
    plt.savefig("price_yield.png")
