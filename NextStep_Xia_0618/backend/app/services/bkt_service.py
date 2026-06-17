from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.bkt_parameters import KnowledgeComponentBKTParameters


@dataclass(frozen=True)
class BKTParameters:
    prior: float = 0.2
    learn: float = 0.15
    guess: float = 0.2
    slip: float = 0.1

    def __post_init__(self) -> None:
        for name, value in (
            ("prior", self.prior),
            ("learn", self.learn),
            ("guess", self.guess),
            ("slip", self.slip),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


DEFAULT_BKT_PARAMETERS = BKTParameters()


def update_knowledge_state(
    current_mastery: float,
    correct: bool,
    params: BKTParameters = DEFAULT_BKT_PARAMETERS,
) -> float:
    probability_known = clamp_probability(current_mastery)

    if correct:
        likelihood_known = 1.0 - params.slip
        likelihood_not_known = params.guess
    else:
        likelihood_known = params.slip
        likelihood_not_known = 1.0 - params.guess

    numerator = probability_known * likelihood_known
    denominator = numerator + ((1.0 - probability_known) * likelihood_not_known)
    posterior = numerator / denominator if denominator else probability_known
    updated = posterior + ((1.0 - posterior) * params.learn)

    if not correct:
        updated = min(updated, probability_known)

    return round(clamp_probability(updated), 4)


def get_bkt_parameters_for_kc(db: Session, kc_id: str) -> BKTParameters:
    row = db.get(KnowledgeComponentBKTParameters, kc_id)

    if row is None:
        return DEFAULT_BKT_PARAMETERS

    return BKTParameters(
        prior=row.prior,
        learn=row.learn,
        guess=row.guess,
        slip=row.slip,
    )


def clamp_probability(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
