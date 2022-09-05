import random
import sympy as sy


class LnkAlg:

    def __init__(self, graph, discard_rate, back_rate, post_rate):
        self.lower_bound = 0.05
        self.upper_bound = 0.1
        self.interval_increase = 0.1
        self.exponent = -3/2
        self.integral_array = []

        self.graph = graph
        self.discard_rate = discard_rate  # 0.65, 0.5-0.75
        self.back_rate = back_rate  # 0.95
        self.post_rate = post_rate  # 0.22

    def f(self, x):
        return x**self.exponent

    def generate_t(self):
        x = sy.Symbol("x")
        print(sy.integrate(self.f(x), (x, 0.05, 0.1)))

        while self.upper_bound <= 20:  # 20
            interval_integral = sy.integrate(self.f(x), (x, self.lower_bound, self.upper_bound))

            self.integral_array.append([self.lower_bound, self.upper_bound, interval_integral])

            self.lower_bound = self.upper_bound
            self.upper_bound += self.interval_increase

        print(self.integral_array)

        values = []
        probabilities = []
        for i in range(len(self.integral_array)):
            values.append(self.integral_array[i][1])
            probabilities.append(self.integral_array[i][2])

        print(random.choices(values, weights=probabilities, k=15))
