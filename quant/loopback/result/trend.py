from .base import Result, Unit



class TrendResult(Result):
    def __init__(self, ops, steps, step_ratio):
        super(TrendResult, self).__init__(ops)
        self.steps = steps
        self.step_ratio = step_ratio
        self.tmp_benefit = 0.0

    def calc_total_cost(self, start_price):
        total = 0.0
        for step in self.steps:
            total += step * start_price
            start_price *= (1 + self.step_ratio)

        return total

    def buy(self, op):
        self.cur_hold.append(Unit(op.price, op.cnt))

    def sell(self, op):
        if op.cnt != self.cur_hold[-1].cnt:
            raise RuntimeError('Incorrect sell unit counts')

        if len(self.cur_hold) == 1:
            return self.stop(op)
        else:
            last_op = self.cur_hold.pop(-1)
            self.tmp_benefit += (op.price - last_op.price) * last_op.cnt

    def stop(self, op):
        benefit = sum([(op.price - unit.price) * unit.cnt for unit in self.cur_hold])
        benefit += self.tmp_benefit
        virtual_total_cost = self.calc_total_cost(self.cur_hold[0].price)
        benefit_rate = benefit / virtual_total_cost
        self.add_benefit_rate(op.date, benefit_rate)

        # cleanup
        self.cur_hold = []
        self.tmp_benefit = 0.0
