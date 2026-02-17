import numpy as np
import matplotlib.pyplot as plt

from bonds.bonds import Bond
from rates.compound import yearly_discount
from rates.discount_context import DiscountContext


def plot_price_yield(ax: plt.Axes, bond: Bond):
    yields = np.linspace(0, 1, 100)
    prices = [bond.present_value(DiscountContext(yearly_discount, kwargs={"y": y})) for y in yields]
    ax.plot(yields, prices, label=bond.name)
      

if __name__ == "__main__":
    fig, ax = plt.subplots()
    bond_3y = Bond(0.1, 100, 6, 2, "3y Bond")
    bond_10y = Bond(0.1, 100, 20, 2, "10y Bond")
    bond_30y = Bond(0.1, 100, 60, 2, "30y Bond")
    plot_price_yield(ax, bond_3y)
    plot_price_yield(ax, bond_10y)
    plot_price_yield(ax, bond_30y)
    ax.legend()
    plt.savefig("price_yield.png")
    plt.close()
