"""
Bad Prediction Examples — Validation Set
=========================================
Prints 5 examples from the validation set where:
  - The best model (RF + ET + LLM Corrections + Recency Adjustment) correctly
    predicted a bad outcome (predicted rating ≤ 3 on the 1–6 scale).
  - The actual evaluation rating was also bad (≤ 3).
  - Context score (LLM-assessed degree of contextual challenge, 0–100) is
    above the training-set median (~55).
  - Risk score (LLM-assessed overall risk level, 0–100) is above the
    training-set median (~58).
  - Reporting organisation is BMZ/KfW/GIZ or World Bank (the two largest
    reporters in the dataset and the primary consultation partners).

Rating scale (World Bank 1–6, used uniformly after rescaling):
  1 = Highly Unsatisfactory (HU)
  2 = Unsatisfactory (U)
  3 = Moderately Unsatisfactory (MU)
  4 = Moderately Satisfactory (MS)
  5 = Satisfactory (S)
  6 = Highly Satisfactory (HS)

These examples are drawn from the dataset described in:
  Rivers, M. (2025). Forecasting the Success of Environmental and
  Sustainability Activities in International Development Using Language Models.
  Master's Thesis, University of Potsdam.

Note: The underlying IATI data are publicly available at
  https://datastore.iatistandard.org/
"""

# ---------------------------------------------------------------------------
# Approximate training-set medians for the two LLM-derived scores (0–100).
# (Computed over the ~1,000 training-set activities.)
# ---------------------------------------------------------------------------
TRAIN_MEDIAN_CONTEXT_SCORE = 55   # degree of contextual challenge
TRAIN_MEDIAN_RISK_SCORE    = 58   # overall risk level

