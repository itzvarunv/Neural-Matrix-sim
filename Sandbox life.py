import random
import json
import os
import sys

# --- PERSISTENT DISK STORAGE ---
AI_BRAIN_FILE = "ai_sandbox_brain.json"
AI_LINEAGE_FILE = "ai_lineage_report.json"

# Mock/Stubs for classes to ensure independent execution if missing from Life_simulator
try:
    from Life_simulator import Civilian, tracker
except ImportError:
    # Safe Fallback Engine if your exact baseline imports shift
    class Civilian:
        def __init__(self, id, gender, age, social_class, economy_mode):
            self.id = id
            self.gender = gender
            self.age = age
            self.social_class = social_class
            self.energy = 100
            self.savings = 15.0 if social_class == "Middle" else (50.0 if social_class == "Wealthy" else 0.0)
            self.puberty_passed = True
            self.children_count = 0
            self.attraction_drive = random.uniform(0.5, 1.0)
            self.post_childbirth_trauma = False

    class MockTracker:
        def register_birth(self, *args, **kwargs): pass
    tracker = MockTracker()

class AISandboxBrain:
    def __init__(self):
        # Expected inputs: [self_energy, self_savings, density_ratio, age, proposal_partner_class]
        self.weights = [random.uniform(-0.5, 0.5) for _ in range(5)]
        self.load_brain()

    def think(self, inputs):
        dot_product = sum(i * w for i, w in zip(inputs, self.weights))
        dot_product = max(-20, min(20, dot_product))
        try:
            import math
            return 1.0 / (1.0 + math.exp(-dot_product))
        except:
            return 0.5

    def receive_reward(self, value):
        """Updates weights via backpropagation values."""
        for i in range(len(self.weights)):
            self.weights[i] += value * 0.01

    def update_weights(self, value):
        """Bridge alias to ensure compatibility with courtship data tracking."""
        self.receive_reward(value)

    def save_brain(self):
        with open(AI_BRAIN_FILE, 'w') as f:
            json.dump(self.weights, f)

    def load_brain(self):
        if os.path.exists(AI_BRAIN_FILE):
            try:
                with open(AI_BRAIN_FILE, 'r') as f:
                    self.weights = json.load(f)
            except:
                pass

def simulate_npc_metabolism_and_mortality(world_spaces, current_year, ai_stats):
    for space_name, population_dict in world_spaces.items():
        dead_list = []
        for entity_id, civ in population_dict.items():
            # 1. Age and natural degradation
            civ.age += 1
            civ.energy = max(0, civ.energy - random.randint(5, 15))
            
            # Cash economy interactions
            if hasattr(civ, 'savings'):
                civ.savings += random.choice([-5.0, 10.0, 15.0]) # Dynamic jobs
                if civ.energy < 40 and civ.savings >= 10:
                    civ.savings -= 10
                    civ.energy = min(100, civ.energy + 30) # Buy food

            # 2. Mortality Checks
            is_dead = False
            cause = ""
            
            if civ.energy <= 0:
                is_dead = True
                cause = "Energy Exhaustion (Overcrowding / Starvation)"
            elif civ.age > 75:
                is_dead = True
                cause = "Old Age / Biological Limit"
            elif civ.age > 15 and random.random() < (0.02 + (civ.age * 0.001)):
                is_dead = True
                cause = "Medieval Disease / Die-Roll"

            if is_dead:
                dead_list.append(entity_id)
                if entity_id == "AI":
                    ai_stats["final_status"] = "Dead"
                    ai_stats["cause_of_death"] = cause
                    ai_stats["year_of_death"] = current_year

        # Purge the dead from the active continent arrays
        for d_id in dead_list:
            population_dict.pop(d_id)
            
    return world_spaces, ai_stats

