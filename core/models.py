from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    ValidationError,
    model_validator,
)

PosFinite = Annotated[float, Field(gt=0, allow_inf_nan=False)]
NonNegFinite = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Int1to5 = Annotated[int, Field(ge=1, le=5)] # we are assuming the risk and the tolerance levels to be int from 1 to 5


AllowedExperiences = Literal["beginner", "advanced", "intermediate"]
AllowedPreference_list = ["high_growth", "capital_protection", "low_cost", "avoid_equity", "tax_saving", "no_lock_in"]
AllowedAssetClass = Literal["cash", "debt", "hybrid", "equity"]

class Investor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    investor_id: str
    goal_label: str
    goal_amount_inr: PosFinite
    horizon_months: Annotated[float, Field(ge=1, allow_inf_nan=False)] 
    # our model will consider a the horizen months to be an int, in case of fractional months, we want to inform the user and round down, but still consider the inverstor valid 
    # rouding down and informing would be done by the validator, so here we'll allow a float 
    # fractional months isn't wrong input but informing the user that our model will consider a month approach is appropriate 
    existing_investment_inr: NonNegFinite
    monthly_sip_inr: NonNegFinite
    risk_tolerance_score: Int1to5
    emergency_fund_months: NonNegFinite
    liquidity_need_inr: NonNegFinite
    experience: AllowedExperiences
    preference: str | None # random preferences are allowed but not considered for a decision

    @model_validator(mode="after")
    def non_zero_capital_check(self) -> "Investor":
        if self.existing_investment_inr + self.monthly_sip_inr == 0:
            raise ValueError("No capital available")
        return self


class Product(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str
    product_name: str
    asset_class: AllowedAssetClass
    risk_score: Int1to5
    assumed_annual_return: Annotated[float, Field(ge=-1, allow_inf_nan=False)] # allwing return to be -100%
    volatility_proxy: NonNegFinite
    annual_expense_ratio: Annotated[float, Field(ge=0, lt=1, allow_inf_nan=False)]
    liquidity_days: NonNegativeInt
    minimum_investment_inr: NonNegativeFloat
    lock_in_months: NonNegativeInt
    category_description: str

class MonthlyReturn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str
    month: Annotated[str, Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]
    monthly_return: Annotated[float, Field(ge=-1, allow_inf_nan=False)]



def increment_month(date:str, inc:int):
    year, month = map(int, date.split("-"))
    year += inc // 12
    month += inc % 12
    if month > 13:
        month -= 1
        year += 1
    return f"{year}-{month:02d}" # maintaing the date style


def main():
    try:
        test = MonthlyReturn(product_id="test", month="no",monthly_return=-2)
        print(test)
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    main()
    