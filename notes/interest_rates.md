---
tags:
  - finance
section: "1.2"
---

Money becomes inherently less valuable with time. We define the **interest rate** as the rate at which this happens.

For example a 1-year loan can have 10% interest rate, meaning that having the money now is 10% more valuable as having it 1 year into the future. This means that today's $100\$$ are as *exactly as valuable* as next year's $110\$$. 

Interest can be **simple** or **compound**, depending on context. For example, having annual $4\%$ payouts on all money deposited in a bank account is simple interest.

When we value money, we need to take a reference interest rate to know its value in the future. If we fix an interest rate, that means that we can compare the value of money across different times. That's the most important idea in financial analysis.

**Observation.** (7-10 rule) 
- A $7\%$ annual interest, compounded over $10$ years equals doubling the amount. 
- A $10\%$ annual interest, compounded over $7$ years equals doubling the amount.

**Definition.** The **present value** of some future flow of money is defined as its future value discounted by the interest rate between the present and the moment of the transaction. Namely
$$
PV = v\cdot \frac{1}{(1 + r)^{t - t_0}}
$$
where $v$ is the future value, $r$ is the interest rate, $t$ is the future moment and $t_0$ is the current time.

For example, given an $4\%$ interest rate and a $100\%$ payout in $4$ years, it's actual present value is
$$
\frac{100\$}{1.04^4} = 85.48
$$

**Definition.** The **present value of a cash flow** $(x_0, x_1, \ldots, x_n)$ is the sum of the present values of all its future flows, this is
$$
PV = \sum_{i=1}^{n}{\frac{x_i}{(1+r)^{t_k-t_0}}}
$$
If we assume that the cash flow is equidistributed in time and there're $m$ such periods in a year, the present value has the formula
$$
PV = \sum_{i=1}^{n}{\frac{x_i}{(1+r/m)^{i}}}
$$

**Definition.** We define an **ideal bank** as some bank that gives loans and takes deposits with the same interest rate. We say that two cash flows are **equivalent** if we can get from one of them into the other via taking loans or making deposits in the ideal bank.

**Theorem 1.1.** Two cash flows are equivalent if and only if they have the same present value.
*Proof:*

**Definition.** An **implicit interest rate** of some cash flow if the interest rate which makes its PV equal to $0$. This is, it's $r$ such that
$$x_0 + rx_1 + r^2x_2 + \cdots + r^n x_n$$

**Theorem 1.2.** Let $(x_0, x_1, \ldots, x_n)$ be a cash flow with $x_0 < 0$ (positive prime value) and $x_k\ge 0$ for $k\ge 1$ (positive coupons/payouts). Then, there is a unique implicit interest rate for that cash flow.
*Proof:* Notice that the polynomial $f(r) = x_0 + rx_1 + r^2x_2 + \cdots + r^n x_n$ is increasing and $f(0) < 0$ whereas $f(r)\to \infty$ as $r\to\infty$. Therefore, there is a unique $r$ s.t. $f(r) = 0$. 