def process_lovers_with_consent(world_spaces, id_counter, settings, current_year, ai_stats):
    if "courtship_rejections" not in ai_stats:
        ai_stats["courtship_rejections"] = []
    if "marriage_history" not in ai_stats:
        ai_stats["marriage_history"] = []

    ai_sector = None
    ai_obj = None
    for sector_name, civilians in world_spaces.items():
        if "AI" in civilians:
            ai_sector = sector_name
            ai_obj = civilians["AI"]
            break

    if not ai_obj or ai_sector == "Dead":
        return world_spaces, id_counter, ai_stats

    # FIXED: Only allow OPPOSITE sex suitors to propose to the AI Agent
    suitors = [
        c for cid, c in world_spaces[ai_sector].items() 
        if cid != "AI" and getattr(c, 'status', 'Alive') == 'Alive' and c.gender != ai_obj.gender
    ]
    
    if suitors:
        partner = random.choice(suitors)
        partner_class_mapped = {"Poor": 1, "Middle": 2, "Wealthy": 3}.get(partner.social_class, 1)

        inputs = [
            ai_obj.energy / 100.0,
            ai_obj.savings / 100.0,
            len(world_spaces[ai_sector]) / 100.0,
            ai_obj.age / 100.0,
            partner_class_mapped / 3.0
        ]
        
        consent_probability = ai_obj.sandbox_brain.think(inputs)
        
        partner_snapshot = {
            "year": current_year,
            "ai_age": ai_obj.age,
            "partner_id": partner.id,
            "partner_gender": partner.gender,
            "partner_class": partner.social_class,
            "partner_savings": getattr(partner, 'savings', 0.0),
            "ai_energy_at_time": ai_obj.energy,
            "ai_wallet_at_time": ai_obj.savings
        }

        if consent_probability >= 0.5:
            # AI ACCEPTS
            marriage_successful = random.random() < 0.7 
            
            if marriage_successful:
                partner_snapshot["marriage_outcome"] = "Successful Union"
                ai_stats["marriage_history"].append(partner_snapshot)
                
                # FIXED: True biological pregnancy check (One male, one female required)
                has_female = (ai_obj.gender == 'F' and 14 <= ai_obj.age <= 45) or (partner.gender == 'F' and 14 <= partner.age <= 45)
                has_male = (ai_obj.gender == 'M') or (partner.gender == 'M')
                
                if has_female and has_male:
                    id_counter += 1
                    ai_obj.children_count += 1
                    ai_stats["total_kids_count"] += 1
                    ai_stats["children_produced_ids"].append(id_counter)
                    
                    if ai_obj.gender == 'F':
                        ai_obj.energy = max(10, ai_obj.energy - 20)
                        ai_obj.post_childbirth_trauma = True
                    else:
                        ai_obj.energy = max(10, ai_obj.energy - 10) # Father energy tax applied
                    
                    ai_obj.sandbox_brain.update_weights(20.0)
            else:
                partner_snapshot["marriage_outcome"] = "Failed Match Roll"
                ai_stats["marriage_history"].append(partner_snapshot)
                ai_obj.sandbox_brain.update_weights(-0.5)
        else:
            # AI REJECTS
            partner_snapshot["rejection_reason_score"] = round(consent_probability, 4)
            ai_stats["courtship_rejections"].append(partner_snapshot)
            ai_obj.sandbox_brain.update_weights(-0.1)

    return world_spaces, id_counter, ai_stats

def process_ai_migration_choice(world_spaces, settings):
    ai_current_space = None
    ai_object = None
    for space_name, pop_dict in world_spaces.items():
        if "AI" in pop_dict:
            ai_current_space = space_name
            ai_object = pop_dict["AI"]
            break
            
    if not ai_object or ai_object.energy < 40: return world_spaces

    max_capacity = settings["spaces"][ai_current_space]["capacity"]
    density_ratio = len(world_spaces[ai_current_space]) / max_capacity if max_capacity > 0 else 1.0
    
    inputs = [ai_object.energy / 100.0, ai_object.savings / 100.0, density_ratio, ai_object.age / 100.0, 0.5]
    migration_urge = ai_object.sandbox_brain.think(inputs)
    
    if migration_urge > 0.75 and ai_object.savings >= 5.0:
        target_space = min(world_spaces.keys(), key=lambda k: len(world_spaces[k]))
        if target_space != ai_current_space:
            print(f"✈️  [AI ACTION] AI evaluated high stress! Spending 5 cash to migrate from '{ai_current_space}' to '{target_space}'!")
            ai_object.savings -= 5.0
            world_spaces[target_space]["AI"] = world_spaces[ai_current_space].pop("AI")
            
    return world_spaces