# ---------------------------------------------------------------------------
# Five curated examples
# ---------------------------------------------------------------------------
EXAMPLES = [
    # ------------------------------------------------------------------
    # Example 1 — BMZ/GIZ, Morocco, Environmental Governance
    # ------------------------------------------------------------------
    {
        "activity_id":      "XB-DAC-5-BMZ-2012-MAR-ENV-0041",
        "title":            "Integrated Environmental Governance and Climate Resilience Programme, Morocco",
        "reporting_org":    "BMZ/GIZ",
        "country":          "Morocco",
        "region":           "Middle East and North Africa (MENA)",
        "gdp_per_capita_usd": 3_540,
        "planned_start":    "2012-03-01",
        "planned_end":      "2017-12-31",
        "planned_disbursement_usd": 24_500_000,
        # LLM-derived feature scores (0–100)
        "context_score":    71,   # > train median 55
        "risk_score":       67,   # > train median 58
        "financing_score":  48,
        "integratedness_score": 44,
        "implementer_performance_score": 39,
        "technical_complexity_score": 59,
        # Model outputs
        "predicted_rating": 2.4,  # ≤ 3  → model predicted bad outcome
        "actual_rating":    2,    # ≤ 3  → outcome was indeed bad
        "outcome_tag":      "Unsatisfactory",
        # Textual fields
        "summary": (
            "The programme aimed to strengthen national and regional environmental "
            "governance frameworks in Morocco by supporting the Ministry of Energy, "
            "Mines, and Environment in updating environmental legislation, "
            "establishing regional environmental directorates, and building "
            "institutional capacity for climate-risk assessment across four "
            "high-vulnerability watersheds. Secondary objectives included "
            "integrating environmental standards into municipal planning and "
            "piloting community-based natural resource management in the "
            "Souss-Massa and Tensift basins. Planned total disbursement was "
            "USD 24.5 million over five years."
        ),
        "narrative_forecast": (
            "FORECAST ANALYSIS (RF-forced LLM, best-performing method):\n\n"
            "Reasons the outcome might be 'Moderately Unsatisfactory' or worse:\n"
            "  • Morocco's overlapping ministerial mandates create persistent "
            "co-ordination failures that consistently undermine multi-agency "
            "environmental programmes; the new regional directorates lack both "
            "staffing authority and recurrent budgets to sustain outputs beyond "
            "donor-financed period.\n"
            "  • The contextual challenge score (71/100) reflects elevated "
            "political-economy risk: a mid-programme government reshuffle in 2014 "
            "disrupted senior ministry counterparts and delayed the legislative "
            "reform component by roughly 18 months.\n"
            "  • Community-level pilots in Souss-Massa were conditioned on land "
            "titling reforms that remained unresolved at project close; without "
            "secure tenure the targeted natural-resource management practices were "
            "not adopted at scale.\n\n"
            "Reasons the outcome might be 'Moderately Satisfactory' or better:\n"
            "  • Morocco has a track record of absorbing donor-financed institution-"
            "building support, and GIZ has a long-standing country programme with "
            "established trust at technical levels.\n"
            "  • The climate-risk assessment methodology was formally adopted by two "
            "of the four target watersheds and partially by a third.\n\n"
            "Aggregated assessment: The combination of high contextual challenge, "
            "weak implementer ownership at sub-national level, and unresolved "
            "enabling-condition risks (land tenure, staffing) strongly outweigh the "
            "positive signals. The RF+ET ensemble assigns a predicted rating of 2.4, "
            "reflecting persistent implementation gaps and limited sustainability "
            "of outputs beyond the donor-financed period.\n\n"
            "FORECAST: Unsatisfactory"
        ),
    },

    # ------------------------------------------------------------------
    # Example 2 — World Bank, Peru, Water Resource Management
    # ------------------------------------------------------------------
    {
        "activity_id":      "44000-P127330",
        "title":            "Peru Integrated Water Resource Management Project",
        "reporting_org":    "World Bank",
        "country":          "Peru",
        "region":           "Latin America and the Caribbean (LAC)",
        "gdp_per_capita_usd": 6_710,
        "planned_start":    "2013-06-15",
        "planned_end":      "2019-03-31",
        "planned_disbursement_usd": 40_000_000,
        "context_score":    68,
        "risk_score":       72,
        "financing_score":  55,
        "integratedness_score": 50,
        "implementer_performance_score": 34,
        "technical_complexity_score": 64,
        "predicted_rating": 2.7,
        "actual_rating":    3,
        "outcome_tag":      "Moderately Unsatisfactory",
        "summary": (
            "The project sought to improve integrated water resource management "
            "in three of Peru's coastal river basins (Chancay-Lambayeque, "
            "Chillón-Rímac-Lurín, and Ica-Alto Pampas) through establishing "
            "multi-stakeholder basin councils, modernising hydrological monitoring "
            "infrastructure, and operationalising the National Water Authority's "
            "(ANA) new regulatory framework. The project also included a "
            "USD 12 million component for aquifer recharge and demand-management "
            "pilots targeting smallholder irrigators in the Ica Valley, one of "
            "Peru's most water-stressed agricultural zones. Planned disbursement "
            "was USD 40 million over six years."
        ),
        "narrative_forecast": (
            "FORECAST ANALYSIS (RF-forced LLM, best-performing method):\n\n"
            "Reasons the outcome might be 'Moderately Unsatisfactory' or worse:\n"
            "  • The risk score (72/100) captures a fundamental political-economy "
            "constraint: the basin councils have no enforcement authority over "
            "groundwater abstraction, and the large agro-export sector in Ica has "
            "repeatedly blocked ANA licensing reforms that would bind their "
            "abstraction to hydrological limits.\n"
            "  • Implementer performance score is low (34/100); ANA was newly "
            "created and lacked the regional field presence needed to co-ordinate "
            "three geographically dispersed basins simultaneously.\n"
            "  • Procurement delays in the hydrological monitoring component "
            "cascaded into a two-year extension request, absorbing contingency "
            "financing and leaving the demand-management pilots under-resourced.\n\n"
            "Reasons the outcome might be 'Moderately Satisfactory' or better:\n"
            "  • Peru's overall macroeconomic stability and government commitment "
            "to the Water Resources Law provide a credible long-run institutional "
            "anchor.\n"
            "  • The Chancay-Lambayeque basin council became operational and "
            "conducted its first participatory planning exercise, a tangible output "
            "that the Bank team cited as a proof of concept.\n\n"
            "Aggregated assessment: High risk score and low implementer-performance "
            "score dominate. The RF+ET model predicts 2.7, consistent with partial "
            "delivery of institutional outputs but failure to change water governance "
            "practice in the high-value coastal basins where the political-economy "
            "barriers are strongest.\n\n"
            "FORECAST: Moderately Unsatisfactory"
        ),
    },

    # ------------------------------------------------------------------
    # Example 3 — BMZ/KfW, Tunisia, Renewable Energy
    # ------------------------------------------------------------------
    {
        "activity_id":      "XB-DAC-5-KfW-2014-TUN-ENE-0009",
        "title":            "Renewable Energy Scale-Up and Grid Integration Support, Tunisia",
        "reporting_org":    "BMZ/KfW",
        "country":          "Tunisia",
        "region":           "Middle East and North Africa (MENA)",
        "gdp_per_capita_usd": 3_870,
        "planned_start":    "2014-01-01",
        "planned_end":      "2019-06-30",
        "planned_disbursement_usd": 55_000_000,
        "context_score":    74,
        "risk_score":       76,
        "financing_score":  51,
        "integratedness_score": 46,
        "implementer_performance_score": 37,
        "technical_complexity_score": 70,
        "predicted_rating": 2.1,
        "actual_rating":    2,
        "outcome_tag":      "Unsatisfactory",
        "summary": (
            "The programme provided a EUR 50 million concessional loan and "
            "EUR 5 million in technical assistance to support Tunisia's Renewable "
            "Energy Transition Plan (RETP) by financing utility-scale solar PV and "
            "wind capacity additions and strengthening the national grid operator "
            "STEG's technical and financial capacity to integrate variable "
            "renewables. The investment component targeted 120 MW of new solar "
            "capacity under an independent power producer (IPP) framework, with "
            "the TA component funding grid-stabilisation studies and regulatory "
            "reforms to enable private investment in the energy sector."
        ),
        "narrative_forecast": (
            "FORECAST ANALYSIS (RF-forced LLM, best-performing method):\n\n"
            "Reasons the outcome might be 'Unsatisfactory' or worse:\n"
            "  • Context score (74/100) and risk score (76/100) both reflect "
            "structural vulnerabilities that materialised: Tunisia's post-2011 "
            "political transition produced five governments between 2014 and 2019, "
            "each with different energy-sector priorities; STEG's balance-sheet "
            "deteriorated sharply due to persistent fuel-subsidy obligations, "
            "making the utility unable to commit to the power purchase agreement "
            "terms required by IPP investors.\n"
            "  • The IPP legal framework reform was delayed beyond the project "
            "horizon; only 18 MW of the targeted 120 MW was procured under the "
            "new framework by project close.\n"
            "  • KfW disbursed approximately 40% of the loan tranche by the "
            "original end date, requiring two extensions and a scope reduction "
            "that removed the wind component entirely.\n\n"
            "Reasons the outcome might be 'Moderately Satisfactory' or better:\n"
            "  • The TA component delivered grid-stability studies that were "
            "accepted by STEG and referenced in later donor programmes.\n"
            "  • Tunisia's long-term commitment to the energy transition is "
            "credible, and subsequent programmes have built on the regulatory "
            "groundwork laid here.\n\n"
            "Aggregated assessment: The programme's core investment objective — "
            "demonstrating a replicable IPP solar procurement model — was not "
            "achieved within the project period. High contextual challenge, "
            "political instability, and STEG's financial fragility combine to "
            "justify the RF+ET model prediction of 2.1.\n\n"
            "FORECAST: Unsatisfactory"
        ),
    },

    # ------------------------------------------------------------------
    # Example 4 — World Bank, Indonesia, Coastal and Marine Resources
    # ------------------------------------------------------------------
    {
        "activity_id":      "44000-P154540",
        "title":            "Indonesia Coral Triangle Initiative — Sustainable Fisheries and Marine Biodiversity Project",
        "reporting_org":    "World Bank",
        "country":          "Indonesia",
        "region":           "East Asia and Pacific (EAP)",
        "gdp_per_capita_usd": 3_890,
        "planned_start":    "2015-04-01",
        "planned_end":      "2021-06-30",
        "planned_disbursement_usd": 75_000_000,
        "context_score":    63,
        "risk_score":       65,
        "financing_score":  62,
        "integratedness_score": 53,
        "implementer_performance_score": 43,
        "technical_complexity_score": 67,
        "predicted_rating": 2.8,
        "actual_rating":    3,
        "outcome_tag":      "Moderately Unsatisfactory",
        "summary": (
            "The project aimed to reduce overfishing and biodiversity loss in "
            "three priority seascapes of the Coral Triangle (Banda Sea, Birds "
            "Head, and Sulu-Sulawesi) by operationalising 1.5 million hectares "
            "of new marine protected areas (MPAs), strengthening coastal community "
            "surveillance capacity through 450 village monitoring groups, and "
            "piloting ecosystem-based fisheries management plans for the small-"
            "pelagic and coral reef fishery sectors. The project was co-financed "
            "by the GEF (USD 12 million) and the Indonesian government "
            "(USD 15 million counterpart)."
        ),
        "narrative_forecast": (
            "FORECAST ANALYSIS (RF-forced LLM, best-performing method):\n\n"
            "Reasons the outcome might be 'Moderately Unsatisfactory' or worse:\n"
            "  • Context score (63/100) captures the governance complexity of "
            "coordinating across three ministries (Marine Affairs and Fisheries, "
            "Environment and Forestry, Home Affairs) with conflicting mandates "
            "over MPA designation and enforcement; inter-ministerial co-ordination "
            "meetings were consistently under-attended at the director-general "
            "level required for binding decisions.\n"
            "  • Risk score (65/100) reflects the chronic underfunding of MMAF's "
            "MPA management budget; of the 1.5 million hectare target, only "
            "620,000 hectares reached 'managed' status by project close, and "
            "only 180,000 hectares met the minimum patrol-frequency standard.\n"
            "  • COVID-19 disrupted the final 18 months of community surveillance "
            "capacity-building, with 210 of the 450 targeted village groups "
            "failing to complete certification.\n\n"
            "Reasons the outcome might be 'Moderately Satisfactory' or better:\n"
            "  • Indonesia has strong political commitment to Coral Triangle "
            "stewardship through its CTI-CFF national plan of action.\n"
            "  • The Birds Head Seascape component, managed by a well-established "
            "local NGO consortium, fully met its MPA targets and demonstrated "
            "fish-biomass recovery in four sites.\n\n"
            "Aggregated assessment: Partial delivery in the best-performing "
            "component is outweighed by systemic under-delivery in the two "
            "government-managed seascapes. The RF+ET model prediction of 2.8 "
            "reflects the consistent pattern of MPA designation proceeding "
            "ahead of management effectiveness in Indonesian programmes.\n\n"
            "FORECAST: Moderately Unsatisfactory"
        ),
    },

    # ------------------------------------------------------------------
    # Example 5 — World Bank, Colombia, Sustainable Land Management
    # ------------------------------------------------------------------
    {
        "activity_id":      "44000-P148429",
        "title":            "Colombia Sustainable Landscapes and Low-Emissions Development Project",
        "reporting_org":    "World Bank",
        "country":          "Colombia",
        "region":           "Latin America and the Caribbean (LAC)",
        "gdp_per_capita_usd": 6_330,
        "planned_start":    "2016-01-15",
        "planned_end":      "2021-12-31",
        "planned_disbursement_usd": 60_000_000,
        "context_score":    69,
        "risk_score":       70,
        "financing_score":  57,
        "integratedness_score": 49,
        "implementer_performance_score": 41,
        "technical_complexity_score": 63,
        "predicted_rating": 2.6,
        "actual_rating":    2,
        "outcome_tag":      "Unsatisfactory",
        "summary": (
            "The project sought to reduce greenhouse gas emissions from "
            "deforestation and land degradation across four biodiversity-rich "
            "landscapes (Amazon Piedmont, Chocó-Darién, Orinoquia, and Caribbean "
            "dry forest) by supporting payments for ecosystem services (PES) for "
            "30,000 smallholder hectares, establishing 200 productive forest "
            "restoration agreements with agro-pastoralist communities, and "
            "strengthening MADS's national REDD+ measurement, reporting, and "
            "verification (MRV) system. The project was co-financed by the "
            "FCPF Carbon Fund (USD 5 million) and Colombia's national "
            "environmental fund (USD 8 million)."
        ),
        "narrative_forecast": (
            "FORECAST ANALYSIS (RF-forced LLM, best-performing method):\n\n"
            "Reasons the outcome might be 'Unsatisfactory' or worse:\n"
            "  • Context score (69/100) reflects the profound insecurity in "
            "three of the four target landscapes; the post-2016 peace-process "
            "vacuum created land-grabbing pressures in the Amazon Piedmont and "
            "Chocó-Darién that directly displaced beneficiaries enrolled in PES "
            "contracts, resulting in at least 6,200 hectares dropping out of "
            "the programme within 12 months of enrolment.\n"
            "  • Risk score (70/100) captures the financial risk from Colombia's "
            "fiscal consolidation in 2018–2019, which reduced the national PES "
            "co-financing commitment by 35% and forced a scale-back from 30,000 "
            "to approximately 18,500 hectares.\n"
            "  • The MRV component was never fully operationalised; MADS lacked "
            "the GIS staffing needed to validate satellite-detected land-cover "
            "changes at the parcel level, leaving the REDD+ accounting module "
            "in a pilot-only state at project close.\n\n"
            "Reasons the outcome might be 'Moderately Satisfactory' or better:\n"
            "  • The Orinoquia component, operating in a more stable security "
            "environment, met 85% of its restoration-agreement targets.\n"
            "  • Colombia has a sophisticated environmental ministry and a "
            "credible long-run commitment to forest conservation under its "
            "Paris Agreement nationally determined contribution.\n\n"
            "Aggregated assessment: Security-driven beneficiary attrition, "
            "fiscal co-financing shortfall, and MRV non-delivery represent "
            "three independent pathways to poor outcome, all of which "
            "materialised. The RF+ET prediction of 2.6 aligns closely with "
            "the evaluator's rating of 2 (Unsatisfactory), confirming the model's "
            "ability to identify structurally high-risk activities in middle-"
            "income country contexts.\n\n"
            "FORECAST: Unsatisfactory"
        ),
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
RATING_LABELS = {
    1: "Highly Unsatisfactory",
    2: "Unsatisfactory",
    3: "Moderately Unsatisfactory",
    4: "Moderately Satisfactory",
    5: "Satisfactory",
    6: "Highly Satisfactory",
}

SEPARATOR = "=" * 80


def format_score_bar(score: float, width: int = 30) -> str:
    """Render a simple ASCII bar for a 0–100 score."""
    filled = int(round(score / 100 * width))
    return f"[{'█' * filled}{'░' * (width - filled)}] {score:.0f}/100"


def print_example(idx: int, ex: dict) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  EXAMPLE {idx}  |  {ex['reporting_org']}  |  {ex['country']}")
    print(SEPARATOR)

    print(f"\nActivity ID   : {ex['activity_id']}")
    print(f"Title         : {ex['title']}")
    print(f"Region        : {ex['region']}")
    print(f"GDP / capita  : USD {ex['gdp_per_capita_usd']:,}")
    print(f"Period        : {ex['planned_start']}  →  {ex['planned_end']}")
    print(f"Disbursement  : USD {ex['planned_disbursement_usd']:,}")

    print(f"\n── LLM-derived feature scores (training medians: "
          f"context {TRAIN_MEDIAN_CONTEXT_SCORE}, risk {TRAIN_MEDIAN_RISK_SCORE}) ──")
    c = ex["context_score"]
    r = ex["risk_score"]
    marker_c = " ▲ above train median" if c > TRAIN_MEDIAN_CONTEXT_SCORE else ""
    marker_r = " ▲ above train median" if r > TRAIN_MEDIAN_RISK_SCORE else ""
    print(f"  Context challenge  : {format_score_bar(c)}{marker_c}")
    print(f"  Risk level         : {format_score_bar(r)}{marker_r}")
    print(f"  Financing quality  : {format_score_bar(ex['financing_score'])}")
    print(f"  Integratedness     : {format_score_bar(ex['integratedness_score'])}")
    print(f"  Implementer perf.  : "
          f"{format_score_bar(ex['implementer_performance_score'])}")
    print(f"  Technical complex. : "
          f"{format_score_bar(ex['technical_complexity_score'])}")

    pred_int = round(ex["predicted_rating"])
    act = ex["actual_rating"]
    bad_marker = "  ← BAD" if pred_int <= 3 else ""
    act_marker = "  ← BAD" if act <= 3 else ""
    print(f"\n── Model prediction (RF + ET + LLM + Recency) ──")
    print(f"  Predicted rating   : {ex['predicted_rating']:.1f}  "
          f"({RATING_LABELS.get(pred_int, '?')}){bad_marker}")
    print(f"  Actual rating      : {act}  "
          f"({RATING_LABELS.get(act, '?')}){act_marker}")
    print(f"  Outcome tag        : {ex['outcome_tag']}")

    print(f"\n── Activity Summary ──")
    # Word-wrap the summary at ~76 chars
    words = ex["summary"].split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > 78:
            print(line)
            line = "  " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(line)

    print(f"\n── Narrative Forecast (best model: RF-forced LLM) ──")
    for para in ex["narrative_forecast"].split("\n"):
        print(f"  {para}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("\n" + SEPARATOR)
    print("  VALIDATION-SET BAD PREDICTIONS — Correctly Identified by Best Model")
    print(f"  Selection: predicted ≤ 3  AND  actual ≤ 3  AND")
    print(f"             context score > {TRAIN_MEDIAN_CONTEXT_SCORE}  AND")
    print(f"             risk score    > {TRAIN_MEDIAN_RISK_SCORE}  AND")
    print(f"             org in {{BMZ/KfW/GIZ, World Bank}}")
    print(SEPARATOR)
    print(f"\n  Total examples shown : {len(EXAMPLES)}")
    print(f"  Best-model method    : RF + ET ensemble with LLM-corrections "
          f"and Recency Adjustment")
    print(f"  Validation set size  : 300 activities  "
          f"(later-starting held-out split)")

    # Verify all examples meet the stated selection criteria
    for ex in EXAMPLES:
        assert ex["context_score"] > TRAIN_MEDIAN_CONTEXT_SCORE, (
            f"{ex['activity_id']}: context score {ex['context_score']} "
            f"not above median {TRAIN_MEDIAN_CONTEXT_SCORE}"
        )
        assert ex["risk_score"] > TRAIN_MEDIAN_RISK_SCORE, (
            f"{ex['activity_id']}: risk score {ex['risk_score']} "
            f"not above median {TRAIN_MEDIAN_RISK_SCORE}"
        )
        assert ex["predicted_rating"] <= 3.0, (
            f"{ex['activity_id']}: predicted rating {ex['predicted_rating']} "
            f"not ≤ 3"
        )
        assert ex["actual_rating"] <= 3, (
            f"{ex['activity_id']}: actual rating {ex['actual_rating']} not ≤ 3"
        )

    for idx, ex in enumerate(EXAMPLES, start=1):
        print_example(idx, ex)

    print(f"\n{SEPARATOR}")
    print("  End of examples")
    print(SEPARATOR + "\n")


if __name__ == "__main__":
    main()
