#War simulation
import random
import copy
import sys

def maker():
    print("=== Simulation Setup ===")
    try:
        years = int(input("Enter the number of years for the simulation to run: "))
    except ValueError:
        print("Invalid input. Defaulting to 50 years.")
        years = 50
    print("\n--- World Conditions ---")
    try:
        conflict_prob = float(input("Enter the annual Conflict Probability (0.0 for never, 1.0 for always): "))
        conflict_prob = max(0.0, min(1.0, conflict_prob)) # Bound between 0 and 1
    except ValueError:
        print("Invalid input. Defaulting to 0.4 (40% chance per year).")
        conflict_prob = 0.4
    print("\n--- Configure Entity 1 ---")
    name_1 = input("Enter name for Entity 1 (e.g., Country A): ") or "Entity 1"
    try:
        might_1 = float(input(f"Enter {name_1}'s Military Might (e.g., 10 to 100): "))
        peace_1 = float(input(f"Enter {name_1}'s Initial Peace Calibration (0.0 to 1.0): "))
    except ValueError:
        print("Invalid input. Using defaults (Might: 50, Peace: 0.5)")
        might_1, peace_1 = 50.0, 0.5
    print("\n--- Configure Entity 2 ---")
    name_2 = input("Enter name for Entity 2 (e.g., Country B): ") or "Entity 2"
    try:
        might_2 = float(input(f"Enter {name_2}'s Military Might (e.g., 10 to 100): "))
        peace_2 = float(input(f"Enter {name_2}'s Initial Peace Calibration (0.0 to 1.0): "))
    except ValueError:
        print("Invalid input. Using defaults (Might: 50, Peace: 0.5)")
        might_2, peace_2 = 50.0, 0.5
    config = {
        "years": years,
        "conflict_probability": conflict_prob,
        "entity_1": {"name": name_1, "might": might_1, "peace": max(0.0, min(1.0, peace_1))},
        "entity_2": {"name": name_2, "might": might_2, "peace": max(0.0, min(1.0, peace_2))}
    }
    print("\n=== Setup Complete! ===")
    print(f"Simulation: {config['years']} years | Conflict Probability: {config['conflict_probability'] * 100}% per year")
    print(f"{config['entity_1']['name']}: Might = {config['entity_1']['might']}, Peace Preference = {config['entity_1']['peace']}")
    print(f"{config['entity_2']['name']}: Might = {config['entity_2']['might']}, Peace Preference = {config['entity_2']['peace']}")
    return config

def execute_war(config):
    e1 = config["entity_1"]
    e2 = config["entity_2"]
    total_might = e1["might"] + e2["might"]
    if total_might == 0:
        total_might = 1  
    e1_win_percentage = int((e1["might"] / total_might) * 100)
    roll = random.randint(1, 100)
    # Track original mights before the war modifiers alter them
    orig_winner_might = e1["might"] if roll <= e1_win_percentage else e2["might"]
    orig_loser_might = e2["might"] if roll <= e1_win_percentage else e1["might"]
    if roll <= e1_win_percentage:
        winner, loser = e1, e2
        was_fluke = (roll > (100 - e1_win_percentage)) 
    else:
        winner, loser = e2, e1
        was_fluke = (roll <= e1_win_percentage) # A2 won despite A1 having a higher win chance 
    reward_multiplier = random.uniform(0.1, 0.5)
    expected_reward = total_might * reward_multiplier
    damage_winner = expected_reward * random.uniform(0.3, 0.7)
    winner["might"] = round(winner["might"] + (winner["might"] * 0.02), 2)
    loser["might"] = round(loser["might"] - (loser["might"] * 0.05), 2)
    if loser["might"] < 1: 
        loser["might"] = 1 
    # 1. THE REVANCHIST GRUDGE 
    # Loser was close in power (>= 80% of winner's might) but lost due to an unlucky roll/fluke.
    if orig_loser_might >= (orig_winner_might * 0.8) and was_fluke:
        loser["peace"] = max(0.0, round(loser["peace"] - 0.04, 2))  
    # 2. THE HEGEMONIC REALISM ("Strategic Submission")
    # Winner is overwhelmingly stronger (more than double the loser's might).
    # Loser accepts peace to survive, but caps long-term peace at 0.70 because they don't fully forget.
    elif orig_winner_might > (orig_loser_might * 2.0):
        loser["peace"] = min(0.70, round(loser["peace"] + 0.03, 2)) 
    # 3. THE STALEMATE DETERRENCE ("Equilibrium")
    # Regular loss between relatively matched nations. They accept the loss and cautiously look for peace.
    else:
        loser["peace"] = min(1.0, round(loser["peace"] + 0.02, 2))  
    # Determine if the war was worth it for the winner
    was_worth_it = damage_winner <= expected_reward
    if not was_worth_it:
        # Heavily increase peace calibration because costs outweighed rewards
        winner["peace"] = min(1.0, round(winner["peace"] + 0.15, 2))
    else:
        # Usual slight drop due to successful aggression
        winner["peace"] = max(0.0, round(winner["peace"] - 0.02, 2))  
    give = {
        "winner_name": winner["name"],
        "loser_name": loser["name"],
        "was_worth_it": was_worth_it,
        "expected_reward": round(expected_reward, 2),
        "winner_damage": round(damage_winner, 2)
    }
    return config, give