def run_sandbox():
    print("="*65)
    print("      🧠 ADVANCED COGNITIVE SIMULATION SANDBOX ENGINE v2")
    print("="*65)
    ai_gender = input("Select biological sex for the unique AI Agent (M/F): ").strip().upper()
    if ai_gender not in ['M', 'F']: ai_gender = 'M'
    
    settings = {
        "economy_mode": "cash",
        "spaces": {"Europe": {"capacity": 100}, "Asia": {"capacity": 150}, "Africa": {"capacity": 100}}
    }
    
    world_spaces = {"Europe": {}, "Asia": {}, "Africa": {}}
    id_counter = 2
    
    # Initialize 120 baseline NPCs distributed across continents
    continents = ["Europe", "Asia", "Africa"]
    for i in range(120):
        chosen_sector = continents[i % 3]
        civ = Civilian(id_counter, random.choice(['M', 'F']), random.randint(16, 35), "Middle", "cash")
        world_spaces[chosen_sector][id_counter] = civ
        id_counter += 1

    # Initialize Explicit AI Entity
    ai_agent = Civilian("AI", ai_gender, 18, "Middle", "cash")
    ai_agent.sandbox_brain = AISandboxBrain()
    world_spaces["Europe"]["AI"] = ai_agent

    # Deep Tracking Dictionary Structure
    ai_stats = {
        "agent_assigned_gender": ai_gender,
        "total_kids_count": 0,
        "children_produced_ids": [],
        "final_status": "Alive",
        "cause_of_death": "N/A",
        "year_of_death": "N/A",
        "final_savings_balance": 0.0,
        "final_energy_level": 100,
        "biometric_history_log": []
    }

    print("\n[✓] Calibration complete. Launching 40-year simulation timeline...\n")

    for year in range(1, 41):
        # 1. Telemetry Capture phase
        total_npcs = sum(len(pop) for pop in world_spaces.values())
        eur_pop = len(world_spaces["Europe"])
        asi_pop = len(world_spaces["Asia"])
        afr_pop = len(world_spaces["Africa"])
        
        # Pull AI Vitals for the live console
        ai_location, ai_energy, ai_savings, ai_age = "Dead", 0, 0.0, 0
        for space_name, pop_dict in world_spaces.items():
            if "AI" in pop_dict:
                ai_location = space_name
                ai_energy = pop_dict["AI"].energy
                ai_savings = pop_dict["AI"].savings
                ai_age = pop_dict["AI"].age
                break

        # Log active historical biometric log entry if alive
        if ai_location != "Dead":
            snapshot = {
                "year": year,
                "age": ai_age,
                "location_sector": ai_location,
                "energy": ai_energy,
                "savings_bank_balance": ai_savings,
                "total_children_so_far": ai_stats["total_kids_count"]
            }
            ai_stats["biometric_history_log"].append(snapshot)
            ai_stats["final_energy_level"] = ai_energy
            ai_stats["final_savings_balance"] = ai_savings

        # PRINT LIVE SCOREBOARD DIAL
        print(f"[YEAR: {year:02d}] Global Population: {total_npcs} | [EU: {eur_pop} | AS: {asi_pop} | AF: {afr_pop}]")
        print(f"  ↳  AI STATUS -> Age: {ai_age} | Energy: {ai_energy} | Wallet: ${ai_savings:.2f} | Loc: {ai_location} | Kids: {ai_stats['total_kids_count']}")

        # Interrupt the matrix instantly if the AI dies so you can see exactly why
        if ai_location == "Dead":
            print(f"\n [CRITICAL ALERT] The AI Agent died on Year {year}! Cause: {ai_stats['cause_of_death']}\n")
            break

        # 2. Cycle Environment Engines Sequential Order
        world_spaces, ai_stats = simulate_npc_metabolism_and_mortality(world_spaces, year, ai_stats)
        world_spaces = process_ai_migration_choice(world_spaces, settings)
        world_spaces, id_counter, ai_stats = process_lovers_with_consent(world_spaces, id_counter, settings, year, ai_stats)

    # Absolute Simulation Wrap up and File Sync
    if "AI" in world_spaces[ai_location if ai_location != "Dead" else "Europe"]:
        world_spaces[ai_location]["AI"].sandbox_brain.save_brain()
    
    with open(AI_LINEAGE_FILE, 'w') as f:
        json.dump(ai_stats, f, indent=4)
        
    print("="*65)
    print(f"[✓] Execution Finished. Deep Biometric Biography stored to '{AI_LINEAGE_FILE}'")
    print("="*65)

if __name__ == "__main__":
    run_sandbox()
