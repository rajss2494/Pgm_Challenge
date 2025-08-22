import pytest
from Source.loan import FixedTermLoan, LoanSchema, Loan

@pytest.fixture
def standard_loan():
    return FixedTermLoan(782000, 168, 0.0481)

@pytest.fixture
def negpricp_loan():
    return FixedTermLoan(-782000, 168, 0.0481)

@pytest.fixture
def incorr_term_loan():
    return FixedTermLoan(-782000, 500, 0.0481)

@pytest.fixture
def incorr_rate_loan():
    return FixedTermLoan(-782000, 500, 0.6)

#test monthly payment
def test_monthly_payment(standard_loan):

    test_val= standard_loan.monthly_payment()
    assert test_val == 6405.58

# test the sum of monthly principals received equals the initial loan amount
def test_amortization_schedule(standard_loan):
    test_schedule= standard_loan.amortization_schedule()
    test_val = 0
    for i in range(len(test_schedule)):
        test_val += test_schedule[i]["principal"]
    assert test_val == pytest.approx(782000, abs =.001)


def test_balance_at(standard_loan):
    test_schedule = standard_loan.amortization_schedule()
    test_balance_5 = test_schedule[4]["balance"]

    assert test_balance_5 == pytest.approx(765513.02, abs=.001)

