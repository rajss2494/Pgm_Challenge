from abc import ABC, abstractmethod
import math
from marshmallow import Schema, fields, ValidationError


class LoanSchema(Schema):
    """Loan Schem"""

    principal = fields.Float(
        required=True,
        validate=lambda x: x > 0,
        error_messages={"validator_failed": "principal must be >0"},
    )
    term = fields.Integer(
        required=True,
        validate=lambda x: 1 <= x <= 360,
        error_messages={"validator_failed": "term must be between " "1 and 360 months"},
    )
    rate = fields.Float(
        required=True,
        validate=lambda x: 0 <= x <= 0.5,
        error_messages={
            "validator_failed": "rate must be positive" " but less than 50%"
        },
    )


class Loan(ABC):

    def __init__(self, principal, term, rate):
        schema = LoanSchema()
        try:
            validated_data = schema.load(
                {"principal": principal, "term": term, "rate": rate}
            )
            self.principal = validated_data["principal"]
            self.term = validated_data["term"]
            self.rate = validated_data["rate"]
        except ValidationError as e:
            raise ValueError(f"Invalid loan parameters : {e.messages}")

    @abstractmethod
    def monthly_payment(self):
        pass

    @abstractmethod
    def amortization_schedule(self):
        pass

    @abstractmethod
    def balance_at(self, month):
        pass


class FixedTermLoan(Loan):
    def __init__(self, principal, term, rate):
        super().__init__(principal, term, rate)

    def __str__(self):
        return (
            f"the loan paremeters are principal={self.principal}, "
            f"term={self.term}, rate={self.rate}"
        )

    def __repr__(self):
        return f"FixedTermLoan('{self.principal}', " f"'{self.term}', '{self.rate}')"

    # assuming term is provided in months, rate in percentage points
    def monthly_payment(self) -> float:
        if self.rate == 0:
            return self.principal / self.term

        mon_rate = self.rate / 12
        numerator = mon_rate * ((1 + mon_rate) ** self.term)
        denominator = (1 + mon_rate) ** self.term - 1

        return math.floor((self.principal * (numerator / denominator)) * 100) / 100

    def amortization_schedule(self) -> list:
        balance = self.principal
        schedule = []
        monthly_payment = self.monthly_payment()
        mon_rate = self.rate / 12
        for month in range(1, self.term + 1):

            int_pay_monthly = math.floor((balance * mon_rate) * 100) / 100
            princ_pay_monthly = (
                math.floor((monthly_payment - int_pay_monthly) * 100) / 100
            )
            balance -= princ_pay_monthly

            # final payment rounding
            if month == self.term:
                # adjustment for remaining balance due to rounding
                princ_pay_monthly += balance
                monthly_payment += balance
                balance = 0

            schedule.append(
                {
                    "month": month,
                    "payment": monthly_payment,
                    "interest": int_pay_monthly,
                    "principal": princ_pay_monthly,
                    "balance": balance,
                }
            )

        return schedule

    def balance_at(self, month) -> float:
        if month < 1 or month > self.term:
            raise ValueError(f"month input must be between 1 and {self.term}")
        schedule = self.amortization_schedule()
        return schedule[month - 1]["balance"]


if __name__ == "__main__":
    try:
        cust1 = FixedTermLoan(782000, 168, 0.0481)
        monthly_payments = cust1.monthly_payment()
        payment_schedule = cust1.amortization_schedule()
        print(payment_schedule)
        print(cust1.balance_at(5))
    except ValueError as e:
        print(f"Error : {e}")
