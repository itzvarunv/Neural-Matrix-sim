import random
import json
import os
import math
import shutil

# =========================================================================
# SYSTEM STORAGE DIRECTORY SETUP
# =========================================================================
LOBBY_DIR = "lobby"
CEMETERY_DIR = "cemetery"

def initialize_directories():
    """Wipes old tracking records to prepare a clean, isolated matrix environment."""
    for folder in [LOBBY_DIR, CEMETERY_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

global_death_ledger = {
    "Wealthy": {"Starvation / Exhaustion": 0, "Biological Limit (Old Age)": 0, "Socio-Economic Disease Roll": 0, "Random Natural Disaster": 0},
    "Middle":  {"Starvation / Exhaustion": 0, "Biological Limit (Old Age)": 0, "Socio-Economic Disease Roll": 0, "Random Natural Disaster": 0},
    "Poor":    {"Starvation / Exhaustion": 0, "Biological Limit (Old Age)": 0, "Socio-Economic Disease Roll": 0, "Random Natural Disaster": 0}
}

# =========================================================================
# NEURAL ENGINE MATRIX WITH PLASTICITY CAPACITY
# =========================================================================
class NPCBrain:
    def __init__(self, weights=None):
        if weights is None:
            # 5 inputs: [self_energy, self_savings, perceived_density, self_age, situational_variable]
            self.weights = [random.uniform(-0.5, 0.5) for _ in range(5)]
        else:
            self.weights = list(weights)

    def think(self, inputs):
        """Standard Sigmoid activation returning choice probability vector maps."""
        dot_product = sum(i * w for i, w in zip(inputs, self.weights))
        dot_product = max(-20, min(20, dot_product))  # Numerical overflow protection
        try:
            return 1.0 / (1.0 + math.exp(-dot_product))
        except:
            return 0.5

    def mutate(self, rate=0.05):
        """Applies Gaussian noise to weights upon generational reproduction mapping."""
        new_weights = [w + random.uniform(-rate, rate) for w in self.weights]
        return NPCBrain(new_weights)

# =========================================================================
# PERSISTENT AGENT CHASSIS WITH REINFORCEMENT LOGIC
# =========================================================================
class BrainedCivilian:
    def __init__(self, cid, gender, age, social_class, economy_mode, initial_location, brain=None):
        self.id = cid
        self.gender = gender       
        self.age = age
        self.social_class = social_class  
        self.economy_mode = economy_mode
        
        self.energy = 100
        self.food_supply = 100
        self.savings = random.uniform(30, 80) if economy_mode == "cash" else 0.0
        self.children_count = 0
        self.puberty_passed = True if age >= 14 else False
        self.attraction_drive = round(random.uniform(0.5, 1.0), 2)
        self.post_childbirth_trauma = False
        
        self.visited_continents = [initial_location]
        self.brain = brain if brain is not None else NPCBrain()
        self.update_class_privileges()
        
        self.biography = {
            "agent_id": self.id,
            "assigned_gender": self.gender,
            "total_kids_count": 0,
            "children_produced_ids": [],
            "final_status": "Alive",
            "cause_of_death": "N/A",
            "year_of_death": "N/A",
            "final_savings_balance": self.savings,
            "final_energy_level": self.energy,
            "travel_history_log": self.visited_continents, 
            "biometric_history_log": [],
            "marriage_history": [],
            "brain_weights": self.brain.weights
        }

    def update_class_privileges(self):
        if self.social_class == "Wealthy": 
            self.food_security_chance = 0.99
            self.class_risk_multiplier = 1.1
        elif self.social_class == "Middle": 
            self.food_security_chance = 0.75
            self.class_risk_multiplier = 1.2  
        else: # Poor
            self.food_security_chance = 0.40
            self.class_risk_multiplier = 4.0

    def track_travel(self, sector_name):
        if not self.visited_continents or self.visited_continents[-1] != sector_name:
            self.visited_continents.append(sector_name)
            self.biography["travel_history_log"] = list(self.visited_continents)

    def log_year_telemetry(self, current_year, current_location):
        if self.biography["final_status"] == "Dead": return
        
        snapshot = {
            "year": current_year,
            "age": self.age,
            "location_sector": current_location,
            "energy": int(self.energy),
            "savings_bank_balance": round(self.savings, 2),
            "social_class": self.social_class
        }
        self.biography["biometric_history_log"].append(snapshot)
        self.biography["final_energy_level"] = int(self.energy)
        self.biography["final_savings_balance"] = round(self.savings, 2)
        self.biography["brain_weights"] = list(self.brain.weights)

    def apply_behavioral_reinforcement(self, reward_type, parameters=None):
        """
        NEW MECHANIC: Dynamic Lifelong Operant Conditioning.
        Directly updates neural network vectors based on economic/metabolic outcomes.
        """
        learning_rate = 0.02
        
        if reward_type == "STATIONARY_INTEREST_GAIN":
            # Reward staying put: increase weight tolerance for local density (W2)
            # and align savings appreciation with high-security inputs
            self.brain.weights[2] += learning_rate * 1.5  # Positive density attachment
            self.brain.weights[1] += learning_rate * 1.0  # Appreciating value of savings input
            
        elif reward_type == "MIGRATION_TAX_PUNISHMENT":
            # Penalize moving blindly: suppress weight that encourages impulsive travel
            self.brain.weights[1] -= learning_rate * 1.5  # Lower the baseline drive to move when holding cash
            self.brain.weights[0] -= learning_rate * 1.0  # Decouple raw metabolic panic from movement
            
        elif reward_type == "OVERCROWDED_SUFFOCATION":
            # Punish getting stuck in an absolute death trap:
            # Force the agent to develop a stronger aversion to high density spaces
            self.brain.weights[2] -= learning_rate * 2.0  # Negative weight to density triggers escape protocols

        # Clamp weights to prevent extreme numerical divergence
        self.brain.weights = [max(-4.0, min(4.0, w)) for w in self.brain.weights]

    def handle_death(self, current_year, cause):
        self.biography["final_status"] = "Dead"
        self.biography["cause_of_death"] = cause
        self.biography["year_of_death"] = current_year
        self.biography["final_energy_level"] = max(0, int(self.energy))
        self.biography["brain_weights"] = list(self.brain.weights)
        
        if cause in global_death_ledger[self.social_class]:
            global_death_ledger[self.social_class][cause] += 1
            
        cemetery_file = os.path.join(CEMETERY_DIR, f"ai_{self.id}_report.json")
        with open(cemetery_file, "w", encoding="utf-8") as f:
            json.dump(self.biography, f, indent=4)

    def save_final_living_biography(self):
        filepath = os.path.join(LOBBY_DIR, f"ai_{self.id}_report.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.biography, f, indent=4)


# =========================================================================
# REWARD-ENGINE LINKED CENTRAL BANK
# =========================================================================
def process_central_bank_dividends(world_spaces):
    """Stationary agents capitalize on compounding interest and receive positive brain rewards."""
    for space_name, population_dict in world_spaces.items():
        for civ in population_dict.values():
            if civ.economy_mode == "cash":
                if len(civ.visited_continents) >= 2 and civ.visited_continents[-1] == civ.visited_continents[-2]:
                    civ.savings = round(civ.savings * 1.05, 2)
                    # Trigger cognitive reinforcement reward loop
                    civ.apply_behavioral_reinforcement("STATIONARY_INTEREST_GAIN")
    return world_spaces


# =========================================================================
# MIGRATION LOOP INTEGRATED WITH PUNISHMENT SYSTEM
# =========================================================================
def process_simultaneous_migration(world_spaces, settings):
    densities = {}
    for name, pop_dict in world_spaces.items():
        cap = settings["spaces"][name]["capacity"]
        densities[name] = len(pop_dict) / cap if cap > 0 else 1.0

    best_target_space = min(world_spaces.keys(), key=lambda k: densities[k])
    scheduled_moves = []

    for space_name, population_dict in world_spaces.items():
        for cid, civ in population_dict.items():
            if civ.energy < 30: continue
            
            inputs = [
                civ.energy / 100.0,
                civ.savings / 100.0 if civ.economy_mode == "cash" else 0.0,
                densities[space_name],
                civ.age / 100.0,
                0.5
            ]
            migration_urge = civ.brain.think(inputs)
            
            if migration_urge > 0.70:
                if civ.economy_mode == "cash" and civ.savings < 5.0:
                    continue  
                if space_name != best_target_space:
                    scheduled_moves.append((cid, space_name, best_target_space))

    migrations_count = 0
    for cid, src, dest in scheduled_moves:
        if cid in world_spaces[src]:
            civ = world_spaces[src].pop(cid)
            if civ.economy_mode == "cash":
                civ.savings -= 5.0
                # Trigger cognitive punishment for paying the migration tax
                civ.apply_behavioral_reinforcement("MIGRATION_TAX_PUNISHMENT")
            civ.track_travel(dest) 
            world_spaces[dest][cid] = civ
            migrations_count += 1
            
    return world_spaces, migrations_count


# =========================================================================
# GLOBAL EVENTS MATRIX
# =========================================================================
def trigger_random_world_events(world_spaces, current_year):
    dice_roll = random.random()
    if dice_roll < 0.03:
        target_continent = random.choice(list(world_spaces.keys()))
        pop_dict = world_spaces[target_continent]
        if pop_dict:
            victim_id = random.choice(list(pop_dict.keys()))
            victim = pop_dict[victim_id]
            print(f" [💥 EVENT] A localized disaster struck {target_continent}! AI ID {victim_id} was lost.")
            pop_dict.pop(victim_id)
            victim.handle_death(current_year, "Random Natural Disaster")
    elif dice_roll < 0.07:
        target_continent = random.choice(list(world_spaces.keys()))
        pop_dict = world_spaces[target_continent]
        if pop_dict:
            lucky_id = random.choice(list(pop_dict.keys()))
            lucky_npc = pop_dict[lucky_id]
            if lucky_npc.economy_mode == "cash":
                lucky_npc.savings += 150.0
                print(f" [🎁 EVENT] Economy System Lottery payout processed! AI ID {lucky_id} gained +$150.00 cash.")


# =========================================================================
# METABOLISM & METABOLIC STRUCTURAL PUNISHMENT
# =========================================================================
def process_metabolism_and_mortality(world_spaces, settings, current_year):
    base_death_rate = 0.01  
    
    for space_name, population_dict in world_spaces.items():
        if not population_dict: continue
        
        cap = settings["spaces"][space_name]["capacity"]
        is_overcrowded = len(population_dict) > cap
        dead_list = []
        
        for cid, civ in population_dict.items():
            civ.age += 1
            if civ.age >= 14: civ.puberty_passed = True
            
            secured_food = random.random() < civ.food_security_chance
            if not secured_food and civ.economy_mode == "cash" and civ.savings >= 20:
                civ.savings -= 20
                secured_food = True
                
            if secured_food: civ.food_supply = min(100, civ.food_supply + 20)
            else: civ.food_supply = max(0, civ.food_supply - 25)
            
            energy_drain = 10
            if is_overcrowded:
                energy_drain += random.randint(20, 45)  
                civ.food_supply = max(0, civ.food_supply - 10)
                # Overcrowding feedback: punish the brain for being in an overallocated zone
                civ.apply_behavioral_reinforcement("OVERCROWDED_SUFFOCATION")
            else:
                if civ.food_supply > 50: civ.energy = min(100, civ.energy + 10)
                
            if civ.food_supply < 30: energy_drain += 20
            civ.energy = max(0, civ.energy - energy_drain)
            
            death_triggered = False
            cause = ""
            
            if civ.energy <= 0:
                death_triggered = True
                cause = "Starvation / Exhaustion"
            elif civ.age > 65:  
                death_triggered = True
                cause = "Biological Limit (Old Age)"
            else:
                calculated_disease_risk = base_death_rate * civ.class_risk_multiplier
                if civ.post_childbirth_trauma:
                    calculated_disease_risk += 0.10
                    civ.post_childbirth_trauma = False
                    
                if random.random() < calculated_disease_risk:
                    death_triggered = True
                    cause = "Socio-Economic Disease Roll"
                    
            if death_triggered:
                dead_list.append(cid)
                civ.handle_death(current_year, cause)
            else:
                civ.log_year_telemetry(current_year, space_name)
                
        for d_id in dead_list:
            population_dict.pop(d_id)
            
    return world_spaces


# =========================================================================
# SOCIO-ECONOMIC APPRAISAL FLUX
# =========================================================================
def process_social_flux(world_spaces, settings):
    for space_dict in world_spaces.values():
        for civ in space_dict.values():
            if civ.economy_mode == "cash":
                civ.savings += random.choice([-10.0, 15.0, 30.0]) 
                
            if civ.social_class == "Poor" and civ.energy >= 80 and civ.food_supply >= 80:
                civ.social_class = "Middle"
                civ.update_class_privileges()
            elif civ.social_class == "Middle":
                if civ.economy_mode == "cash" and civ.savings >= 120.0:  
                    civ.social_class = "Wealthy"
                    civ.update_class_privileges()
                elif civ.energy < 30:
                    civ.social_class = "Poor"
                    civ.update_class_privileges()
            elif civ.social_class == "Wealthy":
                if (civ.economy_mode == "cash" and civ.savings < 50.0) or civ.energy < 40:
                    civ.social_class = "Middle"
                    civ.update_class_privileges()
    return world_spaces


# =========================================================================
# PROCEDURAL MATERNAL WELFARE ENGINE
# =========================================================================
def process_procedural_courtship(world_spaces, id_counter, settings, current_year):
    diminishing_returns = {0: 1.0, 1: 0.8, 2: 0.5, 3: 0.2, 4: 0.0}
    class_values = {"Wealthy": 3, "Middle": 2, "Poor": 1}
    
    for space_name, population_dict in world_spaces.items():
        if len(population_dict) < 2: continue
        
        eligible_males = [m for m in population_dict.values() if m.gender == 'M' and m.puberty_passed and m.energy >= 40]
        eligible_females = [f for f in population_dict.values() if f.gender == 'F' and f.puberty_passed and f.energy >= 40]
        
        if not eligible_males or not eligible_females: continue
        
        selected_bachelors = random.sample(eligible_males, min(6, len(eligible_males)))
        pregnant_mothers = set()
        
        for father in selected_bachelors:
            available_women = [f for f in eligible_females if f.id not in pregnant_mothers]
            if not available_women: break
            
            for mother in random.sample(available_women, min(15, len(available_women))):
                partner_class_mapped = class_values[father.social_class]
                inputs = [
                    mother.energy / 100.0,
                    mother.savings / 100.0 if mother.economy_mode == "cash" else 0.0,
                    len(population_dict) / settings["spaces"][space_name]["capacity"],
                    mother.age / 100.0,
                    partner_class_mapped / 3.0
                ]
                consent_prob = mother.brain.think(inputs)
                
                union_record = {"year": current_year, "partner_id": father.id, "partner_class": father.social_class}
                
                if consent_prob >= 0.5:
                    mutual_love = (mother.attraction_drive + father.attraction_drive) / 2.0
                    fertility = diminishing_returns.get(min(mother.children_count, 4), 0.0)
                    higher_class = mother.social_class if class_values[mother.social_class] >= class_values[father.social_class] else father.social_class
                    success_threshold = 0.65 if higher_class == "Wealthy" else (0.45 if higher_class == "Middle" else 0.25)
                    
                    if random.random() < (mutual_love * fertility * success_threshold):
                        is_wealthy_protected = (mother.social_class == "Wealthy" or father.social_class == "Wealthy")
                        
                        if is_wealthy_protected and settings["economy_mode"] == "cash":
                            mother.energy = max(10, mother.energy - 10)  
                            father.energy = max(10, father.energy - 10)
                            mother.post_childbirth_trauma = False  
                            if father.savings >= 50.0:
                                father.savings -= 50.0
                            mother.savings += 50.0
                            
                        elif mother.social_class == "Middle" and settings["economy_mode"] == "cash":
                            mother.energy = max(10, mother.energy - 20)
                            father.energy = max(10, father.energy - 10)
                            mother.post_childbirth_trauma = True
                            if father.savings >= 25.0:
                                father.savings -= 25.0
                            mother.savings += 25.0
                            
                        else:
                            mother.energy = max(10, mother.energy - 20)
                            father.energy = max(10, father.energy - 10)
                            mother.post_childbirth_trauma = True
                        
                        pregnant_mothers.add(mother.id)
                        
                        mother.children_count += 1
                        father.children_count += 1
                        mother.biography["total_kids_count"] = mother.children_count
                        father.biography["total_kids_count"] = father.children_count
                        
                        child_weights = [(w1 + w2)/2.0 for w1, w2 in zip(mother.brain.weights, father.brain.weights)]
                        child_brain = NPCBrain(child_weights).mutate(rate=0.05)
                        
                        baby = BrainedCivilian(id_counter, random.choice(['M', 'F']), 0, higher_class, settings["economy_mode"], initial_location=space_name, brain=child_brain)
                        
                        mother.biography["children_produced_ids"].append(id_counter)
                        father.biography["children_produced_ids"].append(id_counter)
                        
                        union_record["outcome"] = "Conception Successful"
                        mother.biography["marriage_history"].append(union_record)
                        
                        population_dict[id_counter] = baby
                        id_counter += 1
                        break
                    else:
                        union_record["outcome"] = "Biological Incompatibility Fail"
                        mother.biography["marriage_history"].append(union_record)
                else:
                    union_record["outcome"] = f"Courtship Rejected (Brain Output: {round(consent_prob,2)})"
                    mother.biography["marriage_history"].append(union_record)
                    
    return world_spaces, id_counter


# =========================================================================
# ANALYTICS SUMMARY EXPORTER
# =========================================================================
def generate_simulation_csv():
    try:
        import pandas as pd
    except ImportError:
        print("[!] Install pandas ('pip install pandas') to generate a summary CSV.")
        return

    compiled_records = []
    for folder in [LOBBY_DIR, CEMETERY_DIR]:
        for file in os.listdir(folder):
            if file.endswith(".json"):
                with open(os.path.join(folder, file), "r") as f:
                    data = json.load(f)
                    compiled_records.append({
                        "Agent_ID": data["agent_id"],
                        "Gender": data["assigned_gender"],
                        "Total_Kids": data["total_kids_count"],
                        "Status": data["final_status"],
                        "Cause_of_Death": data["cause_of_death"],
                        "Year_of_Death": data["year_of_death"],
                        "Final_Savings": data["final_savings_balance"],
                        "Final_Energy": data["final_energy_level"],
                        "Unique_Regions_Visited": len(set(data["travel_history_log"])),
                        "W0_Energy_Weight": data["brain_weights"][0],
                        "W2_Density_Weight": data["brain_weights"][2]
                    })
    
    df = pd.DataFrame(compiled_records)
    df.to_csv("simulation_agent_data.csv", index=False)
    print("[📊 REINFORCEMENT LOG] Cognitive metrics exported to 'simulation_agent_data.csv'.")


# =========================================================================
# EXECUTIVE EXECUTION SYSTEM
# =========================================================================
def run_master_brained_engine():
    print("="*75)
    print("      🧠 ISOLATED DECENTRALIZED COGNITIVE LIFE SANDBOX — VER. 5.0")
    print("="*75)
    
    initialize_directories()
    
    seed_pop = int(input("Enter starting total seed population size of AI NPCs: "))
    bias_choice = input("Select Gender Dominance Balance (1 -> Male Bias, 2 -> Female Bias, 3 -> Standard 50/50): ").strip()
    eco_choice = input("Select Asset Medium: (1 -> Barter Trading, 2 -> Cash Savings Account-Paid): ").strip()
    
    economy_mode = "cash" if eco_choice == "2" else "barter"
    male_ratio = 0.70 if bias_choice == "1" else (0.30 if bias_choice == "2" else 0.50)
        
    settings = {
        "economy_mode": economy_mode,
        "spaces": {"Europe": {"capacity": 50}, "Asia": {"capacity": 150}, "Africa": {"capacity": 80}}
    }
    
    world_spaces = {"Europe": {}, "Asia": {}, "Africa": {}}
    id_counter = 1
    
    total_males = int(seed_pop * male_ratio)
    total_females = seed_pop - total_males
    genders = (['M'] * total_males) + (['F'] * total_females)
    random.shuffle(genders)
    
    for i in range(seed_pop):
        gender = genders[i]
        initial_age = random.randint(16, 45)
        
        brain = NPCBrain()
        brain.weights[2] = random.uniform(1.5, 3.0)   
        brain.weights[0] = random.uniform(-1.0, -0.2)  
        
        initial_landmass = "Europe" if i < int(seed_pop * 0.75) else ("Asia" if i < int(seed_pop * 0.90) else "Africa")
        
        civ = BrainedCivilian(id_counter, gender, initial_age, "Poor", economy_mode, initial_location=initial_landmass, brain=brain)
        world_spaces[initial_landmass][id_counter] = civ
        id_counter += 1

    print(f"\n[✓] Environments locked. Running 30-year live reinforcement test...")
    
    year = 1
    max_years = 30
    
    while year <= max_years:
        total_npcs = sum(len(space) for space in world_spaces.values())
        if total_npcs == 0:
            print(f"\n[] Global Extinction event triggered on Year {year}. All entities eliminated.")
            break
            
        eu_c = len(world_spaces["Europe"])
        as_c = len(world_spaces["Asia"])
        af_c = len(world_spaces["Africa"])
        
        # 1. RUN MIGRATION LOVES AND ASSIGN MIGRATION TAX BRAIN PUNISHMENTS
        world_spaces, migrations_count = process_simultaneous_migration(world_spaces, settings)
        trigger_random_world_events(world_spaces, current_year=year)
        
        # 2. ASSIGN AUTOMATIC BANK INTEREST AND REWARD STATIONARY BRAIN WEIGHTS
        world_spaces = process_central_bank_dividends(world_spaces)
        
        overcrowded_alerts = []
        for name, space_dict in world_spaces.items():
            if len(space_dict) > settings["spaces"][name]["capacity"]:
                overcrowded_alerts.append(f"{name} ({len(space_dict)}/{settings['spaces'][name]['capacity']})")
        alert_str = f" | 🚨 OVERALLOCATED: {', '.join(overcrowded_alerts)}" if overcrowded_alerts else ""
        
        print(f"[YEAR {year:02d}] Pop: {total_npcs} [EU: {eu_c} | AS: {as_c} | AF: {af_c}] | Neural Moves: {migrations_count}{alert_str}")
        
        # 3. METABOLISM & STRUCTURAL MORTALITY (INCORPORATING OVERCROWDED DEATH PROTOCOLS)
        world_spaces = process_metabolism_and_mortality(world_spaces, settings, current_year=year)
        world_spaces, id_counter = process_procedural_courtship(world_spaces, id_counter, settings, current_year=year)
        world_spaces = process_social_flux(world_spaces, settings)
        
        year += 1

    for space_dict in world_spaces.values():
        for civ in space_dict.values():
            civ.save_final_living_biography()

    print("\n" + "="*75)
    print("       REINFORCEMENT SIMULATION TERMINATION MATRIX")
    print("="*75)
    for bracket in ["Wealthy", "Middle", "Poor"]:
        print(f"\n[ {bracket.upper()} CLASS ANALYSIS MATRIX]")
        total_class_deaths = sum(global_death_ledger[bracket].values())
        print(f"  ▪ Total Casualties Processed: {total_class_deaths} entities")
        for cause, count in global_death_ledger[bracket].items():
            print(f"    ↳ {cause:<35} : {count:>4} dead")
    print("="*75 + "\n")

    generate_simulation_csv()

if __name__ == "__main__":
    run_master_brained_engine()
