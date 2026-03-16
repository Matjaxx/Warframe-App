def reward_name(reward: dict | None) -> str | None:
    if reward is None:
        return None
    return reward.get("item", {}).get("name")


def reward_slug(reward: dict | None) -> str | None:
    if reward is None:
        return None
    return reward.get("item", {}).get("warframeMarket", {}).get("urlName")


def classify_reward_by_chance(reward: dict) -> str | None:
    chance = reward.get("chance")

    try:
        chance_value = float(chance)
    except (TypeError, ValueError):
        return None

    # valeurs exactes de relic classique
    if chance_value == 25.33:
        return "bronze"
    if chance_value == 11:
        return "argent"
    if chance_value == 2:
        return "gold"

    # fallback
    if chance_value >= 20:
        return "bronze"
    if chance_value >= 10:
        return "argent"
    return "gold"


def split_rewards(
    rewards: list[dict],
) -> tuple[list[dict | None], list[dict | None], list[dict | None]]:
    bronze: list[dict | None] = []
    argent: list[dict | None] = []
    gold: list[dict | None] = []

    for reward in rewards:
        bucket = classify_reward_by_chance(reward)

        if bucket == "bronze":
            bronze.append(reward)
        elif bucket == "argent":
            argent.append(reward)
        elif bucket == "gold":
            gold.append(reward)

    bronze = bronze[:3]
    argent = argent[:2]
    gold = gold[:1]

    while len(bronze) < 3:
        bronze.append(None)

    while len(argent) < 2:
        argent.append(None)

    while len(gold) < 1:
        gold.append(None)

    return bronze, argent, gold