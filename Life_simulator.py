import random
import json
import os

# =========================================================================
# THE COMPREHENSIVE DEMOGRAPHIC LEDGER
# =========================================================================
class SimulationTracker:
    def __init__(self):
        self.registry = {}
        
    def register_birth(self, entity_id, gender, birth_year, generation="Original Seed"):
        self.registry[str(entity_id)] = {
            "id": entity_id,
            "gender": gender,
            "generation": generation,
            "birth_year": birth_year,
            "death_year": None,
            "status": "Alive",
            "cause_of_death": "N/A",
            "final_energy": None,
            "final_class": "N/A"
        }

    def register_death(self, entity_id, death_year, cause, final_energy, final_class):
        if str(entity_id) in self.registry:
            self.registry[str(entity_id)].update({
                "status": "Dead",
                "death_year": death_year,
                "cause_of_death": cause,
                "final_energy": round(final_energy, 2),
                "final_class": final_class
            })

    def update_living_stats(self, world_spaces):
        for space_name, space_dict in world_spaces.items():
            for entity_id, civ in space_dict.items():
                if str(entity_id) in self.registry:
                    self.registry[str(entity_id)].update({
                        "final_energy": round(civ.energy, 2),
                        "final_class": civ.social_class
                    })

    def export_to_json(self, filename="simulation_ledger.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=4)
        print(f"\n[✓] Comprehensive JSON tracking ledger saved to '{filename}'!")

# Instantiate global ledger tracker
tracker = SimulationTracker()

simulation_analytics = {
    "total_deaths_by_cause": {
        "Starvation (No Food)": 0,
        "Energy Exhaustion (Overcrowding)": 0,
        "Old Age / Biological Limit": 0,
        "Medieval Disease / Die-Roll": 0
    },
    "deaths_by_class": {"Wealthy": 0, "Middle": 0, "Poor": 0}
}
        
# =========================================================================
# THE CIVILIAN ARCHETYPE
# =========================================================================
class Civilian:
    def __init__(self, cid, gender, age, social_class, economy_mode):
        self.id = cid
        self.gender = gender       
        self.age = age
        self.social_class = social_class  
        
        self.energy = 100
        self.food_supply = 100
        self.savings = 0.0 if economy_mode == "cash" else None
        
        self.update_class_privileges()
        self.puberty_passed = True if age >= 14 else False
        self.attraction_drive = round(random.uniform(0.5, 1.0), 2)
        self.post_childbirth_trauma = False
        self.children_count = 0

    def update_class_privileges(self):
        if self.social_class == "Wealthy": 
            self.food_security_chance = 0.99
        elif self.social_class == "Middle": 
            self.food_security_chance = 0.75
        else: 
            self.food_security_chance = 0.40

# =========================================================================
# SETUP ENVIRONMENT INTERFACE
# =========================================================================
def gather_world_settings():
    print("\n-- ENVIRONMENT CALIBRATION INTERFACE ---")
    spaces_config = {
        "Europe": {"capacity": 100},  # Expanded capacity to prevent instant day-1 choking
        "Asia": {"capacity": 150},
        "Africa": {"capacity": 100}
    }
    seed_pop = int(input("Enter starting seed population size (e.g., 120): "))
    male_ratio = float(input("Enter percentage of males (0 to 100): ")) / 100.0
    eco_choice = input("Select Economy: (1 -> Barter, 2 -> Cash-Paid): ").strip()
    economy_mode = "cash" if eco_choice == "2" else "barter"
    
    return {
        "spaces": spaces_config,
        "seed_pop": seed_pop,
        "male_ratio": male_ratio,
        "economy_mode": economy_mode
    }

# =========================================================================
# SINGLE-CORE METABOLISM & PROCESSOR (UPGRADED WITH DYNAMIC RISK)
# =========================================================================
def process_metabolism(world_spaces, settings, current_year):
    for space_name, population_dict in world_spaces.items():
        if not population_dict: continue
        
        max_capacity = settings["spaces"][space_name]["capacity"]
        is_overcrowded = len(population_dict) > max_capacity
        
        surviving_population = {}
        
        for civ_id, civ in population_dict.items():
            civ.age += 1
            if civ.age >= 14: civ.puberty_passed = True
            
            # Food Logic
            secured_food = random.random() < civ.food_security_chance
            if not secured_food and settings["economy_mode"] == "cash" and civ.savings >= 20:
                civ.savings -= 20
                secured_food = True
                
            if secured_food: civ.food_supply = min(100, civ.food_supply + 20)
            else: civ.food_supply = max(0, civ.food_supply - 25)
            
            # Energy Calculation
            energy_drain = 10
            if is_overcrowded:
                energy_drain += random.randint(15, 30)
                civ.food_supply = max(0, civ.food_supply - 10)
            else:
                if civ.food_supply > 50: civ.energy = min(100, civ.energy + 10)
                
            if civ.food_supply < 30: energy_drain += 20
            civ.energy = max(0, civ.energy - energy_drain)
            
            # Mortality Checks
            death_triggered = False
            cause = ""
            
            if civ.energy <= 0:
                death_triggered = True
                cause = "Starvation (No Food)" if civ.food_supply <= 0 else "Energy Exhaustion (Overcrowding)"
            elif civ.age > 85:
                death_triggered = True
                cause = "Old Age / Biological Limit"
            else:
                # IMPLEMENTED DYNAMIC RISKING: Class directly determines immunity
                if civ.social_class == "Poor":
                    risk = 0.06
                elif civ.social_class == "Middle":
                    risk = 0.03
                else: # Wealthy
                    risk = 0.005
                
                # Infants have slightly higher strain, old age creeps up slowly
                age_factor = 0.05 if civ.age <= 5 else (0.0 if civ.age <= 45 else (civ.age - 45) * 0.01)
                if civ.post_childbirth_trauma:
                    risk += 0.15
                    civ.post_childbirth_trauma = False
                    
                if random.random() < (risk + age_factor):
                    death_triggered = True
                    cause = "Medieval Disease / Die-Roll"
                    
            if death_triggered:
                simulation_analytics["total_deaths_by_cause"][cause] += 1
                simulation_analytics["deaths_by_class"][civ.social_class] += 1
                tracker.register_death(civ.id, current_year, cause, civ.energy, civ.social_class)
            else:
                surviving_population[civ_id] = civ
                
        world_spaces[space_name] = surviving_population
        
    return world_spaces

# =========================================================================
# STRATEGIC CLASS-BASED MATCHMAKING ENGINE
# =========================================================================
def process_lovers(world_spaces, id_counter, settings, current_year):
    diminishing_returns = {0: 1.0, 1: 0.8, 2: 0.5, 3: 0.2, 4: 0.0}
    class_values = {"Wealthy": 3, "Middle": 2, "Poor": 1}

    for space_name, population_dict in world_spaces.items():
        if len(population_dict) < 2: continue
        
        # 1. Isolate eligible pools locally within this sector
        eligible_males = [
            m for m in population_dict.values() 
            if m.gender == 'M' and m.puberty_passed and m.energy >= 40
        ]
        eligible_females = [
            f for f in population_dict.values() 
            if f.gender == 'F' and f.puberty_passed and f.energy >= 40
        ]
        
        # If either gender pool is empty, no reproduction can physically happen here
        if not eligible_males or not eligible_females: continue
        
        # 2. CHOOSE THE RUNNERS (The 5 Selected Bachelors)
        # We assign statistical weights based on your request: Rich preferred, but Middle and Poor still run
        male_weights = []
        for m in eligible_males:
            if m.social_class == "Wealthy":
                male_weights.append(10.0) # 10x higher priority ticket
            elif m.social_class == "Middle":
                male_weights.append(4.0)  # Moderate priority
            else:
                male_weights.append(1.0)  # Base priority for Poor
                
        # Determine how many runners we can actually pull (up to 5, bounded by available pool)
        num_runners = min(5, len(eligible_males))
        
        # Pull the bachelors using our economic probability rules
        # (We use a loop to avoid picking the exact same person twice)
        selected_bachelors = []
        temp_males = list(eligible_males)
        temp_weights = list(male_weights)
        
        for _ in range(num_runners):
            if not temp_males: break
            chosen_bachelor = random.choices(temp_males, weights=temp_weights, k=1)[0]
            selected_bachelors.append(chosen_bachelor)
            
            # Remove him from the temporary choice pool so he isn't picked twice
            idx = temp_males.index(chosen_bachelor)
            temp_males.pop(idx)
            temp_weights.pop(idx)

        # Track women who get pregnant so they don't have multiple different fathers in 1 year
        pregnant_mothers = set()

        # 3. SERIAL COURTING LOOP (The "Up to 20 Door Checks" Rule)
        for father in selected_bachelors:
            # Gather up to 20 random available women for this specific guy to court
            available_women = [f for f in eligible_females if f.id not in pregnant_mothers]
            if not available_women: break # No available single women left in the sector
            
            # Pick a maximum sample of 20 random women
            courting_sample_size = min(20, len(available_women))
            women_to_court = random.sample(available_women, courting_sample_size)
            
            # The Bachelor goes door-to-door knocking
            for mother in women_to_court:
                mutual_love = (mother.attraction_drive + father.attraction_drive) / 2.0
                fertility = diminishing_returns.get(min(mother.children_count, 4), 0.0)
                
                # Determine the household economic bracket
                higher_class = mother.social_class if class_values[mother.social_class] >= class_values[father.social_class] else father.social_class
                
                if higher_class == "Wealthy": success_threshold = 0.65
                elif higher_class == "Middle": success_threshold = 0.45
                else: success_threshold = 0.25 
                
                # Roll the dice at this specific door
                if random.random() < (mutual_love * fertility * success_threshold):
                    # SUCCESSFUL MATCH FOUND! 
                    mother.energy = max(10, mother.energy - 20)
                    father.energy = max(10, father.energy - 10)
                    mother.post_childbirth_trauma = True
                    pregnant_mothers.add(mother.id)
                    
                    # Twins / Triplets Probability Check
                    litter_roll = random.random()
                    if litter_roll < 0.01:      
                        num_babies = 3
                        generation_tag = "F1_Generation (Triplets)"
                    elif litter_roll < 0.05:    
                        num_babies = 2
                        generation_tag = "F1_Generation (Twins)"
                    else:                       
                        num_babies = 1
                        generation_tag = "F1_Generation"
                    
                    # Spawn the offspring
                    for _ in range(num_babies):
                        mother.children_count += 1
                        father.children_count += 1
                        
                        baby = Civilian(id_counter, random.choice(['M', 'F']), 0, higher_class, settings["economy_mode"])
                
                        if settings["economy_mode"] == "cash" and higher_class == "Wealthy":
                            baby.savings = 50.0
                        elif settings["economy_mode"] == "cash" and higher_class == "Middle":
                            baby.savings = 15.0
                            
                        # Permanently write them into the simulation sector and ledger
                        population_dict[id_counter] = baby
                        tracker.register_birth(id_counter, baby.gender, current_year, generation=generation_tag)
                        id_counter += 1
                        
                    # CRITICAL: He successfully found love! He stops running and goes home for the year
                    break 

    return world_spaces, id_counter

def process_social_flux(world_spaces, settings):
    for space_dict in world_spaces.values():
        for civ in space_dict.values():
            if civ.social_class == "Poor" and civ.energy >= 80 and civ.food_supply >= 80:
                civ.social_class = "Middle"
                civ.update_class_privileges()
            elif civ.social_class == "Middle":
                if settings["economy_mode"] == "cash" and civ.savings >= 250:
                    civ.social_class = "Wealthy"
                    civ.update_class_privileges()
                elif settings["economy_mode"] == "barter" and civ.energy >= 90:
                    civ.social_class = "Wealthy"
                    civ.update_class_privileges()
            elif civ.social_class == "Wealthy" and civ.energy < 40:
                civ.social_class = "Middle"
                civ.update_class_privileges()
            elif civ.social_class == "Middle" and civ.energy < 30:
                civ.social_class = "Poor"
                civ.update_class_privileges()
    return world_spaces

# =========================================================================
# MAIN SYSTEM LOOPS
# =========================================================================
def main():
    print("=======================================================================")
    print(" OPTIMIZED SINGLE-THREAD STRATEGIC LIFE SIMULATOR")
    print("=======================================================================")
    
    settings = gather_world_settings()
    world_spaces = {name: {} for name in settings["spaces"].keys()}
    space_list = list(world_spaces.keys())
    
    total_males = int(settings["seed_pop"] * settings["male_ratio"])
    total_females = settings["seed_pop"] - total_males
    genders = (['M'] * total_males) + (['F'] * total_females)
    random.shuffle(genders)
    
    id_counter = 1
    for i in range(settings["seed_pop"]):
        gender = genders[i]
        # Seeds start as Poor to observe structural economic climb
        civ = Civilian(id_counter, gender, random.randint(16, 35), "Poor", settings["economy_mode"])
        
        if settings["economy_mode"] == "cash":
            civ.savings = random.uniform(30, 80)
            
        world_spaces[random.choice(space_list)][id_counter] = civ
        tracker.register_birth(id_counter, civ.gender, birth_year=1, generation="Original Seed")
        id_counter += 1
        
    print(f"\n[✓] Environment active. Processing computations sequentially...")
    
    year = 1
    remaining_auto_years = 0  
    
    while True:
        total_alive = sum(len(s) for s in world_spaces.values())
        if total_alive == 0:
            print("\n[-] Population hit complete extinction thresholds. Game Over.")
            break
            
        print(f"\n [YEAR CONFIGURATION DIAL: {year:02d}]")
        print(f"   -> Global Demographic Registry Status: {total_alive} Active Living Entities")
        for space_name, space_dict in world_spaces.items():
            cap = settings["spaces"][space_name]["capacity"]
            print(f"      ▪ Spatial Sub-Sector '{space_name:<6}': {len(space_dict):>3} / {cap} Allocation Capacity")
        
        if remaining_auto_years <= 0:
            print("\n[ CONTROL PANEL]")
            print("1 -> Advance simulation automatically by X years")
            print("2 -> Absolute Termination (Exit & Save)")
            turn_choice = input("Select an option (1-2): ").strip()
            
            if turn_choice == "2":
                break
            elif turn_choice == "1":
                try:
                    remaining_auto_years = int(input("How many years do you want to advance?: "))
                    if remaining_auto_years <= 0: continue
                except ValueError: continue
            else: continue
        
        # Sequential Core Execution Phases (Blazing Fast, No Multi-processing Overheads)
        world_spaces = process_metabolism(world_spaces, settings, current_year=year)
        world_spaces, id_counter = process_lovers(world_spaces, id_counter, settings, current_year=year)
        world_spaces = process_social_flux(world_spaces, settings)
        
        year += 1
        remaining_auto_years -= 1  

    print("\n=======================================================================")
    print(" HISTORICAL SIMULATION ANALYTICS DICTIONARY REPORT")
    print("=======================================================================")
    print(f"Total simulated history reached: {year - 1} operational years.")
    
    print("\n[ MORTALITY BREAKDOWN BY BIOLOGICAL CAUSE]")
    for cause, count in simulation_analytics["total_deaths_by_cause"].items():
        print(f" ▪ {cause:<35} : {count:>4} deaths")
        
    print("\n[💸 SOCIAL STRATIFICATION MORTALITY RISK]")
    for s_class, count in simulation_analytics["deaths_by_class"].items():
        print(f" ▪ {s_class:<12} Class Population Casualties : {count:>4} deaths")
    print("=======================================================================\n")

    tracker.update_living_stats(world_spaces=world_spaces)
    tracker.export_to_json()

if __name__ == "__main__":
    main()