def simulator(config):
    history = []
    years_to_run = config["years"]
    conflict_prob = config["conflict_probability"]
    for year in range(1, years_to_run + 1):
        if random.random() <= conflict_prob:
            # 2. Conflict arose! Check if entities want peace or war
            e1_wants_peace = random.random() < config["entity_1"]["peace"]
            e2_wants_peace = random.random() < config["entity_2"]["peace"]
            if e1_wants_peace and e2_wants_peace:
                # Both chose peace -> Diplomacy succeeds!
                config["entity_1"]["peace"] = min(1.0, round(config["entity_1"]["peace"] + 0.05, 2))
                config["entity_2"]["peace"] = min(1.0, round(config["entity_2"]["peace"] + 0.05, 2))
                # Log the diplomatic reaction and snapshot the config
                history.append({
                    "year": year,
                    "event": "Diplomatic Resolution",
                    "details": "Both entities negotiated successfully.",
                    "nation_reactions": copy.deepcopy(config)
                })
            else:
                # At least one chose war -> Call the execute_war function
                config, give = execute_war(config)
                # Log the war results and snapshot the config to see how they reacted
                history.append({
                    "year": year,
                    "event": "War",
                    "details": give,
                    "nation_reactions": copy.deepcopy(config)
                })
    return history, config

def main():
    print("==================================================")
    print("   WELCOME TO THE PEACE VS. WAR SIMULATOR")
    print("==================================================")
    print("This simulation models how two nations interact over time.")
    print("Based on military power, global volatility, and past conflict")
    print("damages, they will learn whether to choose diplomacy or war.\n")
    while True:
        print("Menu:")
        print(" [1] Run a New Simulation")
        print(" [q] Quit Program")
        choice = input("\nSelect an option and press Enter: ").strip().lower()
        if choice == '1':
            config = maker()
            print("\nRunning simulation engine...")
            history, final_config = simulator(config)
            print("\n================ SIMULATION LOG ==================")
            if not history:
                print("The world remained completely peaceful. No conflicts erupted!")
            else:
                for log in history:
                    year = log["year"]
                    event = log["event"]
                    if event == "Diplomatic Resolution":
                        p1 = log["nation_reactions"]["entity_1"]["peace"]
                        p2 = log["nation_reactions"]["entity_2"]["peace"]
                        print(f"[Year {year}] ️ Diplomacy Succeeded! Both chose negotiation.")
                        print(f"         New Peace Mindset -> E1: {p1} | E2: {p2}")
                    elif event == "War":
                        details = log["details"]
                        winner = details["winner_name"]
                        loser = details["loser_name"]
                        worth_it = "YES" if details["was_worth_it"] else "NO (Pyrrhic Victory)"
                        p1 = log["nation_reactions"]["entity_1"]["peace"]
                        p2 = log["nation_reactions"]["entity_2"]["peace"]
                        m1 = log["nation_reactions"]["entity_1"]["might"]
                        m2 = log["nation_reactions"]["entity_2"]["might"]
                        print(f"[Year {year}]  WAR BREAKS OUT! {winner} defeated {loser}.")
                        print(f"         Was it worth it for the winner? {worth_it}")
                        print(f"         Stakes: {details['expected_reward']} | Winner Damage: {details['winner_damage']}")
                        print(f"         Post-War Might    -> E1: {m1} | E2: {m2}")
                        print(f"         Post-War Mindset  -> E1: {p1} | E2: {p2}")
                    print("-" * 50)
            print("\n================ FINAL STATE ================")
            print(f"{final_config['entity_1']['name']}: Might = {final_config['entity_1']['might']}, Final Peace Preference = {final_config['entity_1']['peace']}")
            print(f"{final_config['entity_2']['name']}: Might = {final_config['entity_2']['might']}, Final Peace Preference = {final_config['entity_2']['peace']}")
            print("=============================================\n")  
        elif choice == 'q':
            print("\nThank you for using the simulator. Goodbye!")
            sys.exit()
        else:
            print("\n[Invalid Choice] Please type '1' to run or 'q' to quit.\n")


if __name__ == "__main__":
    main()


